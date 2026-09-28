# 🎿 Ski Marketplace Search Tool

Automated, persistent search tool to monitor and search for used ski listings matching a given set of criteria, notifying via Telegram when matching listings are found.


### Project Status
 - [ ] Design and architecture complete
 - [ ] Core search orchestrator
 - [ ] GitHub criteria sync
 - [ ] Craigslist scraper
 - [ ] eBay API integration
 - [ ] Facebook Marketplace scraper
 - [ ] Telegram notifications
 - [ ] Database and deduplication
 - [ ] Docker deployment
 - [ ] Testing and documentation


### Installation

#### Recommended: Portainer on Proxmox

The easiest way to deploy is using Portainer on a Proxmox LXC container:


### First Time Setup

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

All marketplaces use **free, proven, open-source libraries**:

| Marketplace | Status | Library | Method | 
|-------------|--------|---------|--------|
| **eBay** | Ready | ebaysdk-python (Official) | API 
| **Craigslist** | Ready | python-craigslist | Library 
| **ShopGoodwill** | Ready | requests + BeautifulSoup | Scraper 
| **Facebook Marketplace** | PLANNED | playwright 
| Geartrade TBD | TBD | TBD
| Pinkbike TBD | TBD | TBD

**See [LIBRARY_GUIDE.md](LIBRARY_GUIDE.md) for detailed library documentation.**

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


## Usage



