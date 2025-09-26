import time
import random
from playwright.sync_api import sync_playwright


class HPSpecificScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._setup_hp_specific_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _setup_hp_specific_browser(self):
        """Setup browser specifically for HP's anti-bot measures."""
        # Multiple strategies to try
        strategies = [
            self._setup_http1_strategy,
            self._setup_stealth_strategy,
            self._setup_mobile_strategy,
        ]

        for i, strategy in enumerate(strategies):
            try:
                print(f"Trying strategy {i+1}: {strategy.__name__}")
                strategy()
                self.page = self.context.new_page()
                print(f"Strategy {i+1} setup successful")
                return
            except Exception as e:
                print(f"Strategy {i+1} failed: {e}")
                if self.context:
                    self.context.close()
                if self.browser:
                    self.browser.close()
                continue

        raise Exception("All strategies failed")

    def _setup_http1_strategy(self):
        """Force HTTP/1.1 to avoid HTTP/2 detection."""
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-http2",
                "--disable-spdy",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            ],
        )

        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",  # No br (Brotli) which requires HTTP/2
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            },
        )

    def _setup_stealth_strategy(self):
        """Maximum stealth approach."""
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-setuid-sandbox",
                "--no-zygote",
                "--disable-gpu-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            permissions=["geolocation"],
            geolocation={
                "latitude": 39.9042,
                "longitude": -75.1642,
            },  # Philadelphia coordinates
        )

        # Add maximum stealth scripts
        self.context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({ query: () => Promise.resolve({ state: 'granted' }) })
            });
        """
        )

    def _setup_mobile_strategy(self):
        """Try mobile user agent - sometimes less restricted."""
        self.browser = self.playwright.chromium.launch(
            headless=True, args=["--no-sandbox"]
        )

        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
        )

    def test_hp_urls(self):
        """Test HP URLs with multiple fallback strategies."""
        hp_urls = [
            {
                "name": "HP ProBook 450 G10",
                "url": "https://www.hp.com/us-en/shop/pdp/hp-probook-450-156-inch-g10-notebook-pc-wolf-pro-security-edition-p-8l0e0ua-aba-1",
            },
            {
                "name": "HP ProBook 440 G11",
                "url": "https://www.hp.com/us-en/shop/mdp/pro-352502--1/probook-440",
            },
        ]

        results = []

        for laptop in hp_urls:
            print(f"\n--- Testing {laptop['name']} ---")

            success = False
            for attempt in range(3):  # Try multiple times per URL
                try:
                    print(f"Attempt {attempt + 1}")

                    # Navigate with different wait strategies
                    wait_strategies = ["load", "domcontentloaded", "networkidle"]
                    wait_strategy = wait_strategies[attempt % len(wait_strategies)]

                    self.page.goto(
                        laptop["url"], wait_until=wait_strategy, timeout=90000
                    )

                    # Random delay
                    time.sleep(random.uniform(2, 5))

                    # Check if we got content
                    content = self.page.content()
                    if len(content) > 1000:
                        print(f"✅ SUCCESS: Fetched {len(content)} characters")

                        # Check for HP-specific content
                        if any(
                            keyword in content.lower()
                            for keyword in ["probook", "hp.com", "price"]
                        ):
                            print("✅ Valid HP content detected")
                            results.append(
                                {
                                    "name": laptop["name"],
                                    "status": "SUCCESS",
                                    "size": len(content),
                                }
                            )
                            success = True
                            break
                        else:
                            print("⚠️ Content may be blocked")
                    else:
                        print(f"⚠️ Content too short: {len(content)} characters")

                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)[:100]}...")

                    # Wait before retry
                    if attempt < 2:
                        wait_time = (attempt + 1) * 10
                        print(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)

            if not success:
                results.append({"name": laptop["name"], "status": "FAILED", "size": 0})
                print("❌ All attempts failed")

            # Wait between URLs
            time.sleep(random.uniform(30, 60))

        return results


def test_hp_specific():
    """Main test function for HP-specific scraping."""
    print("Starting HP-specific scraping test...")

    with HPSpecificScraper() as scraper:
        results = scraper.test_hp_urls()

        print("\n" + "=" * 50)
        print("HP SCRAPING RESULTS")
        print("=" * 50)

        for result in results:
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(
                f"{status_icon} {result['name']}: {result['status']} ({result['size']} chars)"
            )

        success_count = len([r for r in results if r["status"] == "SUCCESS"])
        print(f"\nHP Success Rate: {success_count}/{len(results)}")

        if success_count > 0:
            print("🎉 HP scraping breakthrough achieved!")
        else:
            print("💡 Consider proxy services or alternative data sources")


if __name__ == "__main__":
    test_hp_specific()
