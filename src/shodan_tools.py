import mmh3
import requests
import codecs
import shodan
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

def get_favicon_hash(url):
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            favicon = codecs.encode(response.content, 'base64')
            hash_value = mmh3.hash(favicon)
            return 'http.favicon.hash:' + str(hash_value)
        else:
            raise Exception("Favicon")
    except Exception as e:
        print(f'{e}')

def get_favicon_url(site_url):
    if "http" not in site_url:
        site_url = "http://" + site_url

    favicon_url = site_url + '/favicon.ico'
    try:
        return get_favicon_hash(favicon_url)
    except Exception as e:
        print(f'get_favicon_url threw exception: {e}')

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
                return get_favicon_hash(full_icon_url)

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
            return result
    except Exception as e:
        print(f' Favicon hash threw exception: {e}')
        return None


def sub_osint(key, domain, ip=None):
    try:
        SHODAN_API_KEY = key
        subdomain = domain
        api = shodan.Shodan(SHODAN_API_KEY)
        fields = ["timestamp", "ip_str", "port", "hostnames", "location", "org", "isp", "os", "domains", "asn", "title", "product", "version", "cpe", "cve", "tags", "hash", "transport", "ssl", "uptime", "link", "type", "info", "host", "device_type", "device", "telnet", "ssh", "ftp", "smtp", "service", "service_type", "banner"]
        #fields = ["ip_str", "port", "hostnames", "org", "isp", "asn", "os", "location", "domains", "product", "version", "cpe"]
        if ip!=None:
            results = api.search('hostname:' + subdomain + ' ip:' + ip, fields=fields, minify=False)
        else:
            results = api.search('hostname:' + subdomain, fields=fields, minify=False)
        return results

    except Exception as e:
        print(f' Favicon hash threw exception: {e}')
        return None


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("SHODAN_API_KEY")
    fhash = get_favicon_url("python.org")
    print(json.dumps(fhash,indent=4))
    fresult = api(fhash,True, api_key)
    sub_result = sub_osint(api_key, 'python.org')
    print(json.dumps(fresult,indent=4))
    print(json.dumps(sub_result,indent=4))
