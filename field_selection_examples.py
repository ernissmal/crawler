#!/usr/bin/env python3
"""
Universal Scraper with Field Selection - Practical Examples
Demonstrates the smart field selection system for precise data extraction
"""

import asyncio
import json
from universal_scraper import UniversalSearchRequest, SearchType, universal_scraper
from extraction_templates import TemplateLibrary

async def example_john_doe_contacts():
    """Example 1: Search for John Doe contacts using the contact template"""
    print("🔍 EXAMPLE 1: John Doe Contact Search")
    print("=" * 50)
    print("Goal: Find phone numbers and email addresses for John Doe in Lisburn")
    print("Template: john_doe_contacts")
    print()
    
    request = UniversalSearchRequest(
        search_type=SearchType.PERSON,
        primary_query="John Doe Lisburn contact",
        extraction_template="john_doe_contacts",  # Use our pre-built template
        include_keywords=["phone", "email", "contact", "lisburn"],
        cities=["Lisburn"],
        max_results=10,
        output_formats=["json"],
        output_filename="john_doe_contacts_example"
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        
        print(f"✅ Found {results['total_results']} results")
        print(f"📁 Output: {results['output_files'].get('json', 'N/A')}")
        
        # Show extracted data structure
        if results['results']:
            sample = results['results'][0]
            print(f"\n📝 Sample extracted fields:")
            for key, value in sample.items():
                if key in ['phone_number', 'email_address', 'name', 'location']:
                    print(f"   - {key}: {value}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def example_oak_table_dimensions():
    """Example 2: Search for solid oak tables with specific dimension fields"""
    print("\n🔍 EXAMPLE 2: Oak Table Dimensions Search")
    print("=" * 50)
    print("Goal: Find solid oak table surfaces with dimensions, price, and company info")
    print("Template: oak_table_dimensions")
    print()
    
    request = UniversalSearchRequest(
        search_type=SearchType.PRODUCT,
        primary_query="solid oak table surface dimensions cm",
        extraction_template="oak_table_dimensions",  # Use our pre-built template
        include_keywords=["solid oak", "table", "dimensions", "cm", "LxWxH"],
        exclude_keywords=["chair", "stool", "leg", "assembly"],
        max_results=15,
        output_formats=["json", "csv"],
        output_filename="oak_table_dimensions_example"
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        
        print(f"✅ Found {results['total_results']} results")
        print(f"📁 Outputs: {', '.join(results['output_files'].values())}")
        
        # Show extracted data structure
        if results['results']:
            sample = results['results'][0]
            print(f"\n📝 Sample extracted fields:")
            for key, value in sample.items():
                if key in ['company_name', 'price', 'dimensions', 'material', 'product_url']:
                    print(f"   - {key}: {value}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def example_vilnius_it_companies():
    """Example 3: Search for IT companies in Vilnius with comprehensive data"""
    print("\n🔍 EXAMPLE 3: Vilnius IT Companies Search")
    print("=" * 50)
    print("Goal: Find IT companies in Vilnius with contact info, pricing, and reviews")
    print("Template: vilnius_it_wordpress")
    print()
    
    request = UniversalSearchRequest(
        search_type=SearchType.COMPANY,
        primary_query="IT companies Vilnius WordPress development",
        extraction_template="vilnius_it_wordpress",  # Use our pre-built template
        include_keywords=["vilnius", "lithuania", "wordpress", "web development", "IT"],
        cities=["Vilnius"],
        countries=["Lithuania", "LT"],
        max_results=12,
        output_formats=["json", "excel"],
        output_filename="vilnius_it_companies_example"
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        
        print(f"✅ Found {results['total_results']} results")
        print(f"📁 Outputs: {', '.join(results['output_files'].values())}")
        
        # Show extracted data structure
        if results['results']:
            sample = results['results'][0]
            print(f"\n📝 Sample extracted fields:")
            for key, value in sample.items():
                if key in ['company_name', 'address', 'phone_number', 'website', 'price_range', 'reviews']:
                    print(f"   - {key}: {value}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def example_custom_field_extraction():
    """Example 4: Custom field extraction for restaurants"""
    print("\n🔍 EXAMPLE 4: Custom Field Extraction")
    print("=" * 50)
    print("Goal: Find restaurants in Dublin with specific custom fields")
    print("Mode: Custom field selection")
    print()
    
    request = UniversalSearchRequest(
        search_type=SearchType.COMPANY,
        primary_query="restaurants Dublin",
        field_selection_mode="custom",  # Use custom mode
        custom_fields=["name", "phone", "address", "rating", "cuisine", "price_range"],
        include_keywords=["restaurant", "dublin", "food"],
        cities=["Dublin"],
        max_results=8,
        output_formats=["json"],
        output_filename="dublin_restaurants_custom"
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        
        print(f"✅ Found {results['total_results']} results")
        print(f"📁 Output: {results['output_files'].get('json', 'N/A')}")
        
        # Show extracted data structure
        if results['results']:
            sample = results['results'][0]
            print(f"\n📝 Sample extracted fields:")
            for field in request.custom_fields:
                print(f"   - {field}: {sample.get(field, 'N/A')}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def example_hybrid_extraction():
    """Example 5: Hybrid extraction combining template with additional fields"""
    print("\n🔍 EXAMPLE 5: Hybrid Field Extraction")
    print("=" * 50)
    print("Goal: Use oak table template but add extra fields like warranty and shipping")
    print("Mode: Hybrid (template + custom fields)")
    print()
    
    request = UniversalSearchRequest(
        search_type=SearchType.PRODUCT,
        primary_query="solid oak dining table",
        extraction_template="oak_table_dimensions",  # Base template
        field_selection_mode="hybrid",  # Hybrid mode
        custom_fields=["warranty", "shipping", "delivery_time", "brand"],  # Additional fields
        include_keywords=["solid oak", "dining table", "dimensions"],
        max_results=10,
        output_formats=["json"],
        output_filename="oak_table_hybrid_example"
    )
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        
        print(f"✅ Found {results['total_results']} results")
        print(f"📁 Output: {results['output_files'].get('json', 'N/A')}")
        
        # Show extracted data structure
        if results['results']:
            sample = results['results'][0]
            print(f"\n📝 Template fields:")
            for key in ['company_name', 'price', 'dimensions', 'material']:
                print(f"   - {key}: {sample.get(key, 'N/A')}")
            
            print(f"\n📝 Additional custom fields:")
            for field in request.custom_fields:
                print(f"   - {field}: {sample.get(field, 'N/A')}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def show_available_templates():
    """Show all available extraction templates"""
    print("\n🎯 AVAILABLE EXTRACTION TEMPLATES")
    print("=" * 50)
    
    templates = TemplateLibrary.list_available_templates()
    for template in templates:
        print(f"\n📋 {template['name']}")
        print(f"   Description: {template['description']}")
        print(f"   Search Type: {template['search_type']}")
        print(f"   Use Case: {template['use_case']}")

def show_field_types():
    """Show available field types for custom extraction"""
    print("\n🔧 AVAILABLE FIELD TYPES")
    print("=" * 50)
    
    from field_selector import FieldType
    
    field_descriptions = {
        FieldType.TEXT: "General text content",
        FieldType.PHONE: "Phone numbers (auto-formatted)",
        FieldType.EMAIL: "Email addresses (validated)",
        FieldType.PRICE: "Prices with currency detection",
        FieldType.DIMENSIONS: "Product dimensions (LxWxH)",
        FieldType.ADDRESS: "Physical addresses",
        FieldType.URL: "Website URLs",
        FieldType.RATING: "Ratings and reviews",
        FieldType.NUMBER: "Numeric values",
        FieldType.DATE: "Dates and times",
        FieldType.PERCENTAGE: "Percentage values"
    }
    
    for field_type, description in field_descriptions.items():
        print(f"   - {field_type.value}: {description}")

async def run_all_examples():
    """Run all examples in sequence"""
    print("🚀 UNIVERSAL SCRAPER FIELD SELECTION EXAMPLES")
    print("=" * 60)
    
    # Show available options
    show_available_templates()
    show_field_types()
    
    print("\n" + "=" * 60)
    print("RUNNING EXAMPLES...")
    print("=" * 60)
    
    # Run all examples
    examples = [
        example_john_doe_contacts,
        example_oak_table_dimensions,
        example_vilnius_it_companies,
        example_custom_field_extraction,
        example_hybrid_extraction
    ]
    
    results = []
    for example_func in examples:
        try:
            result = await example_func()
            results.append(result)
            print("\n" + "-" * 50)
        except Exception as e:
            print(f"❌ Example failed: {e}")
            results.append(None)
    
    # Summary
    print("\n🎉 ALL EXAMPLES COMPLETED")
    print("=" * 60)
    successful = sum(1 for r in results if r is not None)
    print(f"✅ Successful examples: {successful}/{len(examples)}")
    
    # List generated files
    print(f"\n📁 Generated files:")
    for result in results:
        if result and 'output_files' in result:
            for format_type, filename in result['output_files'].items():
                print(f"   - {filename}")

if __name__ == "__main__":
    # Run a specific example or all examples
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        examples_map = {
            "john_doe": example_john_doe_contacts,
            "oak_table": example_oak_table_dimensions, 
            "vilnius_it": example_vilnius_it_companies,
            "custom": example_custom_field_extraction,
            "hybrid": example_hybrid_extraction
        }
        
        if example_name in examples_map:
            asyncio.run(examples_map[example_name]())
        else:
            print(f"Available examples: {', '.join(examples_map.keys())}")
    else:
        # Run all examples
        asyncio.run(run_all_examples())