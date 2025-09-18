# universal_google_search.py
"""
Universal Google Search Module
Provides automated search capabilities for any search type using Selenium
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
from enhanced_logging import EnhancedLogger, ScrapingOperation, LogLevel

class UniversalGoogleSearch:
    """Universal Google search automation for any search type"""
    
    def __init__(self, headless=True, max_results=50, search_type="universal"):
        self.headless = headless
        self.max_results = max_results
        self.search_type = search_type
        self.driver = None
        self.processed_domains = set()
        self.logger = EnhancedLogger(f"google_search_{search_type}")
        
    def setup_driver(self):
        """Setup Chrome WebDriver with enhanced options"""
        if self.driver:
            return
            
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        
        # Enhanced privacy and stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.logger.log_operation(
            ScrapingOperation.GOOGLE_SEARCH,
            f"Chrome WebDriver initialized for {self.search_type} search",
            LogLevel.INFO
        )
    
    def search(self, query: str, include_keywords: List[str] = None, 
               exclude_keywords: List[str] = None, 
               target_domains: List[str] = None,
               region: str = None) -> List[str]:
        """
        Perform a universal Google search and extract relevant URLs
        
        Args:
            query: Main search query
            include_keywords: Keywords that must be present
            exclude_keywords: Keywords to exclude from results
            target_domains: Specific domains to target
            region: Geographic region for localized results
            
        Returns:
            List of unique URLs found in search results
        """
        if not self.driver:
            self.setup_driver()
        
        # Build enhanced query
        enhanced_query = self._build_enhanced_query(
            query, include_keywords, exclude_keywords, region
        )
        
        self.logger.log_operation(
            ScrapingOperation.GOOGLE_SEARCH,
            f"Searching: {enhanced_query}",
            LogLevel.INFO
        )
        
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
            search_box.send_keys(enhanced_query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.yuRUbf, div[data-ved]"))
            )
            
            # Extract URLs from search results
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a, h3 a")
            
            for element in result_elements[:self.max_results]:
                try:
                    url = element.get_attribute("href")
                    if self._is_valid_url(url, target_domains, exclude_keywords):
                        urls.add(url)
                        
                        if len(urls) >= self.max_results:
                            break
                            
                except Exception as e:
                    self.logger.log_operation(
                        ScrapingOperation.GOOGLE_SEARCH,
                        f"Error extracting URL: {str(e)}",
                        LogLevel.WARNING
                    )
                    continue
            
            # Try next page if we need more results
            if len(urls) < self.max_results:
                urls.update(self._search_next_page(enhanced_query, target_domains, exclude_keywords))
            
            self.logger.log_operation(
                ScrapingOperation.GOOGLE_SEARCH,
                f"Found {len(urls)} valid URLs for query: '{enhanced_query}'",
                LogLevel.INFO
            )
            
        except TimeoutException:
            self.logger.log_operation(
                ScrapingOperation.GOOGLE_SEARCH,
                f"Timeout while searching for: {enhanced_query}",
                LogLevel.ERROR
            )
        except WebDriverException as e:
            self.logger.log_operation(
                ScrapingOperation.GOOGLE_SEARCH,
                f"WebDriver error: {str(e)}",
                LogLevel.ERROR
            )
        except Exception as e:
            self.logger.log_operation(
                ScrapingOperation.GOOGLE_SEARCH,
                f"Unexpected error: {str(e)}",
                LogLevel.ERROR
            )
            
        return list(urls)
    
    def _build_enhanced_query(self, query: str, include_keywords: List[str] = None,
                             exclude_keywords: List[str] = None, region: str = None) -> str:
        """Build an enhanced Google search query with filters"""
        enhanced_query = query
        
        # Add include keywords
        if include_keywords:
            for keyword in include_keywords:
                enhanced_query += f' "{keyword}"'
        
        # Add exclude keywords
        if exclude_keywords:
            for keyword in exclude_keywords:
                enhanced_query += f' -{keyword}'
        
        # Add region filter
        if region:
            enhanced_query += f' region:{region}'
        
        return enhanced_query
    
    def _search_next_page(self, query: str, target_domains: List[str] = None,
                         exclude_keywords: List[str] = None) -> Set[str]:
        """Search the next page of results"""
        urls = set()
        
        try:
            # Look for "Next" button
            next_button = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next page'], a#pnnext")
            if next_button:
                next_button.click()
                
                # Wait for new results
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.yuRUbf, div[data-ved]"))
                )
                
                # Extract URLs from second page
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a, h3 a")
                
                for element in result_elements[:20]:  # Limit second page results
                    try:
                        url = element.get_attribute("href")
                        if self._is_valid_url(url, target_domains, exclude_keywords):
                            urls.add(url)
                    except:
                        continue
                        
        except Exception as e:
            self.logger.log_operation(
                ScrapingOperation.GOOGLE_SEARCH,
                f"Could not access next page: {str(e)}",
                LogLevel.WARNING
            )
        
        return urls
    
    def _handle_cookie_consent(self):
        """Handle Google's cookie consent dialog"""
        try:
            accept_buttons = [
                "button[id*='accept']",
                "button[class*='accept']", 
                "div[role='button'][aria-label*='Accept']",
                "div[role='button'][aria-label*='I agree']",
                "#L2AGLb"  # Google's accept button ID
            ]
            
            for selector in accept_buttons:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    time.sleep(1)
                    break
                except:
                    continue
                    
        except Exception as e:
            pass  # Cookie consent is optional
    
    def _is_valid_url(self, url: str, target_domains: List[str] = None,
                     exclude_keywords: List[str] = None) -> bool:
        """Check if URL is valid for scraping"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        # Parse domain
        try:
            domain = urlparse(url).netloc.lower()
        except:
            return False
        
        # Skip Google's own pages
        if any(google_domain in domain for google_domain in [
            'google.com', 'youtube.com', 'maps.google', 'translate.google'
        ]):
            return False
        
        # Skip common non-content domains
        skip_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'pinterest.com', 'reddit.com', 'quora.com', 'stackoverflow.com'
        ]
        
        # Only skip social media if this isn't a social media search
        if self.search_type != "social_media":
            if any(skip_domain in domain for skip_domain in skip_domains):
                return False
        
        # Check target domains if specified
        if target_domains:
            if not any(target_domain.lower() in domain for target_domain in target_domains):
                return False
        
        # Check exclude keywords in URL
        if exclude_keywords:
            url_lower = url.lower()
            if any(keyword.lower() in url_lower for keyword in exclude_keywords):
                return False
        
        # Skip already processed domains for deduplication
        base_domain = self._extract_base_domain(domain)
        if base_domain in self.processed_domains:
            return False
        
        self.processed_domains.add(base_domain)
        return True
    
    def _extract_base_domain(self, domain: str) -> str:
        """Extract base domain for deduplication"""
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return domain
    
    def bulk_search(self, queries: List[str], **kwargs) -> Dict[str, List[str]]:
        """Perform multiple searches and return combined results"""
        all_results = {}
        
        for query in queries:
            self.logger.log_operation(
                ScrapingOperation.GOOGLE_SEARCH,
                f"Bulk search: {query}",
                LogLevel.INFO
            )
            
            results = self.search(query, **kwargs)
            all_results[query] = results
            
            # Small delay between searches
            time.sleep(2)
        
        return all_results
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.log_operation(
                    ScrapingOperation.GOOGLE_SEARCH,
                    "Browser driver closed",
                    LogLevel.INFO
                )
            except Exception as e:
                self.logger.log_operation(
                    ScrapingOperation.GOOGLE_SEARCH,
                    f"Error closing driver: {str(e)}",
                    LogLevel.WARNING
                )
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Backward compatibility alias
GoogleGeeking = UniversalGoogleSearch

# Test function
def test_universal_search():
    """Test the universal search functionality"""
    
    # Test different search types
    test_cases = [
        {
            "search_type": "product",
            "query": "oak furniture Kaunas",
            "include_keywords": ["table", "chair"],
            "exclude_keywords": ["blog", "news"]
        },
        {
            "search_type": "company", 
            "query": "IT companies Lisburn",
            "include_keywords": ["software", "development"],
            "exclude_keywords": ["jobs", "careers"]
        },
        {
            "search_type": "person",
            "query": "John Smith software engineer Dublin",
            "include_keywords": ["profile", "linkedin"],
            "exclude_keywords": ["facebook", "twitter"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['search_type']} search ---")
        
        with UniversalGoogleSearch(
            headless=True, 
            max_results=5, 
            search_type=test_case['search_type']
        ) as searcher:
            
            results = searcher.search(
                query=test_case['query'],
                include_keywords=test_case.get('include_keywords'),
                exclude_keywords=test_case.get('exclude_keywords')
            )
            
            print(f"Found {len(results)} URLs:")
            for url in results[:3]:  # Show first 3
                print(f"  - {url}")

if __name__ == "__main__":
    test_universal_search()