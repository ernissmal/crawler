import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

from app.models.domain import DomainIntel
from app.models.target import GoogleGeekingModel
from app.services.crawler_service import CrawlerService


class CrawlController:
    def __init__(self):
        load_dotenv()
        self.seed = os.getenv("TARGET_SEED", "John Doe")
        self.seed_type = os.getenv("TARGET_TYPE", "name")
        self.model = GoogleGeekingModel(self.seed, seed_type=self.seed_type)

    def search_duckduckgo(self, query: str, max_results: int = 5):
        """
        Perform a DuckDuckGo search and return a list of URLs.
        """
        urls = []
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                urls.append(result.get("href"))
        return urls

    def run_osint(self):
        """
        Full OSINT pipeline:
        1. Generate queries
        2. Run DuckDuckGo search
        3. Crawl found domains
        """
        results_tree = {}
        queries = self.model.queries

        for category, qlist in queries.items():
            results_tree[category] = []
            for q in qlist:
                urls = self.search_duckduckgo(q)
                crawled_data = []
                for u in urls:
                    crawled_data.append(CrawlerService.crawl_domain(u))
                results_tree[category].append({
                    "query": q,
                    "urls": urls,
                    "intel": crawled_data
                })

        return {
            "seed": self.seed,
            "seed_type": self.seed_type,
            "results": results_tree
        }

    def crawl_domain(self, url: str):
        """Crawl a single domain."""
        return CrawlerService.crawl_domain(url)
