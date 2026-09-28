# Quick Reference Guide

Quick commands and configuration reference for the Ski Marketplace Search Tool.

---

## 🚀 Quick Start (Portainer)

1. Create LXC in Proxmox (enable Nesting)
2. Install Docker: `apt install docker.io`
3. Deploy in Portainer: **Stacks** → **Add Stack** → Repository URL
4. Add env vars (see below)
5. Deploy!

Full guide: [PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md)

---

## 📋 Environment Variables

Required for all deployments:

```bash
# GitHub Configuration (for storing search criteria)
GITHUB_REPO_URL=yourusername/ski-search-config
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxx

# Telegram Bot (for notifications)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

Optional:

```bash
# eBay API (optional, for eBay searches)
EBAY_APP_ID=your_app_id
EBAY_CERT_ID=your_cert_id
EBAY_DEV_ID=your_dev_id

# Application Settings
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
SEARCH_INTERVAL_MINUTES=15            # How often to search
MAX_NOTIFICATIONS_PER_HOUR=20         # Rate limit
TZ=America/Los_Angeles                # Timezone
```

---

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# View logs (real-time)
docker-compose logs -f

# View logs (specific lines)
docker-compose logs --tail 100

# Stop
docker-compose down

# Restart
docker-compose restart

# Update to latest
docker-compose pull
docker-compose up -d

# View status
docker-compose ps

# Enter container shell
docker exec -it ski-marketplace-search /bin/bash

# View resource usage
docker stats ski-marketplace-search
```

---

## 🗄️ Database Commands

```bash
# Access database from container
docker exec -it ski-marketplace-search \
  sqlite3 /app/data/ski_search.db

# Or from host (if data volume is local)
sqlite3 ./data/ski_search.db
```

Useful queries:

```sql
-- View recent search runs
SELECT * FROM search_runs 
ORDER BY started_at DESC 
LIMIT 10;

-- View seen listings
SELECT * FROM seen_listings 
ORDER BY first_seen DESC 
LIMIT 20;

-- Count listings by marketplace
SELECT marketplace, COUNT(*) 
FROM seen_listings 
GROUP BY marketplace;

-- View notifications sent today
SELECT * FROM notifications 
WHERE DATE(sent_at) = DATE('now');

-- Find high-scoring matches
SELECT * FROM seen_listings 
WHERE match_score > 0.8 
ORDER BY match_score DESC;
```

---

## 📁 File Locations

### In Container:
```
/app/                          # Application root
├── data/
│   └── ski_search.db         # SQLite database
├── logs/
│   ├── ski_search.log        # Main application log
│   └── errors.log            # Error log
└── cache/
    └── criteria/             # Cached GitHub criteria
```

### On Host (Docker volumes):
```
./data/ski_search.db          # Database
./logs/ski_search.log         # Logs
./cache/                      # Cache
```

### Portainer Volumes:
```
ski-search-data              # Database volume
ski-search-logs              # Logs volume
ski-search-cache             # Cache volume
```

---

## 🔍 Marketplace URLs

### Craigslist
```
https://seattle.craigslist.org/search/sga?query=k2+way+back+92
```

Regions: seattle, portland, denver, saltlakecity, bozeman, etc.

### eBay
```
https://www.ebay.com/sch/i.html?_nkw=k2+way+back+92+skis
```

### Facebook Marketplace
```
https://www.facebook.com/marketplace/seattle/search?query=k2+way+back+92
```

---

## 🎯 Search Criteria YAML

Basic structure:

```yaml
search_name: "My Search"
enabled: true

keywords:
  required: ["keyword1", "keyword2"]
  optional: ["optional1"]
  exclude: ["broken", "damaged"]

specifications:
  length:
    min: 160
    max: 168
    unit: cm

price:
  max: 500
  currency: USD

marketplaces:
  - name: "craigslist"
    enabled: true

search_frequency:
  interval: 15
  unit: minutes
```

Full example: [criteria/ski_search.yaml](criteria/ski_search.yaml)

---

## 🔔 Telegram Bot Setup

1. Open Telegram, search **@BotFather**
2. Send: `/newbot`
3. Choose name and username
4. Save the **bot token**
5. Send message to your bot
6. Search **@userinfobot**, send message
7. Save your **Chat ID**

---

## 🐙 GitHub Setup

1. Create repo: `ski-search-config`
2. Add folder: `criteria/`
3. Add file: `criteria/ski_search.yaml`
4. Create Personal Access Token:
   - Settings → Developer settings → Personal access tokens
   - Scope: `repo` (full control)
   - Save token

---

## 📊 Monitoring

### Health Check
```bash
# Docker
docker inspect ski-marketplace-search --format='{{.State.Health.Status}}'

# Manual health check
docker exec ski-marketplace-search python -c "
from utils.health_check import HealthMonitor
print(HealthMonitor().check_system_health())
"
```

### Resource Usage
```bash
# CPU and Memory
docker stats ski-marketplace-search --no-stream

# Disk usage
docker exec ski-marketplace-search df -h

# Database size
docker exec ski-marketplace-search du -h /app/data/ski_search.db
```

### Logs
```bash
# Last 100 lines
docker logs --tail 100 ski-marketplace-search

# Follow logs
docker logs -f ski-marketplace-search

# Specific time range
docker logs --since 1h ski-marketplace-search
docker logs --since "2024-01-01T00:00:00" ski-marketplace-search
```

---

## 🔧 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs ski-marketplace-search

# Check environment variables
docker exec ski-marketplace-search env | grep -E 'GITHUB|TELEGRAM|EBAY'

# Verify .env file
cat .env
```

### No notifications
```bash
# Test Telegram connection
docker exec ski-marketplace-search python -c "
from notifications.telegram_notifier import TelegramNotifier
TelegramNotifier().send_test_message()
"

# Check Telegram token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Scraper errors
```bash
# View scraper logs
docker exec ski-marketplace-search tail -f /app/logs/scrapers.log

# Test individual scraper
docker exec ski-marketplace-search python -c "
from scrapers.craigslist_scraper import CraigslistScraper
scraper = CraigslistScraper()
print(scraper.test())
"
```

### Database locked
```bash
# Stop container
docker-compose down

# Backup database
cp ./data/ski_search.db ./data/ski_search.db.backup

# Restart
docker-compose up -d
```

---

## 💾 Backup & Restore

### Backup Database
```bash
# Using SQLite backup command
docker exec ski-marketplace-search \
  sqlite3 /app/data/ski_search.db ".backup /app/data/backup.db"

# Copy to host
docker cp ski-marketplace-search:/app/data/backup.db ./backup.db

# Or just copy the file
cp ./data/ski_search.db ./backup/ski_search_$(date +%Y%m%d).db
```

### Restore Database
```bash
# Stop container
docker-compose down

# Restore file
cp ./backup.db ./data/ski_search.db

# Start container
docker-compose up -d
```

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh
docker exec ski-marketplace-search \
  sqlite3 /app/data/ski_search.db \
  ".backup /app/data/backup_$(date +%Y%m%d_%H%M%S).db"
```

Add to cron: `0 3 * * * /path/to/backup.sh`

---

## 🔄 Updates

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild container
docker-compose down
docker-compose build
docker-compose up -d
```

### Update Search Criteria
```bash
# In your ski-search-config repo
git add criteria/
git commit -m "Update search criteria"
git push

# Tool automatically pulls changes within minutes
```

### Update Dependencies
```bash
# Update requirements.txt
# Then rebuild:
docker-compose build --no-cache
docker-compose up -d
```

---

## 📈 Performance Tuning

### Resource Limits (docker-compose.yml)
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'      # Adjust based on load
      memory: 512M     # Increase if needed
    reservations:
      cpus: '0.1'
      memory: 128M
```

### Search Frequency
Adjust in criteria YAML:
```yaml
search_frequency:
  interval: 30  # Increase to reduce load
  unit: minutes
```

### Rate Limiting
```bash
# In .env
SEARCH_INTERVAL_MINUTES=20
MAX_NOTIFICATIONS_PER_HOUR=10
```

---

## 🆘 Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Check documentation**: 
   - [DESIGN.md](DESIGN.md) - Architecture
   - [SETUP.md](SETUP.md) - Full setup guide
   - [PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md) - Portainer guide
3. **Test components**:
   - GitHub sync
   - Telegram bot
   - Database connection
4. **Open GitHub issue** with logs and configuration (redact secrets!)

---

## 🔗 Useful Links

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **eBay Developers**: https://developer.ebay.com/
- **Docker Documentation**: https://docs.docker.com/
- **Portainer Docs**: https://docs.portainer.io/
- **SQLite Docs**: https://www.sqlite.org/docs.html

---

**Last Updated**: September 28, 2026  
**Version**: 1.0
