from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapeResult:
    title: str
    price: Optional[float]
    url: str
    source: str


class BaseScraper:
    source = "base"

    def scrape(self, url: str) -> Optional[ScrapeResult]:
        raise NotImplementedError
