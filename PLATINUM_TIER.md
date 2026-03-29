# Platinum Tier Implementation Guide

**Personal AI Employee Hackathon 0**
**Tier:** Platinum (Always-On Cloud + Local Executive)
**Estimated Setup Time:** 60+ hours

## Overview

This document provides step-by-step instructions for implementing the Platinum Tier of the Personal AI Employee system. Platinum Tier builds upon Gold Tier by adding:

1. **24/7 Cloud Deployment** - Always-on watchers and orchestrator
2. **Work-Zone Specialization** - Cloud vs Local domain ownership
3. **Delegated Agents via Synced Vault** - Multi-agent coordination
4. **Odoo on Cloud VM** - HTTPS, backups, health monitoring

## Platinum Tier Requirements

### All Gold Tier Requirements ✅

1. ✅ All Silver Tier requirements
2. ✅ Full cross-domain integration (Personal + Business)
3. ✅ Odoo accounting integration via MCP
4. ✅ Facebook, Instagram, Twitter integration
5. ✅ Multiple MCP servers
6. ✅ Weekly Business Audit with CEO Briefing
7. ✅ Error recovery and audit logging
8. ✅ Ralph Wiggum loop for autonomous completion

### Platinum Tier Additions

1. **Cloud Deployment (24/7)**
   - Deploy to Oracle Cloud Free VM (or AWS/Azure/GCP)
   - Always-on watchers and orchestrator
   - Health monitoring and auto-restart
   - Remote access via SSH

2. **Work-Zone Specialization**
   - **Cloud owns:** Email triage, draft replies, social post drafts/scheduling
   - **Local owns:** Approvals, WhatsApp session, payments/banking, final send/post actions

3. **Delegated Agents via Synced Vault**
   - Git-based vault sync between Cloud and Local
   - Claim-by-move rule for task ownership
   - Single-writer rule for Dashboard.md
   - Cloud writes to /Updates/, Local merges to Dashboard.md

4. **Odoo on Cloud VM**
   - Deploy Odoo Community on cloud VM
   - HTTPS with Let's Encrypt
   - Automated backups
   - Health monitoring
   - MCP integration for draft-only accounting

5. **Security**
   - Secrets never sync (.env, tokens, WhatsApp sessions, banking creds)
   - Cloud never stores payment tokens or banking credentials
   - Vault sync includes only markdown/state files

## Architecture

### Platinum Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PLATINUM TIER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      CLOUD VM (24/7)                          │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Cloud Agent (Ollama + qwen-agent)                     │  │  │
│  │  │  - Email triage & draft replies                        │  │  │
│  │  │  - Social post drafts & scheduling                     │  │  │
│  │  │  - Draft-only accounting actions                       │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │  │
│  │  │  Gmail   │ │  File    │ │ LinkedIn │ │   FB/IG  │         │  │
│  │  │  Watcher │ │  Watcher │ │  Poster  │ │  Watcher │         │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Odoo Community (HTTPS + Backups)                      │  │  │
│  │  │  - Invoice creation (draft)                            │  │  │
│  │  │  - Financial reports                                   │  │  │
│  │  │  - Partner management                                  │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Synced Vault (Git)                                    │  │  │
│  │  │  - /Needs_Action/Cloud/                                │  │  │
│  │  │  - /Plans/Cloud/                                       │  │  │
│  │  │  - /Updates/ (Cloud writes)                            │  │  │
│  │  │  - /In_Progress/<agent>/ (claim-by-move)               │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              │ Git Sync (markdown/state only)       │
│                              │ NO SECRETS                           │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      LOCAL MACHINE                            │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Local Agent (Ollama + qwen-agent)                     │  │  │
│  │  │  - Human-in-the-loop approvals                         │  │  │
│  │  │  - Final send/post actions                             │  │  │
│  │  │  - Payment processing                                  │  │  │
│  │  │  - WhatsApp session (QR code)                          │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                      │  │
│  │  │ WhatsApp │ │ Twitter  │ │ Payments │                      │  │
│  │  │ Watcher  │ │ Watcher  │ │ Gateway  │                      │  │
│  │  └──────────┘ └──────────┘ └──────────┘                      │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Synced Vault (Local)                                  │  │  │
│  │  │  - /Needs_Action/Local/                                │  │  │
│  │  │  - /Pending_Approval/ (human reviews)                  │  │  │
│  │  │  - /Approved/ → Cloud executes                         │  │  │
│  │  │  - Dashboard.md (Local merges Updates)                 │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Security Boundaries                                          │  │
│  │  - Secrets (.env, tokens) NEVER sync                         │  │
│  │  - WhatsApp sessions LOCAL ONLY                              │  │
│  │  - Banking credentials LOCAL ONLY                            │  │
│  │  - Payment tokens LOCAL ONLY                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Deploy Cloud VM

**Option A: Oracle Cloud Free Tier**

```bash
# 1. Sign up for Oracle Cloud Free Tier
# Visit: https://www.oracle.com/cloud/free/

# 2. Create VM instance
# - Shape: VM.Standard.A1.Flex (4 OCPU, 24GB RAM - Free)
# - Image: Ubuntu 22.04 LTS
# - SSH keys: Generate and download

# 3. Connect to VM
ssh -i your_key ubuntu@<vm-public-ip>
```

**Option B: AWS EC2 Free Tier**

```bash
# 1. Sign up for AWS Free Tier
# Visit: https://aws.amazon.com/free/

# 2. Launch EC2 instance
# - Type: t2.micro (1 vCPU, 1GB RAM - Free)
# - AMI: Ubuntu 22.04 LTS
# - SSH keys: Generate and download

# 3. Connect to instance
ssh -i your_key.pem ubuntu@<ec2-public-ip>
```

### 2. Setup Cloud VM

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Qwen model
ollama pull qwen2.5:7b

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Git
sudo apt install -y git
```

### 3. Deploy Odoo on Cloud VM

```bash
# Create Odoo directory
mkdir -p ~/odoo
cd ~/odoo

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-data:/var/lib/odoo
      - ./odoo.conf:/etc/odoo/odoo.conf
    restart: unless-stopped

  db:
    image: postgres:15
    container_name: odoo-db
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_DB=odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: odoo-nginx
    depends_on:
      - odoo
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped

volumes:
  odoo-data:
  postgres-data:
EOF

# Create Odoo config
cat > odoo.conf << 'EOF'
[options]
admin_passwd = your_admin_password
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
data_dir = /var/lib/odoo
EOF

# Create Nginx config (for HTTPS)
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name your-domain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://odoo:8069;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Start Odoo
docker-compose up -d

# Get SSL certificate (Let's Encrypt)
sudo apt install -y certbot
sudo mkdir -p /var/www/certbot
sudo certbot certonly --webroot -w /var/www/certbot -d your-domain.com

# Copy certificates to nginx ssl folder
sudo mkdir -p ~/odoo/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ~/odoo/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ~/odoo/ssl/

# Restart nginx
docker-compose restart nginx
```

### 4. Setup Cloud Agent

```bash
# Create project directory
mkdir -p ~/ai-employee-cloud
cd ~/ai-employee-cloud

# Clone your repository
git clone <your-repo-url> .

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd scripts
pip install -r requirements.txt

# Create .env file (CLOUD SECRETS ONLY)
cat > ../.env << 'EOF'
# Cloud AI Configuration
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b

# Cloud-specific settings
DEPLOYMENT_MODE=cloud
CLOUD_DOMAIN=your-domain.com

# Odoo Configuration (Cloud)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your_odoo_password

# Git Sync Configuration
GIT_REMOTE_URL=<your-git-repo-url>
SYNC_INTERVAL=300

# DO NOT INCLUDE:
# - WhatsApp sessions
# - Banking credentials
# - Payment tokens
# - Local-only secrets
EOF

# Setup PM2 for process management
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'cloud-orchestrator',
      script: 'scripts/orchestrator.py',
      interpreter: 'python',
      args: '--vault ../AI_Employee_Vault --ollama --continuous --interval 60',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      restart_delay: 5000,
      max_restarts: 10,
      watch: false
    },
    {
      name: 'cloud-watcher-gmail',
      script: 'scripts/gmail_watcher.py',
      interpreter: 'python',
      args: '../AI_Employee_Vault',
      restart_delay: 5000,
      max_restarts: 10,
      watch: false
    },
    {
      name: 'cloud-watcher-filesystem',
      script: 'scripts/filesystem_watcher.py',
      interpreter: 'python',
      args: '../AI_Employee_Vault',
      restart_delay: 5000,
      max_restarts: 10,
      watch: false
    },
    {
      name: 'vault-sync',
      script: 'scripts/vault_sync.py',
      interpreter: 'python',
      args: '../AI_Employee_Vault',
      restart_delay: 5000,
      max_restarts: 10,
      watch: false
    },
    {
      name: 'health-monitor',
      script: 'scripts/health_monitor.py',
      interpreter: 'python',
      args: '',
      restart_delay: 5000,
      max_restarts: 10,
      watch: false
    }
  ]
};
EOF

# Start all services
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 startup
pm2 startup
# Run the command it outputs
```

### 5. Setup Vault Sync

```bash
# Create vault sync script
cat > scripts/vault_sync.py << 'EOF'
"""
Vault Sync Script for Platinum Tier

Syncs vault between Cloud and Local using Git.
Implements claim-by-move rule and single-writer Dashboard.md rule.
"""

import subprocess
import time
import os
from pathlib import Path
from datetime import datetime

class VaultSync:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.git_remote = os.environ.get('GIT_REMOTE_URL', '')
        self.sync_interval = int(os.environ.get('SYNC_INTERVAL', 300))
        
        # Directories
        self.needs_action_cloud = self.vault_path / 'Needs_Action' / 'Cloud'
        self.needs_action_local = self.vault_path / 'Needs_Action' / 'Local'
        self.in_progress = self.vault_path / 'In_Progress'
        self.updates = self.vault_path / 'Updates'
        
        # Ensure directories exist
        for folder in [self.needs_action_cloud, self.needs_action_local, 
                       self.in_progress, self.updates]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def git_pull(self):
        """Pull latest changes from remote."""
        try:
            subprocess.run(['git', 'pull', '--rebase'], 
                         cwd=str(self.vault_path), 
                         check=True, 
                         capture_output=True)
            print(f"[{datetime.now()}] Git pull successful")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] Git pull failed: {e}")
            return False
    
    def git_push(self):
        """Push local changes to remote."""
        try:
            subprocess.run(['git', 'add', '.'], 
                         cwd=str(self.vault_path), 
                         check=True, 
                         capture_output=True)
            
            subprocess.run(['git', 'commit', '-m', f'Auto-sync {datetime.now().isoformat()}'], 
                         cwd=str(self.vault_path), 
                         check=True, 
                         capture_output=True)
            
            subprocess.run(['git', 'push'], 
                         cwd=str(self.vault_path), 
                         check=True, 
                         capture_output=True)
            
            print(f"[{datetime.now()}] Git push successful")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] Git push failed: {e}")
            return False
    
    def claim_task(self, agent_name: str, task_file: Path) -> bool:
        """
        Claim a task by moving it to In_Progress/<agent>/.
        Returns True if successfully claimed.
        """
        if not task_file.exists():
            return False
        
        agent_folder = self.in_progress / agent_name
        agent_folder.mkdir(parents=True, exist_ok=True)
        
        try:
            dest = agent_folder / task_file.name
            task_file.rename(dest)
            print(f"[{datetime.now()}] Task claimed by {agent_name}: {task_file.name}")
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Failed to claim task: {e}")
            return False
    
    def write_update(self, update_type: str, content: str):
        """Write an update to Updates/ folder for Local to merge."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        update_file = self.updates / f'{update_type}_{timestamp}.md'
        
        update_content = f"""---
type: {update_type}
created: {datetime.now().isoformat()}
source: cloud
---

{content}
"""
        update_file.write_text(update_content, encoding='utf-8')
        print(f"[{datetime.now()}] Update written: {update_file.name}")
    
    def run(self):
        """Run sync loop."""
        print(f"[{datetime.now()}] Vault Sync started")
        print(f"  Vault: {self.vault_path}")
        print(f"  Remote: {self.git_remote}")
        print(f"  Interval: {self.sync_interval}s")
        
        while True:
            # Pull latest changes
            self.git_pull()
            
            # Process any updates from Local
            # (Local merges Cloud updates into Dashboard.md)
            
            # Push any Cloud updates
            if any(self.updates.iterdir()):
                self.git_push()
            
            time.sleep(self.sync_interval)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Vault Sync')
    parser.add_argument('vault_path', help='Path to vault')
    args = parser.parse_args()
    
    sync = VaultSync(args.vault_path)
    sync.run()
EOF

# Make executable
chmod +x scripts/vault_sync.py
```

### 6. Setup Health Monitor

```bash
# Create health monitor script
cat > scripts/health_monitor.py << 'EOF'
"""
Health Monitor for Platinum Tier

Monitors all services and sends alerts if any fail.
"""

import subprocess
import time
import os
from datetime import datetime
from pathlib import Path

class HealthMonitor:
    def __init__(self):
        self.check_interval = 60  # seconds
        self.alert_email = os.environ.get('ALERT_EMAIL', '')
        self.services = [
            'cloud-orchestrator',
            'cloud-watcher-gmail',
            'cloud-watcher-filesystem',
            'vault-sync',
            'odoo',
            'odoo-db',
            'odoo-nginx'
        ]
    
    def check_pm2_service(self, service_name: str) -> bool:
        """Check if PM2 service is running."""
        try:
            result = subprocess.run(
                ['pm2', 'describe', service_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and 'online' in result.stdout
        except Exception as e:
            print(f"[{datetime.now()}] Error checking {service_name}: {e}")
            return False
    
    def check_docker_service(self, service_name: str) -> bool:
        """Check if Docker service is running."""
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format={{.State.Status}}', service_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and 'running' in result.stdout
        except Exception as e:
            print(f"[{datetime.now()}] Error checking {service_name}: {e}")
            return False
    
    def send_alert(self, service_name: str, status: str):
        """Send alert email/notification."""
        if not self.alert_email:
            print(f"[{datetime.now()}] ALERT: {service_name} is {status}")
            return
        
        # TODO: Implement email/SMS alert
        print(f"[{datetime.now()}] ALERT: {service_name} is {status}")
        print(f"  Email would be sent to: {self.alert_email}")
    
    def check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                usage = int(parts[4].replace('%', ''))
                return usage < 90  # Alert if > 90% used
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Error checking disk space: {e}")
            return False
    
    def check_memory(self) -> bool:
        """Check available memory."""
        try:
            result = subprocess.run(
                ['free', '-m'],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                total = int(parts[1])
                used = int(parts[2])
                usage_percent = (used / total) * 100
                return usage_percent < 90  # Alert if > 90% used
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Error checking memory: {e}")
            return False
    
    def run(self):
        """Run health monitoring loop."""
        print(f"[{datetime.now()}] Health Monitor started")
        print(f"  Services: {len(self.services)}")
        print(f"  Check interval: {self.check_interval}s")
        
        while True:
            issues = []
            
            # Check PM2 services
            for service in ['cloud-orchestrator', 'cloud-watcher-gmail', 
                           'cloud-watcher-filesystem', 'vault-sync']:
                if not self.check_pm2_service(service):
                    issues.append(f"PM2 service '{service}' is down")
            
            # Check Docker services
            for service in ['odoo', 'odoo-db', 'odoo-nginx']:
                if not self.check_docker_service(service):
                    issues.append(f"Docker service '{service}' is down")
            
            # Check disk space
            if not self.check_disk_space():
                issues.append("Disk space > 90% used")
            
            # Check memory
            if not self.check_memory():
                issues.append("Memory usage > 90%")
            
            # Send alerts
            for issue in issues:
                self.send_alert(issue, 'DOWN')
            
            if issues:
                print(f"[{datetime.now()}] Issues found: {len(issues)}")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"[{datetime.now()}] All services healthy")
            
            time.sleep(self.check_interval)

if __name__ == '__main__':
    monitor = HealthMonitor()
    monitor.run()
EOF

# Make executable
chmod +x scripts/health_monitor.py
```

### 7. Setup Local Machine

```bash
# On your local machine, create .env file (LOCAL SECRETS ONLY)
cat > .env.local << 'EOF'
# Local AI Configuration
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b

# Local-specific settings
DEPLOYMENT_MODE=local

# WhatsApp Session (LOCAL ONLY)
WHATSAPP_SESSION_PATH=./AI_Employee_Vault/Files/whatsapp_session

# Payment Gateway (LOCAL ONLY)
STRIPE_SECRET_KEY=sk_live_xxx
PAYPAL_CLIENT_SECRET=xxx

# Banking Credentials (LOCAL ONLY)
BANK_API_KEY=xxx
BANK_SECRET=xxx

# Git Sync Configuration
GIT_REMOTE_URL=<your-git-repo-url>
SYNC_INTERVAL=300

# DO NOT INCLUDE:
# - Cloud secrets
# - Odoo credentials (Cloud handles this)
EOF

# Add .env.local to .gitignore
echo ".env.local" >> .gitignore

# Setup Local watchers
cd scripts
pip install -r requirements.txt

# Start Local watchers (WhatsApp, Twitter, Payments)
python whatsapp_watcher.py ../AI_Employee_Vault
python twitter_watcher.py ../AI_Employee_Vault
```

### 8. Test Platinum Tier

```bash
# Test Cloud deployment
ssh ubuntu@<cloud-ip>
cd ~/ai-employee-cloud

# Check all services
pm2 status
docker ps

# Test vault sync
python scripts/vault_sync.py ../AI_Employee_Vault

# Test health monitor
python scripts/health_monitor.py

# Test Odoo integration
curl http://localhost:8069

# Test HTTPS
curl https://your-domain.com

# Test full workflow
# 1. Drop test file in Cloud Inbox
# 2. Cloud processes and creates draft
# 3. Sync to Local
# 4. Local approves
# 5. Cloud executes
```

## Vault Structure (Platinum Tier)

```
AI_Employee_Vault/
├── Dashboard.md                    # Local merges Updates
├── Company_Handbook.md
├── Business_Goals.md
├── /Inbox/                         # Drop folder
├── /Needs_Action/
│   ├── /Cloud/                     # Cloud-owned tasks
│   └── /Local/                     # Local-owned tasks
├── /Plans/
│   ├── /Cloud/                     # Cloud agent plans
│   └── /Local/                     # Local agent plans
├── /Done/                          # Completed tasks
├── /Pending_Approval/              # Awaiting human approval (Local)
├── /Approved/                      # Approved for execution
├── /Rejected/                      # Declined actions
├── /In_Progress/                   # Claimed tasks
│   ├── /cloud-agent/
│   └── /local-agent/
├── /Updates/                       # Cloud writes updates here
├── /Signals/                       # Inter-agent communication
├── /Logs/
│   ├── /Cloud/                     # Cloud logs
│   └── /Local/                     # Local logs
├── /Files/                         # Processed files
├── /Invoices/                      # Generated invoices
├── /Briefings/                     # CEO briefings
└── /Audits/                        # Business audits
```

## Security Rules

### Secrets Management

| Secret Type | Stored On | Syncs? |
|-------------|-----------|--------|
| WhatsApp Session | Local ONLY | ❌ NO |
| Banking Credentials | Local ONLY | ❌ NO |
| Payment Tokens | Local ONLY | ❌ NO |
| Stripe/PayPal Keys | Local ONLY | ❌ NO |
| Odoo Credentials | Cloud ONLY | ❌ NO |
| Ollama Model | Both | ✅ YES (model data) |
| Git Credentials | Both | ❌ NO (use SSH keys) |

### .gitignore for Vault Sync

```gitignore
# NEVER sync these
.env
.env.local
.env.cloud
*.key
*.pem
*.crt
whatsapp_session/
banking/
payments/
secrets/

# Sync only markdown and state
*.md
!Dashboard.md
```

## Testing Checklist

### Cloud Deployment ✅

- [ ] VM running 24/7
- [ ] Ollama installed and working
- [ ] Odoo deployed with HTTPS
- [ ] All PM2 services running
- [ ] Health monitor active
- [ ] Vault sync working
- [ ] Remote SSH access working

### Work-Zone Specialization ✅

- [ ] Cloud processes email drafts only
- [ ] Cloud creates social post drafts only
- [ ] Local handles approvals
- [ ] Local handles WhatsApp
- [ ] Local handles payments
- [ ] Claim-by-move rule working

### Vault Sync ✅

- [ ] Git sync working bidirectional
- [ ] No secrets synced
- [ ] Dashboard.md single-writer rule enforced
- [ ] Updates folder working
- [ ] In_Progress claim system working

### Security ✅

- [ ] .env files not synced
- [ ] WhatsApp session local only
- [ ] Banking credentials local only
- [ ] Payment tokens local only
- [ ] HTTPS working for Odoo
- [ ] Firewall configured on Cloud VM

## Troubleshooting

### Cloud VM Issues

**Problem:** VM not accessible

**Solution:**
```bash
# Check security groups/firewall
# Ensure ports 22, 80, 443 are open

# Check VM status in cloud console
# Restart if needed
```

### Vault Sync Issues

**Problem:** Git conflicts

**Solution:**
```bash
cd AI_Employee_Vault
git status
git pull --rebase
# Resolve conflicts manually
git push
```

### Odoo HTTPS Issues

**Problem:** SSL certificate not working

**Solution:**
```bash
# Renew certificate
sudo certbot renew

# Restart nginx
docker-compose restart nginx
```

## Next Steps

### Phase 2: A2A Upgrade

Replace some file handoffs with direct Agent-to-Agent (A2A) messages:

1. Implement direct messaging between Cloud and Local agents
2. Keep vault as audit record
3. Reduce sync latency
4. Add real-time notifications

### Phase 3: Multi-Agent Delegation

Add specialized agents:

1. Email Agent - Handles all email triage
2. Social Media Agent - Manages all social platforms
3. Accounting Agent - Handles invoices and payments
4. Support Agent - Customer service automation

---

*AI Employee v0.4 - Platinum Tier*
*Last Updated: 2026-03-29*
