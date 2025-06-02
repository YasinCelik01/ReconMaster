import whois
import tldextract
import json
import time
from urllib.parse import urlparse
from modules.log_helper import setup_logger

logger = setup_logger('whois_fetcher', 'modules/logs/whois_fetcher.log')

def extract_domain(url):
    
	try:
		parsed_url = urlparse(url)
		if not parsed_url.scheme:
			url = "http://" + url
		parsed_url = urlparse(url)

		domain = tldextract.extract(parsed_url.netloc)
		return f"{domain.domain}.{domain.suffix}"
	except Exception as e:
		logger.exception("f[ERROR] extracting domain: {e}")
		return None

def get_whois_info(domain):
	try:
		w = whois.whois(domain)
		return w
	except Exception as e:
		logger.exception("f[ERROR] fetching WHOIS information: {e}")
		return None
        
#main dosyasından çağrılacak fonksiyon
def fetch_whois_from_url(url):
	start = time.time()
	logger.info(f"Starting WHOIS fetch for {url}")
	
	domain = extract_domain(url)
	whois_info = get_whois_info(domain)
	
	end = time.time()
	duration = end - start
	logger.debug(f"WHOIS fetch completed in {duration:.2f} seconds")
	
	return(json.dumps(whois_info, default=str, indent=4))

if __name__ == "__main__":
	logger.info(whois.__file__)
	url = "python.org"
	domain = extract_domain(url)
	logger.info(f"Extracted domain: {domain}")
	result = fetch_whois_from_url(url)
	logger.info(result)
	
