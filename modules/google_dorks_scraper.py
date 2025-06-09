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
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('google_dorks_scraper', 'modules/logs/google_dorks_scraper.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('google_dorks_scraper', 'logs/google_dorks_scraper.log')


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
    logger.debug("Cleaning up old screenshots before running Google Scraper")
    if os.path.exists(SCREENSHOTS_DIR):
        shutil.rmtree(SCREENSHOTS_DIR)
        os.makedirs(SCREENSHOTS_DIR, mode=0o777)

# --- Main Asynchronous Routine ---
async def main():
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Browser launch attempt {attempt + 1}/{max_retries}")

            driver = await uc.start(headless=False,
                browser_args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--proxy-server=http://127.0.0.1:3128',
                '--ignore-certificate-errors',
                '--allow-insecure-localhost',
                '--disable-blink-features=AutomationControlled'
                ])
            
            await driver.wait(3)
            logger.debug("Navigating to search page")
            tab = await driver.get("Chrome://new-tab-page")

            logger.debug("Waiting for 5 seconds")

            await driver.wait(5)

            search_boxes = await tab.find_all("Search Google", timeout=3)

            if not search_boxes:
                search_boxes = await tab.find_all("Google'da arayın", timeout=3)
            if not search_boxes:
                raise Exception("Search box not found")

            logger.debug(f"Possible search elements : {search_boxes}")

            search_box = search_boxes[0]

            await take_screenshot(tab, 0)

            logger.debug(f"Searching for: {SEARCH_QUERY}")
            await search_box.click()
            await search_box.send_keys(SEARCH_QUERY)
            await search_box.click()
            await take_screenshot(tab, 1)

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
                await take_screenshot(tab, page_number+1)
                
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

            logger.debug(f"Google Scraper Found {len(result_items)} results:")
            for item in result_items:
                logger.debug(f" - {item.title}: {item.url}")
            
            return result_items

        except Exception as e:
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} attempts failed: {str(e)}")
                return []

# --- Script Entry Point ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Google search scraper for dork automation."
    )

    cleanup_screenshots()

    parser.add_argument("-q", "--query", required=True, help="Search query")
    parser.add_argument("-p", "--page_limit", default="-1", help="Limit the page count in in google search.")
    args = parser.parse_args()
    SEARCH_QUERY = args.query
    PAGE_LIMIT = int(args.page_limit)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True, mode=0o777)
    results = uc.loop().run_until_complete(main())
    logger.debug(json.dumps([r.to_dict() for r in results], indent=2))

# --- Call This From the Main File ---

def google_scraper(query_list, page_limit=-1):
    start = time.time()
    logger.info(f"Starting Google dorks scan for queries: {query_list}")
    
    cleanup_screenshots()
    # Ensure screenshots directory exists
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True, mode=0o777)
    
    all_urls = []
    try:

        for lock in ("/tmp/.X0-lock", "/tmp/.X99-lock", "/tmp/.X11-unix/X0", "/tmp/.X11-unix/X99"):
            try: os.remove(lock)
            except: pass

        # Start virtual display
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        time.sleep(1)
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
    except Exception as e:
        logger.exception(e)
        return []
    finally:
        # Clean up virtual display
        display.stop()