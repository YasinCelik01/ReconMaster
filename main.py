import os
import pprint
import argparse
import time
import concurrent.futures
import json
from datetime import datetime
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
from modules import telegram_bot


logger = setup_logger('main', 'modules/logs/main.log')

app = Flask(__name__)

def passive_recon(target: str, modules: list[str]):
    start = time.time()
    logger.info(f"Starting passive reconnaissance for target: {target} with modules: {modules}")
    result = { "whois_result": [], "dns_info": [], "subdomains": [], "endpoints": [], "open_ports": [] }
    load_dotenv()

    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
    GITHUB_SEARCH_TOKEN = os.getenv("GITHUB_SEARCH_TOKEN")

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        # Schedule only selected modules
        if 'whois' in modules:
            futures['whois'] = executor.submit(whois_fetcher.fetch_whois_from_url, target)
        if 'dns' in modules:
            futures['dns'] = executor.submit(fetch_ip.fetch_ip_from_url, target)
        if 'subfinder' in modules:
            futures['subfinder'] = executor.submit(subfinder.run_subfinder, target)
        if 'shosubgo' in modules:
            futures['shosubgo'] = executor.submit(shosubgo.run_shosubgo, target, SHODAN_API_KEY)
        if 'github' in modules:
            futures['github'] = executor.submit(github_subdomains.run_gh_subdomains, target, GITHUB_SEARCH_TOKEN)
        if 'wayback' in modules:
            futures['wayback'] = executor.submit(wayback.fetch_wayback_200, target)
        if 'smap' in modules:
            futures['smap'] = executor.submit(smap.smap_scan, target)
        if 'googledorks' in modules:
            futures['googledorks'] = executor.submit(google_dorks_scraper.google_scraper, [f"site:{target}"])

        # Collect results
        if 'whois' in futures:
            result['whois_result'] = futures['whois'].result()
        if 'dns' in futures:
            result['dns_info'] = futures['dns'].result()
        subdomains = []
        if 'subfinder' in futures:
            subdomains.extend(futures['subfinder'].result())
        if 'shosubgo' in futures:
            subdomains.extend(futures['shosubgo'].result())
        if 'github' in futures:
            subdomains.extend(futures['github'].result())
        endpoints = []
        if 'wayback' in futures:
            wb = futures['wayback'].result()
            wb_sub, wb_end = separate_subdomains_and_endpoints(wb)
            subdomains.extend(wb_sub)
            endpoints.extend(wb_end)
        if 'googledorks' in futures:
            gd = futures['googledorks'].result()
            gd_sub, gd_end = separate_subdomains_and_endpoints(gd)
            subdomains.extend(gd_sub)
            endpoints.extend(gd_end)
        if 'smap' in futures:
            result['open_ports'] = futures['smap'].result()
        # Finalize lists
        result['subdomains'] = list(set(subdomains))
        result['endpoints'] = list(set(endpoints))

    end = time.time()
    logger.info(f"Passive recon completed in {end-start:.2f}s")
    return result


def active_recon(target: str, modules: list[str]):
    start = time.time()
    logger.info(f"Starting active reconnaissance for {target} with modules: {modules}")
    result = {"subdomains": [], "endpoints": [], "open_ports": [], "waf": [], "wappalyzer": []}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        if 'katana' in modules:
            futures['katana'] = executor.submit(katana.katana_scan, target)
        if 'linkfinder' in modules:
            futures['linkfinder'] = executor.submit(js_endpoints.linkfinder, target)
        if 'nmap' in modules:
            futures['nmap'] = executor.submit(nmap_scan.scan_with_nmap, target)
        if 'wappalyzer' in modules:
            futures['wappalyzer'] = executor.submit(wappalyzer_runner.run_wappalyzer, target)
        if 'waf' in modules:
            futures['waf'] = executor.submit(waf_scan.run_wafw00f, target)

        endpoints = []
        if 'katana' in futures:
            ks, ke = separate_subdomains_and_endpoints(futures['katana'].result())
            result['subdomains'] = ks
            endpoints.extend(ke)
        if 'linkfinder' in futures:
            endpoints.extend(futures['linkfinder'].result())
        if 'nmap' in futures:
            result['open_ports'] = futures['nmap'].result()
        if 'wappalyzer' in futures:
            result['wappalyzer'] = futures['wappalyzer'].result()
        if 'waf' in futures:
            result['waf'] = futures['waf'].result()

        result['endpoints'] = list(set(endpoints))

    end = time.time()
    logger.info(f"Active recon completed in {end-start:.2f}s")
    return result

def save_results(target: str, passive_result: dict, active_result: dict):
    """Save reconnaissance results to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "results"
    
    # Create a sanitized filename from the target
    safe_target = target.replace("://", "_").replace("/", "_").replace(".", "_")
    filename = f"{results_dir}/{safe_target}_{timestamp}.json"
    
    # Create results directory with proper permissions
    os.makedirs(os.path.dirname(filename), exist_ok=True, mode=0o777)
    
    # Ensure directory has proper permissions
    if os.path.exists(results_dir):
        os.chmod(results_dir, 0o777)
    
    # Prepare the data to save
    data = {
        "target": target,
        "timestamp": timestamp,
        "passive_recon": passive_result,
        "active_recon": active_result
    }
    
    # Save to file with proper permissions
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    # Set file permissions to 666, so it's deletable from outside
    os.chmod(filename, 0o666)
    
    logger.info(f"Results saved to {filename}")
    return filename

def run_full_recon(target: str):
    """Run passive + active recon and return results + results file path"""
    logger.info(f"Starting full reconnaissance for target: {target}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        passive_future = executor.submit(passive_recon, target)
        active_future = executor.submit(active_recon, target)

        # Get passive result first
        passive_result = passive_future.result()
        subdomains = passive_result.get("subdomains", [])

        # Run HTTPX after passive recon
        if subdomains:
            httpx_future = executor.submit(httpx_runner.run_httpx, subdomains)
            httpx_result = httpx_future.result()
        else:
            logger.warning("No subdomains found from passive recon. Skipping HTTPX.")
            httpx_result = None

        # Attach HTTPX to passive result (optional)
        passive_result["httpx"] = httpx_result

        # Wait for active
        active_result = active_future.result()

    # Save results to file
    results_file = save_results(target, passive_result, active_result)

    # Send results via Telegram
    # telegram_bot.run_telegram_bot(results_file)

    return passive_result, active_result, results_file


def print_results(passive_result, active_result):
    logger.info("\n=== WEB UI RESULTS ===")
    logger.info(f"Passive endpoints: {len(passive_result.get('endpoints', []))}")
    logger.info(f"Active endpoints: {len(active_result.get('endpoints', []))}")
    logger.info(f"Passive open ports: {len(passive_result.get('open_ports', []))}")
    logger.info(f"Active open ports: {len(active_result.get('open_ports', []))}")
    logger.info(f"Wappalyzer results: {active_result.get('wappalyzer')}")

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

    # If in no-gui mode, provide terminal output:
    TARGET = args.url
    logger.info(f"Starting reconnaissance for target: {TARGET}")
    
    passive_result, active_result, results_file = run_full_recon(TARGET)

    # Debug için sonuçları yazdır
    print_results(passive_result, active_result)


# In your Flask route:
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target = request.form.get('url')
        # Get list of selected modules
        selected = request.form.getlist('modules')
        # Run recon with only selected modules
        passive = passive_recon(target, selected)
        active = active_recon(target, selected)
        return render_template('index.html', results={'passive': passive, 'active': active})
    return render_template('index.html')


if __name__ == "__main__":
    main()
