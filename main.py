import os
import pprint
import argparse
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

app = Flask(__name__)

def passive_recon(target: str):
    print(f"[INFO] Starting passive reconnaissance for target: {target}")
    
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

    # Whois
    print("[INFO] Fetching WHOIS information...")
    whois_result = whois_fetcher.fetch_whois_from_url(target)
    result["whois_result"] = whois_result

    # DNS Info
    print("[INFO] Fetching DNS information...")
    dns_info = fetch_ip.fetch_ip_from_url(target)
    result["dns_info"] = dns_info

    # Subdomain Enumeration
    subdomains = []
    print("[INFO] Starting subdomain enumeration...")
    
    ## Subfinder
    print("[INFO] Running Subfinder...")
    subfinder_results = subfinder.run_subfinder(target)
    subdomains.extend(subfinder_results)
    
    ## Shodan
    print("[INFO] Running Shosubgo...")
    shosubgo_results = shosubgo.run_shosubgo(target, SHODAN_API_KEY)
    subdomains.extend(shosubgo_results)
    
    ## GitHub Subdomains
    print("[INFO] Searching for subdomains via GitHub...")
    github_subdomains_result = github_subdomains.run_gh_subdomains(target, GITHUB_SEARCH_TOKEN)
    subdomains.extend(github_subdomains_result)

    ## Wayback
    print("[INFO] Fetching subdomains and endpoints from Wayback Machine...")
    wayback_200_results = wayback.fetch_wayback_200(target)
    wayback_subdomains, wayback_endpoints = separate_subdomains_and_endpoints(wayback_200_results)
    subdomains.extend(wayback_subdomains)
    
    result["subdomains"] = list(set(subdomains))
    result["endpoints"] = list(set(wayback_endpoints))
    
    # SMAP Port Scan
    print("[INFO] Running SMAP port scan...")
    open_ports = smap.smap_scan(target)
    result["open_ports"] = open_ports
    
    print("[INFO] Passive reconnaissance completed.")
    return result


def active_recon(target: str):
    print(f"[INFO] Starting active reconnaissance for target: {target}")
    
    result = {
        "subdomains": None,
        "endpoints": None,
        "open_ports": None,
        "waf" : None
    }
    
    subdomains = []
    endpoints = []
    open_ports = []

    # Crawling
    print("[INFO] Starting crawling...")
    
    ## Katana
    print("[INFO] Running Katana for subdomain and endpoint discovery...")
    katana_results = katana.katana_scan(target)
    katana_subdomains, katana_endpoints = separate_subdomains_and_endpoints(katana_results)
    subdomains.extend(katana_subdomains)
    endpoints.extend(katana_endpoints)
    
    ## JS Endpoints
    print("[INFO] Extracting JS endpoints with LinkFinder...")
    linfinder_results = js_endpoints.linkfinder(target)
    endpoints.extend(linfinder_results)
    
    # NMAP Scan
    print("[INFO] Scanning Ports with NMAP...")
    open_ports = nmap_scan.scan_with_nmap(target)

    # Kullanılan teknolojilerin tespiti
    print("[INFO] Running wappalyzer...")
    wappalyzer = wappalyzer_runner.run_wappalyzer(target)
    # Yazılım ve WAF tespiti
    print("[INFO] Running wafw00f to identify WAF and CDN")
    waf = waf_scan.run_wafw00f(target)

    # Cloud Provider Check
    print("[TO BE DONE] Determine if the address belongs to a cloud provider.")
    print("[TO BE DONE] integrate CloudRecon (may take 2-3 hours without a ready database).")
    
    print("[INFO] Active reconnaissance completed.")
    
    # Tüm endpointleri birleştir ve temizle
    all_endpoints = []
    if katana_endpoints:
        all_endpoints.extend(katana_endpoints)
    if linfinder_results:
        all_endpoints.extend(linfinder_results)
    
    # Tekrarlanan endpointleri temizle
    result["endpoints"] = list(set(all_endpoints))
    result["subdomains"] = list(set(subdomains))
    result["open_ports"] = open_ports
    result["waf"] = waf
    result["wappalyzer"] = wappalyzer
    
    # Debug için endpoint sayısını yazdır
    print(f"[DEBUG] Total endpoints found: {len(result['endpoints'])}")
    print(f"[DEBUG] Katana endpoints: {len(katana_endpoints)}")
    print(f"[DEBUG] LinkFinder endpoints: {len(linfinder_results)}")
    
    return result



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="balpars.com", help="Target URL or domain")
    parser.add_argument("--no-gui", action="store_true", help="Disable Flask GUI")
    args = parser.parse_args()

    TARGET = args.url
    print(f"[INFO] Starting reconnaissance for target: {TARGET}")

    if not args.no_gui:
        app.run(host="0.0.0.0", port=5000)
        return

    # Eğer no-gui modundaysa terminal çıktısı verir:
    passive_result = passive_recon(TARGET)
    active_result = active_recon(TARGET)

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
            # Sonuçları al
            passive_result = passive_recon(target)
            active_result = active_recon(target)
            
            # Debug için sonuçları yazdır
            print("\n=== WEB UI RESULTS ===")
            print(f"Passive endpoints: {len(passive_result.get('endpoints', []))}")
            print(f"Active endpoints: {len(active_result.get('endpoints', []))}")
            print(f"Passive open ports: {len(passive_result.get('open_ports', []))}")
            print(f"Active open ports: {len(active_result.get('open_ports', []))}")
            print(f"Wappalyzer results: {active_result.get('wappalyzer')}")
            
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
