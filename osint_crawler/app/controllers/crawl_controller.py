from app.services.crawler_service import CrawlerService

class CrawlController:
    @staticmethod
    def crawl_domain(url: str):
        return CrawlerService.crawl_domain(url)
