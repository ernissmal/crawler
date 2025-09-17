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

c = CurrencyRates()

# Configure requests session with retries and proper headers
def create_session():
    session = requests.Session()
    
    # Set up retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
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
def scrape_table_data(url: str, base_currency="EUR") -> dict:
    try:
        res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}

    soup = BeautifulSoup(res.text, "html.parser")

    # ---- Replace these selectors per competitor ----
    product_name = soup.select_one("h1")  # Example
    price_tag = soup.select_one(".price")  # Example
    sku_tag = soup.select_one(".sku")      # Example

    price_val = 0
    price_cur = "EUR"
    if price_tag:
        price_cur, price_val = parse_price(price_tag.get_text())

    # Convert to base currency
    try:
        price_eur = price_val if price_cur == base_currency else c.convert(price_cur, base_currency, price_val)
    except:
        price_eur = price_val

    data = {
        "Uzņēmuma nosaukums": soup.select_one("meta[property='og:site_name']")["content"] if soup.select_one("meta[property='og:site_name']") else "Unknown",
        "Mājaslapa / veikala URL": url.split("/")[2],
        "Produkta lapas URL": url,
        "Valsts / reģions": url.split(".")[-1].upper(),
        "Veikala tips": "Mazumtirdzniecība",
        "SKU / Modelis": sku_tag.get_text().strip() if sku_tag else "",
        "Galda tips": "Ēdamistabas",
        "Materiāls(-i)": "Ozols",
        "Apdare / Krāsa": "Natural",
        "Garums_cm": None,
        "Platums_cm": None,
        "Augstums_cm": None,
        "Izmēru piezīmes": "",
        "Cena_valūta": price_cur,
        "Cena_summa": price_val,
        "Cena_EUR": round(price_eur, 2),
        "Cena_vienība": "gabalā",
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
        "Krājuma statuss": "",
        "Minimālais pasūtījuma daudzums": 1,
        "Apmaksas noteikumi": "",
        "PVN iekļauts": "",
        "Kontakta persona": "",
        "Kontakta e-pasts vai telefons": "",
        "Ekrānuzņēmuma URL": "",
        "Avota piezīmes": "",
        "Datums pārbaudīts": pd.Timestamp.today().strftime("%Y-%m-%d"),
        "Konkurenta vērtējums": None,
        "Darbību priekšlikumi": ""
    }
    return data

@app.post("/crawl")
def crawl_tables(request: CrawlRequest):
    # Read URLs from unique_urls.txt
    url_file = "unique_urls.txt"
    if not os.path.exists(url_file):
        raise HTTPException(status_code=400, detail=f"URL file {url_file} not found.")
    with open(url_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]


    all_data = []
    failed_urls = []
    for url in urls:
        try:
            data = scrape_table_data(url, base_currency=request.base_currency)
            if data:
                all_data.append(data)
            else:
                failed_urls.append(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            failed_urls.append(url)
            # Prompt for user assistance (console input)
            user_input = input(f"Failed to fetch {url}. Type 'skip' to continue, 'retry' to try again, or 'exit' to stop: ").strip().lower()
            if user_input == 'retry':
                try:
                    data = scrape_table_data(url, base_currency=request.base_currency)
                    if data:
                        all_data.append(data)
                        failed_urls.pop()
                except Exception as e2:
                    print(f"Retry failed for {url}: {e2}")
            elif user_input == 'exit':
                break
            # else skip

    # Save failed URLs for review
    if failed_urls:
        with open("failed_urls.txt", "w", encoding="utf-8") as f:
            for url in failed_urls:
                f.write(url + "\n")

    if not all_data:
        raise HTTPException(status_code=404, detail="No data scraped.")

    df = pd.DataFrame(all_data, columns=COLUMNS)

    # Save CSV
    csv_path = "scraped_tables.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # Save or append Excel
    if os.path.exists(request.output_excel):
        book = pd.ExcelWriter(request.output_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay')
        df.to_excel(book, index=False, sheet_name='Scraped Data', startrow=book.sheets['Scraped Data'].max_row if 'Scraped Data' in book.sheets else 0)
        book.close()
    else:
        df.to_excel(request.output_excel, index=False)

    return {"message": f"Scraping done. CSV saved at {csv_path} and Excel updated at {request.output_excel}"}
