from urllib.parse import urlparse
from modules.log_helper import setup_logger

logger = setup_logger('url_endpoint_filter', 'modules/logs/url_endpoint_filter.log')

# main'den çağırılacak fonskiyon
def separate_subdomains_and_endpoints(urls):
    try:
        subdomains = []
        endpoints = []  # Keep the full URLs as they are
        for url in urls:
            parsed_url = urlparse(url)
            # Extract subdomain and keep the full URL for endpoints
            subdomains.append(parsed_url.netloc)
            endpoints.append(url)  # Use the original URL as the endpoint
        return subdomains, endpoints
    except Exception as e:
        logger.exception(f"[ERROR] url_endpoint_filter.py : {e}")
        return [], []

def main():
    url_list = [
        "https://sub.example.com/path/to/resource?query=123#fragment",
        "https://example.com/",
        "https://blog.example.org/article"
    ]

    subdomains, endpoints = separate_subdomains_and_endpoints(url_list)

    logger.info("Subdomains:", subdomains)
    logger.info("Endpoints:", endpoints)


if __name__ == "__main__":
    main()


