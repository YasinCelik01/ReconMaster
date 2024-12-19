import requests

def asn_query(asn_number:str):    
    URL = f"https://ip.guide/{asn_number}"
    response = requests.get(URL)
    return response.json()

if __name__ == "__main__":
    TARGET = "AS14421"
    result = asn_query(TARGET)
    print(result)