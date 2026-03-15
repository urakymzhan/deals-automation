import requests
from bs4 import BeautifulSoup
from typing import Optional
from .base import BaseScraper, ScrapeResult

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class AmazonScraper(BaseScraper):
    source = "amazon"

    def scrape(self, url: str) -> Optional[ScrapeResult]:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title_tag = soup.select_one("#productTitle")
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"

            # Try multiple price selectors (Amazon changes these often)
            price = None
            for selector in [
                "span.a-price span.a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                ".a-price .a-offscreen",
            ]:
                tag = soup.select_one(selector)
                if tag:
                    raw = tag.get_text(strip=True).replace("$", "").replace(",", "")
                    try:
                        price = float(raw)
                        break
                    except ValueError:
                        continue

            return ScrapeResult(title=title, price=price, url=url, source=self.source)
        except Exception as e:
            print(f"[Amazon] Error scraping {url}: {e}")
            return None
