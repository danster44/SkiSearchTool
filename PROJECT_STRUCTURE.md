# Project Structure

```
SkiSearchTool/
├── README.md                      # Project overview and quick start
├── DESIGN.md                      # Comprehensive design documentation
├── SETUP.md                       # Step-by-step setup guide
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── main.py                        # Application entry point
│
├── config/                        # Configuration management
│   ├── __init__.py
│   ├── settings.py               # Load and validate configuration
│   └── logging_config.py         # Logging setup
│
├── criteria/                      # Example criteria files (not synced from GitHub)
│   ├── __init__.py
│   ├── ski_search.yaml           # Example search criteria
│   ├── github_manager.py         # GitHub repository sync
│   ├── criteria_loader.py        # YAML parsing and validation
│   └── validator.py              # Criteria validation logic
│
├── scrapers/                      # Marketplace scraper implementations
│   ├── __init__.py
│   ├── base_scraper.py           # Abstract base class for scrapers
│   ├── ebay_scraper.py           # eBay API integration
│   ├── craigslist_scraper.py     # Craigslist HTML scraping
│   ├── facebook_scraper.py       # Facebook Marketplace (Playwright/Selenium)
│   └── scraper_factory.py        # Factory pattern for scraper instantiation
│
├── matching/                      # Listing matching and filtering
│   ├── __init__.py
│   ├── matcher.py                # Main matching logic and scoring
│   ├── dimension_extractor.py    # Extract ski dimensions from text
│   ├── fuzzy_matcher.py          # Fuzzy string matching for model names
│   └── filters.py                # Price, location, condition filters
│
├── notifications/                 # Notification services
│   ├── __init__.py
│   ├── telegram_notifier.py      # Telegram bot integration
│   ├── email_notifier.py         # Email notifications (fallback)
│   └── notification_formatter.py # Format messages for different channels
│
├── database/                      # Database models and operations
│   ├── __init__.py
│   ├── models.py                 # SQLAlchemy models
│   ├── database.py               # Database connection and session management
│   ├── operations.py             # CRUD operations
│   └── migrations/               # Database migration scripts
│       └── 001_initial_schema.sql
│
├── orchestrator/                  # Search coordination
│   ├── __init__.py
│   ├── search_orchestrator.py    # Coordinate searches across marketplaces
│   └── scheduler.py              # APScheduler integration
│
├── utils/                         # Utility functions
│   ├── __init__.py
│   ├── logging.py                # Custom logging utilities
│   ├── health_check.py           # System health monitoring
│   ├── retry.py                  # Retry decorators and logic
│   └── helpers.py                # General helper functions
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration and fixtures
│   ├── test_scrapers.py          # Scraper tests
│   ├── test_matcher.py           # Matching logic tests
│   ├── test_database.py          # Database operation tests
│   ├── test_criteria.py          # Criteria loading tests
│   ├── test_notifications.py     # Notification tests
│   └── test_integration.py       # End-to-end integration tests
│
├── data/                          # Runtime data (not in git)
│   ├── ski_search.db             # SQLite database
│   └── cache/                    # Cached criteria and temporary data
│
└── logs/                          # Application logs (not in git)
    ├── ski_search.log
    ├── scrapers.log
    └── errors.log
```

## Key Modules

### Entry Point: `main.py`
- Parses command-line arguments
- Initializes configuration
- Starts scheduler or runs one-time search
- Handles graceful shutdown

### Configuration: `config/`
- Loads environment variables
- Validates configuration
- Manages secrets
- Sets up logging

### Criteria Management: `criteria/`
- Syncs with GitHub repository
- Parses YAML criteria files
- Validates search parameters
- Caches criteria locally

### Scrapers: `scrapers/`
- **Base Scraper**: Abstract interface all scrapers implement
- **eBay Scraper**: Uses official eBay Finding API
- **Craigslist Scraper**: BeautifulSoup HTML parsing
- **Facebook Scraper**: Playwright browser automation
- **Scraper Factory**: Instantiates appropriate scraper based on marketplace

### Matching Engine: `matching/`
- **Matcher**: Calculates match scores based on criteria
- **Dimension Extractor**: Regex patterns for ski specs
- **Fuzzy Matcher**: Handles spelling variations
- **Filters**: Apply price, location, condition constraints

### Notifications: `notifications/`
- **Telegram Notifier**: Sends formatted messages via Telegram Bot API
- **Email Notifier**: SMTP fallback notifications
- **Formatter**: Creates rich, user-friendly notification messages

### Database: `database/`
- **Models**: SQLAlchemy ORM models (SeenListing, SearchRun, Notification)
- **Database**: Connection pooling and session management
- **Operations**: High-level CRUD operations
- **Migrations**: Schema evolution scripts

### Orchestrator: `orchestrator/`
- **Search Orchestrator**: Coordinates multi-marketplace searches
- **Scheduler**: APScheduler integration for periodic execution

### Utilities: `utils/`
- **Logging**: Structured logging with rotation
- **Health Check**: System health monitoring
- **Retry**: Exponential backoff retry decorators
- **Helpers**: Date formatting, URL validation, etc.

### Tests: `tests/`
- Unit tests for each module
- Integration tests for full workflows
- Mocked external dependencies
- Test fixtures and factories

## Data Flow

1. **Startup**
   ```
   main.py → config/settings.py → orchestrator/scheduler.py
   ```

2. **Criteria Sync**
   ```
   scheduler → criteria/github_manager.py → criteria/criteria_loader.py
   ```

3. **Search Execution**
   ```
   orchestrator → scrapers/[marketplace]_scraper.py → matching/matcher.py
   ```

4. **Notification**
   ```
   matcher → notifications/telegram_notifier.py → user's phone
   ```

5. **State Persistence**
   ```
   throughout → database/operations.py → data/ski_search.db
   ```

## Development Workflow

1. **Add New Marketplace**
   - Create `scrapers/newsite_scraper.py` extending `BaseScraper`
   - Implement `search()` and `parse_listing()` methods
   - Register in `scraper_factory.py`
   - Add tests in `tests/test_scrapers.py`

2. **Add New Notification Channel**
   - Create `notifications/newchannel_notifier.py`
   - Implement `send_listing_alert()` method
   - Update orchestrator to use new notifier
   - Add configuration options

3. **Modify Search Criteria**
   - Update YAML schema in `criteria/ski_search.yaml`
   - Update parser in `criteria/criteria_loader.py`
   - Update validator in `criteria/validator.py`
   - Update matcher to use new fields

4. **Database Schema Changes**
   - Create migration script in `database/migrations/`
   - Update models in `database/models.py`
   - Run migration on deployment
   - Update operations as needed

## Dependencies

See `requirements.txt` for full list. Key dependencies:

- **Web Scraping**: requests, beautifulsoup4, playwright, selenium
- **APIs**: ebaysdk, python-telegram-bot, PyGithub
- **Database**: sqlalchemy
- **Scheduling**: APScheduler
- **Utilities**: pyyaml, fuzzywuzzy, python-dotenv

## Environment Variables

See `.env.example` for required configuration:

- `GITHUB_REPO_URL`, `GITHUB_ACCESS_TOKEN`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `EBAY_APP_ID`, `EBAY_CERT_ID`, `EBAY_DEV_ID`
- `DATABASE_URL`
- Application settings

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_scrapers.py

# Run specific test
pytest tests/test_matcher.py::test_ski_length_extraction
```

## Deployment

See DESIGN.md Section 10 for deployment guides:

- Local development: `python main.py`
- Production daemon: `python main.py --daemon`
- Docker: `docker-compose up -d`
- Systemd service: See SETUP.md
- Cloud platforms: AWS, DigitalOcean, etc.
