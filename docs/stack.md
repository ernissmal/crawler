2. Tech Stack & Libraries

Flask → API endpoints to control crawlers and retrieve results.

Requests / httpx → Core HTTP client.

BeautifulSoup4 / lxml → HTML parsing.

Scrapy (optional) → If you need high-performance crawling with scheduling, retries, throttling.

Celery + Redis → Task queue for concurrent crawls.

MongoDB / PostgreSQL → Store structured results.

Elasticsearch / OpenSearch (optional) → Searchable index for OSINT data.