from .ebay import EbayScraper
from .amazon import AmazonScraper


def get_scraper(source: str):
    scrapers = {
        "ebay": EbayScraper(),
        "amazon": AmazonScraper(),
    }
    return scrapers.get(source)
