import subprocess
import json
import re

# DNS sorgusu yapan fonksiyon
def get_dns_info(domain,dns_server):

	result = subprocess.run(['dig', domain, '@' + dns_server, '+short'], capture_output=True, text=True)

	ip_addresses = result.stdout.strip().split('\n')

	dns_info = {
		"domain": domain,
		"ip_addresses": ip_addresses
	}

	return dns_info

# Main fonksiyonundan çağrılacak

def fetch_ip_from_url(url,dns_server="8.8.8.8"):

	dns_info = get_dns_info(url,dns_server)
    
	return dns_info

if __name__ == "__main__":
	url = "python.org"
	result = fetch_ip_from_url(url)
	print(json.dumps(result, default=str, indent=4))
