"""
Multi-brand Web scraper for Lenovo and HP laptops with Shadow DOM support.
Handles both direct product pages and collection pages with multiple variants.

WARNING: Always check website ToS before scraping.

Requirements:
pip install playwright beautifulsoup4 requests fake-useragent python-dateutil
playwright install chromium firefox webkit
"""

import time
import random
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from sqlalchemy.orm import Session
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.utils.logger.logging import logger as logging


class BotEvasion:
    """Advanced bot evasion techniques."""

    def __init__(self):
        self.ua = UserAgent()
        self.used_user_agents = set()

    def get_random_user_agent(self) -> str:
        """Get a random user agent that hasn't been used recently."""
        attempts = 0
        while attempts < 10:
            user_agent = self.ua.random
            if user_agent not in self.used_user_agents:
                self.used_user_agents.add(user_agent)
                if len(self.used_user_agents) > 20:
                    self.used_user_agents.pop()
                return user_agent
            attempts += 1
        return self.ua.chrome

    def get_random_viewport(self) -> Dict[str, int]:
        """Get random viewport size."""
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
            {"width": 1600, "height": 900},
            {"width": 2560, "height": 1440},
        ]
        return random.choice(viewports)

    def get_random_timing(self) -> Tuple[float, float]:
        """Get random delays for human-like behavior."""
        base_delay = random.uniform(2.5, 5.0)
        interaction_delay = random.uniform(0.5, 2.0)
        return base_delay, interaction_delay

    def human_like_scroll(self, page: Page):
        """Perform human-like scrolling."""
        scroll_actions = random.choice(
            [
                [0.3, 0.7, 1.0],
                [0.5, 0.2, 0.8, 1.0],
                [0.4, 0.9, 0.6, 1.0],
            ]
        )

        for position in scroll_actions:
            page.evaluate(
                f"window.scrollTo(0, document.body.scrollHeight * {position})"
            )
            time.sleep(random.uniform(0.5, 1.5))

    def add_mouse_movements(self, page: Page):
        """Add random mouse movements."""
        try:
            viewport = page.viewport_size
            if viewport:
                for _ in range(random.randint(2, 5)):
                    x = random.randint(0, viewport["width"])
                    y = random.randint(0, viewport["height"])
                    page.mouse.move(x, y)
                    time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            logging.debug(f"Mouse movement failed: {e}")


class MultiBrandScraperBase:
    """Base class with advanced bot evasion for multiple brands."""

    def __init__(self, db: Session):
        self.db = db
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.evasion = BotEvasion()
        self.session_start = datetime.now()
        self.request_count = 0
        self.max_requests_per_session = random.randint(15, 25)

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._setup_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _setup_browser(self):
        """Setup browser with advanced stealth settings."""
        browser_type = random.choice(["chromium"])  # Stick with chromium for stability

        self.browser = self._launch_chromium()
        viewport = self.evasion.get_random_viewport()
        user_agent = self.evasion.get_random_user_agent()

        self.context = self.browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            geolocation={"latitude": 40.7128, "longitude": -74.0060},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            },
        )

        # Add stealth scripts
        self.context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            window.chrome = {
                runtime: {},
            };
        """
        )

        self.page = self.context.new_page()
        logging.info(f"Browser setup complete with UA: {user_agent[:50]}...")

    def _launch_chromium(self) -> Browser:
        """Launch Chromium with stealth args."""
        return self.playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-default-apps",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-blink-features=AutomationControlled",
                "--disable-component-extensions-with-background-pages",
                "--disable-background-networking",
                "--disable-sync",
                "--metrics-recording-only",
                "--disable-default-apps",
                "--mute-audio",
                "--no-report-upload",
                "--disable-component-update",
                "--disable-domain-reliability",
            ],
        )

    def _check_session_limits(self):
        """Check if we need to restart the session."""
        if (
            self.request_count >= self.max_requests_per_session
            or datetime.now() - self.session_start > timedelta(hours=1)
        ):

            logging.info("Session limits reached, restarting browser...")
            self.__exit__(None, None, None)
            self._setup_browser()
            self.session_start = datetime.now()
            self.request_count = 0
            self.max_requests_per_session = random.randint(15, 25)

    def fetch_page_advanced(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Advanced page fetching with human-like behavior."""
        self._check_session_limits()

        base_delay, interaction_delay = self.evasion.get_random_timing()

        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching {url} (attempt {attempt + 1})")

                self.page.goto(url, wait_until="networkidle", timeout=45000)
                self.request_count += 1

                time.sleep(interaction_delay)
                self.evasion.add_mouse_movements(self.page)
                self.evasion.human_like_scroll(self.page)
                time.sleep(base_delay)

                if self._detect_anti_bot():
                    logging.warning("Anti-bot detection triggered, waiting longer...")
                    time.sleep(random.uniform(10, 20))
                    continue

                return self.page.content()

            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")
                if attempt == max_retries - 1:
                    return None

                wait_time = (2**attempt) + random.uniform(1, 3)
                time.sleep(wait_time)

        return None

    def _detect_anti_bot(self) -> bool:
        """Detect common anti-bot measures."""
        try:
            indicators = [
                "captcha",
                "cloudflare",
                "access denied",
                "blocked",
                "suspicious activity",
                "robot",
                "automated",
            ]
            page_content = self.page.content().lower()
            return any(indicator in page_content for indicator in indicators)
        except Exception as e:
            logging.error(f"Error detecting anti-bot measures: {e}")
            return False

    def load_all_reviews_dynamic(self, laptop: Laptop) -> int:
        """Load all reviews by dynamically clicking 'Load More' buttons."""
        total_reviews = 0
        max_attempts = 20
        attempts = 0

        try:
            self.page.wait_for_timeout(3000)

            while attempts < max_attempts:
                load_more_selectors = [
                    'button:has-text("Load More")',
                    'button:has-text("Show More")',
                    'button:has-text("More Reviews")',
                    '[data-testid="load-more"]',
                    ".load-more-reviews",
                    ".show-more-button",
                    ".pagination-next",
                    ".bv-show-more-button",
                ]

                load_more_button = None
                for selector in load_more_selectors:
                    try:
                        button = self.page.locator(selector).first
                        if button.is_visible() and button.is_enabled():
                            load_more_button = button
                            break
                    except Exception as e:
                        logging.error(f"Error finding load more button: {e}")
                        continue

                if not load_more_button:
                    logging.info("No more 'Load More' buttons found")
                    break

                self.evasion.add_mouse_movements(self.page)

                try:
                    load_more_button.scroll_into_view_if_needed()
                    time.sleep(random.uniform(0.5, 1.5))
                    load_more_button.click()
                    logging.info(f"Clicked 'Load More' button (attempt {attempts + 1})")

                    self.page.wait_for_timeout(random.randint(2000, 4000))

                    current_count = self._count_reviews()
                    if current_count > total_reviews:
                        total_reviews = current_count
                        logging.info(f"New reviews loaded. Total: {total_reviews}")
                    else:
                        logging.info("No new reviews loaded, stopping")
                        break

                except Exception as e:
                    logging.warning(f"Failed to click load more button: {e}")
                    break

                attempts += 1
                time.sleep(random.uniform(1, 3))

            logging.info(
                f"Finished loading reviews. Total attempts: {attempts}, Reviews found: {total_reviews}"
            )
            return total_reviews

        except Exception as e:
            logging.error(f"Error loading reviews dynamically: {e}")
            return 0

    def _count_reviews(self) -> int:
        """Count current number of review elements on page."""
        review_selectors = [
            ".bv-content-item",
            ".review-item",
            ".review-container",
            '[data-testid="review"]',
            ".review",
        ]

        for selector in review_selectors:
            try:
                count = self.page.locator(selector).count()
                if count > 0:
                    return count
            except Exception as e:
                logging.error(f"Error counting reviews for selector {selector}: {e}")
                continue
        return 0

    def scrape_all_reviews_shadow_dom(
        self, laptop: Laptop, variant_info: str = None
    ) -> int:
        """Comprehensive review scraping for Shadow DOM content."""
        try:
            variant_label = f" ({variant_info})" if variant_info else ""
            logging.info(
                f"Starting review scrape for {laptop.full_model_name}{variant_label}"
            )

            total_available = self.load_all_reviews_dynamic(laptop)

            shadow_host_selectors = [
                'section[data-bv-show="reviews"]',
                '[data-testid="reviews-section"]',
                "#reviews-container",
                ".reviews-wrapper",
                ".bv-secondary-summary-container",
                '[class*="review"]',
                ".reviews-section",
            ]

            review_host_element = None
            for selector in shadow_host_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.count() > 0:
                        review_host_element = element
                        logging.info(f"Found review host with selector: {selector}")
                        break
                except Exception as e:
                    logging.error(
                        f"Error finding review host element with selector {selector}: {e}"
                    )
                    continue

            if not review_host_element:
                logging.warning("No review host element found")
                return 0

            review_item_selectors = [
                ".bv-content-item",
                ".review-item",
                ".review-container",
                '[data-testid="review"]',
                ".review",
                ".bv-content-review",
            ]

            review_elements = None
            for selector in review_item_selectors:
                try:
                    elements = review_host_element.locator(selector)
                    count = elements.count()
                    if count > 0:
                        review_elements = elements
                        logging.info(f"Found {count} reviews with selector: {selector}")
                        break
                except Exception as e:
                    logging.error(
                        f"Error finding review elements with selector {selector}: {e}"
                    )
                    continue

            if not review_elements:
                logging.warning("No review elements found within host")
                return 0

            review_count = review_elements.count()
            successful_reviews = 0

            logging.info(f"Processing {review_count} reviews")

            for i in range(review_count):
                try:
                    review_elem = review_elements.nth(i)
                    review_elem.wait_for(timeout=5000)

                    author = self._extract_text_with_fallbacks(
                        review_elem,
                        [
                            ".bv-author",
                            ".review-author",
                            ".reviewer-name",
                            '[data-testid="reviewer"]',
                            ".bv-content-author",
                        ],
                    )

                    rating = self._extract_rating_with_fallbacks(review_elem)

                    review_text = self._extract_text_with_fallbacks(
                        review_elem,
                        [
                            ".bv-content-summary-body",
                            ".review-text",
                            ".review-content",
                            ".bv-content-summary",
                            '[data-testid="review-text"]',
                            ".bv-content-summary-body-text",
                        ],
                    )

                    review_date = self._extract_date_with_fallbacks(review_elem)

                    if author and rating > 0 and review_text:
                        # Add variant info to review text if available
                        if variant_info:
                            review_text = f"[{variant_info}] {review_text}"

                        self.save_review(
                            laptop, author, rating, review_text, review_date
                        )
                        successful_reviews += 1

                        if successful_reviews % 10 == 0:
                            self.db.commit()
                            logging.info(
                                f"Committed {successful_reviews} reviews to database"
                            )

                    if i % 5 == 0:
                        time.sleep(random.uniform(0.1, 0.3))

                except Exception as e:
                    logging.warning(f"Failed to process review {i+1}: {e}")
                    continue

            logging.info(
                f"Successfully scraped {successful_reviews} out of {review_count} reviews"
            )
            return successful_reviews

        except Exception as e:
            logging.error(f"Review scraping failed: {e}")
            return 0

    def _extract_text_with_fallbacks(self, element, selectors: list) -> str:
        """Try multiple selectors to extract text content."""
        for selector in selectors:
            try:
                text_elem = element.locator(selector).first
                if text_elem.count() > 0:
                    text = text_elem.inner_text(timeout=2000).strip()
                    if text:
                        return text
            except Exception as e:
                logging.error(f"Error extracting text with selector {selector}: {e}")
                continue
        return ""

    def _extract_rating_with_fallbacks(self, element) -> int:
        """Extract rating using multiple approaches."""
        rating_selectors = [
            (".bv-rating", "aria-label"),
            (".star-rating", "data-rating"),
            (".rating", "data-value"),
            (".stars", "title"),
            ('[data-testid="rating"]', "aria-label"),
            (".bv-content-rating", "aria-label"),
        ]

        for selector, attribute in rating_selectors:
            try:
                rating_elem = element.locator(selector).first
                if rating_elem.count() > 0:
                    rating_text = rating_elem.get_attribute(attribute, timeout=2000)
                    if rating_text:
                        rating_text = rating_text.lower()
                        if "out of" in rating_text:
                            return int(rating_text.split()[0])
                        elif "/" in rating_text:
                            return int(float(rating_text.split("/")[0]))
                        elif "stars" in rating_text or "star" in rating_text:
                            match = re.search(r"(\d+(?:\.\d+)?)", rating_text)
                            if match:
                                return int(float(match.group(1)))
            except Exception as e:
                logging.error(f"Error extracting rating with selector {selector}: {e}")
                continue

        text_selectors = [
            ".bv-rating",
            ".rating-value",
            ".star-rating",
            '[data-testid="rating-value"]',
        ]

        for selector in text_selectors:
            try:
                rating_elem = element.locator(selector).first
                if rating_elem.count() > 0:
                    rating_text = rating_elem.inner_text(timeout=2000).strip()
                    if rating_text and rating_text.replace(".", "").isdigit():
                        return int(float(rating_text))
            except Exception as e:
                logging.error(
                    f"Error extracting rating text with selector {selector}: {e}"
                )
                continue

        star_selectors = [
            ".star.filled, .star-filled",
            ".fa-star:not(.fa-star-o)",
            ".bv-rating-stars-on",
            '[class*="star-filled"]',
        ]

        for selector in star_selectors:
            try:
                filled_stars = element.locator(selector).count()
                if filled_stars > 0 and filled_stars <= 5:
                    return filled_stars
            except Exception as e:
                logging.error(
                    f"Error counting filled stars with selector {selector}: {e}"
                )
                continue

        return 0

    def _extract_date_with_fallbacks(self, element):
        """Extract review date if available."""
        date_selectors = [
            ".bv-content-datetime",
            ".review-date",
            ".date",
            '[data-testid="review-date"]',
            ".bv-content-datetime-stamp",
        ]

        for selector in date_selectors:
            try:
                date_elem = element.locator(selector).first
                if date_elem.count() > 0:
                    date_text = date_elem.inner_text(timeout=2000).strip()
                    if date_text:
                        try:
                            from dateutil.parser import parse

                            return parse(date_text)
                        except Exception as e:
                            logging.error(f"Error parsing date text '{date_text}': {e}")
            except Exception as e:
                logging.error(
                    f"Error finding date element with selector {selector}: {e}"
                )
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

    @staticmethod
    def _parse_price(price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        try:
            clean = re.sub(r"[^\d.]", "", price_text.replace(",", ""))
            if clean:
                return float(clean)
        except ValueError:
            pass
        return None


class LenovoScraper(MultiBrandScraperBase):
    """Lenovo-specific scraper for direct product pages."""

    def scrape_comprehensive(self, laptop: Laptop):
        """Comprehensive Lenovo scraping."""
        html = self.fetch_page_advanced(laptop.product_page_url)
        if not html:
            logging.error(f"Failed to fetch Lenovo page for {laptop.full_model_name}")
            return

        self._scrape_price_playwright(laptop)
        reviews_scraped = self.scrape_all_reviews_shadow_dom(laptop)
        logging.info(
            f"Lenovo - Total reviews scraped for {laptop.full_model_name}: {reviews_scraped}"
        )

    def _scrape_price_playwright(self, laptop: Laptop):
        """Extract Lenovo price using Playwright."""
        price_selectors = [
            ".price-title",
            ".price-current",
            ".price",
            '[data-testid="price"]',
            ".pricing-current-price",
        ]

        for selector in price_selectors:
            try:
                price_elem = self.page.locator(selector).first
                if price_elem.is_visible():
                    price_text = price_elem.inner_text()
                    price = self._parse_price(price_text)
                    if price:
                        availability = self._check_lenovo_availability()
                        self.save_price_snapshot(
                            laptop, price, availability=availability
                        )
                        return
            except Exception as e:
                logging.debug(f"Lenovo price selector {selector} failed: {e}")
                continue

        logging.warning(f"Could not extract Lenovo price for {laptop.full_model_name}")

    def _check_lenovo_availability(self) -> str:
        """Check Lenovo product availability."""
        availability_selectors = [
            ".merchandising_flag_normal",
            ".availability-status",
            "[data-testid='availability']",
            ".stock-status",
        ]

        for selector in availability_selectors:
            try:
                avail_elem = self.page.locator(selector).first
                if avail_elem.count() > 0:
                    avail_text = avail_elem.inner_text().lower()
                    if any(
                        phrase in avail_text
                        for phrase in ["out of stock", "unavailable", "sold out"]
                    ):
                        return "Out of Stock"
                    elif any(
                        phrase in avail_text
                        for phrase in ["in stock", "available", "ready to ship"]
                    ):
                        return "In Stock"
            except Exception as e:
                logging.error(
                    f"Error checking Lenovo availability with selector {selector}: {e}"
                )
                continue

        return "In Stock"


class HPScraper(MultiBrandScraperBase):
    """HP-specific scraper handling both direct pages and collection pages."""

    def scrape_comprehensive(self, laptop: Laptop):
        """Comprehensive HP scraping with variant detection."""
        html = self.fetch_page_advanced(laptop.product_page_url)
        if not html:
            logging.error(f"Failed to fetch HP page for {laptop.full_model_name}")
            return

        # Check if this is HP ProBook 440 (collection page) or direct page
        if "probook-440" in laptop.product_page_url.lower():
            self._scrape_hp_collection(laptop)
        else:
            self._scrape_hp_direct(laptop)

    def _scrape_hp_direct(self, laptop: Laptop):
        """Scrape HP direct product page (like ProBook 450)."""
        logging.info(f"Scraping HP direct page: {laptop.full_model_name}")

        self._scrape_hp_price(laptop)
        reviews_scraped = self.scrape_all_reviews_shadow_dom(laptop)
        logging.info(
            f"HP Direct - Total reviews scraped for {laptop.full_model_name}: {reviews_scraped}"
        )

    def _scrape_hp_collection(self, laptop: Laptop):
        """Scrape HP ProBook 440 collection page with multiple variants."""
        logging.info(f"Scraping HP collection page: {laptop.full_model_name}")

        # Find all variant links/tiles on the page
        variant_selectors = [
            ".product-tile a",
            ".configuration-option a",
            ".product-card a",
            "[data-testid='product-link']",
            ".tile-link",
            "a[href*='probook-440']",
        ]

        variant_links = []
        for selector in variant_selectors:
            try:
                elements = self.page.locator(selector)
                count = elements.count()
                if count > 0:
                    logging.info(
                        f"Found {count} potential variants with selector: {selector}"
                    )
                    for i in range(count):
                        href = elements.nth(i).get_attribute("href")
                        if href and "probook-440" in href.lower():
                            # Make absolute URL if relative
                            if href.startswith("/"):
                                href = f"https://www.hp.com{href}"
                            variant_links.append(href)
                    break
            except Exception as e:
                logging.debug(f"Variant selector {selector} failed: {e}")
                continue

        if not variant_links:
            logging.warning("No HP 440 variants found, trying fallback method")
            variant_links = self._find_hp_variants_fallback()

        # Remove duplicates
        variant_links = list(set(variant_links))
        logging.info(f"Found {len(variant_links)} unique HP 440 variants to scrape")

        total_reviews = 0
        for i, variant_url in enumerate(variant_links[:9]):  # Limit to 9 as mentioned
            try:
                logging.info(
                    f"Processing HP 440 variant {i+1}/{len(variant_links[:9])}"
                )

                # Navigate to variant page
                variant_html = self.fetch_page_advanced(variant_url)
                if variant_html:
                    # Extract variant configuration info
                    variant_info = self._extract_variant_info()

                    # Scrape price for this variant
                    self._scrape_hp_price(laptop, configuration_summary=variant_info)

                    # Scrape reviews for this variant
                    reviews = self.scrape_all_reviews_shadow_dom(laptop, variant_info)
                    total_reviews += reviews

                    # Delay between variants
                    time.sleep(random.uniform(5, 10))
                else:
                    logging.warning(f"Failed to fetch variant: {variant_url}")

            except Exception as e:
                logging.error(f"Error processing HP 440 variant {i+1}: {e}")
                continue

        logging.info(
            f"HP Collection - Total reviews scraped for {laptop.full_model_name}: {total_reviews}"
        )

    def _find_hp_variants_fallback(self) -> List[str]:
        """Fallback method to find HP 440 variants."""
        try:
            # Look for any links that might be variants
            all_links = self.page.locator("a").all()
            variant_links = []

            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if href and "hp.com" in href and "probook" in href.lower():
                        if href.startswith("/"):
                            href = f"https://www.hp.com{href}"
                        variant_links.append(href)
                except Exception as e:
                    logging.error(f"Error processing link {link}: {e}")
                    continue

            return variant_links
        except Exception as e:
            logging.error(f"Error finding HP 440 variants: {e}")
            return []

    def _extract_variant_info(self) -> str:
        """Extract configuration info for the current variant."""
        config_selectors = [
            ".config-summary",
            ".product-configuration",
            ".spec-summary",
            "[data-testid='configuration']",
            ".configuration-details",
            "h1, .product-title",
        ]

        for selector in config_selectors:
            try:
                config_elem = self.page.locator(selector).first
                if config_elem.count() > 0:
                    config_text = config_elem.inner_text().strip()
                    if config_text:
                        # Clean up and shorten the config text
                        config_text = config_text.replace("\n", " ").strip()
                        if len(config_text) > 100:
                            config_text = config_text[:100] + "..."
                        return config_text
            except Exception as e:
                logging.error(
                    f"Error extracting variant info with selector {selector}: {e}"
                )
                continue

        return "Variant"

    def _scrape_hp_price(self, laptop: Laptop, configuration_summary: str = None):
        """Extract HP price using Playwright."""
        price_selectors = [
            ".product-price",
            '[data-testid="price"]',
            ".price-current",
            ".price",
            ".pricing-display",
            ".product-pricing",
        ]

        for selector in price_selectors:
            try:
                price_elem = self.page.locator(selector).first
                if price_elem.is_visible():
                    price_text = price_elem.inner_text()
                    price = self._parse_price(price_text)
                    if price:
                        availability = self._check_hp_availability()
                        self.save_price_snapshot(
                            laptop,
                            price,
                            availability=availability,
                            configuration_summary=configuration_summary,
                        )
                        return
            except Exception as e:
                logging.debug(f"HP price selector {selector} failed: {e}")
                continue

        logging.warning(f"Could not extract HP price for {laptop.full_model_name}")

    def _check_hp_availability(self) -> str:
        """Check HP product availability."""
        availability_selectors = [
            ".availability-status",
            "[data-testid='availability']",
            ".stock-status",
            ".inventory-status",
        ]

        for selector in availability_selectors:
            try:
                avail_elem = self.page.locator(selector).first
                if avail_elem.count() > 0:
                    avail_text = avail_elem.inner_text().lower()
                    if any(
                        phrase in avail_text
                        for phrase in ["out of stock", "unavailable", "sold out"]
                    ):
                        return "Out of Stock"
                    elif any(
                        phrase in avail_text
                        for phrase in ["in stock", "available", "ready to ship"]
                    ):
                        return "In Stock"
            except Exception as e:
                logging.error(
                    f"Error checking HP availability with selector {selector}: {e}"
                )
                continue

        return "In Stock"


class ScrapingOrchestrator:
    """Main orchestrator that routes laptops to appropriate scrapers."""

    def __init__(self, db: Session):
        self.db = db

    def scrape_all_laptops(self):
        """Scrape all laptops in the database using appropriate scrapers."""
        logging.info("Starting comprehensive laptop scraping...")

        # Get all laptops from database
        laptops = self.db.query(Laptop).all()
        logging.info(f"Found {len(laptops)} laptops to scrape")

        # Group by brand for efficient scraping
        lenovo_laptops = [l for l in laptops if l.brand.lower() == "lenovo"]
        hp_laptops = [l for l in laptops if l.brand.lower() == "hp"]

        total_laptops_processed = 0
        total_reviews_scraped = 0

        # Scrape Lenovo laptops
        if lenovo_laptops:
            logging.info(f"Processing {len(lenovo_laptops)} Lenovo laptops...")
            with LenovoScraper(self.db) as lenovo_scraper:
                for i, laptop in enumerate(lenovo_laptops):
                    try:
                        logging.info(
                            f"Lenovo {i+1}/{len(lenovo_laptops)}: {laptop.full_model_name}"
                        )
                        lenovo_scraper.scrape_comprehensive(laptop)
                        total_laptops_processed += 1

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
                            f"Error scraping Lenovo {laptop.full_model_name}: {e}"
                        )
                        self.db.rollback()
                        continue

        # Scrape HP laptops
        if hp_laptops:
            logging.info(f"Processing {len(hp_laptops)} HP laptops...")
            with HPScraper(self.db) as hp_scraper:
                for i, laptop in enumerate(hp_laptops):
                    try:
                        logging.info(
                            f"HP {i+1}/{len(hp_laptops)}: {laptop.full_model_name}"
                        )
                        hp_scraper.scrape_comprehensive(laptop)
                        total_laptops_processed += 1

                        # Commit after each laptop
                        self.db.commit()

                        # Longer delay for HP (especially 440 series with multiple variants)
                        if i < len(hp_laptops) - 1:
                            delay = random.uniform(40, 80)
                            logging.info(
                                f"Waiting {delay:.1f}s before next HP laptop..."
                            )
                            time.sleep(delay)

                    except Exception as e:
                        logging.error(
                            f"Error scraping HP {laptop.full_model_name}: {e}"
                        )
                        self.db.rollback()
                        continue

        # Final summary
        total_reviews = self.db.query(Review).count()
        total_price_snapshots = self.db.query(PriceSnapshot).count()

        logging.info("=" * 60)
        logging.info("SCRAPING SUMMARY")
        logging.info("=" * 60)
        logging.info(f"Laptops processed: {total_laptops_processed}/{len(laptops)}")
        logging.info(f"Total reviews in database: {total_reviews}")
        logging.info(f"Total price snapshots in database: {total_price_snapshots}")
        logging.info("=" * 60)


def main():
    """Main entry point."""
    logging.info("=" * 60)
    logging.info("MULTI-BRAND LAPTOP SCRAPER")
    logging.info(
        "Supports: Lenovo (direct pages), HP ProBook 450 (direct), HP ProBook 440 (collection)"
    )
    logging.info("=" * 60)

    # Skip setup_test_data() - laptops already exist in database
    # setup_test_data()

    # Create database session
    db = SessionLocal()

    try:
        # Initialize and run orchestrator
        orchestrator = ScrapingOrchestrator(db)
        orchestrator.scrape_all_laptops()

    except Exception as e:
        logging.exception("Critical error during scraping")
        db.rollback()
    finally:
        db.close()

    logging.info("Script completed!")


if __name__ == "__main__":
    main()
