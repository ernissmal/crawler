# field_selector.py
"""
Dynamic Field Selection System
Allows precise control over which data fields are extracted for each search
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse

class FieldType(Enum):
    """Types of fields that can be extracted"""
    TEXT = "text"
    NUMBER = "number"
    PRICE = "price"
    PHONE = "phone"
    EMAIL = "email"
    URL = "url"
    ADDRESS = "address"
    DIMENSIONS = "dimensions"
    DATE = "date"
    RATING = "rating"
    BOOLEAN = "boolean"

class ExtractionStrategy(Enum):
    """How to extract the field value"""
    TEXT_CONTENT = "text_content"      # Get text content
    ATTRIBUTE = "attribute"            # Get attribute value
    REGEX = "regex"                    # Use regex pattern
    MULTIPLE = "multiple"              # Extract multiple values
    CALCULATED = "calculated"          # Calculate from other fields

@dataclass
class FieldSelector:
    """Defines how to extract a specific field"""
    name: str                          # Field name (e.g., "phone_number")
    field_type: FieldType             # Type of data expected
    css_selectors: List[str] = field(default_factory=list)  # CSS selectors to try
    xpath_selectors: List[str] = field(default_factory=list)  # XPath selectors
    regex_patterns: List[str] = field(default_factory=list)   # Regex patterns
    attribute_name: Optional[str] = None                      # HTML attribute to extract
    extraction_strategy: ExtractionStrategy = ExtractionStrategy.TEXT_CONTENT
    required: bool = False                                    # Is this field required?
    multiple_values: bool = False                            # Can have multiple values?
    validation_pattern: Optional[str] = None                 # Validation regex
    format_function: Optional[str] = None                    # Post-processing function
    fallback_selectors: List[str] = field(default_factory=list)  # Backup selectors
    context_keywords: List[str] = field(default_factory=list)    # Context clues

@dataclass 
class ExtractionTemplate:
    """Template defining which fields to extract for a specific search scenario"""
    name: str                          # Template name
    description: str                   # What this template is for
    search_type: str                   # Type of search (person, company, product)
    fields: List[FieldSelector]        # Fields to extract
    priority_fields: List[str] = field(default_factory=list)  # Most important fields
    optional_fields: List[str] = field(default_factory=list)  # Nice-to-have fields
    validation_rules: Dict[str, Any] = field(default_factory=dict)  # Field validation

class SmartFieldExtractor:
    """Intelligent field extraction engine"""
    
    def __init__(self):
        self.field_patterns = self._initialize_field_patterns()
        self.format_functions = self._initialize_format_functions()
        
    def _initialize_field_patterns(self) -> Dict[FieldType, Dict[str, List[str]]]:
        """Initialize common patterns for each field type"""
        return {
            FieldType.PHONE: {
                "patterns": [
                    r"(?:\+44|0)[\s-]?(?:\d[\s-]?){10}",  # UK phone
                    r"(?:\+353|0)[\s-]?(?:\d[\s-]?){8,9}",  # Ireland phone
                    r"(?:\+1)?[\s-]?(?:\d[\s-]?){10}",     # US phone
                    r"(?:\+\d{1,3})?[\s-]?(?:\d[\s-]?){7,14}"  # International
                ],
                "selectors": [
                    "a[href^='tel:']", ".phone", ".telephone", ".contact-phone",
                    "[data-phone]", ".phone-number", "[aria-label*='phone']"
                ]
            },
            
            FieldType.EMAIL: {
                "patterns": [
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                ],
                "selectors": [
                    "a[href^='mailto:']", ".email", ".contact-email", 
                    "[data-email]", "[aria-label*='email']"
                ]
            },
            
            FieldType.PRICE: {
                "patterns": [
                    r"([€£$¥₹])\s?([\d,]+\.?\d*)",
                    r"([\d,]+\.?\d*)\s+(EUR|GBP|USD|AUD|CAD)",
                    r"Price[:\s]+([€£$¥₹])\s?([\d,]+\.?\d*)"
                ],
                "selectors": [
                    ".price", ".cost", ".amount", "[data-price]", 
                    ".price-current", ".product-price", "[aria-label*='price']"
                ]
            },
            
            FieldType.DIMENSIONS: {
                "patterns": [
                    r"(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|inch|in|ft)",
                    r"L:\s*(\d+(?:\.\d+)?)\s*W:\s*(\d+(?:\.\d+)?)\s*H:\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)",
                    r"(\d+(?:\.\d+)?)\s*(cm|mm|m|inch|in|ft)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|inch|in|ft)"
                ],
                "selectors": [
                    ".dimensions", ".size", ".measurements", "[data-dimensions]",
                    ".product-size", ".specs", ".specifications"
                ]
            },
            
            FieldType.ADDRESS: {
                "patterns": [
                    r"\d+\s+[\w\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd)",
                    r"[\w\s]+,\s*[\w\s]+,\s*[A-Z]{2,3}\s*\d*"
                ],
                "selectors": [
                    ".address", ".location", ".contact-address", "[data-address]",
                    ".street-address", ".postal-address", "[aria-label*='address']"
                ]
            },
            
            FieldType.URL: {
                "patterns": [
                    r"https?://[^\s]+"
                ],
                "selectors": [
                    "a[href^='http']", ".website", ".url", "[data-url]",
                    ".company-website", "[aria-label*='website']"
                ]
            },
            
            FieldType.RATING: {
                "patterns": [
                    r"(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+)",
                    r"(\d+(?:\.\d+)?)\s*stars?",
                    r"Rating:\s*(\d+(?:\.\d+)?)"
                ],
                "selectors": [
                    ".rating", ".stars", ".score", "[data-rating]",
                    ".review-rating", ".product-rating", "[aria-label*='rating']"
                ]
            }
        }
    
    def _initialize_format_functions(self) -> Dict[str, callable]:
        """Initialize formatting functions for different field types"""
        return {
            "format_phone": self._format_phone,
            "format_email": self._format_email,
            "format_price": self._format_price,
            "format_dimensions": self._format_dimensions,
            "format_address": self._format_address,
            "format_url": self._format_url,
            "format_rating": self._format_rating
        }
    
    def extract_field(self, soup: BeautifulSoup, field_selector: FieldSelector, 
                     page_url: str = "") -> Optional[Union[str, List[str], Dict[str, Any]]]:
        """Extract a specific field from the page using the field selector"""
        
        values = []
        
        # Try CSS selectors first
        for selector in field_selector.css_selectors:
            elements = soup.select(selector)
            for element in elements:
                value = self._extract_value_from_element(element, field_selector)
                if value:
                    values.append(value)
        
        # Try regex patterns on page text if no values found
        if not values and field_selector.regex_patterns:
            page_text = soup.get_text()
            for pattern in field_selector.regex_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    values.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        # Try fallback selectors
        if not values:
            for selector in field_selector.fallback_selectors:
                elements = soup.select(selector)
                for element in elements:
                    value = self._extract_value_from_element(element, field_selector)
                    if value:
                        values.append(value)
        
        # Use field type patterns as last resort
        if not values:
            values = self._extract_using_field_patterns(soup, field_selector.field_type)
        
        # Process results
        if not values:
            return None
        
        # Apply formatting
        if field_selector.format_function and field_selector.format_function in self.format_functions:
            format_func = self.format_functions[field_selector.format_function]
            values = [format_func(value) for value in values if value]
            values = [v for v in values if v]  # Remove None values
        
        # Apply validation
        if field_selector.validation_pattern:
            validated_values = []
            for value in values:
                if re.match(field_selector.validation_pattern, str(value), re.IGNORECASE):
                    validated_values.append(value)
            values = validated_values
        
        # Return appropriate format
        if not values:
            return None
        elif field_selector.multiple_values:
            return values
        else:
            return values[0]  # Return first valid value
    
    def _extract_value_from_element(self, element: Tag, field_selector: FieldSelector) -> Optional[str]:
        """Extract value from a specific HTML element"""
        
        if field_selector.extraction_strategy == ExtractionStrategy.ATTRIBUTE:
            if field_selector.attribute_name:
                return element.get(field_selector.attribute_name)
        
        elif field_selector.extraction_strategy == ExtractionStrategy.TEXT_CONTENT:
            text = element.get_text().strip()
            
            # Use regex if provided
            if field_selector.regex_patterns:
                for pattern in field_selector.regex_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        return match.group(1) if match.groups() else match.group(0)
            
            return text if text else None
        
        return None
    
    def _extract_using_field_patterns(self, soup: BeautifulSoup, field_type: FieldType) -> List[str]:
        """Use built-in patterns for field type"""
        if field_type not in self.field_patterns:
            return []
        
        patterns_data = self.field_patterns[field_type]
        values = []
        
        # Try selectors first
        for selector in patterns_data.get("selectors", []):
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text:
                    values.append(text)
                # Also check href for links
                if element.name == "a" and element.get("href"):
                    href = element.get("href")
                    if field_type == FieldType.PHONE and href.startswith("tel:"):
                        values.append(href[4:])  # Remove 'tel:'
                    elif field_type == FieldType.EMAIL and href.startswith("mailto:"):
                        values.append(href[7:])  # Remove 'mailto:'
        
        # Try patterns on page text
        page_text = soup.get_text()
        for pattern in patterns_data.get("patterns", []):
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        values.append(' '.join(filter(None, match)))
                    else:
                        values.append(match)
        
        return values
    
    def extract_fields(self, soup: BeautifulSoup, template: ExtractionTemplate, 
                      page_url: str = "") -> Dict[str, Any]:
        """Extract all fields defined in the template"""
        
        results = {
            "url": page_url,
            "template_name": template.name,
            "extraction_timestamp": "2025-09-18T12:00:00Z"
        }
        
        # Extract each field
        for field_selector in template.fields:
            value = self.extract_field(soup, field_selector, page_url)
            if value is not None:
                results[field_selector.name] = value
            elif field_selector.required:
                results[field_selector.name] = None  # Mark as missing but required
        
        # Calculate completeness score
        total_fields = len(template.fields)
        extracted_fields = len([k for k, v in results.items() if v is not None and k not in ["url", "template_name", "extraction_timestamp"]])
        results["data_completeness"] = extracted_fields / total_fields if total_fields > 0 else 0
        
        # Mark priority field status
        priority_extracted = 0
        for field_name in template.priority_fields:
            if field_name in results and results[field_name] is not None:
                priority_extracted += 1
        
        results["priority_completeness"] = priority_extracted / len(template.priority_fields) if template.priority_fields else 1.0
        
        return results
    
    def extract_using_template(self, soup: BeautifulSoup, template: ExtractionTemplate) -> Dict[str, Any]:
        """Extract data using a pre-defined template (alias for extract_fields)"""
        return self.extract_fields(soup, template)
    
    # Formatting functions
    def _format_phone(self, phone: str) -> Optional[str]:
        """Format phone number"""
        if not phone:
            return None
        
        # Remove all non-digits except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Basic validation
        if len(cleaned) < 7:
            return None
        
        return cleaned
    
    def _format_email(self, email: str) -> Optional[str]:
        """Format email address"""
        if not email:
            return None
        
        email = email.lower().strip()
        
        # Basic email validation
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return email
        
        return None
    
    def _format_price(self, price: str) -> Optional[Dict[str, Any]]:
        """Format price information"""
        if not price:
            return None
        
        # Extract currency and amount
        currency_pattern = r'([€£$¥₹])\s?([\d,]+\.?\d*)'
        match = re.search(currency_pattern, price)
        
        if match:
            currency, amount = match.groups()
            try:
                amount_float = float(amount.replace(',', ''))
                return {
                    "currency": currency,
                    "amount": amount_float,
                    "formatted": f"{currency}{amount_float:,.2f}"
                }
            except ValueError:
                pass
        
        # Try amount with currency code
        currency_code_pattern = r'([\d,]+\.?\d*)\s+(EUR|GBP|USD|AUD|CAD)'
        match = re.search(currency_code_pattern, price, re.IGNORECASE)
        
        if match:
            amount, currency_code = match.groups()
            try:
                amount_float = float(amount.replace(',', ''))
                return {
                    "currency_code": currency_code.upper(),
                    "amount": amount_float,
                    "formatted": f"{amount_float:,.2f} {currency_code.upper()}"
                }
            except ValueError:
                pass
        
        return None
    
    def _format_dimensions(self, dimensions: str) -> Optional[Dict[str, Any]]:
        """Format dimensions information"""
        if not dimensions:
            return None
        
        # Pattern: LxWxH with units
        pattern = r'(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|inch|in|ft)'
        match = re.search(pattern, dimensions, re.IGNORECASE)
        
        if match:
            length, width, height, unit = match.groups()
            try:
                return {
                    "length": float(length),
                    "width": float(width),
                    "height": float(height),
                    "unit": unit.lower(),
                    "formatted": f"{length}×{width}×{height} {unit}"
                }
            except ValueError:
                pass
        
        # Pattern: L: W: H: format
        pattern2 = r'L:\s*(\d+(?:\.\d+)?)\s*W:\s*(\d+(?:\.\d+)?)\s*H:\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)'
        match2 = re.search(pattern2, dimensions, re.IGNORECASE)
        
        if match2:
            length, width, height, unit = match2.groups()
            try:
                return {
                    "length": float(length),
                    "width": float(width), 
                    "height": float(height),
                    "unit": unit.lower(),
                    "formatted": f"L:{length} W:{width} H:{height} {unit}"
                }
            except ValueError:
                pass
        
        return None
    
    def _format_address(self, address: str) -> Optional[str]:
        """Format address"""
        if not address:
            return None
        
        # Basic cleanup
        address = re.sub(r'\s+', ' ', address).strip()
        
        return address if len(address) > 5 else None
    
    def _format_url(self, url: str) -> Optional[str]:
        """Format URL"""
        if not url:
            return None
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                return url
        except:
            pass
        
        return None
    
    def _format_rating(self, rating: str) -> Optional[Dict[str, Any]]:
        """Format rating information"""
        if not rating:
            return None
        
        # Pattern: X out of Y or X/Y
        pattern = r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+)'
        match = re.search(pattern, rating)
        
        if match:
            score, max_score = match.groups()
            try:
                return {
                    "score": float(score),
                    "max_score": float(max_score),
                    "percentage": (float(score) / float(max_score)) * 100,
                    "formatted": f"{score}/{max_score}"
                }
            except (ValueError, ZeroDivisionError):
                pass
        
        # Pattern: X stars
        star_pattern = r'(\d+(?:\.\d+)?)\s*stars?'
        star_match = re.search(star_pattern, rating, re.IGNORECASE)
        
        if star_match:
            score = star_match.group(1)
            try:
                return {
                    "score": float(score),
                    "max_score": 5.0,
                    "percentage": (float(score) / 5.0) * 100,
                    "formatted": f"{score}/5 stars"
                }
            except ValueError:
                pass
        
        return None

# Test the field selector
if __name__ == "__main__":
    # Test with sample HTML
    html = """
    <div class="contact-info">
        <div class="phone">+44 28 9267 1234</div>
        <div class="email">contact@company.com</div>
        <div class="address">123 Main Street, Lisburn, BT27 4AA</div>
        <div class="price">£299.99</div>
        <div class="dimensions">120cm x 80cm x 75cm</div>
        <div class="rating">4.5 out of 5</div>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    extractor = SmartFieldExtractor()
    
    # Test phone extraction
    phone_selector = FieldSelector(
        name="phone",
        field_type=FieldType.PHONE,
        css_selectors=[".phone"],
        format_function="format_phone"
    )
    
    phone = extractor.extract_field(soup, phone_selector)
    print(f"Phone: {phone}")
    
    # Test price extraction
    price_selector = FieldSelector(
        name="price",
        field_type=FieldType.PRICE,
        css_selectors=[".price"],
        format_function="format_price"
    )
    
    price = extractor.extract_field(soup, price_selector)
    print(f"Price: {price}")