"""
Debug tool to find correct selectors on Lenovo pages
"""

import time
import random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re


class LenovoSelectorDebugger:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

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
        """Setup browser with working configuration."""
        self.browser = self.playwright.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )

        self.page = self.context.new_page()

    def debug_lenovo_page(self, url):
        """Debug a Lenovo page to find correct selectors."""
        print(f"Debugging Lenovo page: {url}")

        # Fetch the page
        self.page.goto(url, wait_until="load", timeout=120000)
        time.sleep(5)

        content = self.page.content()
        soup = BeautifulSoup(content, "html.parser")

        print(f"Page loaded successfully: {len(content)} characters")

        # Debug price selectors
        print("\n" + "=" * 50)
        print("DEBUGGING PRICE SELECTORS")
        print("=" * 50)

        price_keywords = ["price", "pricing", "cost", "usd", "$"]
        price_elements = []

        # Find elements containing price-related text
        for keyword in price_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                parent = elem.parent
                if parent and parent.name:
                    price_text = parent.get_text().strip()
                    if "$" in price_text or "USD" in price_text:
                        price_elements.append(
                            {
                                "text": price_text[:100],
                                "tag": parent.name,
                                "class": parent.get("class", []),
                                "id": parent.get("id", ""),
                            }
                        )

        print(f"Found {len(price_elements)} potential price elements:")
        for i, elem in enumerate(price_elements[:10]):  # Show first 10
            print(f"{i+1}. Text: {elem['text']}")
            print(f"   Tag: <{elem['tag']}> Class: {elem['class']} ID: {elem['id']}")
            print()

        # Debug review selectors
        print("=" * 50)
        print("DEBUGGING REVIEW SELECTORS")
        print("=" * 50)

        review_keywords = ["review", "rating", "star", "customer"]
        review_elements = []

        for keyword in review_keywords:
            elements = soup.find_all(class_=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                review_elements.append(
                    {
                        "tag": elem.name,
                        "class": elem.get("class", []),
                        "id": elem.get("id", ""),
                        "text": elem.get_text()[:100] if elem.get_text() else "",
                    }
                )

        print(f"Found {len(review_elements)} potential review elements:")
        for i, elem in enumerate(review_elements[:10]):  # Show first 10
            print(f"{i+1}. Tag: <{elem['tag']}> Class: {elem['class']}")
            print(f"   ID: {elem['id']} Text: {elem['text']}")
            print()

        # Look for specific patterns
        print("=" * 50)
        print("LOOKING FOR SPECIFIC PATTERNS")
        print("=" * 50)

        # Check for price patterns
        price_pattern = re.compile(r"\$[\d,]+\.?\d*")
        price_matches = price_pattern.findall(content)
        if price_matches:
            print(f"Found price patterns: {price_matches[:5]}")

        # Check for common review platforms
        review_platforms = ["bazaarvoice", "bv-", "reviews", "rating"]
        for platform in review_platforms:
            if platform in content.lower():
                print(f"Found review platform indicator: {platform}")

        # Save a portion of HTML for manual inspection
        print("\n" + "=" * 50)
        print("SAVING HTML SAMPLE")
        print("=" * 50)

        with open("lenovo_page_debug.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved full page HTML to: lenovo_page_debug.html")

        return {
            "price_elements": price_elements,
            "review_elements": review_elements,
            "price_matches": price_matches,
            "content_length": len(content),
        }


def main():
    """Debug both Lenovo URLs."""
    urls = [
        "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-intel/len101t0064",
        "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-amd/len101t0068",
    ]

    with LenovoSelectorDebugger() as debugger:
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*80}")
            print(f"DEBUGGING URL {i}/2")
            print(f"{'='*80}")

            result = debugger.debug_lenovo_page(url)

            if i < len(urls):
                print("Waiting 30s before next URL...")
                time.sleep(30)

    print("\n" + "=" * 80)
    print("DEBUGGING COMPLETE")
    print("=" * 80)
    print("Check the generated 'lenovo_page_debug.html' file for manual inspection")
    print("Use browser dev tools to find the correct price and review selectors")


if __name__ == "__main__":
    main()
