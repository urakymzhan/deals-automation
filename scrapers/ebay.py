from typing import Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapeResult


class EbayScraper(BaseScraper):
    source = "ebay"

    def scrape(self, url: str) -> Optional[ScrapeResult]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                    locale="en-US",
                )
                page = context.new_page()

                # Hide webdriver flag
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                page.goto(url, wait_until="networkidle", timeout=30000)
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")

            title_tag = soup.select_one("h1.x-item-title__mainTitle span.ux-textspans")
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"

            price_tag = soup.select_one("div.x-price-primary")
            price = None
            if price_tag:
                raw = price_tag.get_text(strip=True).replace("US $", "").replace("$", "").replace(",", "").strip()
                try:
                    price = float(raw)
                except ValueError:
                    pass

            return ScrapeResult(title=title, price=price, url=url, source=self.source)
        except Exception as e:
            print(f"[eBay] Error scraping {url}: {e}")
            return None
