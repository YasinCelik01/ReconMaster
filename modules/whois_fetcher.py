import whois
import tldextract
import json
from urllib.parse import urlparse

def extract_domain(url):
    
	try:
		parsed_url = urlparse(url)
		if not parsed_url.scheme:
			url = "http://" + url
		parsed_url = urlparse(url)

		domain = tldextract.extract(parsed_url.netloc)
		return f"{domain.domain}.{domain.suffix}"
	except Exception as e:
		print(f"Error extracting domain: {e}")
		return None

def get_whois_info(domain):
	try:
		w = whois.whois(domain)
		return w
	except Exception as e:
		print(f"Error fetching WHOIS information: {e}")
		return None
        
#main dosyasından çağrılacak fonksiyon
def fetch_whois_from_url(url):
	domain = extract_domain(url)
	whois_info = get_whois_info(domain)
	return(json.dumps(whois_info, default=str, indent=4))

if __name__ == "__main__":
	print(whois.__file__)
	url = "python.org"
	domain = extract_domain(url)
	print(f"Extracted domain: {domain}")
	result = fetch_whois_from_url(url)
	print(result)
	
