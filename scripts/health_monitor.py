"""
Health Monitor for Platinum Tier

Monitors all services and sends alerts if any fail.
Supports PM2 services, Docker containers, and system health.

Usage:
    python health_monitor.py
"""

import subprocess
import time
import os
import sys
import smtplib
import json
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class HealthMonitor:
    """
    Health monitoring for Platinum Tier deployment.
    
    Monitors:
    - PM2 services (orchestrator, watchers, sync)
    - Docker containers (Odoo, DB, Nginx)
    - System resources (disk, memory, CPU)
    - Ollama service
    - Git sync status
    
    Alerts via:
    - Console logs
    - Email
    - Webhook (optional)
    """
    
    def __init__(self):
        """Initialize health monitor."""
        self.check_interval = int(os.environ.get('HEALTH_CHECK_INTERVAL', 60))
        self.alert_email = os.environ.get('ALERT_EMAIL', '')
        self.alert_webhook = os.environ.get('ALERT_WEBHOOK', '')
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_pass = os.environ.get('SMTP_PASS', '')
        
        # Services to monitor
        self.pm2_services = [
            'cloud-orchestrator',
            'cloud-watcher-gmail',
            'cloud-watcher-filesystem',
            'vault-sync',
            'health-monitor'
        ]
        
        self.docker_services = [
            'odoo',
            'odoo-db',
            'odoo-nginx'
        ]
        
        # Setup logging
        self.logs_path = Path('./AI_Employee_Vault/Logs')
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_path / f'health_monitor_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        # Alert thresholds
        self.disk_threshold = 90  # Alert if > 90% used
        self.memory_threshold = 90  # Alert if > 90% used
        self.cpu_threshold = 90  # Alert if > 90% used
        
        self.log("=" * 60)
        self.log("Health Monitor initialized")
        self.log("=" * 60)
        self.log(f"  PM2 Services: {len(self.pm2_services)}")
        self.log(f"  Docker Services: {len(self.docker_services)}")
        self.log(f"  Check Interval: {self.check_interval}s")
        self.log(f"  Alert Email: {self.alert_email or 'Not configured'}")
        self.log(f"  Alert Webhook: {self.alert_webhook or 'Not configured'}")
    
    def log(self, message: str):
        """Log a message."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception as e:
            print(f"  Warning: Could not write to log file: {e}")
    
    def check_pm2_service(self, service_name: str) -> bool:
        """
        Check if PM2 service is running.
        
        Args:
            service_name: Name of PM2 service
            
        Returns:
            True if running
        """
        try:
            result = subprocess.run(
                ['pm2', 'describe', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'online' in result.stdout.lower():
                return True
            else:
                self.log(f"PM2 service '{service_name}' is not online")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"Timeout checking PM2 service '{service_name}'")
            return False
        except FileNotFoundError:
            self.log("PM2 is not installed or not in PATH")
            return False
        except Exception as e:
            self.log(f"Error checking PM2 service '{service_name}': {e}")
            return False
    
    def check_docker_service(self, service_name: str) -> bool:
        """
        Check if Docker container is running.
        
        Args:
            service_name: Name of Docker container
            
        Returns:
            True if running
        """
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format={{.State.Status}}', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'running' in result.stdout.lower():
                return True
            else:
                self.log(f"Docker service '{service_name}' is not running")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"Timeout checking Docker service '{service_name}'")
            return False
        except FileNotFoundError:
            self.log("Docker is not installed or not in PATH")
            return False
        except Exception as e:
            self.log(f"Error checking Docker service '{service_name}': {e}")
            return False
    
    def check_ollama(self) -> bool:
        """
        Check if Ollama service is running.
        
        Returns:
            True if running
        """
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True
            else:
                self.log("Ollama service is not responding")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Timeout checking Ollama service")
            return False
        except FileNotFoundError:
            self.log("Ollama is not installed or not in PATH")
            return False
        except Exception as e:
            self.log(f"Error checking Ollama service: {e}")
            return False
    
    def check_disk_space(self) -> tuple:
        """
        Check available disk space.
        
        Returns:
            (is_healthy, usage_percent)
        """
        try:
            if os.name == 'nt':  # Windows
                import shutil
                total, used, free = shutil.disk_usage("C:\\")
                usage = (used / total) * 100
            else:  # Linux/Mac
                result = subprocess.run(
                    ['df', '-h', '/'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    usage = int(parts[4].replace('%', ''))
                else:
                    return True, 0
            
            is_healthy = usage < self.disk_threshold
            
            if not is_healthy:
                self.log(f"Disk space critical: {usage}% used (threshold: {self.disk_threshold}%)")
            
            return is_healthy, usage
            
        except subprocess.TimeoutExpired:
            self.log("Timeout checking disk space")
            return True, 0
        except Exception as e:
            self.log(f"Error checking disk space: {e}")
            return True, 0
    
    def check_memory(self) -> tuple:
        """
        Check available memory.
        
        Returns:
            (is_healthy, usage_percent)
        """
        try:
            if os.name == 'nt':  # Windows
                import psutil
                memory = psutil.virtual_memory()
                usage = memory.percent
            else:  # Linux/Mac
                result = subprocess.run(
                    ['free', '-m'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    total = int(parts[1])
                    used = int(parts[2])
                    usage = int((used / total) * 100)
                else:
                    return True, 0
            
            is_healthy = usage < self.memory_threshold
            
            if not is_healthy:
                self.log(f"Memory critical: {usage}% used (threshold: {self.memory_threshold}%)")
            
            return is_healthy, usage
            
        except subprocess.TimeoutExpired:
            self.log("Timeout checking memory")
            return True, 0
        except ImportError:
            self.log("psutil not installed (optional for Windows)")
            return True, 0
        except Exception as e:
            self.log(f"Error checking memory: {e}")
            return True, 0
    
    def check_cpu(self) -> tuple:
        """
        Check CPU usage.
        
        Returns:
            (is_healthy, usage_percent)
        """
        try:
            if os.name == 'nt':  # Windows
                import psutil
                cpu = psutil.cpu_percent(interval=1)
                usage = cpu
            else:  # Linux/Mac
                result = subprocess.run(
                    ['top', '-bn1'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse CPU from top output
                for line in result.stdout.split('\n'):
                    if 'cpu' in line.lower():
                        parts = line.split(',')
                        for part in parts:
                            if 'id' in part.lower():
                                idle = float(part.split()[0])
                                usage = 100 - idle
                                break
                        break
                else:
                    return True, 0
            
            is_healthy = usage < self.cpu_threshold
            
            if not is_healthy:
                self.log(f"CPU critical: {usage}% used (threshold: {self.cpu_threshold}%)")
            
            return is_healthy, usage
            
        except subprocess.TimeoutExpired:
            self.log("Timeout checking CPU")
            return True, 0
        except ImportError:
            self.log("psutil not installed (optional for Windows)")
            return True, 0
        except Exception as e:
            self.log(f"Error checking CPU: {e}")
            return True, 0
    
    def send_email_alert(self, subject: str, message: str):
        """
        Send email alert.
        
        Args:
            subject: Email subject
            message: Email body
        """
        if not self.alert_email or not self.smtp_user or not self.smtp_pass:
            self.log("Email alerts not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = f"[AI Employee Alert] {subject}"
            
            body = f"""
Health Alert from AI Employee

{message}

Timestamp: {datetime.now().isoformat()}
Host: {os.uname().nodename if os.name != 'nt' else 'Windows'}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            
            self.log(f"Email alert sent to {self.alert_email}")
            
        except Exception as e:
            self.log(f"Failed to send email alert: {e}")
    
    def send_webhook_alert(self, subject: str, message: str):
        """
        Send webhook alert (e.g., Slack, Discord, Teams).
        
        Args:
            subject: Alert subject
            message: Alert body
        """
        if not self.alert_webhook:
            return
        
        try:
            import requests
            
            payload = {
                'text': f"🚨 AI Employee Alert\n\n*{subject}*\n\n{message}",
                'username': 'AI Employee Health Monitor',
                'icon_emoji': ':robot_face:'
            }
            
            response = requests.post(self.alert_webhook, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.log("Webhook alert sent")
            else:
                self.log(f"Webhook alert failed: {response.status_code}")
                
        except ImportError:
            self.log("requests not installed, cannot send webhook alerts")
        except Exception as e:
            self.log(f"Failed to send webhook alert: {e}")
    
    def send_alert(self, service_name: str, status: str, details: str = ''):
        """
        Send alert for service failure.
        
        Args:
            service_name: Name of failed service
            status: Service status
            details: Additional details
        """
        subject = f"{service_name} is {status}"
        message = f"""
Service: {service_name}
Status: {status}
Details: {details or 'N/A'}

Immediate action may be required.
        """
        
        self.log(f"ALERT: {subject}")
        
        # Send email alert
        self.send_email_alert(subject, message)
        
        # Send webhook alert
        self.send_webhook_alert(subject, message)
    
    def restart_pm2_service(self, service_name: str) -> bool:
        """
        Attempt to restart a PM2 service.
        
        Args:
            service_name: Name of PM2 service
            
        Returns:
            True if restart successful
        """
        try:
            self.log(f"Attempting to restart PM2 service: {service_name}")
            
            subprocess.run(
                ['pm2', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Verify restart
            time.sleep(5)
            return self.check_pm2_service(service_name)
            
        except Exception as e:
            self.log(f"Failed to restart {service_name}: {e}")
            return False
    
    def run(self):
        """Run health monitoring loop."""
        self.log("=" * 60)
        self.log("Health Monitor loop started")
        self.log("=" * 60)
        
        consecutive_failures = {}
        
        try:
            while True:
                issues = []
                
                # Check PM2 services
                for service in self.pm2_services:
                    if not self.check_pm2_service(service):
                        issues.append(f"PM2 service '{service}' is down")
                        
                        # Track consecutive failures
                        consecutive_failures[service] = consecutive_failures.get(service, 0) + 1
                        
                        # Auto-restart after 2 consecutive failures
                        if consecutive_failures[service] >= 2:
                            self.log(f"Auto-restarting {service}...")
                            if self.restart_pm2_service(service):
                                consecutive_failures[service] = 0
                                issues.remove(issues[-1])
                    else:
                        consecutive_failures[service] = 0
                
                # Check Docker services
                for service in self.docker_services:
                    if not self.check_docker_service(service):
                        issues.append(f"Docker service '{service}' is down")
                
                # Check Ollama
                if not self.check_ollama():
                    issues.append("Ollama service is not responding")
                
                # Check system resources
                disk_healthy, disk_usage = self.check_disk_space()
                if not disk_healthy:
                    issues.append(f"Disk space critical: {disk_usage}%")
                
                memory_healthy, memory_usage = self.check_memory()
                if not memory_healthy:
                    issues.append(f"Memory critical: {memory_usage}%")
                
                cpu_healthy, cpu_usage = self.check_cpu()
                if not cpu_healthy:
                    issues.append(f"CPU critical: {cpu_usage}%")
                
                # Send alerts
                for issue in issues:
                    service_name = issue.split("'")[1] if "'" in issue else issue.split(":")[0]
                    self.send_alert(service_name, 'DOWN', issue)
                
                # Log status
                if issues:
                    self.log(f"Issues found: {len(issues)}")
                    for issue in issues:
                        self.log(f"  - {issue}")
                else:
                    self.log("All services healthy ✓")
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.log("Stopped by user")
        except Exception as e:
            self.log(f"Fatal error in health monitor: {e}")
            raise


def main():
    """Main entry point."""
    monitor = HealthMonitor()
    monitor.run()


if __name__ == '__main__':
    main()
