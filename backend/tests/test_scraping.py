# Enhanced version with better anti-bot evasion
import time
import random
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from fake_useragent import UserAgent


class EnhancedBotEvasion:
    def __init__(self):
        self.ua = UserAgent()
        self.session_cookies = {}

    def get_realistic_user_agent(self) -> str:
        """Get a realistic, recent user agent."""
        # Use specific, recent user agents that are less likely to be flagged
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(agents)


class EnhancedScraper:
    def __init__(self, db):
        self.db = db
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.evasion = EnhancedBotEvasion()

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
        """Setup browser with enhanced stealth."""
        self.browser = self.playwright.chromium.launch(
            headless=True,  # Try False if still failing
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--no-first-run",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor",
                "--user-agent=" + self.evasion.get_realistic_user_agent(),
                "--accept-lang=en-US,en;q=0.9",
            ],
        )

        viewport = {"width": 1366, "height": 768}  # Common resolution

        self.context = self.browser.new_context(
            user_agent=self.evasion.get_realistic_user_agent(),
            viewport=viewport,
            screen={"width": 1366, "height": 768},
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

        # Add enhanced stealth scripts
        self.context.add_init_script(
            """
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Add chrome runtime
            window.chrome = {
                runtime: {},
            };

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """
        )

        self.page = self.context.new_page()
        print("Enhanced browser setup complete")

    def fetch_with_enhanced_evasion(self, url: str) -> Optional[str]:
        """Enhanced fetching with better evasion."""
        try:
            print(f"Attempting to fetch: {url}")

            # Step 1: Navigate with longer timeout and different wait strategy
            self.page.goto(url, wait_until="load", timeout=120000)

            # Step 2: Wait for dynamic content
            time.sleep(random.uniform(3, 7))

            # Step 3: Simulate human behavior
            self._simulate_human_behavior()

            # Step 4: Wait for any remaining async content
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass  # Continue even if networkidle times out

            content = self.page.content()

            if len(content) < 1000:  # Likely blocked if too short
                print("Warning: Page content seems too short, possible blocking")
                return None

            print(f"Successfully fetched {len(content)} characters")
            return content

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

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

            # Random pause (reading time)
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error in behavior simulation: {e}")


# Test function for US-specific URLs
def test_us_urls():
    """Test fetching the specific US URLs from your database."""
    from backend.src.app.core.db import SessionLocal

    # Your exact US URLs
    test_urls = [
        {
            "name": "Lenovo ThinkPad E14 Gen 5 (Intel)",
            "url": "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-intel/len101t0064",
            "keywords": ["thinkpad", "e14", "intel", "price", "reviews"],
        },
        {
            "name": "Lenovo ThinkPad E14 Gen 5 (AMD)",
            "url": "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-amd/len101t0068?orgRef=https%253A%252F%252Fwww.google.com%252F&srsltid=AfmBOoqAS4HFde0cPIpvn4VZodEMsRkvV0akOcfFq_K6PXjuPX2CXlMV",
            "keywords": ["thinkpad", "e14", "amd", "price", "reviews"],
        },
        {
            "name": "HP ProBook 450 G10",
            "url": "https://www.hp.com/us-en/shop/pdp/hp-probook-450-156-inch-g10-notebook-pc-wolf-pro-security-edition-p-8l0e0ua-aba-1",
            "keywords": ["probook", "450", "g10", "price", "reviews"],
        },
        {
            "name": "HP ProBook 440 G11",
            "url": "https://www.hp.com/us-en/shop/mdp/pro-352502--1/probook-440",
            "keywords": [
                "probook",
                "440",
                "g11",
                "mdplist",
            ],  # mdpList for the collection page
        },
    ]

    db = SessionLocal()
    try:
        with EnhancedScraper(db) as scraper:
            results = []

            for i, laptop in enumerate(test_urls):
                print(f"\n--- Testing {laptop['name']} ---")

                content = scraper.fetch_with_enhanced_evasion(laptop["url"])

                if content:
                    print(f"✅ SUCCESS: Fetched {len(content)} characters")

                    # Check for expected content
                    content_lower = content.lower()
                    found_keywords = [
                        kw for kw in laptop["keywords"] if kw in content_lower
                    ]

                    if found_keywords:
                        print(
                            f"✅ Valid content detected. Found keywords: {found_keywords}"
                        )
                        results.append(
                            {
                                "name": laptop["name"],
                                "status": "SUCCESS",
                                "size": len(content),
                            }
                        )
                    else:
                        print(
                            f"⚠️  Content may be blocked. Expected keywords not found: {laptop['keywords']}"
                        )
                        results.append(
                            {
                                "name": laptop["name"],
                                "status": "PARTIAL",
                                "size": len(content),
                            }
                        )
                else:
                    print("❌ FAILED: Could not fetch page")
                    results.append(
                        {"name": laptop["name"], "status": "FAILED", "size": 0}
                    )

                # Wait between requests (especially important for US sites)
                if i < len(test_urls) - 1:
                    wait_time = random.uniform(15, 30)
                    print(f"Waiting {wait_time:.1f}s before next request...")
                    time.sleep(wait_time)

            # Summary
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)
            for result in results:
                status_emoji = (
                    "✅"
                    if result["status"] == "SUCCESS"
                    else "⚠️" if result["status"] == "PARTIAL" else "❌"
                )
                print(
                    f"{status_emoji} {result['name']}: {result['status']} ({result['size']} chars)"
                )

            success_count = len([r for r in results if r["status"] == "SUCCESS"])
            print(f"\nSuccessful fetches: {success_count}/{len(test_urls)}")

            if success_count >= 2:
                print("✅ Enough successful fetches to proceed with full scraping!")
            else:
                print("❌ May need more advanced techniques or alternative approach")

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_us_urls()
