# Ski Marketplace Search Tool - Design Plan

## 1. System Overview

### Purpose
A persistent, automated search tool that continuously monitors multiple used ski marketplaces (Facebook Marketplace, eBay, Craigslist, and others) for listings matching user-defined criteria, sending real-time Telegram notifications when matches are found.

### Core Requirements
- **Multi-marketplace support**: Facebook Marketplace, eBay, Craigslist, with extensibility for additional platforms
- **Dynamic criteria management**: GitHub-based configuration system for remote updates
- **Real-time notifications**: Telegram integration for instant alerts
- **Initial search criteria**: K2 Way Back skis, 92mm width, 160-168cm length
- **Listing deduplication**: Track previously seen listings to avoid duplicate notifications
- **Recency tracking**: Include how recently a listing was posted

---

## 2. System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ criteria/                                           │    │
│  │   ├── ski_search.yaml                              │    │
│  │   ├── additional_criteria_1.yaml                   │    │
│  │   └── additional_criteria_2.yaml                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Search Orchestrator (Core Engine)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Pull latest criteria from GitHub                  │  │
│  │ 2. Schedule marketplace scrapers                     │  │
│  │ 3. Coordinate search execution                       │  │
│  │ 4. Manage state persistence                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                   Marketplace Scrapers                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Facebook │  │   eBay   │  │Craigslist│  │  Other   │     │
│  │ Scraper  │  │ Scraper  │  │ Scraper  │  │ Scrapers │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Matching & Filtering Engine                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Parse listing data                                 │  │
│  │ 2. Apply search criteria filters                      │  │
│  │ 3. Check against seen listings database               │  │
│  │ 4. Calculate match score/confidence                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Notification Service                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Format message with listing details                   │  │
│  │ Include: Title, Price, Location, Link, Recency        │  │
│  │ Send via Telegram Bot API                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              State Database (SQLite/PostgreSQL)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ - Seen listings (ID, URL, first_seen, last_checked)  │  │
│  │ - Search history                                      │  │
│  │ - Error logs                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack Recommendations
- **Language**: Python 3.10+ (rich ecosystem for web scraping, APIs, scheduling)
- **Web Scraping**: 
  - `playwright` or `selenium` (for JavaScript-heavy sites like Facebook)
  - `beautifulsoup4` + `requests` (for simpler sites like Craigslist)
- **API Integration**: 
  - `ebay-sdk-python` for eBay API
  - `python-telegram-bot` for Telegram
- **Scheduling**: `APScheduler` or cron-based execution
- **Database**: SQLite for simple deployments, PostgreSQL for production
- **Configuration**: `pyyaml` for criteria files
- **Version Control**: GitHub API integration via `PyGithub`

---

## 3. Marketplace Integration Strategies

### 3.1 Facebook Marketplace

**Challenges:**
- Heavy JavaScript rendering
- Anti-bot measures
- No official public API
- Login may be required for full access

**Strategy:**
- Use Playwright/Selenium with headless browser
- Implement rotating user agents
- Add random delays between requests (3-8 seconds)
- Store cookies to maintain session
- Search URL pattern: `https://www.facebook.com/marketplace/[location]/search?query=[keywords]`

**Implementation Approach:**
```python
# Pseudocode
def search_facebook_marketplace(criteria):
    browser = launch_playwright()
    navigate_to_marketplace(criteria.location)
    enter_search_query(criteria.keywords)
    apply_filters(category='sporting_goods', price_range=criteria.price)
    listings = extract_listings()
    return parse_listings(listings)
```

**Rate Limiting:** 1 search per 5-10 minutes to avoid detection

---

### 3.2 eBay

**Advantages:**
- Official Finding API available
- Well-documented
- Rate limits are reasonable

**Strategy:**
- Use eBay Finding API (free tier: 5,000 calls/day)
- Implement OAuth 2.0 authentication
- Search using specific category IDs (Winter Sports equipment)
- Use aspect filters for ski dimensions

**Implementation Approach:**
```python
# Pseudocode
def search_ebay(criteria):
    api = eBayFindingAPI(app_id=config.EBAY_APP_ID)
    response = api.findItemsAdvanced(
        keywords="K2 Way Back 92",
        categoryId="59899",  # Downhill Skiing
        itemFilter=[
            {'name': 'Condition', 'value': 'Used'},
            {'name': 'ListingType', 'value': ['Auction', 'FixedPrice']}
        ],
        aspectFilter=[
            {'name': 'Length', 'value': ['160', '162', '164', '166', '168']}
        ]
    )
    return parse_ebay_response(response)
```

**Rate Limiting:** 1 search per 2-3 minutes (well within API limits)

---

### 3.3 Craigslist

**Advantages:**
- Simple HTML structure
- No JavaScript required
- Tolerant of scraping (no official API but scraping is common)

**Strategy:**
- HTTP requests with BeautifulSoup
- Search across multiple regional sites
- RSS feeds available for some searches
- Respect robots.txt

**Implementation Approach:**
```python
# Pseudocode
def search_craigslist(criteria):
    regions = ['seattle', 'portland', 'denver', 'saltlakecity', 'bozeman']
    all_listings = []
    
    for region in regions:
        url = f"https://{region}.craigslist.org/search/sga?query=k2+way+back+92"
        response = requests.get(url, headers={'User-Agent': 'SkiSearchBot/1.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = extract_craigslist_listings(soup)
        all_listings.extend(listings)
    
    return all_listings
```

**Rate Limiting:** 1 search per region per 10 minutes

---

### 3.4 Additional Marketplace Considerations

**Potential Additional Sources:**
- **Geartrade.com**: Outdoor gear marketplace (has API potential)
- **Pinkbike Buy/Sell**: Popular for outdoor sports equipment
- **TGR Sell/Trade Forum**: Teton Gravity Research forums
- **Local Ski Shops**: Some have used gear sections with RSS feeds
- **OfferUp**: Similar to Craigslist, mobile-first
- **Mercari**: Growing marketplace app

**Extensibility Design:**
- Abstract base class `MarketplaceScraper`
- Each marketplace implements: `search()`, `parse_listing()`, `get_rate_limit()`
- Plugin architecture for easy addition of new sources

---

## 4. Search Criteria Management (GitHub-Based)

### 4.1 Repository Structure

```
ski-search-config/
├── README.md
├── criteria/
│   ├── ski_search.yaml
│   ├── binding_search.yaml
│   └── boot_search.yaml
└── config/
    ├── marketplaces.yaml
    └── notification_settings.yaml
```

### 4.2 Criteria File Format (YAML)

**Example: `criteria/ski_search.yaml`**
```yaml
search_name: "K2 Way Back 92 Search"
enabled: true
priority: high

item_type: skis

keywords:
  required:
    - "K2"
    - ["Way Back", "Wayback"]  # Either variant
  optional:
    - "92"
  exclude:
    - "broken"
    - "cracked"
    - "parts only"

specifications:
  model:
    - "Way Back"
    - "Wayback"
  
  width_underfoot:
    min: 90
    max: 94
    unit: mm
  
  length:
    min: 160
    max: 168
    preferred: [162, 164, 166]
    unit: cm
  
  condition:
    accepted:
      - "new"
      - "like new"
      - "excellent"
      - "good"
      - "used"
    excluded:
      - "for parts"
      - "damaged"

price:
  max: 400
  currency: USD
  alert_if_below: 200  # Extra urgent notification

location:
  max_distance: 500
  unit: miles
  from: "98101"  # Seattle ZIP
  
  preferred_regions:
    - "Pacific Northwest"
    - "Colorado"
    - "Utah"

marketplaces:
  - name: "facebook"
    enabled: true
  - name: "ebay"
    enabled: true
  - name: "craigslist"
    enabled: true
    regions:
      - "seattle"
      - "portland"
      - "denver"
      - "saltlakecity"

notification:
  telegram: true
  email: false
  
search_frequency:
  interval: 15
  unit: minutes

notes: |
  Looking for a good touring ski setup. K2 Way Back 92 in 160-168cm range.
  Prefer 92mm width but will consider 88-96mm if the deal is exceptional.
```

### 4.3 GitHub Integration Workflow

```python
# Pseudocode
class GitHubCriteriaManager:
    def __init__(self, repo_url, access_token):
        self.repo = Github(access_token).get_repo(repo_url)
        self.local_cache = "./cache/criteria/"
        self.last_sync = None
    
    def pull_latest_criteria(self):
        """Pull criteria files from GitHub"""
        # Get latest commit SHA
        latest_commit = self.repo.get_commits()[0].sha
        
        # Check if we need to update
        if self.last_sync == latest_commit:
            return False  # No changes
        
        # Download all YAML files from criteria/ directory
        contents = self.repo.get_contents("criteria")
        
        for content in contents:
            if content.name.endswith('.yaml'):
                # Download and save locally
                file_content = content.decoded_content
                save_to_cache(content.name, file_content)
        
        self.last_sync = latest_commit
        return True  # Updated
    
    def load_active_criteria(self):
        """Load all enabled search criteria"""
        criteria_list = []
        for file in os.listdir(self.local_cache):
            if file.endswith('.yaml'):
                with open(file) as f:
                    criteria = yaml.safe_load(f)
                    if criteria.get('enabled', True):
                        criteria_list.append(criteria)
        return criteria_list
```

**Benefits:**
- Update criteria from anywhere (phone, work, home)
- Version control for search history
- Can add/modify searches without accessing the running system
- Collaborative: others can suggest criteria via PRs
- Backup of search configurations

---

## 5. Matching & Filtering Logic

### 5.1 Two-Stage Matching Process

**Stage 1: Keyword Filtering**
- Extract listing title and description
- Check for required keywords (must have ALL)
- Check for optional keywords (boost match score)
- Check for excluded keywords (immediate rejection)

**Stage 2: Specification Matching**
```python
class ListingMatcher:
    def calculate_match_score(self, listing, criteria):
        score = 0
        max_score = 100
        
        # Keyword match (30 points)
        score += self.check_keywords(listing, criteria) * 30
        
        # Specification match (40 points)
        score += self.check_specifications(listing, criteria) * 40
        
        # Price match (15 points)
        score += self.check_price(listing, criteria) * 15
        
        # Location match (15 points)
        score += self.check_location(listing, criteria) * 15
        
        return score / max_score  # Return 0-1
    
    def check_specifications(self, listing, criteria):
        # Extract ski length from title/description
        length = extract_ski_length(listing.text)
        
        if not length:
            return 0.5  # Unknown length, moderate score
        
        if criteria.length.min <= length <= criteria.length.max:
            if length in criteria.length.preferred:
                return 1.0  # Perfect match
            else:
                return 0.8  # Acceptable match
        else:
            return 0.0  # Out of range
```

### 5.2 Fuzzy Matching for Model Names
```python
from fuzzywuzzy import fuzz

def fuzzy_match_model(listing_text, model_names):
    """
    Handle variations like:
    - "K2 Wayback 92" vs "K2 Way Back 92"
    - "K2 WayBack" vs "K2 Way-Back"
    """
    best_match = 0
    for model in model_names:
        ratio = fuzz.partial_ratio(listing_text.lower(), model.lower())
        best_match = max(best_match, ratio)
    
    return best_match / 100  # Return 0-1
```

### 5.3 Dimension Extraction Patterns
```python
import re

def extract_ski_dimensions(text):
    """Extract length and width from listing text"""
    
    # Length patterns: "166cm", "166 cm", "166-cm"
    length_pattern = r'(\d{3})\s*cm'
    length_match = re.search(length_pattern, text, re.IGNORECASE)
    length = int(length_match.group(1)) if length_match else None
    
    # Width patterns: "92mm", "92 underfoot", "92mm waist"
    width_pattern = r'(\d{2,3})\s*(?:mm|underfoot|waist)'
    width_match = re.search(width_pattern, text, re.IGNORECASE)
    width = int(width_match.group(1)) if width_match else None
    
    return {
        'length_cm': length,
        'width_mm': width
    }
```

---

## 6. Telegram Notification System

### 6.1 Bot Setup
1. Create bot via BotFather on Telegram
2. Get bot token
3. Get your personal chat ID (can use @userinfobot)
4. Store credentials securely (environment variables or secrets manager)

### 6.2 Notification Format

```python
class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id
    
    def send_listing_alert(self, listing, match_score, criteria_name):
        """Send formatted notification with listing details"""
        
        # Calculate recency
        recency = self.format_recency(listing.posted_date)
        
        # Build message
        message = f"""
🎿 <b>New Ski Listing Match!</b>

<b>Match Score:</b> {match_score:.0%}
<b>Criteria:</b> {criteria_name}

<b>Title:</b> {listing.title}
<b>Price:</b> ${listing.price}
<b>Location:</b> {listing.location}
<b>Posted:</b> {recency}

<b>Specifications:</b>
• Length: {listing.length}cm
• Width: {listing.width}mm
• Condition: {listing.condition}

<b>Marketplace:</b> {listing.source}
<b>Link:</b> {listing.url}

{self.get_urgency_note(listing, criteria_name)}
        """
        
        # Send with image if available
        if listing.image_url:
            self.bot.send_photo(
                chat_id=self.chat_id,
                photo=listing.image_url,
                caption=message,
                parse_mode='HTML'
            )
        else:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
    
    def format_recency(self, posted_date):
        """Format how long ago listing was posted"""
        now = datetime.now()
        delta = now - posted_date
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    def get_urgency_note(self, listing, criteria):
        """Add urgency indicators"""
        notes = []
        
        if listing.price < criteria.price.alert_if_below:
            notes.append("🔥 <b>GREAT PRICE!</b>")
        
        if listing.posted_within_minutes(30):
            notes.append("⚡ <b>JUST POSTED!</b>")
        
        if listing.location_distance < 50:
            notes.append("📍 <b>LOCAL!</b>")
        
        return "\n".join(notes) if notes else ""
```

### 6.3 Notification Levels
- **High Priority**: Match score >80%, price below threshold, or just posted
- **Medium Priority**: Match score 60-80%
- **Low Priority**: Match score 40-60% (maybe include "possible match" flag)

### 6.4 Rate Limiting
- Max 1 notification per minute to avoid spam
- Queue multiple listings and send as album/batch if >5 matches in short time
- Daily summary option if no high-priority matches

---

## 7. Persistence & Scheduling

### 7.1 Database Schema (SQLite/PostgreSQL)

```sql
-- Seen listings table
CREATE TABLE seen_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id VARCHAR(255) UNIQUE NOT NULL,
    marketplace VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    price DECIMAL(10, 2),
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_checked INTEGER DEFAULT 1,
    notified BOOLEAN DEFAULT FALSE,
    match_score DECIMAL(5, 2)
);

-- Search runs table
CREATE TABLE search_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    criteria_name VARCHAR(255),
    marketplace VARCHAR(50),
    listings_found INTEGER,
    new_listings INTEGER,
    errors TEXT,
    status VARCHAR(20)  -- 'success', 'failed', 'partial'
);

-- Notifications table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id VARCHAR(255),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipient VARCHAR(255),
    message_text TEXT,
    status VARCHAR(20)  -- 'sent', 'failed', 'queued'
);

-- Create indexes
CREATE INDEX idx_seen_listings_marketplace ON seen_listings(marketplace);
CREATE INDEX idx_seen_listings_first_seen ON seen_listings(first_seen);
CREATE INDEX idx_search_runs_started ON search_runs(started_at);
```

### 7.2 Deduplication Strategy

```python
class ListingDatabase:
    def is_seen(self, listing):
        """Check if listing has been seen before"""
        # Generate unique ID from marketplace + listing identifier
        listing_id = self.generate_listing_id(listing)
        
        result = self.db.query(
            "SELECT id FROM seen_listings WHERE listing_id = ?",
            (listing_id,)
        )
        
        return result is not None
    
    def generate_listing_id(self, listing):
        """Create unique identifier for listing"""
        # Different strategies per marketplace
        if listing.marketplace == 'ebay':
            return f"ebay_{listing.item_id}"
        
        elif listing.marketplace == 'facebook':
            return f"facebook_{listing.listing_id}"
        
        elif listing.marketplace == 'craigslist':
            # Craigslist IDs are in the URL
            match = re.search(r'/(\d+)\.html', listing.url)
            return f"craigslist_{match.group(1)}" if match else None
        
        else:
            # Fallback: hash of URL + title
            import hashlib
            content = f"{listing.url}_{listing.title}"
            return hashlib.md5(content.encode()).hexdigest()
    
    def mark_as_seen(self, listing, match_score, notified=False):
        """Add listing to database"""
        listing_id = self.generate_listing_id(listing)
        
        self.db.execute("""
            INSERT OR IGNORE INTO seen_listings 
            (listing_id, marketplace, url, title, price, match_score, notified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (listing_id, listing.marketplace, listing.url, 
              listing.title, listing.price, match_score, notified))
```

### 7.3 Scheduling Mechanisms

**Option 1: Cron-based (Simple)**
```bash
# Run every 15 minutes
*/15 * * * * /usr/bin/python3 /path/to/ski_search.py >> /var/log/ski_search.log 2>&1
```

**Option 2: APScheduler (More Flexible)**
```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BlockingScheduler()

def run_search():
    """Main search execution"""
    # Pull latest criteria from GitHub
    criteria_manager.pull_latest_criteria()
    
    # Load all active searches
    criteria_list = criteria_manager.load_active_criteria()
    
    # Execute each search
    for criteria in criteria_list:
        search_orchestrator.run_search(criteria)

# Schedule based on criteria frequency
for criteria in load_initial_criteria():
    scheduler.add_job(
        func=lambda c=criteria: run_search_for_criteria(c),
        trigger=IntervalTrigger(minutes=criteria.search_frequency.interval),
        id=f"search_{criteria.search_name}",
        replace_existing=True
    )

scheduler.start()
```

**Option 3: Systemd Service (Production)**
```ini
# /etc/systemd/system/ski-search.service
[Unit]
Description=Ski Marketplace Search Service
After=network.target

[Service]
Type=simple
User=skisearch
WorkingDirectory=/opt/ski-search
ExecStart=/usr/bin/python3 /opt/ski-search/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 8. Configuration Management

### 8.1 Environment Variables

```bash
# .env file
# GitHub Configuration
GITHUB_REPO_URL=username/ski-search-config
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxx

# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# eBay API
EBAY_APP_ID=yourappid
EBAY_CERT_ID=yourcertid
EBAY_DEV_ID=yourdevid

# Database
DATABASE_URL=sqlite:///ski_search.db
# Or for PostgreSQL: postgresql://user:pass@localhost/ski_search

# Application Settings
LOG_LEVEL=INFO
SEARCH_INTERVAL_MINUTES=15
MAX_NOTIFICATIONS_PER_HOUR=20
```

### 8.2 Configuration Hierarchy
1. **Environment variables** (highest priority) - secrets, credentials
2. **GitHub repo config files** - search criteria, marketplace settings
3. **Local config.yaml** - application defaults
4. **Hardcoded defaults** (lowest priority)

### 8.3 Secrets Management
- **Development**: `.env` file (not committed to git)
- **Production options**:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Environment variables in systemd service
  - Docker secrets

---

## 9. Error Handling & Reliability

### 9.1 Marketplace Scraping Failures

```python
class MarketplaceScraper:
    def search_with_retry(self, criteria, max_retries=3):
        """Robust search with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return self.search(criteria)
            
            except RateLimitError:
                wait_time = 2 ** attempt * 60  # 1min, 2min, 4min
                logger.warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            
            except ScraperBlocked:
                logger.error(f"Scraper blocked on {self.marketplace}")
                self.send_admin_alert("Scraper blocked, manual intervention needed")
                return []
            
            except NetworkError as e:
                logger.warning(f"Network error: {e}, retrying...")
                time.sleep(10)
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == max_retries - 1:
                    self.send_admin_alert(f"Search failed: {e}")
                    return []
        
        return []
```

### 9.2 Telegram Notification Failures
```python
def send_notification_with_fallback(listing, criteria):
    """Try Telegram, fall back to email if fails"""
    try:
        telegram_notifier.send_listing_alert(listing, criteria)
    except telegram.error.NetworkError:
        logger.warning("Telegram failed, trying email fallback")
        email_notifier.send_listing_alert(listing, criteria)
    except Exception as e:
        logger.error(f"All notification methods failed: {e}")
        # Queue for retry
        notification_queue.add(listing, criteria)
```

### 9.3 Health Monitoring
```python
class HealthMonitor:
    def check_system_health(self):
        """Run health checks and alert if issues"""
        checks = {
            'github_sync': self.check_github_connectivity(),
            'database': self.check_database_connection(),
            'telegram': self.check_telegram_bot(),
            'last_search': self.check_recent_searches(),
            'disk_space': self.check_disk_space()
        }
        
        if not all(checks.values()):
            self.send_health_alert(checks)
        
        return checks
    
    def check_recent_searches(self):
        """Ensure searches are running"""
        last_run = self.db.query(
            "SELECT MAX(started_at) FROM search_runs"
        )
        
        if not last_run:
            return False
        
        time_since = datetime.now() - last_run
        # Alert if no search in last hour
        return time_since.seconds < 3600
```

---

## 10. Deployment Options

### 10.1 Recommended: Docker on Proxmox with Portainer ⭐

**This is the primary deployment method** - containerized, easy to manage, and works great on shared Proxmox infrastructure.

**Pros:**
- Easy deployment via Portainer UI
- No command-line needed after initial setup
- Persistent storage with volume management
- Resource limits configurable via UI
- Health monitoring built-in
- Easy updates and rollbacks
- Minimal resource usage (~128-512MB RAM)
- Works on shared Proxmox infrastructure

**Cons:**
- Requires Proxmox and Portainer setup
- Needs LXC container with Docker support

**Architecture:**
```
Proxmox Host
  └─ LXC Container (Ubuntu/Debian)
      └─ Docker
          ├─ Portainer (Management UI)
          └─ Ski Search Container
              ├─ Python Application
              ├─ SQLite Database (persistent volume)
              └─ Logs (persistent volume)
```

**Quick Setup:**

1. **Create LXC Container in Proxmox:**
   - OS: Ubuntu 22.04 LTS
   - RAM: 1GB (512MB minimum)
   - Cores: 1-2
   - Storage: 8GB
   - **Important:** Enable "Nesting" feature (required for Docker)

2. **Install Docker in LXC:**
   ```bash
   apt update && apt upgrade -y
   apt install -y docker.io docker-compose
   systemctl enable --now docker
   ```

3. **Install Portainer (if not already available):**
   ```bash
   docker run -d \
     --name=portainer \
     --restart=always \
     -p 9000:9000 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v portainer_data:/data \
     portainer/portainer-ce:latest
   ```

4. **Deploy via Portainer UI:**
   - Access Portainer: `http://<LXC-IP>:9000`
   - Navigate to Stacks → Add Stack
   - Choose "Repository" and point to this GitHub repo
   - Add environment variables (Telegram, GitHub tokens)
   - Click Deploy!

**See [PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md) for complete step-by-step guide.**

**Resource Requirements:**
- **Idle:** ~50MB RAM, <1% CPU
- **During Search:** ~200MB RAM, 5-15% CPU
- **Storage:** ~500MB (OS + app + database)

---

### 10.2 Alternative: Cloud VPS with Docker

**Use case:** When you don't have Proxmox or want cloud-hosted

**Providers:**
- **DigitalOcean:** $6/month Droplet
- **Linode:** $5/month Nanode
- **Hetzner Cloud:** €4.5/month CX11
- **Oracle Cloud:** Free tier (ARM instances)

**Setup:**
```bash
# On Ubuntu 22.04 VPS:
apt update && apt install -y docker.io docker-compose git

# Clone repo
git clone https://github.com/yourusername/SkiSearchTool.git
cd SkiSearchTool

# Configure
cp .env.example .env
nano .env  # Add your credentials

# Deploy
docker-compose up -d

# View logs
docker-compose logs -f
```

---

### 10.3 Alternative: Raspberry Pi (Docker)

**Use case:** Home lab, always-on personal server

**Pros:**
- Low power consumption (~5W)
- One-time $75 cost
- Physical control

**Setup:**
```bash
# On Raspberry Pi OS:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Deploy same as VPS
docker-compose up -d
```

---

### 10.4 Alternative: Kubernetes/k3s (Advanced)

**Use case:** Already running k3s/k8s cluster

**Deployment via Helm chart or kubectl:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ski-search
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: ski-search
        image: ski-search:latest
        env:
        - name: GITHUB_ACCESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: ski-search-secrets
              key: github-token
```

---

### 10.5 Not Recommended: Serverless

**Why not recommended:**
- Stateful application (database, seen listings)
- Long-running scrapers (especially Facebook with browser automation)
- 15-minute Lambda timeout too restrictive
- Cold starts affect scheduling reliability

**If you must:** Consider AWS Fargate + EFS for persistent storage

---

### 10.6 Deployment Comparison

| Method | Cost/Month | Setup Complexity | Maintenance | Recommended For |
|--------|------------|------------------|-------------|-----------------|
| **Proxmox + Portainer** | $0 (shared) | Low (UI-based) | Very Low | ⭐ Most users |
| Cloud VPS + Docker | $5-6 | Medium | Low | No Proxmox access |
| Raspberry Pi + Docker | $0 (after $75) | Medium | Low | Home lab enthusiasts |
| Kubernetes | Varies | High | Medium | k8s users only |
| Serverless | $1-2 | Very High | Medium | ❌ Not suitable |

---

### Primary Deployment Guide

**For the recommended Proxmox + Portainer setup, follow these docs:**

1. **[PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md)** - Complete Portainer guide
2. **[SETUP.md](SETUP.md)** - Initial configuration (Telegram, GitHub)
3. **[docker-compose.yml](docker-compose.yml)** - Production-ready compose file

**Quick commands:**
```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Update
docker-compose pull && docker-compose up -d

# Backup database
docker exec ski-marketplace-search \
  sqlite3 /app/data/ski_search.db ".backup /tmp/backup.db"
```

---

## 11. Security Considerations

### 11.1 Credential Protection
- Never commit credentials to git
- Use environment variables or secrets manager
- Rotate API keys periodically
- Use read-only GitHub tokens when possible

### 11.2 Scraping Ethics
- Respect robots.txt
- Implement rate limiting
- Use appropriate user agents
- Don't overwhelm servers
- Consider using official APIs when available

### 11.3 Data Privacy
- Don't store personal information from listings unnecessarily
- Clean up old listings after reasonable period (90 days)
- Encrypt sensitive data in database
- Secure database file permissions

---

## 12. Testing Strategy

### 12.1 Unit Tests
```python
# test_matcher.py
def test_ski_length_extraction():
    text = "K2 Way Back 92 skis, 164cm length"
    dimensions = extract_ski_dimensions(text)
    assert dimensions['length_cm'] == 164
    assert dimensions['width_mm'] == 92

def test_match_score_calculation():
    listing = create_test_listing("K2 Way Back 92", "164cm", "$300")
    criteria = load_test_criteria()
    score = matcher.calculate_match_score(listing, criteria)
    assert score > 0.8  # Should be high match
```

### 12.2 Integration Tests
- Test each marketplace scraper individually
- Test GitHub sync with test repository
- Test Telegram notifications (to test chat)
- Test database operations

### 12.3 End-to-End Test
```python
def test_full_search_workflow():
    """Test complete search cycle"""
    # Setup
    clear_test_database()
    load_test_criteria()
    
    # Run search
    orchestrator.run_all_searches()
    
    # Verify
    assert database.get_search_run_count() > 0
    assert telegram_mock.messages_sent > 0
```

---

## 13. Monitoring & Observability

### 13.1 Logging Strategy
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logger = logging.getLogger('ski_search')
logger.setLevel(logging.INFO)

# File handler with rotation
file_handler = RotatingFileHandler(
    'ski_search.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

# Log key events
logger.info(f"Starting search for criteria: {criteria.name}")
logger.info(f"Found {len(listings)} listings from {marketplace}")
logger.info(f"Sent notification for listing: {listing.title}")
logger.warning(f"Rate limited by {marketplace}, waiting...")
logger.error(f"Failed to scrape {marketplace}: {error}")
```

### 13.2 Metrics to Track
- Searches performed per marketplace per day
- New listings found vs. total listings
- Notification sent count
- Match score distribution
- Scraper failure rate
- Average search duration
- GitHub sync frequency
- Database size growth

### 13.3 Dashboard (Optional)
- Simple web interface showing:
  - Last search times per marketplace
  - Recent notifications
  - System health status
  - Search statistics
  - Active criteria count

---

## 14. Future Enhancements

### 14.1 Phase 2 Features
1. **Machine Learning Integration**
   - Train model to better identify ski specifications from text
   - Learn from user feedback (which notifications were useful)
   - Predict listing quality/authenticity

2. **Price Tracking**
   - Historical price database
   - Price drop alerts
   - Market price analysis ("This is 20% below average")

3. **Image Recognition**
   - Verify ski model from photos
   - Detect damage/condition from images
   - Extract specifications from photos

4. **Advanced Filters**
   - Binding compatibility
   - Ski year/vintage
   - Seller ratings
   - Shipping availability

5. **Multi-User Support**
   - Multiple Telegram recipients
   - Shared criteria repository
   - User preference profiles

### 14.2 Phase 3 Features
1. **Automated Bidding** (eBay)
   - Auto-bid on matching listings
   - Max price constraints
   - Bid sniping

2. **Messaging Integration**
   - Auto-respond to sellers
   - Schedule viewings
   - Negotiation templates

3. **Comparison Tool**
   - Side-by-side listing comparison
   - Price vs. condition analysis
   - Deal scoring

4. **Mobile App**
   - Native iOS/Android app
   - Push notifications
   - Saved searches management
   - Quick listing actions (save, hide, contact)

---

## 15. Development Roadmap

### Phase 1: MVP (Weeks 1-2)
- [x] Design document (this document)
- [ ] Set up project structure
- [ ] Implement GitHub criteria sync
- [ ] Build Craigslist scraper (simplest)
- [ ] Implement basic matching logic
- [ ] Set up SQLite database
- [ ] Integrate Telegram notifications
- [ ] Create initial criteria file format
- [ ] Basic error handling
- [ ] Deploy to test environment

### Phase 2: Multi-Marketplace (Weeks 3-4)
- [ ] Implement eBay API integration
- [ ] Implement Facebook Marketplace scraper
- [ ] Advanced matching with fuzzy logic
- [ ] Improved deduplication
- [ ] Rate limiting for each marketplace
- [ ] Retry logic and error recovery
- [ ] Comprehensive logging

### Phase 3: Production Ready (Week 5)
- [ ] Docker containerization
- [ ] Automated testing suite
- [ ] Health monitoring
- [ ] Documentation
- [ ] Deployment scripts
- [ ] Backup strategy
- [ ] Performance optimization

### Phase 4: Enhancement (Week 6+)
- [ ] Additional marketplaces
- [ ] Web dashboard
- [ ] Price tracking
- [ ] User feedback loop
- [ ] Advanced filters

---

## 16. Cost Estimate

### Running Costs (Monthly)

**Option 1: Home Server (Raspberry Pi)**
- Hardware: $75 one-time (Raspberry Pi 4)
- Electricity: ~$2/month
- **Total: $2/month** (+ initial hardware)

**Option 2: Cloud VPS**
- DigitalOcean Droplet: $6/month
- **Total: $6/month**

**Option 3: AWS Serverless**
- Lambda executions: $0.20/month (96 searches/day)
- DynamoDB: $1/month
- EventBridge: Free tier
- **Total: ~$1.20/month**

**Additional Services:**
- GitHub: Free (public repo) or $4/month (private)
- Telegram Bot: Free
- eBay API: Free (Finding API)
- **Total Additional: $0-4/month**

**Recommended Setup: Docker on DigitalOcean = ~$10/month total**

---

## 17. Quick Start Guide

### Prerequisites
- Python 3.10+
- GitHub account
- Telegram account
- eBay developer account (optional but recommended)

### Setup Steps

1. **Create GitHub Configuration Repository**
   ```bash
   # Create new repo: ski-search-config
   # Add criteria/ski_search.yaml with your search criteria
   ```

2. **Set Up Telegram Bot**
   ```
   1. Message @BotFather on Telegram
   2. Send: /newbot
   3. Follow prompts to get bot token
   4. Message your bot, then get your chat ID from @userinfobot
   ```

3. **Clone and Configure**
   ```bash
   git clone https://github.com/yourusername/ski-search-tool
   cd ski-search-tool
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Install Dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

5. **Run Initial Test**
   ```bash
   python main.py --test
   ```

6. **Deploy**
   ```bash
   # For Docker:
   docker-compose up -d
   
   # For systemd:
   sudo systemctl start ski-search
   ```

---

## 18. Troubleshooting

### Common Issues

**GitHub sync fails**
- Check access token permissions
- Verify repository URL
- Ensure criteria files are valid YAML

**Facebook scraper blocked**
- Try different user agent
- Increase delay between requests
- Consider using residential proxy
- May need to solve captcha occasionally

**Telegram notifications not sending**
- Verify bot token
- Check chat ID (send /start to your bot first)
- Ensure bot isn't rate limited

**Database locked errors**
- Use WAL mode for SQLite: `PRAGMA journal_mode=WAL;`
- Or switch to PostgreSQL for production

**Missing listings**
- Check criteria filters aren't too restrictive
- Verify marketplace scrapers are working
- Check search frequency settings
- Review error logs

---

## 19. Maintenance Tasks

### Daily
- Monitor notification queue
- Check error logs for critical failures

### Weekly
- Review match accuracy (false positives/negatives)
- Update criteria based on market changes
- Check database size

### Monthly
- Update dependencies
- Rotate API keys if needed
- Clean up old database entries
- Review and optimize search criteria
- Check marketplace HTML structure changes

### Quarterly
- Full system backup
- Performance optimization review
- Security audit
- Add new marketplaces as needed

---

## 20. Conclusion

This design provides a robust, extensible foundation for a persistent ski marketplace search tool. The system is designed to be:

- **Reliable**: Built-in error handling, retry logic, and monitoring
- **Flexible**: Easy to add new marketplaces and search criteria
- **Maintainable**: Clean architecture with separated concerns
- **User-Friendly**: Simple GitHub-based configuration
- **Cost-Effective**: Multiple deployment options at low cost
- **Secure**: Proper credential management and ethical scraping

The modular design allows for incremental development, starting with an MVP that delivers value quickly, then adding features as needed.

### Next Steps
1. Review and refine this design based on specific requirements
2. Set up development environment
3. Begin Phase 1 implementation
4. Create initial test criteria file
5. Deploy MVP and iterate based on real-world usage

---

## Appendix A: File Structure

```
ski-search-tool/
├── README.md
├── DESIGN.md (this file)
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── main.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── logging_config.py
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── facebook_scraper.py
│   ├── ebay_scraper.py
│   ├── craigslist_scraper.py
│   └── scraper_factory.py
├── matching/
│   ├── __init__.py
│   ├── matcher.py
│   ├── dimension_extractor.py
│   └── fuzzy_matcher.py
├── notifications/
│   ├── __init__.py
│   ├── telegram_notifier.py
│   └── notification_formatter.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   ├── database.py
│   └── migrations/
├── criteria/
│   ├── __init__.py
│   ├── github_manager.py
│   ├── criteria_loader.py
│   └── validator.py
├── orchestrator/
│   ├── __init__.py
│   ├── search_orchestrator.py
│   └── scheduler.py
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   ├── health_check.py
│   └── helpers.py
└── tests/
    ├── __init__.py
    ├── test_scrapers.py
    ├── test_matcher.py
    ├── test_database.py
    └── test_integration.py
```

---

## Appendix B: Example Requirements.txt

```txt
# Web scraping
requests==2.31.0
beautifulsoup4==4.12.2
playwright==1.40.0
selenium==4.15.2

# eBay API
ebaysdk==2.2.0

# Telegram
python-telegram-bot==20.7

# GitHub
PyGithub==2.1.1

# Database
sqlalchemy==2.0.23

# Scheduling
APScheduler==3.10.4

# Configuration
python-dotenv==1.0.0
pyyaml==6.0.1

# Fuzzy matching
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Testing
pytest==7.4.3
pytest-cov==4.1.0
responses==0.24.1
```

---

**Document Version:** 1.0  
**Last Updated:** September 28, 2026  
**Author:** Ski Search Tool Team
