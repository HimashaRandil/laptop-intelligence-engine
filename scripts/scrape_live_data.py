"""
Web scraper for collecting live pricing and availability.
WARNING: Always check website ToS before scraping.

Requirements:
pip install playwright beautifulsoup4 requests
playwright install chromium
"""

import time
import logging
from datetime import datetime
from typing import Optional, Dict, List
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_DELAY = 3  # seconds between requests
MAX_RETRIES = 3


class ScraperBase:
    """Base class for scrapers with common functionality."""

    def __init__(self, db: Session):
        self.db = db
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page(user_agent=USER_AGENT)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                logging.info(f"Fetching {url} (attempt {attempt + 1})")
                self.page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(REQUEST_DELAY)
                return self.page.content()
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    return None
                time.sleep(REQUEST_DELAY * 2)
        return None

    def save_price_snapshot(
        self,
        laptop: Laptop,
        price: float,
        currency: str = "USD",
        availability: str = "In Stock",
        configuration_summary: str = None,
    ):
        """Save price data to database."""
        snapshot = PriceSnapshot(
            laptop_id=laptop.id,
            price=price,
            currency=currency,
            availability_status=availability,
            configuration_summary=configuration_summary,
            snapshot_date=datetime.now(),
        )
        self.db.add(snapshot)
        logging.info(f"Saved price: ${price} for {laptop.full_model_name}")

    def save_review(
        self,
        laptop: Laptop,
        reviewer_name: str,
        rating: int,
        review_text: str,
        review_date: datetime = None,
    ):
        """Save review to database."""
        review = Review(
            laptop_id=laptop.id,
            reviewer_name=reviewer_name,
            rating=rating,
            review_text=review_text,
            review_date=review_date or datetime.now(),
        )
        self.db.add(review)
        logging.info(f"Saved review from {reviewer_name}")


class LenovoScraper(ScraperBase):
    """Scraper for Lenovo product pages."""

    def scrape(self, laptop: Laptop):
        """Scrape Lenovo product page."""
        html = self.fetch_page(laptop.product_page_url)
        if not html:
            logging.error(f"Failed to fetch Lenovo page for {laptop.full_model_name}")
            return

        soup = BeautifulSoup(html, "html.parser")

        # Extract price - UPDATE THESE SELECTORS BASED ON ACTUAL SITE
        price_elem = soup.select_one(".pricingSummary-price, .price-final")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = self._parse_price(price_text)
            if price:
                # Check availability
                availability = "In Stock"
                avail_elem = soup.select_one(".inventory-status")
                if avail_elem and "out of stock" in avail_elem.get_text().lower():
                    availability = "Out of Stock"

                self.save_price_snapshot(laptop, price, availability=availability)

        # Extract reviews
        self._scrape_reviews(soup, laptop)

    def _scrape_reviews(self, soup: BeautifulSoup, laptop: Laptop):
        """Extract reviews from page."""
        review_section = soup.select(".review-item, .bv-content-item")

        for review_elem in review_section[:10]:  # Limit to 10 reviews
            try:
                reviewer = review_elem.select_one(".bv-author").get_text(strip=True)
                rating_elem = review_elem.select_one(".bv-rating")
                rating = int(rating_elem.get("aria-label", "0").split()[0])
                text = review_elem.select_one(".bv-content-summary").get_text(
                    strip=True
                )

                self.save_review(laptop, reviewer, rating, text)
            except Exception as e:
                logging.warning(f"Failed to parse review: {e}")

    @staticmethod
    def _parse_price(price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        try:
            # Remove currency symbols and commas
            clean = price_text.replace("$", "").replace(",", "").strip()
            return float(clean)
        except ValueError:
            return None


class HPScraper(ScraperBase):
    """Scraper for HP product pages."""

    def scrape(self, laptop: Laptop):
        """Scrape HP product page."""
        html = self.fetch_page(laptop.product_page_url)
        if not html:
            logging.error(f"Failed to fetch HP page for {laptop.full_model_name}")
            return

        soup = BeautifulSoup(html, "html.parser")

        # HP Standard Product Page
        price_elem = soup.select_one('.product-price, [data-testid="price"]')
        if price_elem:
            price = self._parse_price(price_elem.get_text(strip=True))
            if price:
                self.save_price_snapshot(laptop, price)

        self._scrape_reviews(soup, laptop)

    def scrape_collection(self, laptop: Laptop):
        """Scrape HP collection/configuration page with multiple SKUs."""
        html = self.fetch_page(laptop.product_page_url)
        if not html:
            return

        soup = BeautifulSoup(html, "html.parser")

        # Find all product tiles/configurations
        product_tiles = soup.select(".product-tile, .configuration-option")

        for tile in product_tiles:
            try:
                config = tile.select_one(".config-summary").get_text(strip=True)
                price_elem = tile.select_one(".price")
                price = self._parse_price(price_elem.get_text(strip=True))

                if price:
                    self.save_price_snapshot(
                        laptop, price, configuration_summary=config
                    )

                # Follow detail link for reviews
                detail_link = tile.select_one("a.details-link")
                if detail_link:
                    detail_url = detail_link.get("href")
                    self._scrape_detail_page(detail_url, laptop)

            except Exception as e:
                logging.warning(f"Failed to parse tile: {e}")

    def _scrape_detail_page(self, url: str, laptop: Laptop):
        """Scrape individual product detail page."""
        html = self.fetch_page(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            self._scrape_reviews(soup, laptop)

    def _scrape_reviews(self, soup: BeautifulSoup, laptop: Laptop):
        """Extract HP reviews."""
        reviews = soup.select('.review-container, [data-testid="review"]')

        for review_elem in reviews[:10]:
            try:
                reviewer = review_elem.select_one(".reviewer-name").get_text(strip=True)
                rating_elem = review_elem.select_one(".star-rating")
                rating = int(rating_elem.get("data-rating", 0))
                text = review_elem.select_one(".review-text").get_text(strip=True)

                self.save_review(laptop, reviewer, rating, text)
            except Exception as e:
                logging.warning(f"Failed to parse review: {e}")

    @staticmethod
    def _parse_price(price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        try:
            clean = price_text.replace("$", "").replace(",", "").strip()
            return float(clean)
        except ValueError:
            return None


def main():
    """Main scraping orchestrator."""
    logging.info("Starting live data scraping...")

    db = SessionLocal()

    try:
        with LenovoScraper(db) as lenovo_scraper, HPScraper(db) as hp_scraper:
            laptops = db.query(Laptop).all()

            for laptop in laptops:
                try:
                    if "Lenovo" in laptop.brand:
                        lenovo_scraper.scrape(laptop)
                    elif "HP ProBook 440" in laptop.full_model_name:
                        hp_scraper.scrape_collection(laptop)
                    elif "HP" in laptop.brand:
                        hp_scraper.scrape(laptop)

                    time.sleep(REQUEST_DELAY)

                except Exception as e:
                    logging.error(f"Error scraping {laptop.full_model_name}: {e}")

            # Commit all changes
            db.commit()
            logging.info("Scraping complete and data saved.")

    except Exception as e:
        db.rollback()
        logging.exception("Critical error during scraping")
    finally:
        db.close()


if __name__ == "__main__":
    main()
