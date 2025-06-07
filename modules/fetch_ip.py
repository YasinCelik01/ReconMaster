import subprocess
import json
import time
try:
    from modules.log_helper import setup_logger
    logger = setup_logger('fetch_ip', 'modules/logs/fetch_ip.log')
except ModuleNotFoundError:
    from log_helper import setup_logger
    logger = setup_logger('fetch_ip', 'logs/fetch_ip.log')

def run_dig(query_type, domain, dns_server):
    try:
        result = subprocess.run(['dig', domain, '@' + dns_server, '+short', '-t', query_type], capture_output=True, text=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception as e:
        logger.exception(f"[ERROR] run_dig: {e}")
        return []

def get_dns_info(domain, dns_server):
    records = []

    # 1) Orijinal domain için A kayıtlarını al
    a_records = run_dig('A', domain, dns_server)
    for ip in a_records:
        ip = ip.strip()
        # Eğer IP formatındaysa ekle (basit kontrol)
        if ip and all(c.isdigit() or c == '.' for c in ip):
            records.append({
                "type": "A",
                "domain": domain,
                "ip": ip
            })

    # 2) CNAME varsa al
    cname_records = run_dig('CNAME', domain, dns_server)
    for cname_target in cname_records:
        cname_target = cname_target.strip().rstrip('.')  # Sonundaki nokta varsa kaldır
        # cname hedefi IP değil, domain olmalı
        if cname_target and not all(c.isdigit() or c == '.' for c in cname_target):
            records.append({
                "type": "CNAME",
                "source": domain,
                "target": cname_target
            })

            # 3) CNAME hedefi için A kayıtlarını al
            cname_a_records = run_dig('A', cname_target, dns_server)
            for ip in cname_a_records:
                ip = ip.strip()
                if ip and all(c.isdigit() or c == '.' for c in ip):
                    records.append({
                        "type": "A",
                        "domain": cname_target,
                        "ip": ip
                    })

    return {
        "domain": domain,
        "records": records
    }

def fetch_ip_from_url(url, dns_server="8.8.8.8"):
    start = time.time()
    logger.info(f"Starting IP fetch for {url}")

    dns_info = get_dns_info(url, dns_server)

    end = time.time()
    duration = end - start
    logger.debug(f"IP fetch completed in {duration:.2f} seconds")
    logger.debug(f"DNS info found: {json.dumps(dns_info, default=str, indent=4)}")

    return dns_info

if __name__ == "__main__":
    url = "eme.eng.ankara.edu.tr"
    result = fetch_ip_from_url(url)
    logger.info(json.dumps(result, default=str, indent=4))
