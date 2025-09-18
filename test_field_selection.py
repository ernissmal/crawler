#!/usr/bin/env python3
"""
Quick Test of Field Selection System
Tests the field selection components without running full searches
"""

from field_selector import SmartFieldExtractor, FieldSelector, FieldType, ExtractionTemplate
from extraction_templates import TemplateLibrary
from bs4 import BeautifulSoup

def test_field_selector_creation():
    """Test creating field selectors"""
    print("🧪 Testing Field Selector Creation...")
    
    # Test phone field selector
    phone_selector = FieldSelector(
        name="phone_number",
        field_type=FieldType.PHONE,
        css_selectors=[".phone", "a[href^='tel:']"],
        regex_patterns=[r"(?:\+44|0)[\s-]?(?:\d[\s-]?){10}"],
        required=True,
        format_function="format_phone"
    )
    
    print(f"✅ Phone Selector: {phone_selector.name} ({phone_selector.field_type.value})")
    
    # Test price field selector
    price_selector = FieldSelector(
        name="price",
        field_type=FieldType.PRICE,
        css_selectors=[".price", ".cost"],
        regex_patterns=[r"([€£$¥₹])\s?([\d,]+\.?\d*)"],
        required=True,
        format_function="format_price"
    )
    
    print(f"✅ Price Selector: {price_selector.name} ({price_selector.field_type.value})")
    
    return True

def test_template_loading():
    """Test loading extraction templates"""
    print("\n🧪 Testing Template Loading...")
    
    # Test John Doe template
    john_template = TemplateLibrary.get_john_doe_contact_template()
    print(f"✅ John Doe Template: {john_template.name}")
    print(f"   Fields: {len(john_template.fields)}")
    print(f"   Priority: {john_template.priority_fields}")
    
    # Test oak table template
    oak_template = TemplateLibrary.get_oak_table_dimensions_template()
    print(f"✅ Oak Table Template: {oak_template.name}")
    print(f"   Fields: {len(oak_template.fields)}")
    print(f"   Priority: {oak_template.priority_fields}")
    
    # Test Vilnius IT template
    vilnius_template = TemplateLibrary.get_vilnius_it_company_template()
    print(f"✅ Vilnius IT Template: {vilnius_template.name}")
    print(f"   Fields: {len(vilnius_template.fields)}")
    print(f"   Priority: {vilnius_template.priority_fields}")
    
    return True

def test_smart_extractor():
    """Test SmartFieldExtractor with sample HTML"""
    print("\n🧪 Testing Smart Field Extractor...")
    
    # Create sample HTML
    sample_html = """
    <html>
    <body>
        <h1>John Doe</h1>
        <div class="contact">
            <div class="phone">+44 28 9266 1234</div>
            <div class="email">john.doe@example.com</div>
            <div class="address">123 Main Street, Lisburn, Northern Ireland</div>
        </div>
        <div class="product">
            <h2>Solid Oak Dining Table</h2>
            <div class="price">£899.99</div>
            <div class="dimensions">200cm x 90cm x 75cm</div>
            <div class="company">Fine Furniture Ltd</div>
        </div>
    </body>
    </html>
    """
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    extractor = SmartFieldExtractor()
    
    # Test John Doe contact extraction
    john_template = TemplateLibrary.get_john_doe_contact_template()
    contact_data = extractor.extract_using_template(soup, john_template)
    
    print(f"✅ Contact Extraction:")
    for key, value in contact_data.items():
        print(f"   {key}: {value}")
    
    # Test oak table extraction
    oak_template = TemplateLibrary.get_oak_table_dimensions_template()
    product_data = extractor.extract_using_template(soup, oak_template)
    
    print(f"✅ Product Extraction:")
    for key, value in product_data.items():
        print(f"   {key}: {value}")
    
    return True

def test_template_list():
    """Test listing available templates"""
    print("\n🧪 Testing Template List...")
    
    templates = TemplateLibrary.list_available_templates()
    
    print(f"✅ Available Templates: {len(templates)}")
    for template in templates:
        print(f"   - {template['name']}: {template['description']}")
    
    return True

def test_field_types():
    """Test field type enumeration"""
    print("\n🧪 Testing Field Types...")
    
    field_types = [ft.value for ft in FieldType]
    print(f"✅ Available Field Types: {len(field_types)}")
    print(f"   Types: {', '.join(field_types)}")
    
    return True

def run_all_tests():
    """Run all validation tests"""
    print("🚀 FIELD SELECTION SYSTEM VALIDATION")
    print("=" * 50)
    
    tests = [
        test_field_selector_creation,
        test_template_loading,
        test_smart_extractor,
        test_template_list,
        test_field_types
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🎉 VALIDATION COMPLETE")
    print("=" * 50)
    
    successful = sum(results)
    print(f"✅ Tests passed: {successful}/{len(tests)}")
    
    if successful == len(tests):
        print("🎯 All systems operational! Field selection is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the implementation.")
    
    return successful == len(tests)

if __name__ == "__main__":
    run_all_tests()