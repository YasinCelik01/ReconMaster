import subprocess
import json
import time
from modules.log_helper import setup_logger

logger = setup_logger('fetch_ip', 'modules/logs/fetch_ip.log')


# DNS sorgusu yapan fonksiyon
def get_dns_info(domain,dns_server):

	try:
		result = subprocess.run(['dig', domain, '@' + dns_server, '+short'], capture_output=True, text=True)
		ip_addresses = result.stdout.strip().split('\n')

		dns_info = {
			"domain": domain,
			"ip_addresses": ip_addresses
		}

		return dns_info
	except Exception as e:
		logger.exception(f"[ERROR] fetch_ip.py : {e}")
		return 0


# Main fonksiyonundan çağrılacak

def fetch_ip_from_url(url,dns_server="8.8.8.8"):
	start = time.time()
	logger.info(f"Starting IP fetch for {url}")
	
	dns_info = get_dns_info(url,dns_server)
	
	end = time.time()
	duration = end - start
	logger.debug(f"IP fetch completed in {duration:.2f} seconds")
	
	return dns_info

if __name__ == "__main__":
	url = "python.org"
	result = fetch_ip_from_url(url)
	logger.info(json.dumps(result, default=str, indent=4))
