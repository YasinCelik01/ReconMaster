import os
import pprint
import argparse
import time
import concurrent.futures
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from modules import (whois_fetcher, fetch_ip, subfinder, shosubgo,
                     github_subdomains, wayback, smap, katana,
                     js_endpoints, nmap_scan, waf_scan,
                     wappalyzer_runner, google_dorks_scraper,
                     telegram_bot, url_endpoint_filter, log_helper)


logger = log_helper.setup_logger('main', 'modules/logs/main.log')

app = Flask(__name__)

# Tüm modüller ve label’ları
# Bu listeyi terminal modunda modül devre dışı bırakmak için kullanıyoruz
ALL_MODULES = [
    ('whois',       'WHOIS'),
    ('dns',         'DNS'),
    ('subfinder',   'Subfinder'),
    ('shosubgo',    'ShosubGo'),
    ('github',      'GitHub Subdomains'),
    ('wayback',     'Wayback'),
    ('smap',        'Shodan Port Scan'),
    ('googledorks','Google Dorks'),
    ('katana',      'Katana'),
    ('linkfinder',  'JS LinkFinder'),
    ('nmap',        'Nmap'),
    ('wappalyzer',  'Wappalyzer'),
    ('waf',         'WAFW00f'),
    ('httpx',       'HTTPX Scan'),
    ('telegram',    'Telegram Notification'),
]
RESULTS_DIR = 'results'


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

        while True:
            not_done = [name for name, fut in futures.items() if not fut.done()]
            if not not_done:
                break
            logger.info(f"Still Running Passive Recon Modules: {', '.join(not_done)}")
            time.sleep(5)

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
            wb_sub, wb_end = url_endpoint_filter.separate_subdomains_and_endpoints(wb)
            subdomains.extend(wb_sub)
            endpoints.extend(wb_end)
        if 'googledorks' in futures:
            gd = futures['googledorks'].result()
            gd_sub, gd_end = url_endpoint_filter.separate_subdomains_and_endpoints(gd)
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
        
        # 2) Beş saniyede bir hâlâ bitmemiş görevleri logla
        while True:
            not_done = [name for name, fut in futures.items() if not fut.done()]
            if not not_done:
                break
            logger.info(f"Still Running Active Recon Modules: {', '.join(not_done)}")
            time.sleep(5)


        endpoints = []
        if 'katana' in futures:
            ks, ke = url_endpoint_filter.separate_subdomains_and_endpoints(futures['katana'].result())
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

def run_full_recon(target: str, modules: list[str]):
    load_dotenv()
    # paralel passive + active
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        passive_future = executor.submit(passive_recon, target, modules)
        active_future  = executor.submit(active_recon,  target, modules)

        passive_result = passive_future.result()
        active_result  = active_future.result()

    # post-recon: HTTPX
    if 'httpx' in modules and passive_result.get('subdomains'):
        try:
            from modules import httpx_runner
            passive_result['httpx'] = httpx_runner.run_httpx(passive_result['subdomains'])
        except Exception:
            logger.exception("HTTPX scan failed")

    # sonuçları kaydet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe      = target.replace('://','_').replace('.','_').replace('/','_')
    path      = f"{RESULTS_DIR}/{safe}_{timestamp}.json"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(path, 'w') as f:
        json.dump({
            'target': target,
            'timestamp': timestamp,
            'passive_recon': passive_result,
            'active_recon':  active_result
        }, f, indent=2)
    os.chmod(path, 0o666)
    logger.info(f"Results saved to {path}")

    # Telegram
    if 'telegram' in modules:
        try:
            telegram_bot.run_telegram_bot(path)
        except Exception:
            logger.exception("Telegram notification failed")

    return passive_result, active_result, path



def print_results(passive_result, active_result):
    logger.info("\n=== WEB UI RESULTS ===")
    logger.info(f"Passive endpoints: {len(passive_result.get('endpoints', []))}")
    logger.info(f"Active endpoints: {len(active_result.get('endpoints', []))}")
    logger.info(f"Passive open ports: {len(passive_result.get('open_ports', []))}")
    logger.info(f"Active open ports: {len(active_result.get('open_ports', []))}")
    logger.info(f"Wappalyzer results: {active_result.get('wappalyzer')}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url',    help='Target URL/domain')
    p.add_argument('--no-gui', action='store_true', help='Terminal mode')
    args = p.parse_args()

    # --- Terminal Mode ---
    if args.no_gui:
        target = args.url or input("Target URL/domain: ").strip()
        # Modülleri listele, disable için numara al
        print("Modüller (devre dışı bırakmak için numarayı yazın, virgülle ayırın):")
        for i,(key,label) in enumerate(ALL_MODULES,1):
            print(f"{i:2d}. {label}")
        disabled = input(">> ").split(',')
        disabled = {int(x) for x in disabled if x.isdigit() and 1<=int(x)<=len(ALL_MODULES)}
        selected = [k for i,(k,_) in enumerate(ALL_MODULES,1) if i not in disabled]

        passive, active, file = run_full_recon(target, selected)
        print(f"\nSonuç kaydedildi: {file}")
        print(f"Passive subdomains: {len(passive.get('subdomains',[]))}")
        print(f"Active open ports: {len(active.get('open_ports',[]))}")
        return

    # --- GUI Mode ---
    app.run(host='0.0.0.0', port=5000)


@app.route('/', methods=['GET', 'POST'])
def index():
    # --- Dosya listesi için header_timestamp'i önce boş atıyoruz ---
    header_timestamp = ''

    # 1) results klasöründeki JSON dosyalarını oku ve display metni hazırla
    files = []
    for fname in os.listdir(RESULTS_DIR):
        if not fname.endswith('.json'):
            continue

        parts = fname.rsplit('_', 2)
        if len(parts) == 3:
            base, date_str, time_str = parts
            time_str = time_str.replace('.json', '')
            try:
                dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                display = f"{base} {dt.strftime('%H:%M %d/%m/%Y')}"
            except ValueError:
                dt = None
                display = fname
        else:
            dt = None
            display = fname

        files.append({
            'name':    fname,
            'display': display,
            'dt':       dt or datetime.min
        })

    # 2) Tarih/saat bilgisini de dikkate alarak en yeni en önde sıralama
    files.sort(key=lambda x: x['dt'], reverse=True)

    # 3) POST: yeni scan tetikleme
    if request.method == 'POST':
        target  = request.form['url']
        modules = request.form.getlist('modules')
        passive, active, results_file = run_full_recon(target, modules)
        return redirect(url_for('index', results_file=os.path.basename(results_file)))

    # 4) GET: ?results_file parametresi varsa JSON'u oku ve header_timestamp ayarla
    sel = request.args.get('results_file')
    results = None
    if sel:
        # Dropdown'dan seçilen dosyanın display metnini bul
        for f in files:
            if f['name'] == sel:
                header_timestamp = f['display']
                break

        # JSON'u yükle
        with open(os.path.join(RESULTS_DIR, sel), 'r') as jf:
            data = json.load(jf)
        results = {
            'passive': data.get('passive_recon') or data.get('passive'),
            'active':  data.get('active_recon')  or data.get('active')
        }

    # 5) Şablonu render et
    return render_template(
        'index.html',
        files=files,
        results=results,
        header_timestamp=header_timestamp
    )


if __name__=='__main__':
    main()
