from urllib.parse import urlparse

# main'den çağırılacak fonskiyon
def separate_subdomains_and_endpoints(urls):
    subdomains = []
    endpoints = []  # Keep the full URLs as they are
    for url in urls:
        parsed_url = urlparse(url)
        # Extract subdomain and keep the full URL for endpoints
        subdomains.append(parsed_url.netloc)
        endpoints.append(url)  # Use the original URL as the endpoint
    return subdomains, endpoints

def main():
    url_list = [
        "https://sub.example.com/path/to/resource?query=123#fragment",
        "https://example.com/",
        "https://blog.example.org/article"
    ]

    subdomains, endpoints = separate_subdomains_and_endpoints(url_list)

    print("Subdomains:", subdomains)
    print("Endpoints:", endpoints)


if __name__ == "__main__":
    main()


