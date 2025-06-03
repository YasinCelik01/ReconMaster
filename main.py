import os
import pprint
import argparse
import time
import concurrent.futures
from dotenv import load_dotenv
from flask import Flask, render_template, request
from modules import whois_fetcher
from modules import fetch_ip
from modules import subfinder
from modules import shosubgo
from modules import github_subdomains
from modules import wayback
from modules.url_endpoint_filter import separate_subdomains_and_endpoints
from modules import smap
from modules import katana
from modules import js_endpoints
from modules import nmap_scan
from modules import waf_scan
from modules import wappalyzer_runner
from modules import google_dorks_scraper
from modules.log_helper import setup_logger

logger = setup_logger('main', 'modules/logs/main.log')

app = Flask(__name__)

def passive_recon(target: str):
    start = time.time()

    logger.info(f"Starting passive reconnaissance for target: {target}")
    
    result = {
        "whois_result": None,
        "dns_info": None,
        "subdomains": None,
        "endpoints": None,
        "open_ports": None
    }

    load_dotenv()    
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
    GITHUB_SEARCH_TOKEN = os.getenv("GITHUB_SEARCH_TOKEN")

    # Create a thread pool for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Submit tasks
        whois_future = executor.submit(whois_fetcher.fetch_whois_from_url, target)
        dns_future = executor.submit(fetch_ip.fetch_ip_from_url, target)
        subfinder_future = executor.submit(subfinder.run_subfinder, target)
        shosubgo_future = executor.submit(shosubgo.run_shosubgo, target, SHODAN_API_KEY)
        github_future = executor.submit(github_subdomains.run_gh_subdomains, target, GITHUB_SEARCH_TOKEN)
        wayback_future = executor.submit(wayback.fetch_wayback_200, target)
        smap_future = executor.submit(smap.smap_scan, target)
        google_dorks_future = executor.submit(google_dorks_scraper.google_scraper, [f"site:{target}"])

        # Get results as they complete
        result["whois_result"] = whois_future.result()
        result["dns_info"] = dns_future.result()
        
        # Collect subdomain results
        subdomains = []
        subdomains.extend(subfinder_future.result())
        subdomains.extend(shosubgo_future.result())
        subdomains.extend(github_future.result())
        
        # Get wayback results
        wayback_200_results = wayback_future.result()
        wayback_subdomains, wayback_endpoints = separate_subdomains_and_endpoints(wayback_200_results)
        subdomains.extend(wayback_subdomains)
        
        # Get other results
        result["open_ports"] = smap_future.result()
        google_dorks_results = google_dorks_future.result()
        
        result["subdomains"] = list(set(subdomains))
        result["endpoints"] = list(set(wayback_endpoints + google_dorks_results))
    
    logger.info("Passive reconnaissance completed.")
    end = time.time()
    logger.info(f"Time taken for passive recon was {end-start} seconds")
    return result


def active_recon(target: str):
    start = time.time()
    logger.info(f"Starting active reconnaissance for target: {target}")
    
    result = {
        "subdomains": None,
        "endpoints": None,
        "open_ports": None,
        "waf": None,
        "wappalyzer": None
    }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks
        katana_future = executor.submit(katana.katana_scan, target)
        linkfinder_future = executor.submit(js_endpoints.linkfinder, target)
        nmap_future = executor.submit(nmap_scan.scan_with_nmap, target)
        wappalyzer_future = executor.submit(wappalyzer_runner.run_wappalyzer, target)
        waf_future = executor.submit(waf_scan.run_wafw00f, target)

        # Get results
        katana_results = katana_future.result()
        katana_subdomains, katana_endpoints = separate_subdomains_and_endpoints(katana_results)
        linfinder_results = linkfinder_future.result()
        open_ports = nmap_future.result()
        wappalyzer = wappalyzer_future.result()
        waf = waf_future.result()

        # Combine and clean up results
        all_endpoints = []
        if katana_endpoints:
            all_endpoints.extend(katana_endpoints)
        if linfinder_results:
            all_endpoints.extend(linfinder_results)
        
        result["endpoints"] = list(set(all_endpoints))
        result["subdomains"] = list(set(katana_subdomains))
        result["open_ports"] = open_ports
        result["waf"] = waf
        result["wappalyzer"] = wappalyzer

    logger.info("Active reconnaissance completed.")

    
    end = time.time()
    logger.info(f"Time taken for the active recon was {end-start} seconds")
    return result



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Target URL or domain (required in no-gui mode)")
    parser.add_argument("--no-gui", action="store_true", help="Disable Flask GUI")
    args = parser.parse_args()

    if args.no_gui and not args.url:
        parser.error("--url is required when running in no-gui mode")

    if not args.no_gui:
        app.run(host="0.0.0.0", port=5000)
        return

    # Eğer no-gui modundaysa terminal çıktısı verir:
    TARGET = args.url
    logger.info(f"Starting reconnaissance for target: {TARGET}")
    
    # Run both scans in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        passive_future = executor.submit(passive_recon, TARGET)
        active_future = executor.submit(active_recon, TARGET)
        
        # Get results
        passive_result = passive_future.result()
        active_result = active_future.result()

    import pprint
    pp = pprint.PrettyPrinter(depth=4)
    print("\n=== PASSIVE RECON RESULTS ===")
    pp.pprint(passive_result)
    print("\n=== ACTIVE RECON RESULTS ===")
    pp.pprint(active_result)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target = request.form.get('url')
        if target:
            # Run both scans in parallel
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                passive_future = executor.submit(passive_recon, target)
                active_future = executor.submit(active_recon, target)
                
                # Get results
                passive_result = passive_future.result()
                active_result = active_future.result()
            end = time.time()
            logger.info(f"Time taken total was {end-start} seconds")
            # Debug için sonuçları yazdır
            logger.info("\n=== WEB UI RESULTS ===")
            logger.info(f"Passive endpoints: {len(passive_result.get('endpoints', []))}")
            logger.info(f"Active endpoints: {len(active_result.get('endpoints', []))}")
            logger.info(f"Passive open ports: {len(passive_result.get('open_ports', []))}")
            logger.info(f"Active open ports: {len(active_result.get('open_ports', []))}")
            logger.info(f"Wappalyzer results: {active_result.get('wappalyzer')}")
            
            # Sonuçları düzenle
            if passive_result.get('endpoints'):
                passive_result['endpoints'] = list(set(passive_result['endpoints']))
            if active_result.get('endpoints'):
                active_result['endpoints'] = list(set(active_result['endpoints']))
            if passive_result.get('subdomains'):
                passive_result['subdomains'] = list(set(passive_result['subdomains']))
            if active_result.get('subdomains'):
                active_result['subdomains'] = list(set(active_result['subdomains']))
            
            # Boş listeleri None yerine boş liste olarak ayarla
            if not passive_result.get('open_ports'):
                passive_result['open_ports'] = []
            if not active_result.get('open_ports'):
                active_result['open_ports'] = []
            
            # Sonuçları template'e gönder
            return render_template('index.html', results={
                'passive': passive_result,
                'active': active_result
            })
    return render_template('index.html')

if __name__ == "__main__":
    main()
