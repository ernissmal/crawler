# extraction_templates.py
"""
Pre-built Extraction Templates for Common Search Scenarios
These templates define exactly which fields to extract for specific use cases
"""

from typing import List, Dict, Any
from field_selector import ExtractionTemplate, FieldSelector, FieldType, ExtractionStrategy

class TemplateLibrary:
    """Library of pre-built extraction templates"""
    
    @staticmethod
    def get_john_doe_contact_template() -> ExtractionTemplate:
        """Template for finding contact info for people named John Doe"""
        return ExtractionTemplate(
            name="john_doe_contacts",
            description="Extract phone numbers and email addresses for John Doe searches",
            search_type="person",
            fields=[
                FieldSelector(
                    name="phone_number",
                    field_type=FieldType.PHONE,
                    css_selectors=[
                        ".phone", ".telephone", ".contact-phone", ".mobile",
                        "a[href^='tel:']", "[data-phone]", ".phone-number"
                    ],
                    regex_patterns=[
                        r"(?:\+44|0)[\s-]?(?:\d[\s-]?){10}",  # UK format
                        r"(?:\+353|0)[\s-]?(?:\d[\s-]?){8,9}",  # Ireland format
                        r"(?:\+\d{1,3})?[\s-]?(?:\d[\s-]?){7,14}"  # International
                    ],
                    fallback_selectors=[".contact", ".info", "[aria-label*='phone']"],
                    required=True,
                    format_function="format_phone",
                    validation_pattern=r"[\d+\s-]+"
                ),
                FieldSelector(
                    name="email_address",
                    field_type=FieldType.EMAIL,
                    css_selectors=[
                        ".email", ".contact-email", "a[href^='mailto:']",
                        "[data-email]", ".email-address"
                    ],
                    regex_patterns=[
                        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    ],
                    fallback_selectors=[".contact", ".info", "[aria-label*='email']"],
                    required=True,
                    format_function="format_email",
                    validation_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                ),
                FieldSelector(
                    name="name",
                    field_type=FieldType.TEXT,
                    css_selectors=[
                        "h1", "h2", ".name", ".person-name", ".profile-name",
                        ".contact-name", "[data-name]"
                    ],
                    required=False  # Optional since we know it's John Doe
                ),
                FieldSelector(
                    name="location",
                    field_type=FieldType.ADDRESS,
                    css_selectors=[
                        ".address", ".location", ".city", ".area",
                        "[data-location]", ".contact-address"
                    ],
                    context_keywords=["lisburn", "belfast", "northern ireland"],
                    required=False
                )
            ],
            priority_fields=["phone_number", "email_address"],
            optional_fields=["name", "location"],
            validation_rules={
                "min_priority_fields": 1,  # At least one contact method
                "location_filter": ["lisburn"]  # Must be in Lisburn
            }
        )
    
    @staticmethod
    def get_oak_table_dimensions_template() -> ExtractionTemplate:
        """Template for solid oak table surfaces with dimensions"""
        return ExtractionTemplate(
            name="oak_table_dimensions",
            description="Extract URL, company, price, dimensions, and location for solid oak tables",
            search_type="product",
            fields=[
                FieldSelector(
                    name="product_url",
                    field_type=FieldType.URL,
                    css_selectors=[
                        "a[href*='product']", "a[href*='table']", ".product-link",
                        "a.product-title", "[data-product-url]"
                    ],
                    extraction_strategy=ExtractionStrategy.ATTRIBUTE,
                    attribute_name="href",
                    required=True,
                    format_function="format_url"
                ),
                FieldSelector(
                    name="company_name",
                    field_type=FieldType.TEXT,
                    css_selectors=[
                        ".brand", ".company", ".manufacturer", ".seller",
                        ".store-name", "[data-brand]", ".vendor"
                    ],
                    fallback_selectors=[
                        ".logo img", "img[alt*='logo']", ".header .brand"
                    ],
                    required=True
                ),
                FieldSelector(
                    name="price",
                    field_type=FieldType.PRICE,
                    css_selectors=[
                        ".price", ".cost", ".amount", "[data-price]",
                        ".price-current", ".product-price", ".sale-price"
                    ],
                    regex_patterns=[
                        r"([€£$¥₹])\s?([\d,]+\.?\d*)",
                        r"([\d,]+\.?\d*)\s+(EUR|GBP|USD|AUD|CAD)",
                        r"Price[:\s]+([€£$¥₹])\s?([\d,]+\.?\d*)"
                    ],
                    required=True,
                    format_function="format_price"
                ),
                FieldSelector(
                    name="dimensions",
                    field_type=FieldType.DIMENSIONS,
                    css_selectors=[
                        ".dimensions", ".size", ".measurements", "[data-dimensions]",
                        ".product-size", ".specs", ".specifications", ".details"
                    ],
                    regex_patterns=[
                        r"(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)",
                        r"L:\s*(\d+(?:\.\d+)?)\s*W:\s*(\d+(?:\.\d+)?)\s*H:\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)",
                        r"Length[:\s]*(\d+(?:\.\d+)?)\s*Width[:\s]*(\d+(?:\.\d+)?)\s*Height[:\s]*(\d+(?:\.\d+)?)\s*(cm|mm|m)"
                    ],
                    context_keywords=["dimensions", "size", "measurements", "LxWxH"],
                    required=True,
                    format_function="format_dimensions"
                ),
                FieldSelector(
                    name="location_available",
                    field_type=FieldType.ADDRESS,
                    css_selectors=[
                        ".location", ".availability", ".delivery", ".shipping",
                        ".store-location", "[data-location]", ".available-at"
                    ],
                    regex_patterns=[
                        r"(?:Available in|Ships to|Delivery to)[\s:]*([^,]+)",
                        r"Location[\s:]*([^,\n]+)"
                    ],
                    context_keywords=["available", "delivery", "shipping", "location"],
                    required=False
                ),
                FieldSelector(
                    name="material",
                    field_type=FieldType.TEXT,
                    css_selectors=[
                        ".material", ".wood-type", ".construction", "[data-material]"
                    ],
                    regex_patterns=[
                        r"(solid oak|oak wood|oak veneer|solid wood)",
                        r"Material[\s:]*([^,\n]+)"
                    ],
                    context_keywords=["solid oak", "oak", "wood", "material"],
                    required=False
                )
            ],
            priority_fields=["product_url", "company_name", "price", "dimensions"],
            optional_fields=["location_available", "material"],
            validation_rules={
                "material_filter": ["solid oak", "oak"],  # Must mention oak
                "dimension_required": True,  # Must have dimensions
                "price_min": 50.0,  # Minimum price filter
                "price_max": 5000.0  # Maximum price filter
            }
        )
    
    @staticmethod
    def get_vilnius_it_company_template() -> ExtractionTemplate:
        """Template for IT companies in Vilnius specializing in WordPress development"""
        return ExtractionTemplate(
            name="vilnius_it_wordpress",
            description="Extract comprehensive info for IT companies in Vilnius doing WordPress development",
            search_type="company",
            fields=[
                FieldSelector(
                    name="company_name",
                    field_type=FieldType.TEXT,
                    css_selectors=[
                        "h1", ".company-name", ".business-name", ".org-name",
                        "[data-company]", ".header .brand", ".logo"
                    ],
                    required=True
                ),
                FieldSelector(
                    name="address",
                    field_type=FieldType.ADDRESS,
                    css_selectors=[
                        ".address", ".location", ".office-address", ".headquarters",
                        "[data-address]", ".contact-address", ".street-address"
                    ],
                    regex_patterns=[
                        r"([^,]+,\s*Vilnius[^,]*,?\s*Lithuania)",
                        r"(\d+\s+[^,]+,\s*Vilnius)",
                        r"(Vilnius[^,\n]+)"
                    ],
                    context_keywords=["vilnius", "lithuania"],
                    required=True,
                    format_function="format_address"
                ),
                FieldSelector(
                    name="phone_number",
                    field_type=FieldType.PHONE,
                    css_selectors=[
                        ".phone", ".telephone", ".contact-phone", "a[href^='tel:']",
                        "[data-phone]", ".phone-number"
                    ],
                    regex_patterns=[
                        r"(?:\+370|8)[\s-]?(?:\d[\s-]?){7,8}",  # Lithuania format
                        r"(?:\+\d{1,3})?[\s-]?(?:\d[\s-]?){7,14}"  # International
                    ],
                    required=True,
                    format_function="format_phone"
                ),
                FieldSelector(
                    name="website",
                    field_type=FieldType.URL,
                    css_selectors=[
                        ".website", ".url", "a[href^='http']", "[data-website]",
                        ".company-website", ".external-link"
                    ],
                    extraction_strategy=ExtractionStrategy.ATTRIBUTE,
                    attribute_name="href",
                    required=True,
                    format_function="format_url"
                ),
                FieldSelector(
                    name="reviews",
                    field_type=FieldType.RATING,
                    css_selectors=[
                        ".rating", ".review", ".stars", ".score", "[data-rating]",
                        ".review-rating", ".customer-rating", ".testimonials"
                    ],
                    regex_patterns=[
                        r"(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+)",
                        r"(\d+(?:\.\d+)?)\s*stars?",
                        r"Rating[\s:]*(\d+(?:\.\d+)?)"
                    ],
                    multiple_values=True,
                    required=False,
                    format_function="format_rating"
                ),
                FieldSelector(
                    name="price_range",
                    field_type=FieldType.TEXT,
                    css_selectors=[
                        ".pricing", ".rates", ".cost", ".price-range",
                        "[data-pricing]", ".service-cost", ".hourly-rate"
                    ],
                    regex_patterns=[
                        r"(?:€|EUR)\s*(\d+)\s*-\s*(\d+)",
                        r"(\d+)\s*-\s*(\d+)\s*(?:€|EUR)",
                        r"Starting from\s*(?:€|EUR)\s*(\d+)",
                        r"From\s*(?:€|EUR)\s*(\d+)"
                    ],
                    context_keywords=["price", "cost", "rate", "pricing", "budget"],
                    required=True
                ),
                FieldSelector(
                    name="wordpress_specialization",
                    field_type=FieldType.TEXT,
                    css_selectors=[
                        ".services", ".specialization", ".expertise", ".skills",
                        ".technologies", "[data-services]", ".capabilities"
                    ],
                    regex_patterns=[
                        r"(WordPress[^,.\n]*)",
                        r"(WP[^,.\n]*)",
                        r"(web development[^,.\n]*)",
                        r"(CMS[^,.\n]*)"
                    ],
                    context_keywords=["wordpress", "wp", "cms", "web development"],
                    required=False,
                    multiple_values=True
                ),
                FieldSelector(
                    name="team_size",
                    field_type=FieldType.NUMBER,
                    css_selectors=[
                        ".team-size", ".employees", ".staff", "[data-team-size]"
                    ],
                    regex_patterns=[
                        r"(\d+)\s*(?:employees|staff|people|team members)",
                        r"Team of\s*(\d+)",
                        r"(\d+)\s*person team"
                    ],
                    required=False
                ),
                FieldSelector(
                    name="email",
                    field_type=FieldType.EMAIL,
                    css_selectors=[
                        ".email", ".contact-email", "a[href^='mailto:']",
                        "[data-email]", ".business-email"
                    ],
                    regex_patterns=[
                        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    ],
                    required=False,
                    format_function="format_email"
                )
            ],
            priority_fields=["company_name", "address", "phone_number", "website", "price_range"],
            optional_fields=["reviews", "wordpress_specialization", "team_size", "email"],
            validation_rules={
                "location_filter": ["vilnius", "lithuania"],
                "specialization_filter": ["wordpress", "wp", "web development"],
                "min_priority_fields": 4
            }
        )
    
    @staticmethod
    def get_template_by_name(template_name: str) -> ExtractionTemplate:
        """Get template by name"""
        templates = {
            "john_doe_contacts": TemplateLibrary.get_john_doe_contact_template(),
            "oak_table_dimensions": TemplateLibrary.get_oak_table_dimensions_template(),
            "vilnius_it_wordpress": TemplateLibrary.get_vilnius_it_company_template()
        }
        
        return templates.get(template_name)
    
    @staticmethod
    def list_available_templates() -> List[Dict[str, str]]:
        """List all available templates"""
        return [
            {
                "name": "john_doe_contacts",
                "description": "Extract phone numbers and email addresses for John Doe searches",
                "search_type": "person",
                "use_case": "Finding contact info for people named John Doe in Lisburn"
            },
            {
                "name": "oak_table_dimensions", 
                "description": "Extract URL, company, price, dimensions for solid oak tables",
                "search_type": "product",
                "use_case": "Finding solid oak table surfaces with specific dimensions in cm"
            },
            {
                "name": "vilnius_it_wordpress",
                "description": "Extract comprehensive info for IT companies in Vilnius doing WordPress",
                "search_type": "company", 
                "use_case": "Finding IT companies in Vilnius specializing in WordPress development"
            }
        ]

# Template Builder for creating custom templates
class TemplateBuilder:
    """Helper class to build custom extraction templates"""
    
    def __init__(self):
        self.template = ExtractionTemplate(
            name="",
            description="",
            search_type="",
            fields=[],
            priority_fields=[],
            optional_fields=[],
            validation_rules={}
        )
    
    def set_basic_info(self, name: str, description: str, search_type: str):
        """Set basic template information"""
        self.template.name = name
        self.template.description = description
        self.template.search_type = search_type
        return self
    
    def add_field(self, field_selector: FieldSelector, is_priority: bool = False):
        """Add a field to the template"""
        self.template.fields.append(field_selector)
        
        if is_priority:
            self.template.priority_fields.append(field_selector.name)
        else:
            self.template.optional_fields.append(field_selector.name)
        
        return self
    
    def add_validation_rule(self, rule_name: str, rule_value: Any):
        """Add a validation rule"""
        self.template.validation_rules[rule_name] = rule_value
        return self
    
    def build(self) -> ExtractionTemplate:
        """Build and return the template"""
        return self.template

# Quick template creation helpers
def create_contact_template(required_fields: List[str]) -> ExtractionTemplate:
    """Quick template for contact information"""
    builder = TemplateBuilder()
    builder.set_basic_info("custom_contact", "Custom contact extraction", "person")
    
    if "phone" in required_fields:
        builder.add_field(
            FieldSelector(
                name="phone",
                field_type=FieldType.PHONE,
                css_selectors=[".phone", ".telephone", "a[href^='tel:']"],
                format_function="format_phone",
                required=True
            ),
            is_priority=True
        )
    
    if "email" in required_fields:
        builder.add_field(
            FieldSelector(
                name="email",
                field_type=FieldType.EMAIL,
                css_selectors=[".email", "a[href^='mailto:']"],
                format_function="format_email",
                required=True
            ),
            is_priority=True
        )
    
    if "address" in required_fields:
        builder.add_field(
            FieldSelector(
                name="address",
                field_type=FieldType.ADDRESS,
                css_selectors=[".address", ".location"],
                format_function="format_address",
                required=True
            ),
            is_priority=True
        )
    
    return builder.build()

def create_product_template(required_fields: List[str]) -> ExtractionTemplate:
    """Quick template for product information"""
    builder = TemplateBuilder()
    builder.set_basic_info("custom_product", "Custom product extraction", "product")
    
    if "price" in required_fields:
        builder.add_field(
            FieldSelector(
                name="price",
                field_type=FieldType.PRICE,
                css_selectors=[".price", ".cost"],
                format_function="format_price",
                required=True
            ),
            is_priority=True
        )
    
    if "dimensions" in required_fields:
        builder.add_field(
            FieldSelector(
                name="dimensions",
                field_type=FieldType.DIMENSIONS,
                css_selectors=[".dimensions", ".size"],
                format_function="format_dimensions",
                required=True
            ),
            is_priority=True
        )
    
    if "company" in required_fields:
        builder.add_field(
            FieldSelector(
                name="company",
                field_type=FieldType.TEXT,
                css_selectors=[".brand", ".company"],
                required=True
            ),
            is_priority=True
        )
    
    return builder.build()

# Test the templates
if __name__ == "__main__":
    # List available templates
    templates = TemplateLibrary.list_available_templates()
    print("Available Templates:")
    for template in templates:
        print(f"- {template['name']}: {template['description']}")
    
    # Get specific template
    john_doe_template = TemplateLibrary.get_john_doe_contact_template()
    print(f"\nJohn Doe Template has {len(john_doe_template.fields)} fields:")
    for field in john_doe_template.fields:
        print(f"- {field.name} ({field.field_type.value}): Required={field.required}")