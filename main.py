# fastapi_oak_scraper.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from forex_python.converter import CurrencyRates
import re
import concurrent.futures
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import webbrowser
import subprocess
import json

app = FastAPI(title="International Solid Oak Table Scraper")

@app.get("/")
def health_check():
    return {"status": "OK", "message": "Oak Table Scraper API is running"}

@app.post("/test-manual")
def test_manual_extraction(url: str = "https://www.oakfurnitureland.co.uk/category/dining-tables/"):
    """Test manual extraction with a single URL"""
    session = create_session()
    result = scrape_table_data(url, base_currency="EUR", session=session, manual_assistance=True)
    return {"url": url, "extracted_data": result}

c = CurrencyRates()

# Configure requests session with retries and proper headers
def create_session():
    session = requests.Session()
    
    # Set up retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set proper headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    return session

# Input model
class CrawlRequest(BaseModel):
    output_excel: Optional[str] = "Competitor_Oak_Tables.xlsx"
    base_currency: Optional[str] = "EUR"
    manual_assistance: Optional[bool] = False  # Enable manual browser assistance

# Excel columns in Latvian
COLUMNS = [
    "Uzņēmuma nosaukums", "Mājaslapa / veikala URL", "Produkta lapas URL", "Valsts / reģions",
    "Veikala tips", "SKU / Modelis", "Galda tips", "Materiāls(-i)", "Apdare / Krāsa",
    "Garums_cm", "Platums_cm", "Augstums_cm", "Izmēru piezīmes", "Cena_valūta",
    "Cena_summa", "Cena_EUR", "Cena_vienība", "Cena_piezīmes", "Piegādes izmaksas",
    "Piegādes noteikumi", "Piegādes laiks_dienas", "Piegādes veids", "Montāža nepieciešama",
    "Atgriešanas noteikumi_dienas", "Garantija_mēneši", "Pielāgošanas iespējas",
    "Pielāgošanas laiks_dienas", "Krājuma statuss", "Minimālais pasūtījuma daudzums",
    "Apmaksas noteikumi", "PVN iekļauts", "Kontakta persona", "Kontakta e-pasts vai telefons",
    "Ekrānuzņēmuma URL", "Avota piezīmes", "Datums pārbaudīts",
    "Konkurenta vērtējums", "Darbību priekšlikumi"
]

# Utility: detect price and currency from string
def parse_price(price_str: str):
    # Example: "£299.99", "€249", "$199"
    price_str = price_str.replace("\xa0", "").strip()
    match = re.search(r"([€£$])\s?([\d.,]+)", price_str)
    if not match:
        return None, None
    currency, amount = match.groups()
    amount = float(amount.replace(",", "."))
    currency_map = {"€": "EUR", "£": "GBP", "$": "USD"}
    return currency_map.get(currency, "EUR"), amount

# Extract dimensions from product page with manual assistance
def extract_dimensions_with_assistance(soup, title, url, manual_mode=False):
    """Extract length, width, height from product page with manual fallback"""
    dimensions = {'length': None, 'width': None, 'height': None, 'notes': ''}
    
    # Enhanced dimension patterns - much more comprehensive
    dimension_patterns = [
        # Standard formats
        r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*cm',
        r'(\d+)\s*cm\s*[x×]\s*(\d+)\s*cm\s*[x×]\s*(\d+)\s*cm',
        r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)',
        
        # With units
        r'(\d+)\s*cm\s*[x×]\s*(\d+)\s*cm\s*[x×]\s*(\d+)\s*cm',
        r'(\d+)\s*mm\s*[x×]\s*(\d+)\s*mm\s*[x×]\s*(\d+)\s*mm',
        
        # With labels
        r'L[ength]*[\s:]*(\d+)[cm]*\s*[x×]\s*W[idth]*[\s:]*(\d+)[cm]*\s*[x×]\s*H[eight]*[\s:]*(\d+)[cm]*',
        r'Length[\s:]*(\d+)[cm]*\s*[x×]\s*Width[\s:]*(\d+)[cm]*\s*[x×]\s*Height[\s:]*(\d+)[cm]*',
        r'(\d+)[cm]*\s*[Ll]\s*[x×]\s*(\d+)[cm]*\s*[Ww]\s*[x×]\s*(\d+)[cm]*\s*[Hh]',
        
        # Dimensions with spacing variations
        r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*cm',
        r'(\d+)cm\s*x\s*(\d+)cm\s*x\s*(\d+)cm',
        r'(\d+)\s*×\s*(\d+)\s*×\s*(\d+)\s*cm',
        
        # Table specific
        r'Table[\s\w]*:?\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)',
        r'Size[\s:]*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)',
        r'Dimensions[\s:]*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)',
        
        # Bracket formats
        r'\((\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\)',
        r'\[(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\]',
        
        # With measurements in inches (convert to cm)
        r'(\d+)["\']\s*[x×]\s*(\d+)["\']\s*[x×]\s*(\d+)["\']',
        r'(\d+)\s*inch[es]*\s*[x×]\s*(\d+)\s*inch[es]*\s*[x×]\s*(\d+)\s*inch[es]*',
    ]
    
    # Enhanced search areas - look in more specific places
    search_selectors = [
        '.dimensions', '.specs', '.specifications', '.product-details', '.description',
        '.product-info', '.details', '.measurements', '.size', '.product-specifications',
        '.tech-specs', '.product-dimensions', '.item-details', '.features',
        '[class*="dimension"]', '[class*="spec"]', '[class*="detail"]', 
        '[id*="dimension"]', '[id*="spec"]', '[id*="detail"]',
        'table', '.table', '#specifications', '#details', '#dimensions'
    ]
    
    search_areas = [title]
    
    # Add specific element content
    for selector in search_selectors:
        elements = soup.select(selector)
        for element in elements:
            if element:
                search_areas.append(element.get_text())
    
    # Add full page text as last resort
    search_areas.append(soup.get_text())
    
    # Try to find dimensions in all areas
    found_match = None
    for area in search_areas:
        if not area:
            continue
        for pattern in dimension_patterns:
            match = re.search(pattern, area, re.IGNORECASE)
            if match:
                try:
                    l, w, h = match.groups()
                    # Convert inches to cm if needed
                    if '"' in match.group(0) or 'inch' in match.group(0):
                        l, w, h = int(float(l) * 2.54), int(float(w) * 2.54), int(float(h) * 2.54)
                    else:
                        l, w, h = int(l), int(w), int(h)
                    
                    # Validate reasonable furniture dimensions
                    if 50 <= l <= 500 and 50 <= w <= 200 and 50 <= h <= 120:
                        dimensions['length'] = l
                        dimensions['width'] = w
                        dimensions['height'] = h
                        dimensions['notes'] = f"Auto-found: {match.group(0)}"
                        print(f"✓ Found dimensions: {l}×{w}×{h}cm")
                        return dimensions
                    else:
                        found_match = match
                except (ValueError, AttributeError):
                    continue
    
    # If no valid dimensions found, ask for manual assistance
    if not dimensions['length'] and manual_mode:
        print(f"⚠️  Could not auto-extract dimensions for {url}")
        manual_dims = get_manual_dimensions(url, found_match)
        if manual_dims:
            dimensions.update(manual_dims)
    elif not dimensions['length']:
        dimensions['notes'] = "Auto-extraction failed, manual mode disabled"
    
    return dimensions

def get_manual_dimensions(url, found_match=None):
    """Open browser and get manual input for dimensions"""
    print(f"\n🌐 Opening browser for manual dimension extraction...")
    print(f"URL: {url}")
    
    if found_match:
        print(f"Found potential match: {found_match.group(0)} (but dimensions seem invalid)")
    
    # Open the URL in default browser
    webbrowser.open(url)
    
    print("\n📏 MANUAL DIMENSION EXTRACTION")
    print("Please find the product dimensions on the webpage and enter them below.")
    print("Look for: Length × Width × Height (in cm)")
    print("Example formats: '180×90×75cm', '180 x 90 x 75', 'L:180 W:90 H:75'")
    print("\nIf you need to:")
    print("- Complete a CAPTCHA")
    print("- Navigate to a different page")
    print("- Accept cookies")
    print("- Deal with popups")
    print("\nDo so now, then come back here to enter the dimensions.")
    
    while True:
        user_input = input("\nEnter dimensions (L×W×H in cm) or 'skip' to skip this product: ").strip()
        
        if user_input.lower() == 'skip':
            print("⏭️  Skipping this product...")
            return None
        
        # Try to parse user input
        parsed_dims = parse_manual_dimensions(user_input)
        if parsed_dims:
            print(f"✅ Parsed dimensions: {parsed_dims['length']}×{parsed_dims['width']}×{parsed_dims['height']}cm")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '']:
                return parsed_dims
        else:
            print("❌ Could not parse dimensions. Please try again.")
            print("Expected format: numbers like '180×90×75' or '180 90 75' or '180x90x75'")

def get_manual_price(url):
    """Get manual input for price when auto-extraction fails"""
    print(f"\n💰 MANUAL PRICE EXTRACTION")
    print(f"Could not automatically find price for: {url}")
    print("The browser should already be open. Please find the price and enter it below.")
    
    while True:
        user_input = input("\nEnter price (e.g., '£299.99', '€250', '$199') or 'skip': ").strip()
        
        if user_input.lower() == 'skip':
            return None
        
        # Try to parse the price
        parsed_cur, parsed_val = parse_price(user_input)
        if parsed_cur and parsed_val:
            print(f"✅ Parsed price: {parsed_val} {parsed_cur}")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '']:
                return {'currency': parsed_cur, 'amount': parsed_val}
        else:
            print("❌ Could not parse price. Please include currency symbol (£, €, $)")

def parse_manual_dimensions(user_input):
    """Parse manually entered dimensions"""
    # Clean up input
    user_input = user_input.replace('cm', '').replace('CM', '').strip()
    
    # Try various parsing patterns
    patterns = [
        r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)',
        r'(\d+)\s+(\d+)\s+(\d+)',
        r'[Ll][\s:]*(\d+).*[Ww][\s:]*(\d+).*[Hh][\s:]*(\d+)',
        r'(\d+).*(\d+).*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input)
        if match:
            try:
                l, w, h = map(int, match.groups())
                # Validate reasonable dimensions
                if 50 <= l <= 500 and 50 <= w <= 200 and 50 <= h <= 120:
                    return {
                        'length': l,
                        'width': w,
                        'height': h,
                        'notes': f"Manual entry: {user_input}"
                    }
            except ValueError:
                continue
    
    return None

# Extract delivery information
def extract_delivery_info(soup):
    """Extract delivery cost, time, and terms"""
    delivery_info = {'cost': None, 'terms': '', 'time_days': None, 'method': ''}
    
    text = soup.get_text().lower()
    
    # Delivery cost patterns
    delivery_cost_patterns = [
        r'delivery[:\s]*[£€$]?([\d.,]+)',
        r'shipping[:\s]*[£€$]?([\d.,]+)',
        r'postage[:\s]*[£€$]?([\d.,]+)'
    ]
    
    for pattern in delivery_cost_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                delivery_info['cost'] = float(match.group(1).replace(',', ''))
                break
            except ValueError:
                continue
    
    # Free delivery
    if any(phrase in text for phrase in ['free delivery', 'free shipping', 'free postage']):
        delivery_info['cost'] = 0
        delivery_info['terms'] = 'Free delivery'
    
    # Delivery time patterns
    time_patterns = [
        r'(\d+)[\s-]*(?:to[\s-]*(\d+))?[\s-]*(?:working[\s]*)?days?',
        r'(\d+)[\s-]*(?:to[\s-]*(\d+))?[\s-]*weeks?'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                days = int(match.group(1))
                if 'week' in match.group(0):
                    days *= 7
                delivery_info['time_days'] = days
                break
            except (ValueError, AttributeError):
                continue
    
    return delivery_info

# Extract service information (assembly, warranty, etc.)
def extract_service_info(soup):
    """Extract assembly, warranty, customization info"""
    service_info = {
        'assembly_required': '',
        'return_days': None,
        'warranty_months': None,
        'customization': '',
        'customization_days': None
    }
    
    text = soup.get_text().lower()
    
    # Assembly
    if any(phrase in text for phrase in ['assembly required', 'requires assembly', 'self assembly']):
        service_info['assembly_required'] = 'Yes'
    elif any(phrase in text for phrase in ['pre-assembled', 'fully assembled', 'no assembly']):
        service_info['assembly_required'] = 'No'
    
    # Returns policy
    return_patterns = [
        r'(\d+)[\s-]*days?[\s]*return',
        r'return[\s]*within[\s]*(\d+)[\s]*days?'
    ]
    
    for pattern in return_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                service_info['return_days'] = int(match.group(1))
                break
            except ValueError:
                continue
    
    # Warranty
    warranty_patterns = [
        r'(\d+)[\s-]*year[\s]*warranty',
        r'(\d+)[\s-]*month[\s]*warranty',
        r'warranty[\s]*(\d+)[\s]*(?:year|month)'
    ]
    
    for pattern in warranty_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                months = int(match.group(1))
                if 'year' in match.group(0):
                    months *= 12
                service_info['warranty_months'] = months
                break
            except ValueError:
                continue
    
    # Customization
    if any(phrase in text for phrase in ['bespoke', 'custom', 'made to order', 'personalized']):
        service_info['customization'] = 'Available'
        
        # Custom time
        custom_time_patterns = [
            r'(\d+)[\s-]*(?:to[\s-]*(\d+))?[\s-]*weeks?[\s]*(?:for[\s]*)?(?:custom|bespoke)',
            r'(?:custom|bespoke)[\s]*(\d+)[\s-]*(?:to[\s-]*(\d+))?[\s-]*weeks?'
        ]
        
        for pattern in custom_time_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    weeks = int(match.group(1))
                    service_info['customization_days'] = weeks * 7
                    break
                except ValueError:
                    continue
    
    return service_info

# Extract stock status
def extract_stock_status(soup):
    """Extract availability/stock status"""
    text = soup.get_text().lower()
    
    if any(phrase in text for phrase in ['in stock', 'available now', 'ready to ship']):
        return 'In Stock'
    elif any(phrase in text for phrase in ['out of stock', 'sold out', 'unavailable']):
        return 'Out of Stock'
    elif any(phrase in text for phrase in ['pre-order', 'coming soon', 'expected']):
        return 'Pre-order'
    elif any(phrase in text for phrase in ['made to order', 'bespoke']):
        return 'Made to Order'
    else:
        return 'Unknown'

# Extract payment information
def extract_payment_info(soup):
    """Extract payment terms and options"""
    text = soup.get_text().lower()
    
    payment_methods = []
    if 'paypal' in text:
        payment_methods.append('PayPal')
    if any(card in text for card in ['visa', 'mastercard', 'credit card']):
        payment_methods.append('Credit Card')
    if 'klarna' in text:
        payment_methods.append('Klarna')
    if 'finance' in text or 'installment' in text:
        payment_methods.append('Finance Available')
    
    return ', '.join(payment_methods) if payment_methods else ''

# Extract contact information
def extract_contact_info(soup):
    """Extract contact email or phone"""
    text = soup.get_text()
    
    # Email pattern
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        return email_match.group(0)
    
    # Phone pattern
    phone_match = re.search(r'(?:\+44|0)[\s-]?[\d\s-]{10,}', text)
    if phone_match:
        return phone_match.group(0).strip()
    
    return ''

# Scrape single product page
def scrape_table_data(url: str, base_currency="EUR", session=None, manual_assistance=False) -> dict:
    if session is None:
        session = create_session()
    
    try:
        print(f"Scraping: {url}")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract basic info
        title_tag = soup.select_one("h1") or soup.select_one("title")
        title = title_tag.get_text().strip() if title_tag else "Unknown Product"
        
        # Try to find price with multiple selectors - enhanced
        price_selectors = [
            ".price", ".product-price", ".price-current", "[data-price]", 
            ".cost", ".amount", ".value", "[class*='price']", "[id*='price']",
            ".price-box", ".price-wrapper", ".product-price-value", ".current-price",
            ".sale-price", ".regular-price", ".price-display", ".cost-display",
            "[class*='cost']", "[class*='amount']", "[id*='cost']", "[id*='amount']"
        ]
        
        price_val = 0
        price_cur = "EUR"
        price_found = False
        
        for selector in price_selectors:
            price_tag = soup.select_one(selector)
            if price_tag:
                price_text = price_tag.get_text().strip()
                parsed_cur, parsed_val = parse_price(price_text)
                if parsed_cur and parsed_val:
                    price_cur, price_val = parsed_cur, parsed_val
                    price_found = True
                    break
        
        # If no price found automatically, try manual assistance for important data
        if not price_found and manual_assistance:
            print(f"⚠️  Could not auto-extract price for {url}")
            manual_price = get_manual_price(url)
            if manual_price:
                price_cur, price_val = manual_price['currency'], manual_price['amount']
        
        # Extract dimensions with manual assistance
        dimensions = extract_dimensions_with_assistance(soup, title, url, manual_assistance)
        
        # Extract delivery information
        delivery_info = extract_delivery_info(soup)
        
        # Extract assembly and warranty info
        service_info = extract_service_info(soup)
        
        # Convert to base currency
        try:
            price_eur = price_val if price_cur == base_currency else c.convert(price_cur, base_currency, price_val)
        except Exception:
            price_eur = price_val
        
        # Extract domain for company name
        domain = url.split("//")[1].split("/")[0].replace("www.", "").capitalize()
        
        data = {
            "Uzņēmuma nosaukums": domain,
            "Mājaslapa / veikala URL": f"https://{url.split('//')[1].split('/')[0]}",
            "Produkta lapas URL": url,
            "Valsts / reģions": "UK" if ".uk" in url else "Unknown",
            "Veikala tips": "Online",
            "SKU / Modelis": title[:50],  # Use product title as SKU
            "Galda tips": "Dining Table",
            "Materiāls(-i)": "Oak",
            "Apdare / Krāsa": "Natural",
            "Garums_cm": dimensions.get('length'),
            "Platums_cm": dimensions.get('width'),
            "Augstums_cm": dimensions.get('height'),
            "Izmēru piezīmes": dimensions.get('notes', ''),
            "Cena_valūta": price_cur,
            "Cena_summa": price_val,
            "Cena_EUR": round(price_eur, 2) if price_eur else 0,
            "Cena_vienība": "each",
            "Cena_piezīmes": "",
            "Piegādes izmaksas": delivery_info.get('cost'),
            "Piegādes noteikumi": delivery_info.get('terms', ''),
            "Piegādes laiks_dienas": delivery_info.get('time_days'),
            "Piegādes veids": delivery_info.get('method', ''),
            "Montāža nepieciešama": service_info.get('assembly_required', ''),
            "Atgriešanas noteikumi_dienas": service_info.get('return_days'),
            "Garantija_mēneši": service_info.get('warranty_months'),
            "Pielāgošanas iespējas": service_info.get('customization', ''),
            "Pielāgošanas laiks_dienas": service_info.get('customization_days'),
            "Krājuma statuss": extract_stock_status(soup),
            "Minimālais pasūtījuma daudzums": 1,
            "Apmaksas noteikumi": extract_payment_info(soup),
            "PVN iekļauts": "Yes" if any(keyword in soup.get_text().lower() for keyword in ['inc vat', 'including vat', 'incl. vat']) else "Unknown",
            "Kontakta persona": "",
            "Kontakta e-pasts vai telefons": extract_contact_info(soup),
            "Ekrānuzņēmuma URL": "",
            "Avota piezīmes": f"Scraped from {domain}",
            "Datums pārbaudīts": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "Konkurenta vērtējums": None,
            "Darbību priekšlikumi": ""
        }
        
        print(f"✓ Successfully scraped: {domain} - {title[:30]}... (Dims: {dimensions.get('length')}×{dimensions.get('width')}×{dimensions.get('height')})")
        return data
        
    except requests.exceptions.Timeout:
        print(f"✗ Timeout error for {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error for {url}: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"✗ Parsing error for {url}: {str(e)[:100]}")
        return None

@app.post("/crawl")
def crawl_tables(request: CrawlRequest):
    try:
        # Read URLs from unique_urls.txt
        url_file = "unique_urls.txt"
        if not os.path.exists(url_file):
            raise HTTPException(status_code=400, detail=f"URL file {url_file} not found.")
        
        with open(url_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            raise HTTPException(status_code=400, detail="No URLs found in unique_urls.txt")
        
        print(f"Starting to crawl {len(urls)} URLs...")
        
        all_data = []
        failed_urls = []
        session = create_session()
        
        # Process URLs with concurrent processing for better speed
        def process_url(url):
            result = scrape_table_data(url, base_currency=request.base_currency, session=session, manual_assistance=request.manual_assistance)
            return url, result
        
        # Process URLs - sequential if manual assistance, concurrent otherwise
        if request.manual_assistance:
            print("🤝 Manual assistance enabled - processing URLs sequentially...")
            for url in urls:
                try:
                    url, data = process_url(url)
                    if data:
                        all_data.append(data)
                    else:
                        failed_urls.append(url)
                except Exception as exc:
                    print(f'URL {url} generated an exception: {exc}')
                    failed_urls.append(url)
        else:
            # Use ThreadPoolExecutor for concurrent processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_url = {executor.submit(process_url, url): url for url in urls}
                
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        url, data = future.result()
                        if data:
                            all_data.append(data)
                        else:
                            failed_urls.append(url)
                    except Exception as exc:
                        print(f'URL {url} generated an exception: {exc}')
                        failed_urls.append(url)
        
        # Save failed URLs for review
        if failed_urls:
            with open("failed_urls.txt", "w", encoding="utf-8") as f:
                for url in failed_urls:
                    f.write(url + "\n")
            print(f"Saved {len(failed_urls)} failed URLs to failed_urls.txt")
        
        if not all_data:
            raise HTTPException(status_code=404, detail="No data scraped successfully.")
        
        print(f"Successfully scraped {len(all_data)} out of {len(urls)} URLs")
        
        df = pd.DataFrame(all_data)
        
        # Save CSV
        csv_path = "scraped_tables.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        
        # Save Excel
        df.to_excel(request.output_excel, index=False)
        
        return {
            "message": f"Scraping completed!",
            "total_urls": len(urls),
            "successful": len(all_data),
            "failed": len(failed_urls),
            "csv_file": csv_path,
            "excel_file": request.output_excel
        }
    
    except Exception as e:
        print(f"Error in crawl_tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
