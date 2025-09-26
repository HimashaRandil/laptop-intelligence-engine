"""
Debug script to understand why review extraction is failing
"""

import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re


def debug_lenovo_reviews():
    """Debug Lenovo review extraction step by step."""

    url = "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-intel/len101t0064"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible browser for debugging
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        page = context.new_page()

        print("Step 1: Loading page...")
        page.goto(url, wait_until="load", timeout=120000)
        time.sleep(5)

        print(f"Page loaded: {len(page.content())} characters")

        print("\nStep 2: Looking for Reviews tab...")

        # Try to find and click Reviews tab
        review_tab_selectors = [
            "text=Reviews",
            "[data-tab='reviews']",
            "a:has-text('Reviews')",
            ".tab:has-text('Reviews')",
        ]

        tab_found = False
        for selector in review_tab_selectors:
            try:
                tab = page.locator(selector)
                count = tab.count()
                print(f"  Selector '{selector}': {count} matches")

                if count > 0 and tab.first.is_visible():
                    print(f"  Clicking Reviews tab with selector: {selector}")
                    tab.first.click()
                    time.sleep(5)
                    tab_found = True
                    break

            except Exception as e:
                print(f"  Error with selector '{selector}': {e}")

        if not tab_found:
            print("  No Reviews tab found")

        print("\nStep 3: Analyzing page content for review elements...")

        # Get current page content
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")

        # Look for various review-related elements
        review_indicators = [
            "bv-content-item",
            "review-item",
            "review",
            "bv-",
            "rating",
            "star",
        ]

        print("Looking for elements containing review indicators:")
        for indicator in review_indicators:
            # Find by class
            by_class = soup.find_all(class_=re.compile(indicator, re.I))
            print(f"  Elements with class containing '{indicator}': {len(by_class)}")

            if len(by_class) > 0:
                for i, elem in enumerate(by_class[:3]):  # Show first 3
                    print(
                        f"    {i+1}. Tag: {elem.name}, Class: {elem.get('class', [])}"
                    )
                    text = elem.get_text()[:100].replace("\n", " ").strip()
                    print(f"       Text preview: {text}")

        print("\nStep 4: Using Playwright to count elements...")

        # Try different selectors with Playwright
        test_selectors = [
            ".bv-content-item",
            "[data-testid='review']",
            ".review-item",
            ".review",
            "[class*='bv-']",
            "[class*='review']",
        ]

        for selector in test_selectors:
            try:
                count = page.locator(selector).count()
                print(f"  Playwright selector '{selector}': {count} elements")

                if count > 0:
                    # Get text from first few elements
                    for i in range(min(count, 3)):
                        try:
                            elem = page.locator(selector).nth(i)
                            text = elem.inner_text()[:100].replace("\n", " ")
                            print(f"    Element {i+1} text: {text}")
                        except:
                            pass

            except Exception as e:
                print(f"  Error with selector '{selector}': {e}")

        print("\nStep 5: Looking for Load More buttons...")

        load_more_selectors = [
            "text=Load More",
            "button:has-text('Load More')",
            "a:has-text('Load More')",
            ".load-more",
        ]

        for selector in load_more_selectors:
            try:
                count = page.locator(selector).count()
                print(f"  Load More selector '{selector}': {count} buttons")

                if count > 0:
                    button = page.locator(selector).first
                    is_visible = button.is_visible()
                    print(f"    First button visible: {is_visible}")

            except Exception as e:
                print(f"  Error with selector '{selector}': {e}")

        print("\nStep 6: Saving page content for inspection...")

        # Save current page content
        with open("lenovo_reviews_debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("  Saved page content to: lenovo_reviews_debug.html")

        print("\nStep 7: Taking screenshot...")
        page.screenshot(path="lenovo_reviews_debug.png", full_page=True)
        print("  Saved screenshot to: lenovo_reviews_debug.png")

        # Keep browser open for manual inspection
        input("\nPress Enter to close browser and continue...")

        browser.close()


if __name__ == "__main__":
    debug_lenovo_reviews()
