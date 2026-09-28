# Ski Marketplace Search Tool - Setup Guide

This guide will walk you through setting up the ski marketplace search tool step by step.

## Prerequisites

- **Python 3.10 or higher**
- **Git**
- **GitHub account** (for storing search criteria)
- **Telegram account** (for receiving notifications)
- *Optional:* Docker (for containerized deployment)
- *Optional:* eBay developer account (for eBay API access)

---

## Step 1: Telegram Bot Setup

1. Open Telegram and search for **@BotFather**
2. Send the command: `/newbot`
3. Follow the prompts:
   - Choose a name for your bot (e.g., "My Ski Search Bot")
   - Choose a username (must end in 'bot', e.g., "myskisearch_bot")
4. **Save the bot token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

5. Get your **Chat ID**:
   - Send a message to your new bot (e.g., "/start")
   - Search for **@userinfobot** on Telegram
   - Send it any message
   - It will reply with your user info including your **Chat ID** (a number like `123456789`)
   - **Save this Chat ID**

---

## Step 2: GitHub Configuration Repository

1. Create a new GitHub repository called `ski-search-config` (can be private)

2. Create the following structure:
   ```
   ski-search-config/
   ├── README.md
   └── criteria/
       └── ski_search.yaml
   ```

3. Copy the example `criteria/ski_search.yaml` from this repo and customize it:
   - Update the location ZIP code
   - Adjust price ranges
   - Modify Craigslist regions
   - Set your preferred search parameters

4. Create a **Personal Access Token** for GitHub:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name like "Ski Search Tool"
   - Select scope: **`repo`** (full control of private repositories)
   - Click "Generate token"
   - **Copy and save the token** (starts with `ghp_`)

---

## Step 3: eBay API Setup (Optional but Recommended)

1. Go to [eBay Developers Program](https://developer.ebay.com/)
2. Sign in or create an account
3. Go to "My Account" → "Application Keys"
4. Create a new application keyset:
   - Choose "Keyset Type": Production (or Sandbox for testing)
   - Fill in the required information
5. **Save your keys**:
   - App ID (Client ID)
   - Cert ID (Client Secret)
   - Dev ID

> **Note:** eBay API is optional. The tool will work without it but won't search eBay listings.

---

## Step 4: Local Development Setup

### Option A: Manual Python Setup

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/SkiSearchTool.git
   cd SkiSearchTool
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Install Playwright browsers
   playwright install chromium
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   ```bash
   nano .env  # or use your preferred editor
   ```
   
   Required fields:
   - `GITHUB_REPO_URL` (e.g., "yourusername/ski-search-config")
   - `GITHUB_ACCESS_TOKEN` (the token from Step 2)
   - `TELEGRAM_BOT_TOKEN` (from Step 1)
   - `TELEGRAM_CHAT_ID` (from Step 1)
   
   Optional fields:
   - eBay API credentials (from Step 3)

5. **Test the setup:**
   ```bash
   python main.py --test
   ```

---

### Option B: Docker Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/SkiSearchTool.git
   cd SkiSearchTool
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Fill in your credentials
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the container:**
   ```bash
   docker-compose down
   ```

---

## Step 5: First Run

Once everything is set up, test your configuration:

```bash
# Test GitHub sync
python -c "from criteria.github_manager import GitHubCriteriaManager; \
           mgr = GitHubCriteriaManager(); \
           print('GitHub sync:', mgr.pull_latest_criteria())"

# Test Telegram notifications
python -c "from notifications.telegram_notifier import TelegramNotifier; \
           notifier = TelegramNotifier(); \
           notifier.send_test_message()"

# Run a test search
python main.py --marketplace craigslist --dry-run
```

If all tests pass, you're ready to go!

---

## Step 6: Running the Tool

### Manual Execution
```bash
# Single search run
python main.py

# Run with verbose logging
python main.py --verbose

# Test mode (no notifications sent)
python main.py --dry-run
```

### Continuous Operation

**Option 1: Using the built-in scheduler**
```bash
python main.py --daemon
```

**Option 2: Using cron (Linux/macOS)**
```bash
# Edit crontab
crontab -e

# Add this line to run every 15 minutes
*/15 * * * * cd /path/to/SkiSearchTool && /path/to/venv/bin/python main.py >> /var/log/ski_search.log 2>&1
```

**Option 3: Using systemd (Linux)**

Create `/etc/systemd/system/ski-search.service`:
```ini
[Unit]
Description=Ski Marketplace Search Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/SkiSearchTool
Environment="PATH=/path/to/SkiSearchTool/venv/bin"
ExecStart=/path/to/SkiSearchTool/venv/bin/python main.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ski-search.service
sudo systemctl start ski-search.service
sudo systemctl status ski-search.service
```

**Option 4: Docker (recommended)**
```bash
docker-compose up -d
```

---

## Step 7: Adding More Search Criteria

To add additional search criteria (e.g., for boots, bindings, or other skis):

1. Go to your `ski-search-config` GitHub repository
2. Create a new YAML file in the `criteria/` folder
3. Copy the format from `ski_search.yaml` and modify for your new search
4. Commit and push to GitHub
5. The tool will automatically pick up the new criteria on the next run (within minutes!)

Example: `criteria/boots_search.yaml`
```yaml
search_name: "Ski Boots Search - Size 27.5"
enabled: true
item_type: boots

keywords:
  required:
    - "ski boots"
    - ["27.5", "275"]
  # ... rest of configuration
```

---

## Step 8: Monitoring

### Check Logs
```bash
# If running manually
tail -f ski_search.log

# If using Docker
docker-compose logs -f

# If using systemd
journalctl -u ski-search.service -f
```

### Database Inspection
```bash
# SQLite (default)
sqlite3 data/ski_search.db

# View recent searches
SELECT * FROM search_runs ORDER BY started_at DESC LIMIT 10;

# View seen listings
SELECT * FROM seen_listings ORDER BY first_seen DESC LIMIT 20;
```

### Health Check
```bash
python -c "from utils.health_check import HealthMonitor; \
           health = HealthMonitor(); \
           print(health.check_system_health())"
```

---

## Troubleshooting

### "GitHub sync failed"
- Verify your GitHub token has `repo` scope
- Check that the repository URL is correct (format: `username/repo-name`)
- Ensure the `criteria/` folder exists in your config repo

### "Telegram notifications not working"
- Send `/start` to your bot first
- Verify the bot token is correct
- Check that your Chat ID is a number (not a username)
- Test with: `curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe`

### "Scraper is blocked"
- This is common with Facebook. Try:
  - Increasing delays between requests
  - Using a different IP/proxy
  - Running at different times of day
- eBay and Craigslist are generally more reliable

### "Database locked error"
- Enable WAL mode (should be automatic)
- Or switch to PostgreSQL for production use

### "No listings found"
- Check if your criteria are too restrictive
- Run with `--verbose` to see what's being filtered out
- Verify the marketplaces are working: `python main.py --test-scrapers`

---

## Security Notes

- **Never commit your `.env` file to git**
- Keep your API tokens and bot token secret
- Use read-only GitHub tokens when possible
- Regularly rotate your credentials
- For production, consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)

---

## Updating

To update to the latest version:

```bash
git pull origin main
pip install --upgrade -r requirements.txt

# If using Docker
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Getting Help

1. Check the [DESIGN.md](DESIGN.md) for architecture details
2. Review logs for error messages
3. Open an issue on GitHub
4. Ensure all prerequisites are met and credentials are correct

---

## Next Steps

Once your setup is running:

1. Monitor the first few searches to ensure accuracy
2. Adjust your criteria based on results
3. Fine-tune match thresholds and filters
4. Add additional search criteria files as needed
5. Consider adding more marketplaces
6. Set up a simple monitoring dashboard (optional)

Happy ski hunting! 🎿
