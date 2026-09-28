# Tonight's Implementation Plan

Quick, incremental setup to get the ski search tool running.

---

## Phase 1: Setup (15 minutes)

### 1.1 Create GitHub Config Repo
```bash
# On GitHub web UI:
# Create new repo: ski-search-config (can be private)
# Add folder: criteria/
# Copy criteria/ski_search.yaml from this repo
# Customize: location, price, regions
```

### 1.2 Create Telegram Bot
```
1. Open Telegram, message @BotFather
2. Send: /newbot
3. Save bot token
4. Message your bot with /start
5. Message @userinfobot
6. Save your chat ID
```

### 1.3 GitHub Personal Access Token
```
GitHub Settings → Developer settings → Personal access tokens
Create token with 'repo' scope
Save token
```

---

## Phase 2: Local Test (30 minutes)

### 2.1 Clone and Configure
```bash
git clone https://github.com/danster44/SkiSearchTool.git
cd SkiSearchTool
cp .env.example .env
nano .env  # Fill in your tokens
```

### 2.2 Test Components
```bash
# Create virtual env
python -m venv venv
source venv/bin/activate

# Install deps
pip install python-craigslist python-telegram-bot PyGithub python-dotenv pyyaml

# Test Telegram
python -c "
from telegram import Bot
bot = Bot(token='YOUR_TOKEN')
bot.send_message(chat_id='YOUR_CHAT_ID', text='Test from ski search!')
print('✅ Telegram works!')
"

# Test Craigslist
python -c "
from craigslist import CraigslistForSale
cl = CraigslistForSale(site='seattle', category='sss')
results = list(cl.get_results(filters={'query': 'skis'}, limit=3))
print(f'✅ Found {len(results)} Craigslist listings')
for r in results:
    print(f'  - {r[\"name\"]}: {r[\"price\"]}')
"
```

---

## Phase 3: Proxmox Deployment (20 minutes)

### 3.1 Create LXC Container
```
Proxmox UI:
- Create CT → Ubuntu 22.04
- RAM: 1GB, Cores: 1, Disk: 8GB
- Options → Features → ✅ Nesting
- Start container
```

### 3.2 Install Docker
```bash
# SSH into LXC
apt update && apt install -y docker.io docker-compose git
systemctl enable --now docker
```

### 3.3 Install Portainer (optional but recommended)
```bash
docker run -d \
  --name=portainer \
  --restart=always \
  -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# Access at http://<LXC-IP>:9000
```

---

## Phase 4: Deploy App (15 minutes)

### 4.1 Via Portainer (Easy)
```
1. Portainer → Stacks → Add Stack
2. Name: ski-search
3. Build method: Repository
4. URL: https://github.com/danster44/SkiSearchTool
5. Compose path: docker-compose.yml
6. Add environment variables:
   - GITHUB_REPO_URL
   - GITHUB_ACCESS_TOKEN
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
7. Deploy
```

### 4.2 Or Via CLI
```bash
# In LXC
git clone https://github.com/danster44/SkiSearchTool.git
cd SkiSearchTool
nano .env  # Add your tokens
docker-compose up -d
docker-compose logs -f
```

---

## Phase 5: Verify (10 minutes)

```bash
# Check container is running
docker ps

# Check logs
docker logs ski-marketplace-search

# Test Telegram notification manually
docker exec -it ski-marketplace-search python -c "
from telegram import Bot
bot = Bot(token='YOUR_TOKEN')
bot.send_message(chat_id='YOUR_CHAT_ID', text='🎿 Ski search is live!')
"

# View criteria sync (once implemented)
docker exec -it ski-marketplace-search ls -la /app/cache/criteria/
```

---

## What Actually Works Right Now

✅ **Docker setup** - container will run  
✅ **Telegram** - can send test messages  
✅ **Libraries** - all proven and ready  
⏳ **Main app** - needs implementation (see ROADMAP.md)

---

## If You Want to Code Tonight

### Quick Win: Implement Craigslist Scraper

```python
# Create: scrapers/craigslist_scraper.py
from craigslist import CraigslistForSale

class CraigslistScraper:
    def search(self, keywords, regions, max_price):
        results = []
        for region in regions:
            cl = CraigslistForSale(site=region, category='sss')
            listings = cl.get_results(
                filters={
                    'query': keywords,
                    'max_price': max_price
                },
                limit=50
            )
            results.extend(list(listings))
        return results

# Test it
scraper = CraigslistScraper()
listings = scraper.search('k2 way back 92', ['seattle', 'portland'], 500)
print(f'Found {len(listings)} listings')
```

---

## Total Time: ~90 minutes

- Setup: 15 min
- Testing: 30 min  
- Proxmox: 20 min
- Deploy: 15 min
- Verify: 10 min

---

## Next Session (Tomorrow+)

Follow ROADMAP.md Phase 1:
1. Config loading
2. GitHub sync
3. Complete scrapers
4. Matching logic
5. Database
6. Scheduler

---

**Priority Tonight:** Get infrastructure running and test the libraries work.
