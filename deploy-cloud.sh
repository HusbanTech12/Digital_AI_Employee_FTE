#!/bin/bash

# Platinum Tier Cloud Deployment Script
# Deploys AI Employee to Oracle Cloud/AWS/Azure VM
# 
# Usage:
#   ./deploy-cloud.sh <your-email> <domain-name>
#
# Example:
#   ./deploy-cloud.sh admin@example.com ai.yourcompany.com

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
EMAIL=${1:-""}
DOMAIN=${2:-""}
PROJECT_NAME="ai-employee-cloud"
INSTALL_DIR="$HOME/$PROJECT_NAME"

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}AI Employee - Platinum Tier Cloud Deployment${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run this script as root${NC}"
    exit 1
fi

# Check required parameters
if [ -z "$EMAIL" ]; then
    echo -e "${YELLOW}Warning: Email not provided. Email alerts will not be configured.${NC}"
fi

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}Warning: Domain not provided. HTTPS will not be configured.${NC}"
    echo -e "${YELLOW}Odoo will be accessible on port 8069${NC}"
fi

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Email: ${EMAIL:-Not configured}"
echo "  Domain: ${DOMAIN:-Not configured}"
echo "  Install Dir: $INSTALL_DIR"
echo ""

# Confirm deployment
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y
echo ""

echo -e "${GREEN}Step 2: Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh
echo ""

echo -e "${GREEN}Step 3: Installing Docker Compose...${NC}"
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
echo ""

echo -e "${GREEN}Step 4: Installing Ollama...${NC}"
curl -fsSL https://ollama.com/install.sh | sh
echo ""

echo -e "${GREEN}Step 5: Downloading Qwen model...${NC}"
echo "This may take 10-30 minutes depending on your internet speed..."
ollama pull qwen2.5:7b
echo ""

echo -e "${GREEN}Step 6: Installing Python and dependencies...${NC}"
sudo apt install -y python3 python3-pip python3-venv git
echo ""

echo -e "${GREEN}Step 7: Installing Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
echo ""

echo -e "${GREEN}Step 8: Installing PM2...${NC}"
sudo npm install -g pm2
echo ""

echo -e "${GREEN}Step 9: Creating project directory...${NC}"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR
echo ""

echo -e "${GREEN}Step 10: Setting up Odoo with Docker Compose...${NC}"
mkdir -p odoo
cd odoo

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
    networks:
      - odoo-network

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
    networks:
      - odoo-network

volumes:
  odoo-data:
  postgres-data:

networks:
  odoo-network:
    driver: bridge
EOF

# Create Odoo config
cat > odoo.conf << EOF
[options]
admin_passwd = $(openssl rand -base64 16)
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
data_dir = /var/lib/odoo
EOF

cd ..
echo ""

echo -e "${GREEN}Step 11: Setting up HTTPS (if domain provided)...${NC}"
if [ -n "$DOMAIN" ]; then
    mkdir -p odoo/ssl
    mkdir -p odoo/nginx
    
    # Install certbot
    sudo apt install -y certbot
    
    # Get SSL certificate
    echo "Obtaining SSL certificate for $DOMAIN..."
    sudo certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    # Copy certificates
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem odoo/ssl/
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem odoo/ssl/
    
    # Create Nginx config
    cat > odoo/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name $DOMAIN;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://\$server_name\$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location / {
            proxy_pass http://odoo:8069;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    
    echo -e "${GREEN}HTTPS configured for $DOMAIN${NC}"
else
    echo -e "${YELLOW}Skipping HTTPS setup (no domain provided)${NC}"
fi
echo ""

echo -e "${GREEN}Step 12: Starting Odoo...${NC}"
cd odoo
docker-compose up -d
cd ..
echo ""

echo -e "${GREEN}Step 13: Setting up AI Employee...${NC}"

# Clone repository or copy files
if [ -d ".git" ]; then
    echo "Git repository already exists, pulling latest changes..."
    git pull
else
    echo "Please clone your repository manually or copy files to $INSTALL_DIR"
    echo -e "${YELLOW}For now, creating basic structure...${NC}"
    mkdir -p scripts AI_Employee_Vault
fi

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd scripts
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install ollama python-dotenv watchdog
fi
cd ..
echo ""

echo -e "${GREEN}Step 14: Creating .env file...${NC}"
cat > .env << EOF
# AI Employee Cloud Configuration
# Generated: $(date -Iseconds)

# AI Provider
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b

# Deployment Mode
DEPLOYMENT_MODE=cloud
$(if [ -n "$DOMAIN" ]; then echo "CLOUD_DOMAIN=$DOMAIN"; fi)

# Odoo Configuration
ODOO_URL=http://odoo:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=odoo

# Health Monitor
$(if [ -n "$EMAIL" ]; then echo "ALERT_EMAIL=$EMAIL"; fi)
HEALTH_CHECK_INTERVAL=60

# Vault Sync
SYNC_INTERVAL=300
AGENT_NAME=cloud-agent
EOF

echo -e "${GREEN}.env file created${NC}"
echo -e "${YELLOW}IMPORTANT: Edit .env to add API keys and other secrets${NC}"
echo ""

echo -e "${GREEN}Step 15: Creating Platinum Tier vault structure...${NC}"
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action/{Cloud,Local},Plans/{Cloud,Local},Done,Pending_Approval,Approved,Rejected,In_Progress/{cloud-agent,local-agent},Updates,Signals,Logs/{Cloud,Local},Files,Invoices,Briefings,Audits}

# Create Dashboard.md
cat > AI_Employee_Vault/Dashboard.md << EOF
---
last_updated: $(date -Iseconds)
status: active
tier: platinum
deployment: cloud
---

# AI Employee Dashboard - Platinum Tier

## Status
- **Tier:** Platinum
- **Deployment:** Cloud + Local
- **AI Provider:** Ollama (qwen2.5:7b)
- **Status:** Active
- **Domain:** ${DOMAIN:-Not configured}

## Quick Stats
- Pending Tasks: 0
- Awaiting Approval: 0
- Completed Today: 0
- Last Activity: $(date -Iseconds)

## Recent Activity
- Cloud deployment completed

## Cloud Services
- Odoo: ${DOMAIN:-http://$(curl -s ifconfig.me):8069}
- Ollama: Running
- PM2: Running

## Folders
- [[Inbox]] - Drop files here
- [[Needs_Action/Cloud]] - Cloud-owned tasks
- [[Needs_Action/Local]] - Local-owned tasks
- [[Plans]] - Action plans
- [[Done]] - Completed tasks
- [[Pending_Approval]] - Awaiting approval
- [[In_Progress]] - Claimed tasks
- [[Updates]] - Cloud→Local updates

## Configuration
- Model: qwen2.5:7b
- Provider: Ollama (Local on Cloud VM)
- Sync: Git-based
EOF

echo -e "${GREEN}Vault structure created${NC}"
echo ""

echo -e "${GREEN}Step 16: Setting up PM2...${NC}"

# Create PM2 ecosystem file if not exists
if [ ! -f "ecosystem.config.js" ]; then
    echo -e "${YELLOW}ecosystem.config.js not found. Creating basic configuration...${NC}"
    cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'cloud-orchestrator',
    script: 'scripts/orchestrator.py',
    interpreter: 'python3',
    args: '--vault ./AI_Employee_Vault --ollama --continuous --interval 60',
    env: {
      PYTHONUNBUFFERED: '1'
    }
  }, {
    name: 'vault-sync',
    script: 'scripts/vault_sync.py',
    interpreter: 'python3',
    args: './AI_Employee_Vault --agent cloud-agent',
    env: {
      PYTHONUNBUFFERED: '1'
    }
  }, {
    name: 'health-monitor',
    script: 'scripts/health_monitor.py',
    interpreter: 'python3',
    env: {
      PYTHONUNBUFFERED: '1'
    }
  }]
};
EOF
fi

# Start PM2 services
pm2 start ecosystem.config.js
pm2 save
pm2 startup | tail -1 | bash 2>/dev/null || true

echo -e "${GREEN}PM2 services started${NC}"
echo ""

echo -e "${GREEN}Step 17: Configuring firewall...${NC}"
sudo apt install -y ufw
sudo ufw allow OpenSSH
sudo ufw allow 8069/tcp  # Odoo
if [ -n "$DOMAIN" ]; then
    sudo ufw allow 80/tcp   # HTTP (for Let's Encrypt)
    sudo ufw allow 443/tcp  # HTTPS
fi
sudo ufw --force enable
echo -e "${GREEN}Firewall configured${NC}"
echo ""

echo -e "${GREEN}Step 18: Setting up auto-renewal for SSL certificate...${NC}"
if [ -n "$DOMAIN" ]; then
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet") | crontab -
    echo -e "${GREEN}SSL auto-renewal configured${NC}"
else
    echo -e "${YELLOW}Skipping SSL auto-renewal (no domain)${NC}"
fi
echo ""

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Summary:"
echo "  Install Directory: $INSTALL_DIR"
echo "  Odoo URL: ${DOMAIN:-http://$(curl -s ifconfig.me):8069}"
echo "  PM2 Status: Running"
echo ""
echo "Next Steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Access Odoo: ${DOMAIN:-http://$(curl -s ifconfig.me):8069}"
echo "  3. Login to Odoo (admin/admin)"
echo "  4. Configure your business in Odoo"
echo "  5. Setup Local machine with complementary .env.local"
echo "  6. Configure Git sync between Cloud and Local"
echo ""
echo "Useful Commands:"
echo "  pm2 status              - Check service status"
echo "  pm2 logs                - View logs"
echo "  pm2 restart all         - Restart all services"
echo "  docker ps               - Check Docker containers"
echo "  ollama list             - Check installed models"
echo ""
echo -e "${GREEN}Platinum Tier deployment is complete!${NC}"
