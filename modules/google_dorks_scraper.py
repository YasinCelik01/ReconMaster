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
import time
from modules.log_helper import setup_logger

logger = setup_logger('google_dorks_scraper', 'modules/logs/google_dorks_scraper.log')

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
    time.sleep(2)
    try:
        logger.info("Initializing Google Dorks scanner")
        driver = await uc.start(headless=False,  # Changed to False since we're using virtual display
                    browser_args=['--disable-web-security'],)

        await driver.wait(5)
        logger.debug("Navigating to search page")
        tab = await driver.get("Chrome://new-tab-page")
        await tab.find_all('*[src]', timeout=3)

        await take_screenshot(tab, "newtab")
        search_boxes = await tab.find_elements_by_text("Search Google or type a URL")

        if not search_boxes:
            search_boxes = await tab.find_elements_by_text("Google'da arayın veya URL'yi yazın")
        if not search_boxes:
            logger.error("Search box not found")
            return []
        search_box = search_boxes[0]
        logger.debug(f"Searching for: {SEARCH_QUERY}")
        await search_box.click()
        await search_box.send_keys(SEARCH_QUERY)
        await search_box.click()
        await take_screenshot(tab, "newtab_search_box")

        await driver.wait(3)
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
            logger.debug(f"Processing page {page_number}")
            
            # Take screenshot of current page
            await take_screenshot(tab, page_number)
            
            results = await tab.select_all("h3")
            if not results:
                logger.info("No results found")
                return []

            for r in results:
                r_url = r.parent.attrs.get("href", "")
                if r_url and not any(item.url == r_url for item in result_items):
                    result_items.append(ResultItem(r_url, r.text, ""))

            next_page = await tab.find_elements_by_text("Sonraki", tag_hint="span")

            if not next_page:
                next_page = await tab.find_elements_by_text("Next", tag_hint="span")

            if not next_page or "script" in str(next_page):
                logger.debug("Search completed")
                break

            next_page = next_page[0]
            page_number += 1

            if PAGE_LIMIT != -1 and page_number > PAGE_LIMIT:
                logger.debug(f"Reached page limit of {PAGE_LIMIT}")
                break

            await next_page.click()

        logger.info(f"Google Scraper Found {len(result_items)} results:")
        for item in result_items:
            logger.info(f" - {item.title}: {item.url}")
        
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
    logger.debug(json.dumps([r.to_dict() for r in results], indent=2))
    logger.debug("[INFO] Cleaning up screenshots")
    cleanup_screenshots()

# --- Call This From the Main File ---

def google_scraper(query_list, page_limit=-1):
    start = time.time()
    logger.info(f"Starting Google dorks scan for queries: {query_list}")
    
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
        
        end = time.time()
        duration = end - start
        logger.debug(f"Google dorks scan completed in {duration:.2f} seconds")
        
        return all_urls
    finally:
        # Clean up screenshots after scraping is done
        logger.debug("Cleaning up screenshots")
        cleanup_screenshots()