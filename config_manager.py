# config_manager.py
"""
Configuration Management System
Provides customizable settings for extraction patterns, timeouts, retry settings, and user preferences
"""

import json
import os
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ExtractionMode(Enum):
    """Extraction mode preferences"""
    AGGRESSIVE = "aggressive"  # Try many patterns, longer processing
    BALANCED = "balanced"     # Default mode
    CONSERVATIVE = "conservative"  # Only high-confidence patterns

class OutputFormat(Enum):
    """Supported output formats"""
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    ALL = "all"

@dataclass
class ScrapingConfig:
    """Main scraping configuration"""
    # Request settings
    timeout: int = 15
    max_retries: int = 3
    delay_between_requests: float = 1.0
    max_workers: int = 3
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    
    # Extraction settings
    extraction_mode: str = ExtractionMode.BALANCED.value
    enable_manual_assistance: bool = False
    price_extraction_timeout: int = 30
    dimension_extraction_timeout: int = 30
    
    # Data validation
    min_price: float = 10.0
    max_price: float = 50000.0
    min_length: float = 30.0
    max_length: float = 500.0
    min_width: float = 30.0
    max_width: float = 200.0
    min_height: float = 50.0
    max_height: float = 120.0
    
    # Output settings
    default_output_formats: List[str] = None
    excel_formatting: bool = True
    include_timestamps: bool = True
    
    # Company tracking
    skip_processed_companies: bool = True
    company_tracking_file: str = "processed_companies.json"
    
    # Logging
    log_level: str = "INFO"
    log_directory: str = "logs"
    keep_logs_days: int = 30
    
    def __post_init__(self):
        if self.default_output_formats is None:
            self.default_output_formats = [OutputFormat.EXCEL.value, OutputFormat.CSV.value]

@dataclass
class PriceExtractionConfig:
    """Configuration for price extraction patterns and behavior"""
    currency_symbols: List[str] = None
    currency_codes: List[str] = None
    price_patterns: List[str] = None
    price_selectors: List[str] = None
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.currency_symbols is None:
            self.currency_symbols = ["€", "£", "$", "¥", "₹"]
        
        if self.currency_codes is None:
            self.currency_codes = ["EUR", "GBP", "USD", "CAD", "AUD", "JPY", "INR"]
        
        if self.price_patterns is None:
            self.price_patterns = [
                r"([€£$¥₹])\s?([\d,]+\.?\d*)",
                r"(USD|EUR|GBP|CAD|AUD|JPY|INR)\s?([\d,]+\.?\d*)",
                r"(?:price|cost|from)[\s:]*([€£$])\s?([\d,]+\.?\d*)",
                r"([€£$])\s?([\d,]+\.?\d*)\s*-\s*[€£$]?\s?[\d,]+\.?\d*",
                r"([€£$])\s?([\d]+)[,\.]([\d]{2})",
                r"([\d,]+\.?\d*)\s+(EUR|GBP|USD|CAD|AUD)"
            ]
        
        if self.price_selectors is None:
            self.price_selectors = [
                ".price", ".product-price", ".price-current", "[data-price]",
                ".cost", ".amount", ".value", "[class*='price']", "[id*='price']",
                ".price-box", ".price-wrapper", ".product-price-value", ".current-price",
                ".sale-price", ".regular-price", ".price-display", ".cost-display",
                ".price-now", ".price-was", ".product-cost", ".item-price"
            ]
        
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                r"was\s*[€£$]",  # "was £299" - old prices
                r"save\s*[€£$]", # "save £50" - savings amount
                r"rrp\s*[€£$]"   # "RRP £299" - recommended retail price
            ]

@dataclass
class DimensionExtractionConfig:
    """Configuration for dimension extraction"""
    dimension_patterns: List[str] = None
    dimension_selectors: List[str] = None
    unit_conversions: Dict[str, float] = None
    
    def __post_init__(self):
        if self.dimension_patterns is None:
            self.dimension_patterns = [
                r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*cm',
                r'(\d+)\s*cm\s*[x×]\s*(\d+)\s*cm\s*[x×]\s*(\d+)\s*cm',
                r'L[ength]*[\s:]*(\d+)[cm]*\s*[x×]\s*W[idth]*[\s:]*(\d+)[cm]*\s*[x×]\s*H[eight]*[\s:]*(\d+)[cm]*',
                r'Length[\s:]*(\d+)[cm]*\s*[x×]\s*Width[\s:]*(\d+)[cm]*\s*[x×]\s*Height[\s:]*(\d+)[cm]*',
                r'(\d+)["\']\s*[x×]\s*(\d+)["\']\s*[x×]\s*(\d+)["\']',  # inches
                r'(\d+)\s*inch[es]*\s*[x×]\s*(\d+)\s*inch[es]*\s*[x×]\s*(\d+)\s*inch[es]*'
            ]
        
        if self.dimension_selectors is None:
            self.dimension_selectors = [
                '.dimensions', '.specs', '.specifications', '.product-details',
                '.description', '.product-info', '.details', '.measurements',
                '.size', '.product-specifications', '.tech-specs',
                '[class*="dimension"]', '[class*="spec"]', '[class*="detail"]',
                'table', '.table', '#specifications', '#details', '#dimensions'
            ]
        
        if self.unit_conversions is None:
            self.unit_conversions = {
                'inch': 2.54,
                'ft': 30.48,
                'mm': 0.1,
                'm': 100.0
            }

@dataclass
class MaterialDetectionConfig:
    """Configuration for material detection"""
    material_keywords: Dict[str, List[str]] = None
    finish_keywords: Dict[str, List[str]] = None
    color_keywords: List[str] = None
    
    def __post_init__(self):
        if self.material_keywords is None:
            self.material_keywords = {
                'oak': ['oak', 'solid oak', 'oak wood', 'english oak', 'american oak'],
                'pine': ['pine', 'pine wood', 'scots pine'],
                'walnut': ['walnut', 'walnut wood', 'american walnut'],
                'mahogany': ['mahogany', 'mahogany wood'],
                'beech': ['beech', 'beech wood'],
                'ash': ['ash wood', 'ash', 'european ash'],
                'birch': ['birch', 'birch wood'],
                'maple': ['maple', 'maple wood'],
                'cherry': ['cherry wood', 'cherry'],
                'teak': ['teak', 'teak wood'],
                'mdf': ['mdf', 'medium density fibreboard', 'medium density fiberboard'],
                'plywood': ['plywood', 'ply wood'],
                'veneer': ['veneer', 'veneered', 'wood veneer'],
                'reclaimed': ['reclaimed wood', 'reclaimed', 'recycled wood'],
                'bamboo': ['bamboo', 'bamboo wood']
            }
        
        if self.finish_keywords is None:
            self.finish_keywords = {
                'natural': ['natural', 'unfinished', 'raw', 'bare wood'],
                'stained': ['stained', 'dark stain', 'light stain', 'wood stain'],
                'painted': ['painted', 'white painted', 'black painted'],
                'waxed': ['waxed', 'bee wax', 'furniture wax', 'wax finish'],
                'oiled': ['oiled', 'oil finish', 'danish oil', 'tung oil'],
                'lacquered': ['lacquered', 'lacquer finish', 'clear lacquer'],
                'distressed': ['distressed', 'weathered', 'aged', 'shabby chic'],
                'rustic': ['rustic', 'farmhouse finish', 'country style']
            }
        
        if self.color_keywords is None:
            self.color_keywords = [
                'white', 'black', 'brown', 'honey', 'natural', 'dark',
                'light', 'golden', 'amber', 'espresso', 'charcoal'
            ]

@dataclass
class GoogleSearchConfig:
    """Configuration for Google search functionality"""
    max_results_per_query: int = 5
    max_queries: int = 15
    search_delay: float = 2.0
    headless_browser: bool = True
    chrome_options: List[str] = None
    base_search_terms: List[str] = None
    exclude_domains: List[str] = None
    target_domains: List[str] = None
    
    def __post_init__(self):
        if self.chrome_options is None:
            self.chrome_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ]
        
        if self.base_search_terms is None:
            self.base_search_terms = [
                "solid oak dining table",
                "oak kitchen table",
                "wooden dining table UK",
                "oak furniture store",
                "handmade oak table"
            ]
        
        if self.exclude_domains is None:
            self.exclude_domains = [
                'google.com', 'youtube.com', 'facebook.com', 'twitter.com',
                'instagram.com', 'pinterest.com', 'wikipedia.org', 'amazon.com'
            ]

class ConfigManager:
    """
    Manages all configuration settings for the scraper
    """
    
    def __init__(self, config_file: str = "scraper_config.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.scraping_config = ScrapingConfig()
        self.price_config = PriceExtractionConfig()
        self.dimension_config = DimensionExtractionConfig()
        self.material_config = MaterialDetectionConfig()
        self.search_config = GoogleSearchConfig()
        
        # Load existing config if available
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Update configurations
                if 'scraping' in config_data:
                    self._update_dataclass(self.scraping_config, config_data['scraping'])
                
                if 'price_extraction' in config_data:
                    self._update_dataclass(self.price_config, config_data['price_extraction'])
                
                if 'dimension_extraction' in config_data:
                    self._update_dataclass(self.dimension_config, config_data['dimension_extraction'])
                
                if 'material_detection' in config_data:
                    self._update_dataclass(self.material_config, config_data['material_detection'])
                
                if 'google_search' in config_data:
                    self._update_dataclass(self.search_config, config_data['google_search'])
                
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("No existing config file found, using defaults")
                self.save_config()  # Create default config file
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
    
    def _update_dataclass(self, obj, data):
        """Update dataclass fields from dictionary"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'scraping': asdict(self.scraping_config),
                'price_extraction': asdict(self.price_config),
                'dimension_extraction': asdict(self.dimension_config),
                'material_detection': asdict(self.material_config),
                'google_search': asdict(self.search_config),
                'last_updated': str(datetime.now())
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_config(self, config_type: str = "all"):
        """
        Get specific configuration or all configurations
        
        Args:
            config_type: Type of config to get (scraping, price, dimension, material, search, all)
            
        Returns:
            Configuration object or dictionary
        """
        config_map = {
            'scraping': self.scraping_config,
            'price': self.price_config,
            'dimension': self.dimension_config,
            'material': self.material_config,
            'search': self.search_config
        }
        
        if config_type == "all":
            return {name: asdict(config) for name, config in config_map.items()}
        else:
            return config_map.get(config_type)
    
    def update_config(self, config_type: str, updates: Dict[str, Any]):
        """
        Update specific configuration settings
        
        Args:
            config_type: Type of config to update
            updates: Dictionary of updates to apply
        """
        config_map = {
            'scraping': self.scraping_config,
            'price': self.price_config,
            'dimension': self.dimension_config,
            'material': self.material_config,
            'search': self.search_config
        }
        
        if config_type in config_map:
            config_obj = config_map[config_type]
            self._update_dataclass(config_obj, updates)
            self.save_config()
            logger.info(f"Updated {config_type} configuration")
        else:
            raise ValueError(f"Unknown config type: {config_type}")
    
    def reset_config(self, config_type: str = "all"):
        """
        Reset configuration to defaults
        
        Args:
            config_type: Type of config to reset (or "all")
        """
        if config_type == "all" or config_type == "scraping":
            self.scraping_config = ScrapingConfig()
        
        if config_type == "all" or config_type == "price":
            self.price_config = PriceExtractionConfig()
        
        if config_type == "all" or config_type == "dimension":
            self.dimension_config = DimensionExtractionConfig()
        
        if config_type == "all" or config_type == "material":
            self.material_config = MaterialDetectionConfig()
        
        if config_type == "all" or config_type == "search":
            self.search_config = GoogleSearchConfig()
        
        self.save_config()
        logger.info(f"Reset {config_type} configuration to defaults")
    
    def validate_config(self) -> List[str]:
        """
        Validate current configuration and return any issues
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Validate scraping config
        if self.scraping_config.timeout <= 0:
            issues.append("Timeout must be positive")
        
        if self.scraping_config.max_workers <= 0:
            issues.append("Max workers must be positive")
        
        if self.scraping_config.min_price >= self.scraping_config.max_price:
            issues.append("Min price must be less than max price")
        
        # Validate price patterns
        try:
            import re
            for pattern in self.price_config.price_patterns:
                re.compile(pattern)
        except re.error as e:
            issues.append(f"Invalid price pattern: {e}")
        
        # Validate dimension patterns
        try:
            for pattern in self.dimension_config.dimension_patterns:
                re.compile(pattern)
        except re.error as e:
            issues.append(f"Invalid dimension pattern: {e}")
        
        return issues
    
    def export_sample_config(self, filename: str = "sample_config.yaml"):
        """Export a sample configuration file with comments"""
        sample_config = {
            'scraping': {
                'timeout': 15,
                'max_retries': 3,
                'delay_between_requests': 1.0,
                'max_workers': 3,
                'extraction_mode': 'balanced',  # aggressive, balanced, conservative
                'enable_manual_assistance': False,
                'min_price': 10.0,
                'max_price': 50000.0
            },
            'price_extraction': {
                'currency_symbols': ["€", "£", "$"],
                'price_selectors': [".price", ".product-price", ".cost"]
            },
            'google_search': {
                'max_results_per_query': 5,
                'headless_browser': True,
                'base_search_terms': ["solid oak dining table", "oak furniture"]
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Sample configuration exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting sample config: {e}")


# Global config manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_scraping_config() -> ScrapingConfig:
    """Get scraping configuration"""
    return get_config_manager().scraping_config

def get_price_config() -> PriceExtractionConfig:
    """Get price extraction configuration"""
    return get_config_manager().price_config

def get_dimension_config() -> DimensionExtractionConfig:
    """Get dimension extraction configuration"""
    return get_config_manager().dimension_config

def get_material_config() -> MaterialDetectionConfig:
    """Get material detection configuration"""
    return get_config_manager().material_config

def get_search_config() -> GoogleSearchConfig:
    """Get Google search configuration"""
    return get_config_manager().search_config

if __name__ == "__main__":
    # Example usage and testing
    from datetime import datetime
    
    print("Configuration Manager - Testing")
    print("=" * 40)
    
    config_manager = ConfigManager()
    
    # Show current config
    print("Current configuration:")
    scraping_config = config_manager.get_config('scraping')
    print(f"  Timeout: {scraping_config.timeout}")
    print(f"  Max workers: {scraping_config.max_workers}")
    print(f"  Extraction mode: {scraping_config.extraction_mode}")
    
    # Update some settings
    config_manager.update_config('scraping', {
        'timeout': 20,
        'max_workers': 5,
        'extraction_mode': 'aggressive'
    })
    
    print("\nAfter update:")
    scraping_config = config_manager.get_config('scraping')
    print(f"  Timeout: {scraping_config.timeout}")
    print(f"  Max workers: {scraping_config.max_workers}")
    print(f"  Extraction mode: {scraping_config.extraction_mode}")
    
    # Validate config
    issues = config_manager.validate_config()
    print(f"\nValidation issues: {issues}")
    
    # Export sample config
    config_manager.export_sample_config("test_sample_config.yaml")
    
    print("\nConfiguration testing completed!")