import requests
from bs4 import BeautifulSoup
from app.models.domain import DomainIntel

class CrawlerService:
    @staticmethod
    def crawl_domain(url: str):
        """Very simple crawler that fetches title + IP."""
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "N/A"
            intel = DomainIntel(domain=url, ip="1.2.3.4", registrar="MockRegistrar", risk_score=0.1)
            data = intel.to_dict()
            data["title"] = title
            return data
        except Exception as e:
            return {"error": str(e), "domain": url}
