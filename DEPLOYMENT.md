# 🚀 Deployment Guide

This guide will help you deploy the German Tax Calculator Bot to production.

## Prerequisites

- Python 3.9 or higher
- Git
- A Linux server (Ubuntu 20.04+ recommended)
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Your Telegram User ID

## Getting Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow the instructions to choose a name and username
4. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Save this token securely

## Getting Your Telegram User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Start the bot
3. It will show your user ID (a number like `123456789`)
4. Save this ID - you'll use it as the admin ID

## Deployment Options

### Option 1: Direct Deployment (Simple)

#### Step 1: Clone the Repository

```bash
cd /opt
git clone https://github.com/yourusername/Steuer_Deutschland.git
cd Steuer_Deutschland
```

#### Step 2: Install Dependencies

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip -y

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

Add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_TELEGRAM_ID=your_telegram_id_here
```

Save and exit (Ctrl+X, then Y, then Enter)

#### Step 4: Create Systemd Service

Create a service file:

```bash
sudo nano /etc/systemd/system/tax-bot.service
```

Add this content:

```ini
[Unit]
Description=German Tax Calculator Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Steuer_Deutschland
Environment="PATH=/opt/Steuer_Deutschland/venv/bin"
ExecStart=/opt/Steuer_Deutschland/venv/bin/python /opt/Steuer_Deutschland/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit.

#### Step 5: Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tax-bot

# Start the service
sudo systemctl start tax-bot

# Check status
sudo systemctl status tax-bot
```

#### Step 6: View Logs

```bash
# View real-time logs
sudo journalctl -u tax-bot -f

# View recent logs
sudo journalctl -u tax-bot -n 100
```

### Option 2: Docker Deployment (Recommended)

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data and logs directories
RUN mkdir -p data logs

CMD ["python", "main.py"]
```

#### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  tax-bot:
    build: .
    container_name: german-tax-bot
    restart: always
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Step 3: Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

## Production Configuration

### 1. Security

**Change default admin settings:**
```env
ADMIN_TELEGRAM_ID=your_actual_telegram_id
```

**Configure error logging:**
```env
LOG_LEVEL=WARNING
ERROR_LOG_FILE=logs/errors.log
ENABLE_DETAILED_ERRORS=true
ENABLE_STACK_TRACE=true
```

### 2. Database

**For production, consider using PostgreSQL:**

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database
sudo -u postgres psql
CREATE DATABASE taxbot;
CREATE USER taxbot_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE taxbot TO taxbot_user;
\q
```

**Update .env:**
```env
DATABASE_URL=postgresql+asyncpg://taxbot_user:secure_password@localhost/taxbot
```

### 3. Logging

**Adjust log level for production:**
```env
LOG_LEVEL=WARNING
```

### 4. Update Monitoring

**Configure update check frequency:**
```env
CHECK_UPDATES_INTERVAL_HOURS=12
TAX_SOURCES_CHECK_ENABLED=true
```

## Monitoring

### Health Checks

Create a monitoring script:

```bash
#!/bin/bash
# /opt/scripts/check-bot-health.sh

if systemctl is-active --quiet tax-bot; then
    echo "Bot is running"
    exit 0
else
    echo "Bot is not running!"
    systemctl start tax-bot
    exit 1
fi
```

Make it executable and add to cron:

```bash
chmod +x /opt/scripts/check-bot-health.sh

# Add to crontab (check every 5 minutes)
crontab -e
*/5 * * * * /opt/scripts/check-bot-health.sh >> /var/log/bot-health.log 2>&1
```

### Log Rotation

Create logrotate config:

```bash
sudo nano /etc/logrotate.d/tax-bot
```

Add:

```
/opt/Steuer_Deutschland/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
}
```

## Backup

### Database Backup Script

```bash
#!/bin/bash
# /opt/scripts/backup-bot.sh

BACKUP_DIR="/opt/backups/tax-bot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /opt/Steuer_Deutschland/data/tax_bot.db $BACKUP_DIR/tax_bot_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to crontab (daily at 2 AM):

```bash
0 2 * * * /opt/scripts/backup-bot.sh >> /var/log/bot-backup.log 2>&1
```

## Updates

### Updating the Bot

```bash
cd /opt/Steuer_Deutschland

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart tax-bot
```

### Zero-downtime Updates (Docker)

```bash
cd /opt/Steuer_Deutschland

# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### Bot not responding

```bash
# Check service status
sudo systemctl status tax-bot

# Check logs
sudo journalctl -u tax-bot -n 100

# Restart service
sudo systemctl restart tax-bot
```

### Database issues

```bash
# Check database file permissions
ls -la /opt/Steuer_Deutschland/data/

# Reset database (WARNING: deletes all data)
rm /opt/Steuer_Deutschland/data/tax_bot.db
sudo systemctl restart tax-bot
```

### Memory issues

```bash
# Check memory usage
free -h

# Check bot process
ps aux | grep python

# Restart if using too much memory
sudo systemctl restart tax-bot
```

## Performance Optimization

### 1. Enable Python optimizations

Update systemd service:

```ini
Environment="PYTHONOPTIMIZE=2"
Environment="PYTHONDONTWRITEBYTECODE=1"
```

### 2. Use production-grade database

For high traffic, use PostgreSQL instead of SQLite.

### 3. Enable caching

Add Redis for caching (future enhancement).

## Security Checklist

- [ ] Secure server with firewall (UFW)
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`
- [ ] Use strong passwords
- [ ] Enable fail2ban
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep bot token secret
- [ ] Use environment variables, never hardcode secrets
- [ ] Enable detailed error logging
- [ ] Set up log rotation and monitoring
- [ ] Set up SSL/TLS for database connections

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u tax-bot -n 100`
2. Check error log: `tail -f logs/errors.log`
3. Verify configuration: `cat .env`
4. Test bot token: Try sending a message to your bot
5. Check system resources: `htop` or `top`
6. Review detailed errors: `cat logs/errors_detailed.jsonl | tail -n 10`

For additional help, open an issue on GitHub.
