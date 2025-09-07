import requests
import socket
import whois
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.models.domain import DomainIntel

class CrawlerService:
    @staticmethod
    def crawl_domain(url: str):
        """Crawler that fetches title, real IP, and registrar info."""
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "N/A"
            
            # Get real IP
            parsed_url = urlparse(url)
            domain = parsed_url.netloc or parsed_url.path
            try:
                ip = socket.gethostbyname(domain)
            except:
                ip = "N/A"
            
            # Get registrar info
            try:
                w = whois.whois(domain)
                registrar = w.registrar or "N/A"
            except:
                registrar = "N/A"
            
            # Simple risk score based on domain age or something (placeholder)
            risk_score = 0.1  # Could be enhanced with more logic
            
            intel = DomainIntel(domain=url, ip=ip, registrar=registrar, risk_score=risk_score)
            data = intel.to_dict()
            data["title"] = title
            return data
        except Exception as e:
            return {"error": str(e), "domain": url}
