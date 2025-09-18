# company_tracker.py
"""
Company and Domain Tracking Module
Ensures only one source per company is processed to avoid duplicates
"""

import json
import os
import logging
from urllib.parse import urlparse
from typing import Set, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CompanyTracker:
    """
    Tracks processed companies/domains to ensure uniqueness
    """
    
    def __init__(self, storage_file: str = "processed_companies.json"):
        """
        Initialize company tracker
        
        Args:
            storage_file: JSON file to store processed company data
        """
        self.storage_file = storage_file
        self.processed_companies: Dict[str, Dict] = {}
        self.domain_aliases: Dict[str, str] = {}  # Maps variations to canonical domain
        self.load_processed_companies()
        
    def _normalize_domain(self, url: str) -> str:
        """
        Normalize URL to get canonical domain name
        
        Args:
            url: Full URL or domain
            
        Returns:
            Normalized domain string
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
                
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove common prefixes
            domain = domain.replace('www.', '').replace('shop.', '').replace('store.', '')
            
            # Handle common domain patterns
            if domain.endswith('.co.uk'):
                domain = domain.replace('.co.uk', '')
            elif domain.endswith('.com'):
                domain = domain.replace('.com', '')
            elif domain.endswith('.org'):
                domain = domain.replace('.org', '')
                
            return domain
            
        except Exception as e:
            logger.warning(f"Error normalizing domain from {url}: {e}")
            return url.lower()
    
    def _get_company_name(self, domain: str, url: str = None) -> str:
        """
        Extract company name from domain
        
        Args:
            domain: Normalized domain
            url: Original URL (optional)
            
        Returns:
            Company name
        """
        # Clean up domain to get company name
        company_name = domain.replace('-', ' ').replace('_', ' ')
        
        # Title case
        company_name = ' '.join(word.capitalize() for word in company_name.split())
        
        # Handle special cases
        special_mappings = {
            'oakfurnitureland': 'Oak Furniture Land',
            'next': 'Next',
            'ikea': 'IKEA',
            'johnlewis': 'John Lewis',
            'westelm': 'West Elm',
            'crateandbarrel': 'Crate & Barrel',
            'potterybarn': 'Pottery Barn'
        }
        
        domain_key = domain.replace(' ', '').lower()
        if domain_key in special_mappings:
            company_name = special_mappings[domain_key]
            
        return company_name
    
    def is_company_processed(self, url: str) -> bool:
        """
        Check if company from this URL has already been processed
        
        Args:
            url: URL to check
            
        Returns:
            True if company already processed
        """
        domain = self._normalize_domain(url)
        
        # Check direct domain match
        if domain in self.processed_companies:
            logger.info(f"Company already processed: {domain}")
            return True
            
        # Check domain aliases
        if domain in self.domain_aliases:
            canonical_domain = self.domain_aliases[domain]
            if canonical_domain in self.processed_companies:
                logger.info(f"Company already processed under canonical domain: {canonical_domain}")
                return True
                
        return False
    
    def mark_company_processed(self, url: str, additional_data: Dict = None) -> str:
        """
        Mark a company as processed
        
        Args:
            url: URL that was processed
            additional_data: Additional metadata about the processing
            
        Returns:
            Canonical domain that was marked
        """
        domain = self._normalize_domain(url)
        company_name = self._get_company_name(domain, url)
        
        company_data = {
            'domain': domain,
            'company_name': company_name,
            'original_url': url,
            'processed_date': datetime.now().isoformat(),
            'status': 'processed'
        }
        
        if additional_data:
            company_data.update(additional_data)
            
        self.processed_companies[domain] = company_data
        
        # Save to file
        self.save_processed_companies()
        
        logger.info(f"Marked company as processed: {company_name} ({domain})")
        return domain
    
    def add_domain_alias(self, alias_domain: str, canonical_domain: str):
        """
        Add domain alias mapping
        
        Args:
            alias_domain: Alternative domain
            canonical_domain: Main domain it should map to
        """
        alias_normalized = self._normalize_domain(alias_domain)
        canonical_normalized = self._normalize_domain(canonical_domain)
        
        self.domain_aliases[alias_normalized] = canonical_normalized
        self.save_processed_companies()
        
    def get_processed_companies(self) -> Dict[str, Dict]:
        """
        Get all processed companies
        
        Returns:
            Dictionary of processed companies
        """
        return self.processed_companies.copy()
    
    def filter_unique_urls(self, urls: List[str]) -> List[str]:
        """
        Filter URLs to ensure only one per company
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            Filtered list with unique companies only
        """
        unique_urls = []
        seen_domains = set()
        
        for url in urls:
            domain = self._normalize_domain(url)
            
            # Skip if we've already seen this domain in current batch
            if domain in seen_domains:
                logger.debug(f"Skipping duplicate domain in current batch: {domain}")
                continue
                
            # Skip if company already processed previously
            if self.is_company_processed(url):
                logger.debug(f"Skipping previously processed company: {domain}")
                continue
                
            unique_urls.append(url)
            seen_domains.add(domain)
            
        logger.info(f"Filtered {len(urls)} URLs down to {len(unique_urls)} unique companies")
        return unique_urls
    
    def load_processed_companies(self):
        """Load processed companies from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_companies = data.get('companies', {})
                    self.domain_aliases = data.get('aliases', {})
                logger.info(f"Loaded {len(self.processed_companies)} processed companies")
            else:
                logger.info("No existing company tracking file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading processed companies: {e}")
            self.processed_companies = {}
            self.domain_aliases = {}
    
    def save_processed_companies(self):
        """Save processed companies to storage file"""
        try:
            data = {
                'companies': self.processed_companies,
                'aliases': self.domain_aliases,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug("Saved processed companies to file")
        except Exception as e:
            logger.error(f"Error saving processed companies: {e}")
    
    def reset_tracking(self):
        """Reset all tracking data"""
        self.processed_companies = {}
        self.domain_aliases = {}
        
        if os.path.exists(self.storage_file):
            os.remove(self.storage_file)
            
        logger.info("Reset all company tracking data")
    
    def get_company_stats(self) -> Dict:
        """
        Get statistics about processed companies
        
        Returns:
            Dictionary with statistics
        """
        total_companies = len(self.processed_companies)
        successful_companies = len([c for c in self.processed_companies.values() 
                                   if c.get('status') == 'processed'])
        
        # Get companies by date
        by_date = {}
        for company_data in self.processed_companies.values():
            date = company_data.get('processed_date', '')[:10]  # YYYY-MM-DD
            if date:
                by_date[date] = by_date.get(date, 0) + 1
        
        return {
            'total_companies': total_companies,
            'successful_companies': successful_companies,
            'companies_by_date': by_date,
            'domain_aliases': len(self.domain_aliases)
        }
    
    def export_company_list(self, filename: str = "processed_companies_list.txt"):
        """
        Export list of processed companies to text file
        
        Args:
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Processed Companies List\n")
                f.write("=" * 50 + "\n\n")
                
                for domain, data in sorted(self.processed_companies.items()):
                    company_name = data.get('company_name', domain)
                    processed_date = data.get('processed_date', 'Unknown')[:10]
                    status = data.get('status', 'Unknown')
                    
                    f.write(f"Company: {company_name}\n")
                    f.write(f"Domain: {domain}\n")
                    f.write(f"Date: {processed_date}\n")
                    f.write(f"Status: {status}\n")
                    f.write("-" * 30 + "\n")
                    
            logger.info(f"Exported company list to {filename}")
        except Exception as e:
            logger.error(f"Error exporting company list: {e}")


# Convenience functions
def get_company_tracker() -> CompanyTracker:
    """Get a company tracker instance (singleton pattern)"""
    if not hasattr(get_company_tracker, '_instance'):
        get_company_tracker._instance = CompanyTracker()
    return get_company_tracker._instance


def filter_unique_companies(urls: List[str]) -> List[str]:
    """
    Convenience function to filter URLs for unique companies
    
    Args:
        urls: List of URLs to filter
        
    Returns:
        Filtered list with unique companies
    """
    tracker = get_company_tracker()
    return tracker.filter_unique_urls(urls)


def mark_company_processed(url: str, success: bool = True, additional_data: Dict = None) -> str:
    """
    Convenience function to mark a company as processed
    
    Args:
        url: URL that was processed
        success: Whether processing was successful
        additional_data: Additional metadata
        
    Returns:
        Canonical domain that was marked
    """
    tracker = get_company_tracker()
    
    if additional_data is None:
        additional_data = {}
        
    additional_data['status'] = 'processed' if success else 'failed'
    
    return tracker.mark_company_processed(url, additional_data)


if __name__ == "__main__":
    # Example usage and testing
    print("Company Tracker Module - Testing")
    print("=" * 40)
    
    tracker = CompanyTracker()
    
    # Test URLs
    test_urls = [
        "https://www.oakfurnitureland.co.uk/dining-tables/",
        "https://oakfurnitureland.co.uk/kitchen-tables/",  # Same company
        "https://www.next.co.uk/furniture/dining-tables",
        "https://shop.next.co.uk/furniture/dining-tables",  # Same company, different subdomain
        "https://www.ikea.com/gb/en/cat/dining-tables-21825/",
        "https://www.johnlewis.com/browse/home-garden/furniture/dining-tables"
    ]
    
    print(f"Original URLs: {len(test_urls)}")
    for url in test_urls:
        print(f"  - {url}")
    
    filtered_urls = tracker.filter_unique_urls(test_urls)
    
    print(f"\nFiltered URLs: {len(filtered_urls)}")
    for url in filtered_urls:
        print(f"  - {url}")
    
    # Mark some as processed
    for url in filtered_urls[:2]:
        tracker.mark_company_processed(url, {'test': True})
    
    # Test filtering again
    new_filtered = tracker.filter_unique_urls(test_urls)
    print(f"\nAfter marking 2 as processed: {len(new_filtered)}")
    for url in new_filtered:
        print(f"  - {url}")
    
    # Show stats
    stats = tracker.get_company_stats()
    print(f"\nStats: {stats}")