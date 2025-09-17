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

app = FastAPI(title="International Solid Oak Table Scraper")

@app.get("/")
def health_check():
    return {"status": "OK", "message": "Oak Table Scraper API is running"}

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

# Scrape single product page
def scrape_table_data(url: str, base_currency="EUR", session=None) -> dict:
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
        
        # Try to find price with multiple selectors
        price_selectors = [
            ".price", ".product-price", ".price-current", "[data-price]", 
            ".cost", ".amount", ".value", "[class*='price']", "[id*='price']"
        ]
        
        price_val = 0
        price_cur = "EUR"
        
        for selector in price_selectors:
            price_tag = soup.select_one(selector)
            if price_tag:
                price_text = price_tag.get_text().strip()
                parsed_cur, parsed_val = parse_price(price_text)
                if parsed_cur and parsed_val:
                    price_cur, price_val = parsed_cur, parsed_val
                    break
        
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
            "Garums_cm": None,
            "Platums_cm": None,
            "Augstums_cm": None,
            "Izmēru piezīmes": "",
            "Cena_valūta": price_cur,
            "Cena_summa": price_val,
            "Cena_EUR": round(price_eur, 2) if price_eur else 0,
            "Cena_vienība": "each",
            "Cena_piezīmes": "",
            "Piegādes izmaksas": None,
            "Piegādes noteikumi": "",
            "Piegādes laiks_dienas": None,
            "Piegādes veids": "",
            "Montāža nepieciešama": "",
            "Atgriešanas noteikumi_dienas": None,
            "Garantija_mēneši": None,
            "Pielāgošanas iespējas": "",
            "Pielāgošanas laiks_dienas": None,
            "Krājuma statuss": "Available",
            "Minimālais pasūtījuma daudzums": 1,
            "Apmaksas noteikumi": "",
            "PVN iekļauts": "",
            "Kontakta persona": "",
            "Kontakta e-pasts vai telefons": "",
            "Ekrānuzņēmuma URL": "",
            "Avota piezīmes": f"Scraped from {domain}",
            "Datums pārbaudīts": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "Konkurenta vērtējums": None,
            "Darbību priekšlikumi": ""
        }
        
        print(f"✓ Successfully scraped: {domain} - {title[:30]}...")
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
            result = scrape_table_data(url, base_currency=request.base_currency, session=session)
            return url, result
        
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
