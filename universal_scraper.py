# universal_scraper.py
"""
Universal Multi-Purpose Scraping Platform
Configurable tool for scraping products, companies, people, social media accounts, and more
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import yaml
import json
import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import pandas as pd

# Import our enhanced modules but make them generic
from google_geeking import GoogleGeeking
from company_tracker import CompanyTracker
from enhanced_logging import EnhancedLogger, ScrapingOperation, LogLevel
from config_manager import ConfigManager
from field_selector import SmartFieldExtractor, FieldSelector, FieldType, ExtractionTemplate
from extraction_templates import TemplateLibrary

app = FastAPI(title="Universal Multi-Purpose Scraper", version="2.0.0")

class SearchType(Enum):
    """Types of searches the platform can handle"""
    PRODUCT = "product"
    COMPANY = "company"
    PERSON = "person"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    CUSTOM = "custom"

class ExtractionMode(Enum):
    """Data extraction modes"""
    BASIC = "basic"          # Extract minimal required data
    DETAILED = "detailed"    # Extract comprehensive data
    CUSTOM = "custom"        # Use custom extraction rules

# Universal Request Models
class UniversalSearchRequest(BaseModel):
    """Universal search request that can handle any search type"""
    search_type: SearchType
    config_file: Optional[str] = None  # Path to specific config file
    
    # Field Selection Options
    extraction_template: Optional[str] = Field(default=None, description="Pre-built template name (john_doe_contacts, oak_table_dimensions, vilnius_it_wordpress)")
    custom_fields: Optional[List[str]] = Field(default=[], description="Custom field names to extract")
    field_selection_mode: Optional[str] = Field(default="template", description="template, custom, or hybrid")
    
    # Core search parameters
    primary_query: str = Field(..., description="Main search term or entity name")
    secondary_queries: Optional[List[str]] = Field(default=[], description="Additional search terms")
    
    # Location/Region targeting
    regions: Optional[List[str]] = Field(default=[], description="Geographic regions to search")
    countries: Optional[List[str]] = Field(default=[], description="Country codes")
    cities: Optional[List[str]] = Field(default=[], description="Specific cities")
    
    # Keywords and filters
    include_keywords: Optional[List[str]] = Field(default=[], description="Must include these terms")
    exclude_keywords: Optional[List[str]] = Field(default=[], description="Must exclude these terms")
    
    # Search behavior
    max_results: Optional[int] = Field(default=50, description="Maximum results to return")
    search_depth: Optional[str] = Field(default="medium", description="shallow, medium, deep")
    extraction_mode: Optional[ExtractionMode] = Field(default=ExtractionMode.DETAILED)
    
    # Type-specific parameters (flexible dict for any search type)
    type_specific_params: Optional[Dict[str, Any]] = Field(default={}, description="Parameters specific to search type")
    
    # Output preferences
    output_formats: Optional[List[str]] = Field(default=["json", "csv"], description="Output formats")
    output_filename: Optional[str] = Field(default=None, description="Custom output filename")

class UniversalConfig:
    """Universal configuration manager that loads type-specific configs"""
    
    def __init__(self, base_config_dir: str = "configs"):
        self.base_config_dir = base_config_dir
        self.configs = {}
        os.makedirs(base_config_dir, exist_ok=True)
        
    def load_config(self, search_type: SearchType, config_file: str = None) -> Dict[str, Any]:
        """Load configuration for specific search type"""
        if config_file:
            config_path = os.path.join(self.base_config_dir, config_file)
        else:
            config_path = os.path.join(self.base_config_dir, f"{search_type.value}_config.yaml")
            
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.configs[search_type.value] = config
            return config
        else:
            # Return default config
            return self.get_default_config(search_type)
    
    def get_default_config(self, search_type: SearchType) -> Dict[str, Any]:
        """Get default configuration for search type"""
        defaults = {
            SearchType.PRODUCT: {
                "extraction": {
                    "required_fields": ["name", "price", "description"],
                    "optional_fields": ["brand", "model", "features", "reviews"],
                    "price_patterns": [r"([€£$¥₹])\s?([\d,]+\.?\d*)", r"([\d,]+\.?\d*)\s+(EUR|GBP|USD)"],
                    "selectors": {
                        "name": ["h1", ".product-title", ".product-name"],
                        "price": [".price", ".product-price", ".cost"],
                        "description": [".description", ".product-description"]
                    }
                },
                "validation": {
                    "price_min": 0.01,
                    "price_max": 999999.99
                }
            },
            SearchType.COMPANY: {
                "extraction": {
                    "required_fields": ["name", "industry", "location"],
                    "optional_fields": ["website", "employees", "revenue", "founded"],
                    "selectors": {
                        "name": ["h1", ".company-name", ".business-name"],
                        "industry": [".industry", ".sector", ".category"],
                        "location": [".address", ".location", ".headquarters"]
                    }
                }
            },
            SearchType.PERSON: {
                "extraction": {
                    "required_fields": ["name", "profession"],
                    "optional_fields": ["company", "location", "education", "social_media"],
                    "selectors": {
                        "name": ["h1", ".person-name", ".profile-name"],
                        "profession": [".title", ".profession", ".job-title"],
                        "company": [".company", ".employer", ".organization"]
                    }
                }
            }
        }
        return defaults.get(search_type, {})

class UniversalExtractor:
    """Universal data extraction engine that adapts to different content types"""
    
    def __init__(self, config: Dict[str, Any], search_type: SearchType, extraction_template: Optional[ExtractionTemplate] = None):
        self.config = config
        self.search_type = search_type
        self.extraction_config = config.get('extraction', {})
        self.logger = EnhancedLogger(f"universal_{search_type.value}")
        
        # Initialize field-based extraction
        self.field_extractor = SmartFieldExtractor()
        self.extraction_template = extraction_template
        
    def extract_data(self, soup, url: str, extraction_mode: ExtractionMode = ExtractionMode.DETAILED) -> Dict[str, Any]:
        """Extract data based on search type and configuration"""
        
        extracted_data = {
            "url": url,
            "search_type": self.search_type.value,
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_mode": extraction_mode.value
        }
        
        # Use smart field extraction if template is provided
        if self.extraction_template:
            self.logger.log_operation(
                ScrapingOperation.DATA_VALIDATION,
                f"Using extraction template: {self.extraction_template.name}",
                LogLevel.INFO, url
            )
            
            # Extract using smart field selector
            template_data = self.field_extractor.extract_using_template(soup, self.extraction_template)
            extracted_data.update(template_data)
            
            # Add template metadata
            extracted_data["template_used"] = self.extraction_template.name
            extracted_data["fields_extracted"] = list(template_data.keys())
            
        else:
            # Fall back to legacy extraction method
            extracted_data.update(self._extract_legacy_data(soup, url, extraction_mode))
        
        # Validate extracted data
        self._validate_data(extracted_data, url)
        
        return extracted_data
    
    def _extract_legacy_data(self, soup, url: str, extraction_mode: ExtractionMode) -> Dict[str, Any]:
        """Legacy extraction method for backward compatibility"""
        legacy_data = {}
        
        # Get required and optional fields
        required_fields = self.extraction_config.get('required_fields', [])
        optional_fields = self.extraction_config.get('optional_fields', [])
        selectors = self.extraction_config.get('selectors', {})
        
        # Extract required fields
        for field in required_fields:
            value = self._extract_field(soup, field, selectors.get(field, []), required=True)
            legacy_data[field] = value
            
        # Extract optional fields if in detailed mode
        if extraction_mode in [ExtractionMode.DETAILED, ExtractionMode.CUSTOM]:
            for field in optional_fields:
                value = self._extract_field(soup, field, selectors.get(field, []), required=False)
                if value:
                    legacy_data[field] = value
        
        # Apply type-specific extraction
        if self.search_type == SearchType.PRODUCT:
            legacy_data.update(self._extract_product_specific(soup))
        elif self.search_type == SearchType.COMPANY:
            legacy_data.update(self._extract_company_specific(soup))
        elif self.search_type == SearchType.PERSON:
            legacy_data.update(self._extract_person_specific(soup))
            
        return legacy_data
    
    def _extract_field(self, soup, field_name: str, selectors: List[str], required: bool = False) -> Optional[str]:
        """Extract a specific field using provided selectors"""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                if element and element.get_text().strip():
                    text = element.get_text().strip()
                    self.logger.log_success(
                        ScrapingOperation.DATA_VALIDATION, 
                        f"Extracted {field_name}: {text[:50]}..."
                    )
                    return text
        
        if required:
            self.logger.log_operation(
                ScrapingOperation.DATA_VALIDATION,
                f"Required field '{field_name}' not found",
                LogLevel.WARNING
            )
        
        return None
    
    def _extract_product_specific(self, soup) -> Dict[str, Any]:
        """Extract product-specific data"""
        product_data = {}
        
        # Price extraction with multiple patterns
        price_patterns = self.extraction_config.get('price_patterns', [])
        text = soup.get_text()
        
        for pattern in price_patterns:
            import re
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) >= 2:
                        currency, amount = match.groups()[:2]
                        product_data['price_currency'] = currency
                        product_data['price_amount'] = float(amount.replace(',', ''))
                        break
                except (ValueError, AttributeError):
                    continue
        
        # Extract features/specifications
        spec_selectors = ['.specifications', '.features', '.details', '.product-specs']
        for selector in spec_selectors:
            spec_elements = soup.select(selector)
            if spec_elements:
                specs = {}
                for element in spec_elements:
                    # Extract key-value pairs from specification tables
                    rows = element.select('tr, .spec-row, .feature-row')
                    for row in rows:
                        cells = row.select('td, .spec-key, .spec-value')
                        if len(cells) >= 2:
                            key = cells[0].get_text().strip()
                            value = cells[1].get_text().strip()
                            if key and value:
                                specs[key] = value
                
                if specs:
                    product_data['specifications'] = specs
                    break
        
        return product_data
    
    def _extract_company_specific(self, soup) -> Dict[str, Any]:
        """Extract company-specific data"""
        company_data = {}
        
        # Extract employee count
        text = soup.get_text().lower()
        import re
        
        employee_patterns = [
            r'(\d+[\d,]*)\s*employees',
            r'(\d+[\d,]*)\s*staff',
            r'team\s*of\s*(\d+[\d,]*)',
            r'(\d+[\d,]*)\s*people'
        ]
        
        for pattern in employee_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    count = int(match.group(1).replace(',', ''))
                    company_data['employee_count'] = count
                    break
                except ValueError:
                    continue
        
        # Extract founded year
        year_pattern = r'(?:founded|established|since)\s*(\d{4})'
        match = re.search(year_pattern, text)
        if match:
            try:
                company_data['founded_year'] = int(match.group(1))
            except ValueError:
                pass
        
        return company_data
    
    def _extract_person_specific(self, soup) -> Dict[str, Any]:
        """Extract person-specific data"""
        person_data = {}
        
        # Extract social media links
        social_links = {}
        social_patterns = {
            'linkedin': r'linkedin\.com/in/([^/\s]+)',
            'twitter': r'twitter\.com/([^/\s]+)',
            'facebook': r'facebook\.com/([^/\s]+)',
            'instagram': r'instagram\.com/([^/\s]+)'
        }
        
        page_html = str(soup)
        import re
        
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, page_html, re.IGNORECASE)
            if match:
                social_links[platform] = match.group(0)
        
        if social_links:
            person_data['social_media'] = social_links
        
        return person_data
    
    def _validate_data(self, data: Dict[str, Any], url: str):
        """Validate extracted data based on configuration"""
        validation_config = self.config.get('validation', {})
        
        # Product-specific validation
        if self.search_type == SearchType.PRODUCT:
            price_amount = data.get('price_amount')
            if price_amount:
                min_price = validation_config.get('price_min', 0)
                max_price = validation_config.get('price_max', float('inf'))
                
                if not (min_price <= price_amount <= max_price):
                    self.logger.log_data_quality_issue(
                        url, 'price_amount', 
                        f"Price {price_amount} outside valid range {min_price}-{max_price}"
                    )

class UniversalScraper:
    """Main universal scraper class"""
    
    def __init__(self):
        self.config_manager = UniversalConfig()
        self.company_tracker = CompanyTracker(storage_file="universal_processed.json")
        self.logger = EnhancedLogger("universal_scraper")
        
    async def search_and_scrape(self, request: UniversalSearchRequest) -> Dict[str, Any]:
        """Main method to search and scrape based on request"""
        
        # Load appropriate configuration
        config = self.config_manager.load_config(request.search_type, request.config_file)
        
        # Determine extraction template
        extraction_template = None
        if request.extraction_template:
            extraction_template = TemplateLibrary.get_template_by_name(request.extraction_template)
            if not extraction_template:
                self.logger.log_operation(
                    ScrapingOperation.DATA_VALIDATION,
                    f"Template '{request.extraction_template}' not found, using default extraction",
                    LogLevel.WARNING
                )
        elif request.field_selection_mode == "custom" and request.custom_fields:
            # Create custom template from specified fields
            extraction_template = self._create_custom_template(request)
        
        # Initialize extractor with template
        extractor = UniversalExtractor(config, request.search_type, extraction_template)
        
        # Generate search queries
        queries = self._generate_queries(request)
        
        # Perform Google search
        urls = await self._perform_search(queries, request)
        
        # Filter unique URLs if needed
        if request.search_type in [SearchType.COMPANY, SearchType.PRODUCT]:
            urls = self.company_tracker.filter_unique_urls(urls)
        
        # Scrape data from URLs
        results = await self._scrape_urls(urls, extractor, request)
        
        # Export results
        output_files = self._export_results(results, request)
        
        return {
            "search_type": request.search_type.value,
            "extraction_template": request.extraction_template or "legacy",
            "total_urls_found": len(urls),
            "total_results": len(results),
            "results": results,
            "output_files": output_files,
            "session_summary": self.logger.get_session_summary()
        }
    
    def _generate_queries(self, request: UniversalSearchRequest) -> List[str]:
        """Generate search queries based on request parameters"""
        queries = [request.primary_query]
        
        # Add secondary queries
        queries.extend(request.secondary_queries)
        
        # Add region-specific queries
        for region in request.regions:
            queries.append(f"{request.primary_query} {region}")
            
        # Add keyword combinations
        for keyword in request.include_keywords:
            queries.append(f"{request.primary_query} {keyword}")
            
        return queries[:20]  # Limit to reasonable number
    
    async def _perform_search(self, queries: List[str], request: UniversalSearchRequest) -> List[str]:
        """Perform Google search for queries"""
        all_urls = []
        
        geeking = GoogleGeeking(headless=True, max_results=request.max_results // len(queries))
        
        try:
            for query in queries:
                # Add exclude keywords to query
                if request.exclude_keywords:
                    exclude_terms = " ".join([f"-{keyword}" for keyword in request.exclude_keywords])
                    query = f"{query} {exclude_terms}"
                
                urls = geeking.search(query)
                all_urls.extend(urls)
                
        finally:
            geeking.close()
        
        # Remove duplicates
        return list(set(all_urls))
    
    async def _scrape_urls(self, urls: List[str], extractor: UniversalExtractor, 
                          request: UniversalSearchRequest) -> List[Dict[str, Any]]:
        """Scrape data from URLs using the universal extractor"""
        results = []
        
        # Import scraping utilities
        from enhanced_main import create_enhanced_session
        import requests
        from bs4 import BeautifulSoup
        
        session = create_enhanced_session()
        
        for url in urls:
            try:
                self.logger.log_operation(
                    ScrapingOperation.URL_FETCH,
                    f"Scraping {request.search_type.value} data",
                    LogLevel.INFO, url
                )
                
                response = session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                data = extractor.extract_data(soup, url, request.extraction_mode)
                results.append(data)
                
                # Mark as processed if it's a company/product
                if request.search_type in [SearchType.COMPANY, SearchType.PRODUCT]:
                    self.company_tracker.mark_company_processed(url, True)
                
            except Exception as e:
                self.logger.log_operation(
                    ScrapingOperation.URL_FETCH,
                    f"Failed to scrape: {str(e)}",
                    LogLevel.ERROR, url
                )
                continue
        
        return results
    
    def _create_custom_template(self, request: UniversalSearchRequest) -> ExtractionTemplate:
        """Create a custom extraction template from request parameters"""
        fields = []
        
        # Map common field names to FieldTypes
        field_type_mapping = {
            'phone': FieldType.PHONE,
            'email': FieldType.EMAIL,
            'price': FieldType.PRICE,
            'dimensions': FieldType.DIMENSIONS,
            'address': FieldType.ADDRESS,
            'url': FieldType.URL,
            'rating': FieldType.RATING,
            'number': FieldType.NUMBER,
            'date': FieldType.DATE,
            'percentage': FieldType.PERCENTAGE
        }
        
        for field_name in request.custom_fields:
            # Determine field type
            field_type = FieldType.TEXT  # Default
            for key, ftype in field_type_mapping.items():
                if key in field_name.lower():
                    field_type = ftype
                    break
            
            # Create field selector
            field_selector = FieldSelector(
                name=field_name,
                field_type=field_type,
                css_selectors=[f".{field_name}", f"[data-{field_name}]", f".{field_name.replace('_', '-')}"],
                required=True if field_name in ['name', 'title', 'company'] else False
            )
            fields.append(field_selector)
        
        # Create custom template
        template = ExtractionTemplate(
            name="custom_extraction",
            description=f"Custom extraction for {request.search_type.value}",
            search_type=request.search_type.value,
            fields=fields,
            priority_fields=request.custom_fields[:3],  # First 3 as priority
            optional_fields=request.custom_fields[3:],
            validation_rules={}
        )
        
        return template
    
    def _export_results(self, results: List[Dict[str, Any]], 
                       request: UniversalSearchRequest) -> Dict[str, str]:
        """Export results in requested formats"""
        output_files = {}
        
        if not results:
            return output_files
        
        # Generate base filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = request.output_filename or f"{request.search_type.value}_results_{timestamp}"
        
        # Export to different formats
        df = pd.DataFrame(results)
        
        for format_type in request.output_formats:
            if format_type == "csv":
                filename = f"{base_filename}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                output_files['csv'] = filename
                
            elif format_type == "json":
                filename = f"{base_filename}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                output_files['json'] = filename
                
            elif format_type == "excel":
                filename = f"{base_filename}.xlsx"
                df.to_excel(filename, index=False)
                output_files['excel'] = filename
        
        return output_files

# Initialize universal scraper
universal_scraper = UniversalScraper()

# API Endpoints
@app.get("/")
def health_check():
    return {
        "status": "OK",
        "message": "Universal Multi-Purpose Scraper API",
        "version": "2.0.0",
        "supported_search_types": [t.value for t in SearchType]
    }

@app.post("/search")
async def universal_search(request: UniversalSearchRequest):
    """Universal search endpoint that handles any search type"""
    try:
        results = await universal_scraper.search_and_scrape(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/search-types")
def get_search_types():
    """Get available search types and their configurations"""
    search_types = {}
    for search_type in SearchType:
        config = universal_scraper.config_manager.get_default_config(search_type)
        search_types[search_type.value] = {
            "description": f"Search for {search_type.value}s",
            "required_fields": config.get('extraction', {}).get('required_fields', []),
            "optional_fields": config.get('extraction', {}).get('optional_fields', [])
        }
    return search_types

@app.post("/create-config")
def create_config_template(search_type: SearchType, filename: Optional[str] = None):
    """Create a configuration template for a specific search type"""
    config = universal_scraper.config_manager.get_default_config(search_type)
    
    if filename is None:
        filename = f"{search_type.value}_config.yaml"
    
    config_path = os.path.join("configs", filename)
    os.makedirs("configs", exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {
        "message": f"Configuration template created for {search_type.value}",
        "filename": config_path,
        "config": config
    }

@app.get("/templates")
def list_extraction_templates():
    """List all available extraction templates"""
    return {
        "templates": TemplateLibrary.list_available_templates(),
        "custom_template_support": True,
        "supported_field_types": [ft.value for ft in FieldType]
    }

@app.get("/templates/{template_name}")
def get_template_details(template_name: str):
    """Get detailed information about a specific template"""
    template = TemplateLibrary.get_template_by_name(template_name)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    return {
        "template": {
            "name": template.name,
            "description": template.description,
            "search_type": template.search_type,
            "total_fields": len(template.fields),
            "priority_fields": template.priority_fields,
            "optional_fields": template.optional_fields,
            "validation_rules": template.validation_rules,
            "fields": [
                {
                    "name": field.name,
                    "type": field.field_type.value,
                    "required": field.required,
                    "css_selectors": field.css_selectors,
                    "context_keywords": getattr(field, 'context_keywords', [])
                }
                for field in template.fields
            ]
        }
    }

@app.post("/search/john-doe-contacts")
async def search_john_doe_contacts(
    query: str = "John Doe Lisburn contact",
    max_results: int = 20
):
    """Specialized endpoint for John Doe contact searches"""
    request = UniversalSearchRequest(
        search_type=SearchType.PERSON,
        primary_query=query,
        extraction_template="john_doe_contacts",
        max_results=max_results,
        include_keywords=["lisburn", "contact", "phone", "email"],
        cities=["Lisburn"]
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/oak-table-dimensions")
async def search_oak_tables(
    query: str = "solid oak table surface dimensions",
    max_results: int = 30
):
    """Specialized endpoint for oak table searches with dimensions"""
    request = UniversalSearchRequest(
        search_type=SearchType.PRODUCT,
        primary_query=query,
        extraction_template="oak_table_dimensions",
        max_results=max_results,
        include_keywords=["solid oak", "table", "dimensions", "cm"],
        exclude_keywords=["chair", "stool", "leg"]
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/vilnius-it-companies")
async def search_vilnius_it_companies(
    query: str = "IT companies Vilnius WordPress development",
    max_results: int = 25
):
    """Specialized endpoint for Vilnius IT companies"""
    request = UniversalSearchRequest(
        search_type=SearchType.COMPANY,
        primary_query=query,
        extraction_template="vilnius_it_wordpress",
        max_results=max_results,
        include_keywords=["vilnius", "lithuania", "wordpress", "web development"],
        cities=["Vilnius"],
        countries=["LT", "Lithuania"]
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)