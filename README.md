# Universal Multi-Purpose Scraper 🔍

A flexible, configurable web scraping platform that can search and extract data for multiple purposes: products, companies, people, social media accounts, and email addresses.

## 🌟 Features

### Multi-Purpose Search Types
- **Products**: Oak furniture, electronics, any merchandise
- **Companies**: IT firms, startups, businesses of any industry  
- **People**: Public profiles, professionals, executives
- **Social Media**: Twitter, LinkedIn, Instagram accounts
- **Email Addresses**: Business contacts, public email directories
- **Custom**: Define your own search type with custom configuration

### Intelligent Data Extraction
- **Configurable selectors** for different website structures
- **Smart pattern recognition** for prices, contact info, social links
- **Validation rules** to ensure data quality
- **Multiple extraction modes**: Basic, Detailed, Custom

### Google Search Integration
- **Advanced query building** with include/exclude keywords
- **Region and language targeting**
- **Multi-page result collection**
- **Intelligent URL filtering** to avoid irrelevant pages

### Flexible Output Options
- **Multiple formats**: JSON, CSV, Excel
- **Structured data export** with consistent schemas
- **Real-time logging** and session analytics
- **Deduplication** to avoid processing the same companies twice

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd crawler

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x setup.sh
chmod +x cli.py
```

### Basic Usage Examples

#### 1. Search for Products
```bash
# Search for oak furniture in Kaunas
python cli.py product "oak furniture Kaunas" --include "table,chair" --max-results 20

# Search for electronics under €1000
python cli.py product "laptops under 1000 euros" --regions "Ireland" --exclude "blog,news"
```

#### 2. Search for Companies
```bash
# Search for IT companies in Lisburn
python cli.py company "IT companies Lisburn" --regions "Northern Ireland" --exclude "jobs,careers"

# Search for startups in Dublin
python cli.py company "tech startups Dublin" --include "software,innovation" --max-results 15
```

#### 3. Search for People (Public Data Only)
```bash
# Search for business executives in Dubai
python cli.py person "business executives Dubai public directory" --regions "UAE" --extraction basic

# Search for professors at Trinity College
python cli.py person "professor computer science Trinity College" --include "academic,research"
```

#### 4. Search for Social Media Accounts
```bash
# Search for tech startup social media
python cli.py social_media "tech startup Ireland Twitter" --include "startup,innovation"

# Search for professional LinkedIn profiles
python cli.py social_media "software engineer LinkedIn Dublin" --include "developer,programmer"
```

#### 5. Search for Email Addresses
```bash
# Search for business contact emails
python cli.py email "tech companies contact Ireland" --include "contact,info" --exclude "noreply"

# Search for university faculty emails
python cli.py email "university faculty contact Belfast" --include "academic,professor"
```

## � Configuration System

The scraper uses YAML configuration files to define how to extract data for each search type.

### Example: Product Configuration
```yaml
# configs/product_config.yaml
extraction:
  required_fields:
    - "name"
    - "price" 
    - "description"
  
  optional_fields:
    - "brand"
    - "rating"
    - "reviews"
  
  selectors:
    name: 
      - "h1"
      - ".product-title"
      - ".product-name"
    
    price:
      - ".price"
      - ".product-price"
      - ".cost"

validation:
  price_min: 0.01
  price_max: 999999.99
```

### Creating Custom Configurations
```bash
# Create a configuration template for any search type
python -c "
from universal_scraper import app
import requests
response = requests.post('http://localhost:8000/create-config', 
                        json={'search_type': 'product', 'filename': 'my_config.yaml'})
print(response.json())
"
```

## 🔧 API Usage

### Start the API Server
```bash
# Start the FastAPI server
python universal_scraper.py

# Or with uvicorn
uvicorn universal_scraper:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Universal Search Endpoint
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "product",
    "primary_query": "oak furniture Kaunas",
    "include_keywords": ["table", "chair"],
    "regions": ["Lithuania"],
    "max_results": 20,
    "extraction_mode": "detailed",
    "output_formats": ["json", "csv"]
  }'
```

#### Get Available Search Types
```bash
curl "http://localhost:8000/search-types"
```

## 📊 Python Library Usage

```python
import asyncio
from universal_scraper import UniversalSearchRequest, SearchType, universal_scraper

async def search_products():
    request = UniversalSearchRequest(
        search_type=SearchType.PRODUCT,
        primary_query="oak furniture Kaunas",
        include_keywords=["table", "chair", "oak"],
        exclude_keywords=["blog", "news"],
        regions=["Lithuania", "Kaunas"],
        max_results=20,
        output_formats=["json", "csv", "excel"]
    )
    
    results = await universal_scraper.search_and_scrape(request)
    
    print(f"Found {results['total_results']} products")
    print(f"Exported to: {list(results['output_files'].values())}")
    
    return results

# Run the search
results = asyncio.run(search_products())
```

## 🎯 Use Cases & Examples

### E-commerce Research
```bash
# Find furniture suppliers in Eastern Europe
python cli.py product "oak furniture manufacturers" --regions "Lithuania,Latvia,Estonia" --include "wholesale,supplier"

# Research electronics pricing across regions
python cli.py product "laptop computers" --regions "Ireland,UK" --include "price,buy" --max-results 50
```

### Business Development
```bash
# Find potential clients in tech sector
python cli.py company "software companies" --regions "Dublin,Cork,Belfast" --include "IT,development"

# Research competitors in specific market
python cli.py company "fintech startups Ireland" --include "financial,technology" --exclude "jobs"
```

### Market Research
```bash
# Find industry influencers
python cli.py social_media "tech CEO Ireland LinkedIn" --include "startup,founder,CEO"

# Research academic experts
python cli.py person "AI researcher university" --regions "Ireland,UK" --include "professor,research"
```

### Lead Generation
```bash
# Find business contact information
python cli.py email "marketing agencies Dublin contact" --include "contact,info" --exclude "noreply"

# Research potential partnerships
python cli.py company "SaaS companies Ireland" --include "software,service" --max-results 30
```

## 🔄 Data Flow

```
Search Query → Google Search → URL Collection → Content Extraction → Data Validation → Export
```

1. **Query Enhancement**: Add region filters, include/exclude keywords
2. **Google Search**: Automated search with stealth browsing
3. **URL Filtering**: Remove irrelevant sites, handle duplicates
4. **Content Scraping**: Extract data using configurable selectors
5. **Data Validation**: Verify extracted information meets criteria
6. **Export**: Save results in multiple formats

## 📈 Output Examples

### Product Search Results
```json
{
  "search_type": "product",
  "total_results": 15,
  "results": [
    {
      "name": "Oak Dining Table",
      "price_amount": 299.99,
      "price_currency": "€",
      "description": "Solid oak dining table for 6 people",
      "brand": "FurnitureCraft",
      "url": "https://example.com/oak-table",
      "extraction_timestamp": "2024-01-15T10:30:00"
    }
  ],
  "output_files": {
    "json": "product_results_20240115_103000.json",
    "csv": "product_results_20240115_103000.csv"
  }
}
```

### Company Search Results
```json
{
  "search_type": "company", 
  "total_results": 12,
  "results": [
    {
      "name": "TechCorp Solutions",
      "industry": "Software Development",
      "location": "Lisburn, Northern Ireland",
      "employee_count": 45,
      "website": "https://techcorp.ie",
      "url": "https://example.com/techcorp",
      "extraction_timestamp": "2024-01-15T10:35:00"
    }
  ]
}
```

## ⚙️ Configuration Options

### Search Behavior
- **search_depth**: `shallow`, `medium`, `deep`
- **max_results**: Number of results to collect
- **extraction_mode**: `basic`, `detailed`, `custom`

### Regional Targeting
- **regions**: Geographic regions for localized results
- **cities**: Specific cities to focus on
- **countries**: Country codes for filtering

### Content Filtering
- **include_keywords**: Must be present in results
- **exclude_keywords**: Must not be present in results
- **target_domains**: Specific websites to prioritize

## 🛡️ Privacy & Ethics

- **Public data only**: Only scrapes publicly available information
- **Rate limiting**: Respects website rate limits and robots.txt
- **GDPR compliant**: Includes data retention and privacy controls
- **Ethical guidelines**: Built-in safeguards for responsible scraping

## 🔧 Advanced Features

### Custom Extractors
Create custom data extraction rules for specific websites or data types.

### Batch Processing  
Process multiple search queries in sequence with automatic rate limiting.

### Session Analytics
Track scraping performance, success rates, and data quality metrics.

### Export Integrations
Direct integration with Google Sheets, databases, and other data platforms.

## 📚 Development

### Project Structure
```
crawler/
├── universal_scraper.py       # Main API and scraping engine
├── universal_google_search.py # Google search automation
├── enhanced_logging.py        # Logging and analytics
├── company_tracker.py         # Deduplication logic
├── config_manager.py          # Configuration management
├── cli.py                     # Command line interface
├── examples.py               # Usage examples
├── configs/                   # Configuration templates
│   ├── product_config.yaml
│   ├── company_config.yaml
│   ├── person_config.yaml
│   ├── social_media_config.yaml
│   └── email_config.yaml
└── requirements.txt
```

### Running Tests
```bash
# Test individual search types
python examples.py

# Test CLI functionality  
python cli.py product "test query" --dry-run

# Test API endpoints
python test_framework.py
```

### Contributing
1. Add new search types by creating configuration templates
2. Enhance extractors for specific website patterns
3. Improve filtering and validation logic
4. Add new export formats and integrations

## 📞 Support

For questions, issues, or feature requests:
1. Check the configuration examples in `configs/`
2. Review the example usage in `examples.py`
3. Test with `--dry-run` to preview searches
4. Use `--verbose` for detailed debugging output

## 🚀 Future Roadmap

- **Real-time monitoring** of search results and data changes
- **Machine learning** for improved data extraction accuracy
- **Browser automation** alternatives for JavaScript-heavy sites
- **Integration APIs** for CRM, marketing, and business tools
- **Advanced analytics** and data visualization features

---

**Universal Multi-Purpose Scraper** - Your one-stop solution for intelligent web data extraction! 🎯

## 🎯 Usage

### Basic Web Interface
Navigate to `http://localhost:8000` for the API documentation and testing interface.

### API Endpoints

#### 1. Health Check
```http
GET /
```

#### 2. Google Search for URLs
```http
POST /search
```
```json
{
  "search_terms": ["solid oak dining table", "oak furniture"],
  "max_results_per_query": 5,
  "headless": true,
  "save_results": true
}
```

#### 3. Enhanced Crawling
```http
POST /crawl-enhanced
```
```json
{
  "use_google_search": false,
  "urls": ["https://example.com/table1", "https://example.com/table2"],
  "base_currency": "EUR",
  "manual_assistance": false,
  "max_workers": 3,
  "timeout": 15,
  "output_excel": "results.xlsx",
  "output_csv": "results.csv",
  "output_json": "results.json",
  "skip_processed_companies": true
}
```

#### 4. Get Statistics
```http
GET /stats
```

#### 5. Reset Tracking Data
```http
POST /reset
```

### Command Line Usage

#### Run Google Search
```python
from google_geeking import bulk_furniture_search

urls = bulk_furniture_search(
    base_terms=["solid oak dining table", "oak kitchen table"],
    max_results=5,
    headless=True
)
print(f"Found {len(urls)} unique URLs")
```

#### Use Company Tracker
```python
from company_tracker import filter_unique_companies, mark_company_processed

# Filter URLs for unique companies
urls = ["https://company1.com/table1", "https://company1.com/table2", "https://company2.com/table3"]
unique_urls = filter_unique_companies(urls)

# Mark company as processed
mark_company_processed("https://company1.com/table1", success=True)
```

#### Configure Settings
```python
from config_manager import get_config_manager

config = get_config_manager()
config.update_config('scraping', {
    'timeout': 20,
    'max_workers': 5,
    'extraction_mode': 'aggressive'
})
```

## 📊 Data Output

The scraper extracts comprehensive furniture data:

### Core Product Information
- Company name and website
- Product page URL
- Country/region
- Store type
- SKU/Model
- Table type (dining, kitchen, etc.)
- Materials (oak, pine, etc.)
- Finish/color

### Dimensions & Measurements
- Length, width, height (in cm)
- Dimension notes
- Automatic unit conversion

### Pricing Information
- Price in original currency
- Converted price in EUR
- Price unit and notes
- VAT inclusion status

### Delivery & Service
- Delivery costs and terms
- Delivery time (in days)
- Assembly requirements
- Return policy (days)
- Warranty (months)
- Customization options

### Contact & Metadata
- Contact information
- Source notes
- Date checked
- Competitor rating
- Action suggestions

## 🔧 Configuration

### Default Configuration File (`scraper_config.yaml`)
```yaml
scraping:
  timeout: 15
  max_retries: 3
  delay_between_requests: 1.0
  max_workers: 3
  extraction_mode: "balanced"  # aggressive, balanced, conservative
  enable_manual_assistance: false

price_extraction:
  currency_symbols: ["€", "£", "$"]
  price_selectors: [".price", ".product-price", ".cost"]

google_search:
  max_results_per_query: 5
  headless_browser: true
  base_search_terms: ["solid oak dining table", "oak furniture"]
```

### Extraction Modes
- **Conservative**: High-confidence patterns only, faster processing
- **Balanced**: Good balance of accuracy and speed (default)
- **Aggressive**: Try all patterns, more thorough but slower

## 📈 Monitoring & Analytics

### Session Statistics
- Total operations performed
- Success/failure rates
- Processing time
- Error breakdowns by type
- Problematic URLs identification

### Company Tracking
- Number of companies processed
- Processing dates
- Success rates per company
- Domain aliases and mappings

### Data Quality Metrics
- Price extraction success rate
- Dimension extraction success rate
- Manual intervention frequency
- Data validation issues

## 🧪 Testing

Run the test suite:
```bash
python test_framework.py
```

Or with pytest:
```bash
pip install pytest
pytest test_framework.py -v
```

### Test Coverage
- Unit tests for all extraction functions
- Integration tests for complete workflows
- Configuration validation tests
- Mock-based testing for external dependencies
- Performance benchmarks

## 🔍 Troubleshooting

### Common Issues

#### 1. ChromeDriver Not Found
```bash
# Install ChromeDriver
brew install chromedriver

# Or set path manually
export PATH=$PATH:/path/to/chromedriver
```

#### 2. Selenium Timeout Issues
- Increase timeout in configuration
- Check internet connection
- Verify target websites are accessible

#### 3. Price Extraction Failures
- Enable manual assistance mode
- Check currency patterns in configuration
- Verify website structure hasn't changed

#### 4. Memory Issues with Large Datasets
- Reduce max_workers
- Process URLs in smaller batches
- Increase system memory allocation

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check session reports in the `logs/` directory for detailed analysis.

## 📋 Migration from v1.0

### Key Changes
1. Replace `main.py` usage with `enhanced_main.py`
2. Update API endpoint calls to use new enhanced endpoints
3. Review and update configuration settings
4. Install additional dependencies

### Backward Compatibility
- Original `main.py` still functional
- Existing URL files (`unique_urls.txt`) still supported
- Output format remains compatible

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup
```bash
pip install -r requirements.txt
pip install pytest black flake8
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔄 Changelog

### v2.0.0 (Current)
- ✅ Google search integration with Selenium
- ✅ Company deduplication system
- ✅ Enhanced logging and error tracking
- ✅ Advanced data extraction patterns
- ✅ Configuration management system
- ✅ Comprehensive testing framework
- ✅ Multi-format export (Excel, CSV, JSON)
- ✅ Data validation and quality checks
- ✅ Session monitoring and analytics

### v1.0.0
- Basic web scraping functionality
- Manual URL input
- Excel export
- Simple error handling

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a detailed issue report
4. Include logs and configuration details

---

**Enhanced Oak Table Scraper v2.0** - Making furniture data extraction intelligent, reliable, and comprehensive.