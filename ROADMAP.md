# Implementation Roadmap

This document outlines the next steps for implementing the Ski Marketplace Search Tool based on the design plan in DESIGN.md.

## ✅ Phase 0: Design & Planning (COMPLETE)

- [x] Comprehensive system architecture design
- [x] Multi-marketplace integration strategies
- [x] GitHub-based criteria management design
- [x] Telegram notification system design
- [x] Database schema and deduplication strategy
- [x] Docker deployment configuration
- [x] Setup documentation
- [x] Example configuration files
- [x] Project structure definition

## 🚀 Phase 1: MVP - Core Functionality (Next Steps)

### 1.1 Configuration & Setup
- [ ] Implement `config/settings.py` to load environment variables
- [ ] Implement `config/logging_config.py` for structured logging
- [ ] Create `.env` validation on startup
- [ ] Test configuration loading

### 1.2 GitHub Criteria Sync
- [ ] Implement `criteria/github_manager.py`
  - Pull latest files from GitHub repo
  - Cache locally
  - Track last sync timestamp
- [ ] Implement `criteria/criteria_loader.py` to parse YAML files
- [ ] Implement `criteria/validator.py` to validate criteria format
- [ ] Test with example `ski_search.yaml`

### 1.3 Database Setup
- [ ] Implement `database/models.py` with SQLAlchemy models
  - SeenListing model
  - SearchRun model
  - Notification model
- [ ] Implement `database/database.py` for connection management
- [ ] Implement `database/operations.py` for CRUD operations
- [ ] Create initial migration script
- [ ] Test database operations

### 1.4 Craigslist Scraper (Simplest First)
- [ ] Implement `scrapers/base_scraper.py` abstract class
- [ ] Implement `scrapers/craigslist_scraper.py`
  - Multi-region support
  - HTML parsing with BeautifulSoup
  - Extract title, price, location, date, URL
- [ ] Implement rate limiting
- [ ] Test with multiple regions

### 1.5 Matching Engine
- [ ] Implement `matching/dimension_extractor.py`
  - Extract ski length from text (regex patterns)
  - Extract ski width from text
  - Extract condition keywords
- [ ] Implement `matching/fuzzy_matcher.py`
  - Model name matching with fuzzywuzzy
- [ ] Implement `matching/matcher.py`
  - Calculate match scores
  - Apply filters
- [ ] Test with sample listings

### 1.6 Telegram Notifications
- [ ] Implement `notifications/telegram_notifier.py`
  - Send messages via Telegram Bot API
  - Format listing details
  - Handle errors and rate limits
- [ ] Implement `notifications/notification_formatter.py`
  - Rich message formatting
  - Recency calculation
  - Urgency indicators
- [ ] Test with dummy listings

### 1.7 Search Orchestrator
- [ ] Implement `orchestrator/search_orchestrator.py`
  - Coordinate single search run
  - Pull criteria from GitHub
  - Run scrapers
  - Match listings
  - Send notifications
  - Update database
- [ ] Implement error handling
- [ ] Test end-to-end flow

### 1.8 MVP Testing & Deployment
- [ ] Create test suite in `tests/`
- [ ] Manual testing with real searches
- [ ] Deploy to test environment
- [ ] Monitor for 24 hours
- [ ] Fix any issues

**Estimated Complexity:** Core MVP requires implementing ~15 modules with proper error handling and testing

---

## 📦 Phase 2: Additional Marketplaces

### 2.1 eBay Integration
- [ ] Register for eBay Developer account
- [ ] Implement `scrapers/ebay_scraper.py`
  - eBay Finding API integration
  - OAuth authentication
  - Category and aspect filters
- [ ] Test with various search criteria
- [ ] Monitor API rate limits

### 2.2 Facebook Marketplace
- [ ] Implement `scrapers/facebook_scraper.py`
  - Playwright browser automation
  - Handle JavaScript rendering
  - Implement anti-detection measures
  - Cookie management
- [ ] Test with multiple locations
- [ ] Implement robust error recovery

### 2.3 Scraper Factory
- [ ] Implement `scrapers/scraper_factory.py`
- [ ] Dynamic scraper loading based on criteria
- [ ] Test with all marketplaces

---

## ⏰ Phase 3: Scheduling & Continuous Operation

### 3.1 Scheduler Implementation
- [ ] Implement `orchestrator/scheduler.py`
  - APScheduler integration
  - Per-criteria scheduling
  - Dynamic job updates when criteria change
- [ ] Implement health monitoring
- [ ] Test daemon mode

### 3.2 Reliability Improvements
- [ ] Implement retry logic with exponential backoff
- [ ] Implement graceful error recovery
- [ ] Add circuit breaker for failing scrapers
- [ ] Implement health check endpoint

### 3.3 Monitoring & Logging
- [ ] Implement `utils/health_check.py`
- [ ] Set up log rotation
- [ ] Add metrics tracking
- [ ] Create simple status dashboard (optional)

---

## 🚢 Phase 4: Production Deployment

### 4.1 Docker Deployment
- [ ] Test Docker build
- [ ] Test docker-compose setup
- [ ] Create deployment scripts
- [ ] Document deployment process

### 4.2 Documentation
- [ ] Update README with real examples
- [ ] Create troubleshooting guide
- [ ] Add API documentation
- [ ] Create video walkthrough (optional)

### 4.3 Production Testing
- [ ] Deploy to production environment
- [ ] Run for 1 week with monitoring
- [ ] Gather user feedback
- [ ] Optimize based on real-world usage

---

## 🎯 Phase 5: Enhancements (Future)

### Additional Features
- [ ] Email notification fallback
- [ ] Price tracking and history
- [ ] Multiple user support
- [ ] Web dashboard for configuration
- [ ] Mobile app (iOS/Android)
- [ ] Additional marketplaces (Geartrade, Pinkbike, etc.)
- [ ] Machine learning for better matching
- [ ] Image recognition for ski identification
- [ ] Automated seller messaging

---

## Development Guidelines

### Code Quality
- Write tests for all new features
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Document complex logic
- Keep functions focused and small

### Git Workflow
1. Create feature branch for each major component
2. Commit working code frequently
3. Write descriptive commit messages
4. Test before pushing
5. Create PR for review (if collaborative)

### Testing Strategy
- Unit tests for individual functions
- Integration tests for module interactions
- End-to-end tests for complete workflows
- Manual testing with real searches
- Test with various edge cases

### Security Checklist
- [ ] Never commit credentials
- [ ] Validate all external inputs
- [ ] Sanitize URLs and data
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Follow ethical scraping practices

---

## Quick Start for Development

```bash
# 1. Set up development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Create and configure .env
cp .env.example .env
# Edit .env with your credentials

# 3. Run tests
pytest

# 4. Start development
# Begin with Phase 1.1 - Configuration & Setup
```

---

## Current Status

**Phase:** Design Complete ✅  
**Next Milestone:** MVP Core Functionality  
**Next Tasks:**  
1. Implement configuration loading
2. Implement GitHub criteria sync
3. Implement Craigslist scraper
4. Implement basic matching logic

---

## Getting Help

- **Design Questions:** See DESIGN.md
- **Setup Help:** See SETUP.md  
- **Project Structure:** See PROJECT_STRUCTURE.md
- **Implementation Details:** This file (ROADMAP.md)

---

## Success Metrics

MVP is considered complete when:
- [ ] Can pull criteria from GitHub
- [ ] Can search at least one marketplace (Craigslist)
- [ ] Can match listings against criteria
- [ ] Can send Telegram notifications
- [ ] Deduplicates seen listings
- [ ] Runs without errors for 24 hours
- [ ] All core tests pass

---

**Last Updated:** September 28, 2026  
**Version:** 1.0  
**Status:** Ready for implementation
