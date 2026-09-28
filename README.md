# 🎿 Ski Marketplace Search Tool

An automated, persistent search tool that monitors multiple used ski marketplaces (Facebook Marketplace, eBay, Craigslist, and more) and sends real-time Telegram notifications when matching listings are found.

## Features

- 🔍 **Multi-Marketplace Search**: Monitors Facebook Marketplace, eBay, Craigslist, and extensible to other platforms
- 📱 **Telegram Notifications**: Instant alerts with listing details, price, location, and recency
- 🔄 **GitHub-Based Configuration**: Update search criteria remotely from any device
- 🎯 **Smart Matching**: Fuzzy matching and specification extraction (ski length, width, condition)
- 🗄️ **Deduplication**: Tracks seen listings to avoid duplicate notifications
- ⏰ **Persistent Monitoring**: Runs continuously with configurable search intervals
- 🐳 **Docker Support**: Easy deployment with Docker and docker-compose
- 📊 **Match Scoring**: Weighted scoring system to prioritize best matches

## Quick Start

Looking for **K2 Way Back 92 skis** in **160-168cm** range? This tool will find them for you!

### Prerequisites

- Python 3.10+ or Docker
- Telegram account (for notifications)
- GitHub account (for storing search criteria)
- Optional: eBay developer account (for eBay API access)

### Installation

#### Recommended: Portainer on Proxmox

The easiest way to deploy is using Portainer on a Proxmox LXC container:

1. **Create Ubuntu LXC** in Proxmox (enable "Nesting" feature)
2. **Install Docker** in the container
3. **Deploy via Portainer UI** - point to this repo
4. **Configure** environment variables in Portainer
5. **Done!** No command-line needed

See **[PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md)** for complete step-by-step guide.

#### Alternative: Docker Compose (VPS, Raspberry Pi, etc.)

```bash
# Clone the repository
git clone https://github.com/yourusername/SkiSearchTool.git
cd SkiSearchTool

# Copy environment template
cp .env.example .env

# Edit .env with your credentials (see SETUP.md for details)
nano .env

# Deploy with Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Alternative: Python Virtual Environment (Development)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### First Time Setup

See **[SETUP.md](SETUP.md)** for detailed step-by-step instructions including:
- Creating a Telegram bot
- Setting up GitHub configuration repo
- Getting eBay API credentials
- Configuring search criteria

## Documentation

- **[PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md)** ⭐ - Complete Portainer deployment guide (RECOMMENDED)
- **[SETUP.md](SETUP.md)** - Step-by-step setup guide for all deployment methods
- **[DESIGN.md](DESIGN.md)** - Comprehensive system architecture and design documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick commands and configuration reference
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Module organization and development guide
- **[ROADMAP.md](ROADMAP.md)** - Implementation phases and development roadmap
- **[criteria/ski_search.yaml](criteria/ski_search.yaml)** - Example search criteria file

## How It Works

1. **Configure Search Criteria**: Create YAML files defining what you're looking for (model, size, price, location)
2. **Store on GitHub**: Push criteria files to your GitHub repo for remote access and version control
3. **Automated Monitoring**: The tool runs continuously, checking marketplaces at your specified interval
4. **Smart Matching**: Extracts specifications from listings and scores them against your criteria
5. **Instant Alerts**: Sends Telegram notifications for high-quality matches with all listing details

## Example Search Criteria

```yaml
search_name: "K2 Way Back 92 Search"
enabled: true

keywords:
  required:
    - "K2"
    - ["Way Back", "Wayback"]
  optional:
    - "92"

specifications:
  width_underfoot:
    min: 90
    max: 94
    unit: mm
  
  length:
    min: 160
    max: 168
    preferred: [162, 164, 166]
    unit: cm

price:
  max: 500
  currency: USD
  alert_if_below: 250

marketplaces:
  - name: "facebook"
    enabled: true
  - name: "ebay"
    enabled: true
  - name: "craigslist"
    enabled: true

search_frequency:
  interval: 15
  unit: minutes
```

## Supported Marketplaces

| Marketplace | Status | Method | Notes |
|-------------|--------|--------|-------|
| eBay | ✅ Supported | Official API | Stable, reliable |
| Craigslist | ✅ Supported | Web Scraping | Simple, effective |
| Facebook Marketplace | 🚧 Planned | Web Scraping | May require browser automation |
| Geartrade | 🔜 Future | TBD | Outdoor gear marketplace |
| Pinkbike | 🔜 Future | TBD | Popular for gear |

## Architecture

```
GitHub Repo (Criteria) → Search Orchestrator → Marketplace Scrapers
                              ↓
                      Matching Engine → Filter & Score
                              ↓
                      Notification Service → Telegram
                              ↓
                      Database (Seen Listings)
```

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

## Usage

```bash
# Run once
python main.py

# Run as daemon (continuous monitoring)
python main.py --daemon

# Dry run (no notifications)
python main.py --dry-run

# Test specific marketplace
python main.py --marketplace craigslist

# Verbose logging
python main.py --verbose
```

## Adding New Search Criteria

Simply add a new YAML file to your GitHub configuration repo:

1. Go to your `ski-search-config` repository
2. Create `criteria/boots_search.yaml` (or any name)
3. Copy the format from `ski_search.yaml` and customize
4. Commit and push
5. Tool automatically picks up new criteria on next run!

No need to restart the service or modify code. 🎉

## Deployment Options

- **Raspberry Pi**: Low-cost, always-on home server
- **Cloud VPS**: DigitalOcean, Linode, AWS EC2 (~$6/month)
- **Serverless**: AWS Lambda + EventBridge (~$1/month)
- **Docker**: Run anywhere with container support
- **Local Machine**: Simple cron job or scheduled task

See [DESIGN.md](DESIGN.md) section 10 for detailed deployment guides.

## Project Status

- [x] Design and architecture complete
- [ ] Core search orchestrator
- [ ] GitHub criteria sync
- [ ] Craigslist scraper
- [ ] eBay API integration
- [ ] Facebook Marketplace scraper
- [ ] Telegram notifications
- [ ] Database and deduplication
- [ ] Docker deployment
- [ ] Testing and documentation

## Contributing

This is currently a personal project, but feel free to:
- Open issues for bugs or feature requests
- Submit PRs for improvements
- Share your custom marketplace scrapers
- Suggest additional marketplaces to support

## Security & Ethics

- **API Keys**: Never commit credentials to git, use environment variables
- **Rate Limiting**: Respects marketplace rate limits and robots.txt
- **Ethical Scraping**: Random delays, appropriate user agents, no aggressive crawling
- **Privacy**: Only stores listing URLs and metadata, no personal seller information

## License

MIT License - feel free to use and modify for your own ski hunting!

## Acknowledgments

Built for backcountry skiers who want to find great deals without constantly checking multiple marketplaces.

---

**Happy Ski Hunting! 🎿⛷️🏔️**

*Currently searching for: K2 Way Back 92, 160-168cm, good condition, under $500* 
