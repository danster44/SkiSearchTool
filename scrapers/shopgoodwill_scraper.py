"""
ShopGoodwill.com Scraper Implementation
Simple scraper for ShopGoodwill online auctions
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import logging

logger = logging.getLogger(__name__)


class ShopGoodwillScraper:
    """
    Scraper for ShopGoodwill.com online auctions.
    
    ShopGoodwill is a nationwide online auction site run by Goodwill stores.
    It has a dedicated Sporting Goods category (ID: 69) that includes skis,
    boots, bindings, and other winter sports equipment.
    """
    
    BASE_URL = "https://shopgoodwill.com"
    SPORTING_GOODS_CATEGORY = 69
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search(self, keywords, max_price=None):
        """
        Search ShopGoodwill for items matching keywords.
        
        Args:
            keywords: String or list of keywords to search
            max_price: Maximum price filter (optional)
            
        Returns:
            List of listing dictionaries
        """
        if isinstance(keywords, list):
            query = ' '.join(keywords)
        else:
            query = keywords
        
        # Build search URL
        url = f"{self.BASE_URL}/search"
        params = {
            'searchText': query,
            'categoryId': self.SPORTING_GOODS_CATEGORY
        }
        
        try:
            # Add respectful delay
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            listings = self._parse_search_results(response.content, max_price)
            
            logger.info(f"ShopGoodwill: Found {len(listings)} listings for '{query}'")
            return listings
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ShopGoodwill search failed: {e}")
            return []
    
    def _parse_search_results(self, html_content, max_price=None):
        """Parse HTML and extract listing data."""
        soup = BeautifulSoup(html_content, 'html.parser')
        listings = []
        
        # Find all auction items
        items = soup.find_all('div', class_='product-tile')
        
        for item in items:
            try:
                listing = self._parse_listing_item(item)
                
                # Apply price filter if specified
                if max_price and listing['price'] > max_price:
                    continue
                
                listings.append(listing)
                
            except Exception as e:
                logger.warning(f"Failed to parse ShopGoodwill item: {e}")
                continue
        
        return listings
    
    def _parse_listing_item(self, item_element):
        """Extract data from a single listing element."""
        # Title
        title_elem = item_element.find('p', class_='product-title')
        title = title_elem.text.strip() if title_elem else 'Unknown'
        
        # Current price
        price_elem = item_element.find('span', class_='current-price')
        price_text = price_elem.text.strip() if price_elem else '$0'
        price = self._parse_price(price_text)
        
        # Item link
        link_elem = item_element.find('a', class_='product-link')
        relative_url = link_elem['href'] if link_elem else ''
        url = f"{self.BASE_URL}{relative_url}" if relative_url else self.BASE_URL
        
        # Item ID from URL
        item_id = self._extract_item_id(relative_url)
        
        # Image
        img_elem = item_element.find('img')
        image_url = img_elem['src'] if img_elem else None
        
        # Time remaining (auction end)
        time_elem = item_element.find('span', class_='time-remaining')
        time_remaining = time_elem.text.strip() if time_elem else 'Unknown'
        
        # Location (Goodwill store)
        location_elem = item_element.find('span', class_='item-location')
        location = location_elem.text.strip() if location_elem else 'Unknown'
        
        return {
            'title': title,
            'price': price,
            'url': url,
            'item_id': item_id,
            'image_url': image_url,
            'time_remaining': time_remaining,
            'location': location,
            'source': 'shopgoodwill',
            'listing_type': 'auction',
            'shipping': 'Available',  # Most items ship
            'posted_date': datetime.now()  # Approximate, actual is auction end
        }
    
    def _parse_price(self, price_text):
        """Parse price string like '$125.00' to float."""
        try:
            # Remove $, commas, and convert to float
            clean_price = price_text.replace('$', '').replace(',', '').strip()
            return float(clean_price)
        except (ValueError, AttributeError):
            return 0.0
    
    def _extract_item_id(self, url):
        """Extract item ID from URL."""
        # URL format: /item/12345678
        import re
        match = re.search(r'/item/(\d+)', url)
        return match.group(1) if match else None
    
    def get_rate_limit(self):
        """Return recommended rate limit in seconds."""
        # Be respectful: 1 search per 5 minutes
        return 300


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = ShopGoodwillScraper()
    
    # Search for skis
    listings = scraper.search('touring skis', max_price=400)
    
    print(f"\nFound {len(listings)} ski auctions:\n")
    for listing in listings[:5]:  # Show first 5
        print(f"  {listing['title']}")
        print(f"  Price: ${listing['price']}")
        print(f"  Time left: {listing['time_remaining']}")
        print(f"  URL: {listing['url']}")
        print()
