#main.py
import asyncio
import nodriver as uc
import json
import datetime
import re
import os
import random
import requests
import time
import argparse
from pyvirtualdisplay import Display
import shutil

# --- Classes and Global Variables ---

class ResultItem:
    def __init__(self, url, title, desc):
        self.url = url
        self.title = title
        self.desc = desc

    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'desc': self.desc
        }

SEARCH_QUERY = ""
PAGE_LIMIT = -1
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "chrome_screenshots")

async def take_screenshot(tab, page_number):
    """Take a screenshot and save it with a timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"page_{page_number}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    await tab.save_screenshot(filepath)
    return filepath

def cleanup_screenshots():
    """Remove all screenshots from the directory"""
    if os.path.exists(SCREENSHOTS_DIR):
        shutil.rmtree(SCREENSHOTS_DIR)
        os.makedirs(SCREENSHOTS_DIR)

# --- Main Asynchronous Routine ---
async def main():
    # Start virtual display
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    try:
        print("[INFO] Initializing the web driver for Google Dorks")
        driver = await uc.start(headless=False,  # Changed to False since we're using virtual display
                    browser_args=['--disable-web-security'],)

        await driver.wait(2)
        print("[INFO] Navigating to the New Tab Page")
        tab = await driver.get("Chrome://new-tab-page")
        print("[INFO] Waiting for elements to load")
        await tab.find_all('*[src]', timeout=3)

        await take_screenshot(tab, "newtab")
        print("[INFO] Locating the search box...")
        search_boxes = await tab.find_elements_by_text("Search Google or type a URL")

        if not search_boxes:
            search_boxes = await tab.find_elements_by_text("Google'da arayın veya URL'yi yazın")
        if not search_boxes:
            print("[ERROR] Search box not found!")
            return []
        search_box = search_boxes[0]
        print("[INFO] Clicking the search box and entering query")
        print("[INFO] Query is", SEARCH_QUERY)
        await search_box.click()
        await search_box.send_keys(SEARCH_QUERY)
        await search_box.click()
        await take_screenshot(tab, "newtab_search_box")

        print("[INFO] Pressing Enter to search")
        await driver.wait(2)
        await tab.send(uc.cdp.input_.dispatch_key_event(
            type_="rawKeyDown", key="Enter", code="Enter", windows_virtual_key_code=13))
        await tab.send(uc.cdp.input_.dispatch_key_event(
            type_="keyUp", modifiers=8, key="Enter", code="Enter", windows_virtual_key_code=13))

        # --- Extract search results ---

        result_items = []
        page_number = 1

        while True:
            x = random.randint(3, 5)
            await driver.wait(x)
            print(f"[INFO] Extracting titles and URLs from page {page_number}")
            
            # Take screenshot of current page
            await take_screenshot(tab, page_number)
            
            results = await tab.select_all("h3")
            if not results:
                print("[INFO] No results found!")
                return []

            for r in results:
                r_url = r.parent.attrs.get("href", "")
                if r_url and not any(item.url == r_url for item in result_items):
                    result_items.append(ResultItem(r_url, r.text, ""))

            print("[INFO] Looking for next page...")
            next_page = await tab.find_elements_by_text("Sonraki", tag_hint="span")

            if not next_page:
                next_page = await tab.find_elements_by_text("Next", tag_hint="span")

            if not next_page or "script" in str(next_page):
                print("[INFO] No next page found. Ending search.")
                break

            next_page = next_page[0]
            page_number += 1

            if PAGE_LIMIT != -1 and page_number > PAGE_LIMIT:
                print(f"[INFO] Page limit of {PAGE_LIMIT} reached.")
                break

            print("[INFO] Clicking next page")
            await next_page.click()

        print("[INFO] Search finished. Found results:")
        for item in result_items:
            print(f" - {item.title}: {item.url}")
        print(f"[INFO] Total results: {len(result_items)} in {page_number} pages")
        
        return result_items

    finally:
        # Clean up virtual display
        display.stop()


# --- Script Entry Point ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Google search scraper for dork automation."
    )

    parser.add_argument("-q", "--query", required=True, help="Search query")
    parser.add_argument("-p", "--page_limit", default="-1", help="Limit the page count in in google search.")
    args = parser.parse_args()
    SEARCH_QUERY = args.query
    PAGE_LIMIT = int(args.page_limit)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    results = uc.loop().run_until_complete(main())
    print(json.dumps([r.to_dict() for r in results], indent=2))
    print("[INFO] Cleaning up screenshots")
    cleanup_screenshots()

# --- Call This From the Main File ---

def google_scraper(query_list, page_limit=-1):
    # Ensure screenshots directory exists
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    all_urls = []
    try:
        for query in query_list:
            global SEARCH_QUERY, PAGE_LIMIT
            SEARCH_QUERY = query
            PAGE_LIMIT = page_limit
            results = uc.loop().run_until_complete(main())
            if results:
                all_urls.extend([r.url for r in results])
        return all_urls
    finally:
        # Clean up screenshots after scraping is done
        print("[INFO] Cleaning up screenshots")
        cleanup_screenshots()