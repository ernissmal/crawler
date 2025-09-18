# google_geeking.py
"""
Google Geeking Module for the Oak Table Scraper
Provides automated search capabilities using Selenium to find relevant product URLs
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import logging
import re
from urllib.parse import urlparse
from typing import List, Set, Dict, Optional
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleGeeking:
    """
    Google search automation class for finding furniture-related URLs
    """
    
    def __init__(self, driver_path: str = None, headless: bool = True, max_results: int = 10):
        """
        Initialize the Google Geeking module
        
        Args:
            driver_path: Path to ChromeDriver executable (optional if in PATH)
            headless: Run browser in headless mode
            max_results: Maximum number of URLs to return per search
        """
        self.driver_path = driver_path
        self.headless = headless
        self.max_results = max_results
        self.driver = None
        self.processed_domains = set()  # Track processed domains for deduplication
        
    def _setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            
        # Add common options for better compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        
        try:
            if self.driver_path:
                self.driver = webdriver.Chrome(executable_path=self.driver_path, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            logger.info("Chrome driver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def search(self, query: str, target_domains: List[str] = None) -> List[str]:
        """
        Perform a Google search and extract relevant URLs
        
        Args:
            query: Search query string
            target_domains: Optional list of specific domains to target
            
        Returns:
            List of unique URLs found in search results
        """
        if not self.driver:
            self._setup_driver()
            
        urls = set()
        
        try:
            # Navigate to Google
            self.driver.get("https://www.google.com")
            
            # Handle cookie consent if present
            self._handle_cookie_consent()
            
            # Find search box and perform search
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.yuRUbf"))
            )
            
            # Extract URLs from search results
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a")
            
            for element in result_elements[:self.max_results]:
                try:
                    url = element.get_attribute("href")
                    if self._is_valid_url(url, target_domains):
                        urls.add(url)
                except Exception as e:
                    logger.warning(f"Error extracting URL from result element: {e}")
                    continue
            
            logger.info(f"Found {len(urls)} valid URLs for query: '{query}'")
            
        except TimeoutException:
            logger.error(f"Timeout while searching for: {query}")
        except WebDriverException as e:
            logger.error(f"WebDriver error during search: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            
        return list(urls)
    
    def _handle_cookie_consent(self):
        """Handle Google's cookie consent dialog"""
        try:
            # Try to find and click accept button
            accept_buttons = [
                "button[id*='accept']",
                "button[class*='accept']",
                "div[role='button'][aria-label*='Accept']",
                "div[role='button'][aria-label*='I agree']"
            ]
            
            for selector in accept_buttons:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    logger.info("Accepted cookie consent")
                    return
                except TimeoutException:
                    continue
                    
        except Exception as e:
            logger.debug(f"No cookie consent dialog found or error handling it: {e}")
    
    def _is_valid_url(self, url: str, target_domains: List[str] = None) -> bool:
        """
        Validate if URL is relevant for furniture scraping
        
        Args:
            url: URL to validate
            target_domains: Optional list of target domains
            
        Returns:
            Boolean indicating if URL is valid
        """
        if not url or not url.startswith(('http://', 'https://')):
            return False
            
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower().replace('www.', '')
            
            # Skip if we've already processed this domain (for deduplication)
            if domain in self.processed_domains:
                logger.debug(f"Skipping already processed domain: {domain}")
                return False
            
            # Check against target domains if specified
            if target_domains:
                if not any(target in domain for target in target_domains):
                    return False
            
            # Skip unwanted domains
            unwanted_domains = [
                'google.com', 'youtube.com', 'facebook.com', 'twitter.com',
                'instagram.com', 'pinterest.com', 'wikipedia.org', 'amazon.com'
            ]
            
            if any(unwanted in domain for unwanted in unwanted_domains):
                return False
            
            # Look for furniture-related keywords in URL
            furniture_keywords = [
                'furniture', 'table', 'dining', 'oak', 'wood', 'chair',
                'kitchen', 'home', 'interior', 'design'
            ]
            
            url_lower = url.lower()
            if any(keyword in url_lower for keyword in furniture_keywords):
                self.processed_domains.add(domain)
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error validating URL {url}: {e}")
            return False
    
    def search_multiple_queries(self, queries: List[str], target_domains: List[str] = None) -> Dict[str, List[str]]:
        """
        Perform multiple searches and return organized results
        
        Args:
            queries: List of search queries
            target_domains: Optional list of target domains
            
        Returns:
            Dictionary mapping queries to their found URLs
        """
        results = {}
        
        for query in queries:
            logger.info(f"Searching for: {query}")
            urls = self.search(query, target_domains)
            results[query] = urls
            
            # Add delay between searches to avoid rate limiting
            time.sleep(2)
            
        return results
    
    def generate_furniture_queries(self, base_terms: List[str]) -> List[str]:
        """
        Generate comprehensive search queries for furniture products
        
        Args:
            base_terms: Base product terms (e.g., ['oak table', 'dining table'])
            
        Returns:
            List of generated search queries
        """
        qualifiers = [
            'buy', 'shop', 'purchase', 'furniture store',
            'solid oak', 'wooden', 'dining room', 'kitchen',
            'handmade', 'rustic', 'modern', 'traditional'
        ]
        
        locations = ['UK', 'Britain', 'England', 'Scotland', 'Wales']
        
        queries = []
        
        # Basic queries
        for term in base_terms:
            queries.append(term)
            queries.append(f"{term} UK")
            queries.append(f"buy {term}")
            queries.append(f"{term} furniture store")
            
        # Qualified queries
        for term in base_terms:
            for qualifier in qualifiers[:3]:  # Limit to avoid too many queries
                queries.append(f"{qualifier} {term}")
                
        # Location-specific queries
        for term in base_terms[:2]:  # Limit to main terms
            for location in locations[:2]:  # Limit locations
                queries.append(f"{term} {location}")
                
        return queries
    
    def save_results(self, results: Dict[str, List[str]], filename: str = "search_results.json"):
        """
        Save search results to JSON file
        
        Args:
            results: Dictionary of search results
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Search results saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def load_results(self, filename: str = "search_results.json") -> Dict[str, List[str]]:
        """
        Load search results from JSON file
        
        Args:
            filename: Input filename
            
        Returns:
            Dictionary of search results
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                logger.info(f"Search results loaded from {filename}")
                return results
            else:
                logger.warning(f"File {filename} not found")
                return {}
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return {}
    
    def get_unique_urls(self, results: Dict[str, List[str]]) -> List[str]:
        """
        Extract unique URLs from search results, maintaining domain uniqueness
        
        Args:
            results: Dictionary of search results
            
        Returns:
            List of unique URLs
        """
        all_urls = []
        domain_tracker = set()
        
        for query, urls in results.items():
            for url in urls:
                try:
                    domain = urlparse(url).netloc.lower().replace('www.', '')
                    if domain not in domain_tracker:
                        all_urls.append(url)
                        domain_tracker.add(domain)
                except Exception as e:
                    logger.warning(f"Error processing URL {url}: {e}")
                    
        logger.info(f"Generated {len(all_urls)} unique URLs from {sum(len(urls) for urls in results.values())} total URLs")
        return all_urls
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")


# Convenience functions
def quick_search(query: str, max_results: int = 10, headless: bool = True) -> List[str]:
    """
    Quick search function for simple use cases
    
    Args:
        query: Search query
        max_results: Maximum results to return
        headless: Run in headless mode
        
    Returns:
        List of URLs
    """
    geeking = GoogleGeeking(headless=headless, max_results=max_results)
    try:
        results = geeking.search(query)
        return results
    finally:
        geeking.close()


def bulk_furniture_search(base_terms: List[str] = None, max_results: int = 5, headless: bool = True) -> List[str]:
    """
    Perform bulk search for furniture URLs
    
    Args:
        base_terms: Base search terms (defaults to oak table related terms)
        max_results: Maximum results per query
        headless: Run in headless mode
        
    Returns:
        List of unique URLs
    """
    if base_terms is None:
        base_terms = [
            'solid oak dining table',
            'oak kitchen table',
            'wooden dining table UK',
            'oak furniture store',
            'handmade oak table'
        ]
    
    geeking = GoogleGeeking(headless=headless, max_results=max_results)
    
    try:
        # Generate comprehensive queries
        queries = geeking.generate_furniture_queries(base_terms)
        
        # Limit to reasonable number of queries to avoid rate limiting
        queries = queries[:15]
        
        logger.info(f"Generated {len(queries)} search queries")
        
        # Perform searches
        results = geeking.search_multiple_queries(queries)
        
        # Save results
        geeking.save_results(results)
        
        # Get unique URLs
        unique_urls = geeking.get_unique_urls(results)
        
        return unique_urls
        
    finally:
        geeking.close()


if __name__ == "__main__":
    # Example usage
    print("Google Geeking Module - Furniture URL Discovery")
    print("=" * 50)
    
    # Quick test
    test_query = "solid oak dining table UK"
    print(f"Testing with query: '{test_query}'")
    
    try:
        urls = quick_search(test_query, max_results=5, headless=False)
        print(f"\nFound {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
            
    except Exception as e:
        print(f"Error during test: {e}")
        print("Make sure ChromeDriver is installed and in PATH")
        print("Install with: brew install chromedriver (macOS)")