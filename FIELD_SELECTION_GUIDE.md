# Universal Scraper with Smart Field Selection - Complete Guide

## 🎯 Overview

Your universal scraper now includes a sophisticated **Smart Field Selection System** that solves the "unnecessary mess of data" problem by allowing you to extract only the specific fields you need for each search scenario.

## 🆕 What's New

### Before (The Problem)
- Searches returned massive amounts of unstructured data
- Difficult to find specific information like "John Doe phone/email only"
- No way to specify exactly what fields to extract

### After (The Solution)
- **Pre-built Templates**: Ready-to-use extraction patterns for common scenarios
- **Custom Field Selection**: Specify exactly which fields to extract
- **Smart Field Types**: Automatic detection and formatting for phones, emails, prices, dimensions, etc.
- **Hybrid Mode**: Combine templates with additional custom fields

## 🎯 Your Specific Examples - Now Implemented!

### 1. John Doe Contact Search ✅
**Problem**: "If someone wants to search for John Doe contacts then they only want the phone and or email."

**Solution**: 
```bash
python cli.py person "John Doe Lisburn" --template john_doe_contacts --max-results 10
```

**Extracts Only**:
- ✅ Phone numbers (auto-formatted)
- ✅ Email addresses (validated)
- ✅ Name confirmation
- ✅ Location in Lisburn

### 2. Oak Table Dimensions Search ✅
**Problem**: "If someone wants to search for solid oak table surfaces in cm, company and price."

**Solution**:
```bash
python cli.py product "solid oak table surface" --template oak_table_dimensions --include "dimensions,cm"
```

**Extracts Only**:
- ✅ Product URL
- ✅ Company name
- ✅ Price (with currency)
- ✅ Dimensions in cm (LxWxH format)
- ✅ Material confirmation (solid oak)
- ✅ Location/availability

### 3. Vilnius IT Companies Search ✅
**Problem**: "If someone wants to search for IT companies in Vilnius specializing in WordPress."

**Solution**:
```bash
python cli.py company "IT Vilnius WordPress" --template vilnius_it_wordpress --cities "Vilnius"
```

**Extracts Only**:
- ✅ Company name
- ✅ Address in Vilnius
- ✅ Phone number (Lithuania format)
- ✅ Website URL
- ✅ Reviews/ratings
- ✅ Price range for services
- ✅ WordPress specialization confirmation
- ✅ Team size
- ✅ Email contact

## 🛠️ Three Ways to Use Field Selection

### 1. Pre-built Templates (Recommended)
Use ready-made templates for common scenarios:
```bash
# Available templates:
--template john_doe_contacts       # Contact info extraction
--template oak_table_dimensions    # Product dimensions + company + price
--template vilnius_it_wordpress    # IT company comprehensive info
```

### 2. Custom Field Selection
Specify exactly which fields you want:
```bash
python cli.py company "restaurants Dublin" --fields "name,phone,address,rating" --field-mode custom
```

**Available Field Types**:
- `text` - General text content
- `phone` - Phone numbers (auto-formatted)
- `email` - Email addresses (validated)
- `price` - Prices with currency detection
- `dimensions` - Product dimensions (LxWxH)
- `address` - Physical addresses
- `url` - Website URLs
- `rating` - Ratings and reviews
- `number` - Numeric values
- `date` - Dates and times
- `percentage` - Percentage values

### 3. Hybrid Mode
Combine a template with additional custom fields:
```bash
python cli.py product "electronics" --template oak_table_dimensions --fields "warranty,brand" --field-mode hybrid
```

## 🚀 API Usage

### Using Templates
```python
from universal_scraper import UniversalSearchRequest, SearchType

request = UniversalSearchRequest(
    search_type=SearchType.PERSON,
    primary_query="John Doe Lisburn contact",
    extraction_template="john_doe_contacts",  # Use template
    max_results=10
)
```

### Using Custom Fields
```python
request = UniversalSearchRequest(
    search_type=SearchType.COMPANY,
    primary_query="restaurants Dublin",
    field_selection_mode="custom",
    custom_fields=["name", "phone", "address", "rating"],
    max_results=15
)
```

### New API Endpoints
```bash
# List available templates
GET /templates

# Get template details
GET /templates/john_doe_contacts

# Specialized endpoints for your examples
POST /search/john-doe-contacts
POST /search/oak-table-dimensions  
POST /search/vilnius-it-companies
```

## 📂 New Files Created

1. **`field_selector.py`** - Core field selection engine
   - `SmartFieldExtractor` class
   - `FieldSelector` dataclass 
   - `FieldType` enum (11 types)
   - Regex patterns and validation

2. **`extraction_templates.py`** - Pre-built templates
   - `TemplateLibrary` with your 3 examples
   - `TemplateBuilder` for custom templates
   - Quick template creation helpers

3. **`field_selection_examples.py`** - Practical examples
   - Working examples for all 3 scenarios
   - Custom and hybrid extraction demos

4. **`test_field_selection.py`** - Validation tests
   - ✅ All tests passing
   - Validates templates and extraction logic

## 🎯 Usage Examples

### Example 1: John Doe Contacts
```bash
# CLI
python cli.py person "John Doe Lisburn" --template john_doe_contacts -v

# API
curl -X POST "http://localhost:8000/search/john-doe-contacts" \
  -H "Content-Type: application/json" \
  -d '{"query": "John Doe Lisburn contact", "max_results": 10}'
```

**Output** (only relevant fields):
```json
{
  "phone_number": "+44 28 9266 1234",
  "email_address": "john.doe@example.com", 
  "name": "John Doe",
  "location": "Lisburn, Northern Ireland"
}
```

### Example 2: Oak Table Dimensions
```bash
# CLI  
python cli.py product "solid oak table surface" --template oak_table_dimensions -v

# API
curl -X POST "http://localhost:8000/search/oak-table-dimensions" \
  -H "Content-Type: application/json" \
  -d '{"query": "solid oak table surface dimensions", "max_results": 15}'
```

**Output** (only relevant fields):
```json
{
  "product_url": "https://example.com/oak-table-123",
  "company_name": "Fine Furniture Ltd",
  "price": "£899.99",
  "dimensions": "200cm x 90cm x 75cm",
  "material": "Solid Oak"
}
```

### Example 3: Vilnius IT Companies
```bash
# CLI
python cli.py company "IT Vilnius WordPress" --template vilnius_it_wordpress -v

# API  
curl -X POST "http://localhost:8000/search/vilnius-it-companies" \
  -H "Content-Type: application/json" \
  -d '{"query": "IT companies Vilnius WordPress", "max_results": 12}'
```

**Output** (only relevant fields):
```json
{
  "company_name": "TechSolutions Vilnius",
  "address": "Gedimino pr. 45, Vilnius, Lithuania", 
  "phone_number": "+370 5 234 5678",
  "website": "https://techsolutions.lt",
  "price_range": "€50-150 per hour",
  "reviews": "4.8 out of 5",
  "wordpress_specialization": "WordPress development and customization"
}
```

## 🔥 Key Benefits

1. **Precise Data Extraction**: Get exactly the fields you need, nothing more
2. **No Data Mess**: Eliminates the "unnecessary mess of data" problem
3. **Smart Formatting**: Automatic formatting for phones, emails, prices, dimensions
4. **Template Reusability**: Save common extraction patterns for repeated use
5. **Flexible Options**: Templates, custom fields, or hybrid approaches
6. **Validation**: Built-in validation and quality scoring
7. **Performance**: Faster processing by extracting only needed fields

## 🚀 Getting Started

1. **Start the API server**:
   ```bash
   cd /Users/ernestssmalikis/projects/crawler
   /Users/ernestssmalikis/projects/crawler/.venv/bin/python -m uvicorn universal_scraper:app --reload
   ```

2. **Run your specific examples**:
   ```bash
   # John Doe contacts
   python cli.py person "John Doe Lisburn" --template john_doe_contacts -v
   
   # Oak table dimensions
   python cli.py product "solid oak table" --template oak_table_dimensions -v
   
   # Vilnius IT companies
   python cli.py company "IT Vilnius WordPress" --template vilnius_it_wordpress -v
   ```

3. **Run example demos**:
   ```bash
   python field_selection_examples.py
   ```

## 🎉 Mission Accomplished!

Your universal scraper now has **smart field selection** that solves your exact problem:

✅ **"John Doe contacts only phone/email"** - Implemented with `john_doe_contacts` template  
✅ **"Oak table dimensions + company + price"** - Implemented with `oak_table_dimensions` template  
✅ **"IT companies in Vilnius with specific fields"** - Implemented with `vilnius_it_wordpress` template  

No more "unnecessary mess of data" - just the precise information you need! 🎯