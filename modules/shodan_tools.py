import mmh3
import requests
import codecs
import shodan
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('shodan_tools', 'modules/logs/shodan_tools.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('shodan_tools', 'logs/shodan_tools.log')


def get_favicon_hash(url):
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            favicon = codecs.encode(response.content, 'base64')
            hash_value = mmh3.hash(favicon)
            result = 'http.favicon.hash:' + str(hash_value)
            logger.debug(f"Favicon hash result: {result}")
            return result
        else:
            raise Exception("Favicon")
    except Exception as e:
        logger.exception(f'[ERROR] get_favicon_hash threw exception: {e}')

def get_favicon_url(site_url):
    if "http" not in site_url:
        site_url = "http://" + site_url

    favicon_url = site_url + '/favicon.ico'
    try:
        result = get_favicon_hash(favicon_url)
        logger.debug(f"Favicon URL result: {result}")
        return result
    except Exception as e:
        logger.exception(f'[ERROR] get_favicon_url threw exception: {e}')

    try:
        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        response = requests.get(site_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        icon_links = soup.find_all("link", rel=lambda x: x and 'icon' in x.lower())

        for icon_link in icon_links:
            icon_url = icon_link['href']
            full_icon_url = urljoin(base_url, icon_url)

            if base_url in full_icon_url:
                result = get_favicon_hash(full_icon_url)
                logger.debug(f"Favicon URL result: {result}")
                return result

        return None
    except requests.RequestException as e:
        return e
    return None

def api(favhash=None,use_api_key=False, api_key=None):
    try:
        if use_api_key:
            if api_key and favhash:
                key = shodan.Shodan(api_key)
                fields = ["timestamp", "ip_str", "port", "hostnames", "location", "org", "isp", "os", "timestamp", "domains", "asn", "title", "product", "version", "cpe", "cve", "tags", "hash", "transport", "ssl", "uptime", "link", "type", "info", "host", "device_type", "device", "telnet", "ssh", "ftp", "smtp", "service", "service_type", "banner"]
                #fields = ["ip_str", "port", "hostnames", "org", "isp", "asn", "os", "location", "domains", "product", "version", "cpe"]
                result = key.search(favhash, fields=fields, minify=False)
                logger.debug(f"Shodan API result: {json.dumps(result, indent=2)}")
            return result
    except Exception as e:
        logger.exception(f'[ERROR] Favicon hash threw exception: {e}')
        return None


def sub_osint(key, domain, ip=None):
    try:
        subdomain = domain
        api = shodan.Shodan(key)
        fields = ["timestamp", "ip_str", "port", "hostnames", "location", "org", "isp", "os", "domains", "asn", "title", "product", "version", "cpe", "cve", "tags", "hash", "transport", "ssl", "uptime", "link", "type", "info", "host", "device_type", "device", "telnet", "ssh", "ftp", "smtp", "service", "service_type", "banner"]
        #fields = ["ip_str", "port", "hostnames", "org", "isp", "asn", "os", "location", "domains", "product", "version", "cpe"]
        if ip!=None:
            results = api.search('hostname:' + subdomain + ' ip:' + ip, fields=fields, minify=False)
        else:
            results = api.search('hostname:' + subdomain, fields=fields, minify=False)
        logger.debug(f"Shodan sub_osint result: {json.dumps(results, indent=2)}")
        return results

    except Exception as e:
        logger.exception(f'[ERROR] Favicon hash threw exception: {e}')
        return None



if __name__ == "__main__":
    load_dotenv()
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

    fhash = get_favicon_url("python.org")
    logger.info(json.dumps(fhash,indent=4))
    fresult = api(fhash,True, SHODAN_API_KEY)
    sub_result = sub_osint(SHODAN_API_KEY, 'python.org')
    logger.info(json.dumps(fresult,indent=4))
    logger.info(json.dumps(sub_result,indent=4))

