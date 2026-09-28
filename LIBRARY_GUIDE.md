# Free & Proven Marketplace Libraries Guide

This document details the free, battle-tested libraries we use for each marketplace.

---

## 📦 Library Selection Criteria

All libraries selected based on:
- ✅ **Free and Open Source** (MIT/Apache license)
- ✅ **Proven in Production** (1000+ downloads/month or 500+ GitHub stars)
- ✅ **Actively Maintained** (commits within last 6 months)
- ✅ **Good Documentation**
- ✅ **Python 3.10+ Compatible**

---

## 🛒 Marketplace Libraries

### 1. Craigslist: `python-craigslist`

**Repository:** https://github.com/juliomalegria/python-craigslist  
**PyPI:** https://pypi.org/project/python-craigslist/  
**License:** MIT  
**Stars:** 1,100+  
**Status:** ✅ Actively Maintained

**Why This Library:**
- Simple, Pythonic API
- Handles all HTML parsing internally
- Multi-region support built-in
- Automatic pagination
- Filter support (price, location, images)
- RSS feed integration

**Installation:**
```bash
pip install python-craigslist
```

**Quick Example:**
```python
from craigslist import CraigslistForSale

# Search Seattle sporting goods
cl = CraigslistForSale(site='seattle', category='sss')
results = cl.get_results(
    filters={'query': 'k2 way back 92', 'max_price': 500},
    sort_by='newest',
    limit=100
)

for result in results:
    print(result['name'], result['price'], result['url'])
```

**Features:**
- ✅ No manual HTML parsing needed
- ✅ Respects Craigslist rate limits
- ✅ Returns structured data
- ✅ Handles errors gracefully
- ✅ Supports all Craigslist regions
- ✅ Built-in filters

**Limitations:**
- Craigslist can change HTML structure (library usually updates quickly)
- No official API, so changes can break temporarily

**Cost:** FREE

---

### 2. eBay: `ebaysdk-python` (Official)

**Repository:** https://github.com/timotheus/ebaysdk-python  
**PyPI:** https://pypi.org/project/ebaysdk/  
**Documentation:** https://developer.ebay.com/  
**License:** Apache 2.0  
**Stars:** 700+  
**Status:** ✅ Maintained by eBay

**Why This Library:**
- Official eBay SDK
- Uses Finding API (5,000 free calls/day)
- No scraping needed
- Well-documented
- Reliable and fast
- Structured API responses

**Installation:**
```bash
pip install ebaysdk
```

**Setup:**
1. Register at https://developer.ebay.com/
2. Create application (Sandbox or Production)
3. Get App ID (Client ID) - FREE
4. 5,000 API calls/day included free

**Quick Example:**
```python
from ebaysdk.finding import Connection as Finding

api = Finding(appid='YOUR_APP_ID', config_file=None)

response = api.execute('findItemsAdvanced', {
    'keywords': 'k2 way back 92',
    'categoryId': '159049',  # Downhill Skiing
    'itemFilter': [
        {'name': 'MaxPrice', 'value': 500},
        {'name': 'Condition', 'value': 'Used'}
    ],
    'sortOrder': 'StartTimeNewest'
})

items = response.dict()['searchResult']['item']
for item in items:
    print(item['title'], item['sellingStatus']['currentPrice']['value'])
```

**Features:**
- ✅ Official API (no scraping)
- ✅ 5,000 free calls/day (more than enough)
- ✅ Structured JSON responses
- ✅ Category and aspect filters
- ✅ Advanced search options
- ✅ Multiple marketplaces (US, UK, CA, etc.)
- ✅ Real-time data

**APIs Included (Free Tier):**
- **Finding API** - Search listings (what we use)
- **Shopping API** - Get item details
- **Merchandising API** - Related items

**Rate Limits:**
- 5,000 calls/day (free tier)
- At 15-min search intervals: ~96 calls/day
- Well within limits!

**Cost:** FREE (up to 5,000 calls/day)

---

### 3. Facebook Marketplace: `playwright` (Browser Automation)

**Repository:** https://github.com/microsoft/playwright-python  
**PyPI:** https://pypi.org/project/playwright/  
**Documentation:** https://playwright.dev/python/  
**License:** Apache 2.0  
**Stars:** 60,000+  
**Status:** ✅ Actively maintained by Microsoft

**Why This Library:**
- Facebook Marketplace has NO official API
- No free proven scraper libraries (all break frequently)
- Playwright is the most reliable approach
- Handles JavaScript rendering
- Maintained by Microsoft (very stable)
- Can bypass basic anti-bot measures

**Installation:**
```bash
pip install playwright
playwright install chromium
```

**Quick Example:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Search Seattle marketplace
    url = "https://www.facebook.com/marketplace/seattle/search?query=k2+way+back+92"
    page.goto(url)
    page.wait_for_selector('[data-testid="marketplace-search-result"]')
    
    # Extract listings
    items = page.query_selector_all('[data-testid="marketplace-search-result"]')
    for item in items:
        title = item.query_selector('span').inner_text()
        print(title)
    
    browser.close()
```

**Features:**
- ✅ Handles JavaScript (required for Facebook)
- ✅ Can take screenshots
- ✅ Supports multiple browsers
- ✅ Network interception
- ✅ Mobile emulation
- ✅ Auto-waiting for elements
- ✅ Very reliable

**Alternatives Considered:**

| Library | Stars | Status | Why Not Used |
|---------|-------|--------|--------------|
| selenium | 30k+ | ✅ Active | Heavier, slower than Playwright |
| facebook-scraper | 2k+ | ⚠️ Breaks often | Not reliable for Marketplace |
| BeautifulSoup | 10k+ | ✅ Active | Doesn't handle JS rendering |

**Playwright vs Selenium:**
- Playwright is faster (async by default)
- Better auto-waiting
- Smaller browser footprint
- Maintained by Microsoft
- Better documentation

**Cost:** FREE (open source)

**Note:** Facebook Marketplace is the trickiest:
- No official API
- Anti-scraping measures
- UI changes frequently
- May require occasional maintenance

**Recommended Approach:**
1. Start with Playwright (most reliable)
2. Use conservative rate limits (1 search per 5-10 min)
3. Implement good error handling
4. Have manual fallback if needed

---

## 📊 Library Comparison

| Marketplace | Library | Type | API/Scrape | Free Tier | Reliability | Maintenance |
|-------------|---------|------|------------|-----------|-------------|-------------|
| **Craigslist** | python-craigslist | Wrapper | Scrape | Unlimited | ⭐⭐⭐⭐ | ✅ Active |
| **eBay** | ebaysdk-python | Official | API | 5k/day | ⭐⭐⭐⭐⭐ | ✅ Official |
| **Facebook** | playwright | Automation | Browser | Unlimited | ⭐⭐⭐⭐ | ✅ Microsoft |

---

## 🎯 Usage Patterns

### Daily Searches (15-min intervals, 96 searches/day):

**Craigslist:** 
- 5 regions × 96 searches = 480 requests/day
- Status: ✅ No problem (no official limit)

**eBay:**
- 1 × 96 searches = 96 requests/day  
- Free tier: 5,000/day
- Status: ✅ Only 1.9% of free tier used

**Facebook:**
- 1 × 96 searches = 96 requests/day
- Status: ✅ No problem (with conservative rate limiting)

---

## 💰 Total Cost

**All Libraries:** $0/month

All three libraries are:
- Free to use
- Open source
- No paid tiers needed
- No API fees
- No rate limit concerns for our use case

---

## 🔧 Installation

Add to `requirements.txt`:
```txt
# Marketplace Libraries (all free)
python-craigslist==1.0.4      # Craigslist
ebaysdk==2.2.0                  # eBay (official)
playwright==1.40.0              # Facebook (browser automation)
```

Install:
```bash
pip install -r requirements.txt
playwright install chromium  # One-time browser install
```

---

## 📚 Documentation Links

- **python-craigslist:** https://github.com/juliomalegria/python-craigslist
- **ebaysdk-python:** https://github.com/timotheus/ebaysdk-python
- **eBay Finding API:** https://developer.ebay.com/devzone/finding/Concepts/FindingAPIGuide.html
- **Playwright Python:** https://playwright.dev/python/docs/intro

---

## 🚨 Maintenance Notes

### Craigslist
- Update library when Craigslist changes HTML structure
- Usually updated within days of changes
- Fallback: Can implement manual BeautifulSoup scraper

### eBay
- Very stable (official API)
- Rarely breaks
- Well-documented breaking changes

### Facebook
- Most likely to need maintenance
- Facebook changes UI frequently
- Playwright is most resilient option
- May need selector updates occasionally

---

## 🎓 Learning Resources

### python-craigslist
```python
# Basic usage examples
from craigslist import CraigslistForSale, CraigslistHousing

# Sporting goods
cl = CraigslistForSale(site='seattle', category='sss')

# Get results with filters
results = cl.get_results(
    filters={
        'query': 'skis',
        'min_price': 100,
        'max_price': 500,
        'has_image': True
    },
    sort_by='newest',
    limit=50
)

# Iterate results
for result in results:
    print(f"{result['name']}: ${result['price']} - {result['url']}")
```

### ebaysdk-python
```python
# Finding API examples
from ebaysdk.finding import Connection

api = Connection(appid='YOUR_APP_ID', config_file=None)

# Simple keyword search
response = api.execute('findItemsByKeywords', {'keywords': 'skis'})

# Advanced search
response = api.execute('findItemsAdvanced', {
    'keywords': 'touring skis',
    'categoryId': '159049',
    'itemFilter': [
        {'name': 'Condition', 'value': 'Used'},
        {'name': 'MaxPrice', 'value': '500'},
    ],
    'paginationInput': {'entriesPerPage': 100}
})

items = response.dict()['searchResult']['item']
```

### playwright
```python
# Synchronous API example
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com')
    
    # Wait for element
    page.wait_for_selector('.listing')
    
    # Extract data
    titles = page.query_selector_all('.title')
    for title in titles:
        print(title.inner_text())
    
    browser.close()

# Async API example (more efficient)
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://example.com')
        await browser.close()

asyncio.run(main())
```

---

## ✅ Recommendation Summary

For this ski search project:

1. **Start with eBay** (easiest, most reliable)
   - Official API
   - Free 5k calls/day
   - Clean data

2. **Add Craigslist** (simple library)
   - python-craigslist library
   - Multi-region search
   - Very straightforward

3. **Add Facebook last** (most complex)
   - Use Playwright
   - Conservative rate limits
   - More maintenance needed

This gives you three major marketplaces with all free, proven libraries.

---

**Last Updated:** September 28, 2026  
**Status:** All libraries actively maintained and free
