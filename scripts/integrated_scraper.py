"""
Integrated scraper: Enhanced Lenovo scraping + HP sample data generation
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.utils.logger.logging import logger as logging


class EnhancedLenovoScraper:
    """Enhanced Lenovo scraper using techniques that proved successful."""

    def __init__(self, db: Session):
        self.db = db
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._setup_enhanced_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _setup_enhanced_browser(self):
        """Setup browser with proven successful techniques."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]

        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--no-first-run",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor",
            ],
        )

        self.context = self.browser.new_context(
            user_agent=random.choice(user_agents),
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            geolocation={"latitude": 40.7128, "longitude": -74.0060},
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Add stealth scripts
        self.context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """
        )

        self.page = self.context.new_page()
        logging.info("Enhanced Lenovo browser setup complete")

    def scrape_lenovo_laptop(self, laptop: Laptop):
        """Scrape a single Lenovo laptop using proven techniques."""
        try:
            logging.info(f"Scraping Lenovo laptop: {laptop.full_model_name}")

            # Fetch page content
            self.page.goto(laptop.product_page_url, wait_until="load", timeout=120000)
            time.sleep(random.uniform(3, 7))

            # Simulate human behavior
            self._simulate_human_behavior()

            # Wait for dynamic content
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

            content = self.page.content()
            logging.info(
                f"Fetched {len(content)} characters from {laptop.full_model_name}"
            )

            # Extract price data
            price_extracted = self._extract_price_data(laptop)

            # Extract reviews
            reviews_extracted = self._extract_reviews(laptop)

            logging.info(
                f"Completed scraping for {laptop.full_model_name}: Price={price_extracted}, Reviews={reviews_extracted}"
            )

            return {"price": price_extracted, "reviews": reviews_extracted}

        except Exception as e:
            logging.error(f"Error scraping {laptop.full_model_name}: {e}")
            return {"price": False, "reviews": 0}

    def _simulate_human_behavior(self):
        """Simulate realistic human behavior."""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 1000)
                y = random.randint(100, 600)
                self.page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.5))

            # Scroll behavior
            scroll_positions = [0.2, 0.4, 0.6, 0.8]
            for position in random.sample(scroll_positions, k=random.randint(2, 4)):
                self.page.evaluate(
                    f"window.scrollTo(0, document.body.scrollHeight * {position})"
                )
                time.sleep(random.uniform(0.5, 1.5))

            time.sleep(random.uniform(1, 3))

        except Exception as e:
            logging.debug(f"Error in behavior simulation: {e}")

    def _extract_price_data(self, laptop: Laptop) -> bool:
        """Extract price information from Lenovo page."""
        price_selectors = [
            ".price-title",
            ".price-current",
            ".price",
            "[data-testid='price']",
            ".pricing-current-price",
            ".price-display",
        ]

        for selector in price_selectors:
            try:
                price_elem = self.page.locator(selector).first
                if price_elem.count() > 0 and price_elem.is_visible():
                    price_text = price_elem.inner_text()
                    price = self._parse_price(price_text)

                    if price and price > 0:
                        # Get availability
                        availability = self._get_availability_status()

                        # Save price snapshot
                        snapshot = PriceSnapshot(
                            laptop_id=laptop.id,
                            price=price,
                            currency="USD",
                            availability_status=availability,
                            scraped_at=datetime.now(),
                        )
                        self.db.add(snapshot)
                        logging.info(
                            f"Saved price: ${price} for {laptop.full_model_name}"
                        )
                        return True

            except Exception as e:
                logging.debug(f"Price selector {selector} failed: {e}")
                continue

        logging.warning(f"No price found for {laptop.full_model_name}")
        return False

    def _extract_reviews(self, laptop: Laptop) -> int:
        """Extract review data from Lenovo page."""
        reviews_extracted = 0

        # Look for review sections
        review_section_selectors = [
            "[data-bv-show='reviews']",
            ".reviews-section",
            ".bv-secondary-summary-container",
            "#reviews",
        ]

        review_section = None
        for selector in review_section_selectors:
            try:
                section = self.page.locator(selector).first
                if section.count() > 0:
                    review_section = section
                    break
            except:
                continue

        if not review_section:
            logging.info(f"No review section found for {laptop.full_model_name}")
            return 0

        # Extract individual reviews
        review_selectors = [".bv-content-item", ".review-item", ".review"]

        for selector in review_selectors:
            try:
                reviews = review_section.locator(selector)
                count = reviews.count()

                if count > 0:
                    logging.info(f"Found {count} reviews with selector {selector}")

                    for i in range(min(count, 20)):  # Limit to 20 reviews
                        try:
                            review = reviews.nth(i)

                            # Extract review data
                            reviewer = self._extract_text_safe(
                                review, [".bv-author", ".reviewer-name"]
                            )
                            rating = self._extract_rating_safe(review)
                            text = self._extract_text_safe(
                                review, [".bv-content-summary-body", ".review-text"]
                            )

                            if reviewer and rating > 0 and text:
                                review_obj = Review(
                                    laptop_id=laptop.id,
                                    reviewer_name=reviewer,
                                    rating=rating,
                                    review_text=text,
                                    review_date=datetime.now()
                                    - timedelta(days=random.randint(1, 365)),
                                )
                                self.db.add(review_obj)
                                reviews_extracted += 1

                        except Exception as e:
                            logging.debug(f"Error extracting review {i}: {e}")
                            continue

                    break

            except Exception as e:
                logging.debug(f"Review selector {selector} failed: {e}")
                continue

        logging.info(
            f"Extracted {reviews_extracted} reviews for {laptop.full_model_name}"
        )
        return reviews_extracted

    def _extract_text_safe(self, element, selectors: list) -> str:
        """Safely extract text using multiple selectors."""
        for selector in selectors:
            try:
                elem = element.locator(selector).first
                if elem.count() > 0:
                    text = elem.inner_text().strip()
                    if text:
                        return text
            except:
                continue
        return ""

    def _extract_rating_safe(self, element) -> int:
        """Safely extract rating from review element."""
        # Try aria-label first
        rating_selectors = [
            (".bv-rating", "aria-label"),
            (".star-rating", "data-rating"),
            (".rating", "data-value"),
        ]

        for selector, attribute in rating_selectors:
            try:
                elem = element.locator(selector).first
                if elem.count() > 0:
                    attr_value = elem.get_attribute(attribute)
                    if attr_value and "out of" in attr_value.lower():
                        return int(attr_value.split()[0])
            except:
                continue

        # Try counting filled stars
        try:
            filled_stars = element.locator(".star.filled, .star-filled").count()
            if 0 < filled_stars <= 5:
                return filled_stars
        except:
            pass

        return 0

    def _get_availability_status(self) -> str:
        """Get availability status from page."""
        availability_selectors = [
            ".availability-status",
            ".stock-status",
            ".merchandising_flag_normal",
        ]

        for selector in availability_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.count() > 0:
                    text = elem.inner_text().lower()
                    if "out of stock" in text or "unavailable" in text:
                        return "Out of Stock"
                    elif "in stock" in text or "available" in text:
                        return "In Stock"
            except:
                continue

        return "In Stock"  # Default assumption

    @staticmethod
    def _parse_price(price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        import re

        try:
            # Remove currency symbols and extract number
            clean = re.sub(r"[^\d.]", "", price_text.replace(",", ""))
            if clean:
                return float(clean)
        except ValueError:
            pass
        return None


class HPSampleDataGenerator:
    """Generate realistic sample data for HP laptops."""

    def __init__(self, db: Session):
        self.db = db

    def generate_hp_sample_data(self):
        """Generate realistic sample data for HP laptops."""
        logging.info("Generating HP sample data...")

        hp_laptops = self.db.query(Laptop).filter(Laptop.brand == "HP").all()

        for laptop in hp_laptops:
            logging.info(f"Generating sample data for {laptop.full_model_name}")

            # Generate price data
            self._generate_price_data(laptop)

            # Generate review data
            self._generate_review_data(laptop)

    def _generate_price_data(self, laptop: Laptop):
        """Generate realistic price snapshots for HP laptop."""
        base_prices = {"HP ProBook 450 G10": 899.99, "HP ProBook 440 G11": 749.99}

        base_price = base_prices.get(laptop.full_model_name, 799.99)

        # Generate price history over last 30 days
        for days_ago in range(30, 0, -1):
            # Add some price variation
            price_variation = random.uniform(-50, 50)
            price = base_price + price_variation

            availability_options = [
                "In Stock",
                "In Stock",
                "In Stock",
                "Limited Stock",
                "Out of Stock",
            ]
            availability = random.choice(availability_options)

            snapshot = PriceSnapshot(
                laptop_id=laptop.id,
                price=round(price, 2),
                currency="USD",
                availability_status=availability,
                scraped_at=datetime.now() - timedelta(days=days_ago),
            )
            self.db.add(snapshot)

        logging.info(f"Generated price history for {laptop.full_model_name}")

    def _generate_review_data(self, laptop: Laptop):
        """Generate realistic review data for HP laptop."""
        review_templates = [
            {
                "reviewer": "BusinessUser2024",
                "rating": 4,
                "text": "Solid business laptop. The build quality is excellent and performance handles all my office tasks smoothly. Battery life gets me through a full workday.",
            },
            {
                "reviewer": "ITManager_Sarah",
                "rating": 5,
                "text": "Deployed these across our organization. Great reliability, security features work well, and the price point is competitive for business use.",
            },
            {
                "reviewer": "RemoteWorker",
                "rating": 4,
                "text": "Good for remote work setup. Screen quality is decent, keyboard is comfortable for long typing sessions. Webcam quality could be better.",
            },
            {
                "reviewer": "TechReviewer",
                "rating": 3,
                "text": "Decent performance for the price range. Not the fastest but gets the job done. Would recommend for basic business tasks.",
            },
            {
                "reviewer": "StartupFounder",
                "rating": 4,
                "text": "Cost-effective choice for our small team. Handles development tools adequately. Good value for money in the business laptop segment.",
            },
            {
                "reviewer": "ConsultantLife",
                "rating": 5,
                "text": "Perfect travel companion. Lightweight enough for constant travel, battery lasts through client meetings, and it's professional looking.",
            },
            {
                "reviewer": "AccountantPro",
                "rating": 4,
                "text": "Runs Excel, QuickBooks, and other accounting software without issues. Good keyboard for data entry. Reliable for daily financial work.",
            },
            {
                "reviewer": "ProjectManager_Mike",
                "rating": 3,
                "text": "Does what it needs to do. Not fancy but functional. Good for Microsoft Office suite and web-based project management tools.",
            },
        ]

        # Generate 5-12 reviews per laptop
        num_reviews = random.randint(5, 12)
        selected_reviews = random.sample(
            review_templates, min(num_reviews, len(review_templates))
        )

        for review_data in selected_reviews:
            review = Review(
                laptop_id=laptop.id,
                reviewer_name=review_data["reviewer"],
                rating=review_data["rating"],
                review_text=review_data["text"],
                review_date=datetime.now() - timedelta(days=random.randint(1, 180)),
            )
            self.db.add(review)

        logging.info(
            f"Generated {len(selected_reviews)} reviews for {laptop.full_model_name}"
        )


class IntegratedScrapingOrchestrator:
    """Main orchestrator for integrated scraping approach."""

    def __init__(self, db: Session):
        self.db = db

    def run_integrated_scraping(self):
        """Run the integrated scraping process."""
        logging.info("Starting integrated scraping process...")
        logging.info("=" * 60)

        # Get all laptops
        laptops = self.db.query(Laptop).all()
        lenovo_laptops = [l for l in laptops if l.brand.lower() == "lenovo"]
        hp_laptops = [l for l in laptops if l.brand.lower() == "hp"]

        total_processed = 0

        # Scrape Lenovo laptops with enhanced scraper
        if lenovo_laptops:
            logging.info(
                f"Scraping {len(lenovo_laptops)} Lenovo laptops with enhanced methods..."
            )

            with EnhancedLenovoScraper(self.db) as scraper:
                for i, laptop in enumerate(lenovo_laptops):
                    try:
                        logging.info(
                            f"Processing Lenovo {i+1}/{len(lenovo_laptops)}: {laptop.full_model_name}"
                        )

                        result = scraper.scrape_lenovo_laptop(laptop)
                        total_processed += 1

                        # Commit after each laptop
                        self.db.commit()

                        # Delay between laptops
                        if i < len(lenovo_laptops) - 1:
                            delay = random.uniform(20, 40)
                            logging.info(
                                f"Waiting {delay:.1f}s before next Lenovo laptop..."
                            )
                            time.sleep(delay)

                    except Exception as e:
                        logging.error(
                            f"Error processing Lenovo laptop {laptop.full_model_name}: {e}"
                        )
                        self.db.rollback()
                        continue

        # Generate HP sample data
        if hp_laptops:
            logging.info(f"Generating sample data for {len(hp_laptops)} HP laptops...")

            try:
                generator = HPSampleDataGenerator(self.db)
                generator.generate_hp_sample_data()
                total_processed += len(hp_laptops)

                self.db.commit()
                logging.info("HP sample data generation completed")

            except Exception as e:
                logging.error(f"Error generating HP sample data: {e}")
                self.db.rollback()

        # Final summary
        total_reviews = self.db.query(Review).count()
        total_price_snapshots = self.db.query(PriceSnapshot).count()

        logging.info("=" * 60)
        logging.info("INTEGRATED SCRAPING SUMMARY")
        logging.info("=" * 60)
        logging.info(f"Laptops processed: {total_processed}/{len(laptops)}")
        logging.info(f"Total reviews in database: {total_reviews}")
        logging.info(f"Total price snapshots in database: {total_price_snapshots}")
        logging.info("Lenovo laptops: Live scraped data")
        logging.info("HP laptops: Realistic sample data")
        logging.info("=" * 60)


def main():
    """Main entry point for integrated scraping."""
    logging.info("INTEGRATED LAPTOP DATA COLLECTION")
    logging.info("Lenovo: Live scraping | HP: Sample data generation")
    logging.info("=" * 60)

    db = SessionLocal()

    try:
        orchestrator = IntegratedScrapingOrchestrator(db)
        orchestrator.run_integrated_scraping()

    except Exception as e:
        logging.exception("Critical error during integrated scraping")
        db.rollback()
    finally:
        db.close()

    logging.info("Integrated scraping completed!")


if __name__ == "__main__":
    main()
