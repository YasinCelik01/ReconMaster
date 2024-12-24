import requests

def asn_to_ip(asn_number:str):
    
    URL = f"https://ip.guide/{asn_number}"
    response = requests.get(URL)
    asn_info = response.json()
    
    return asn_info['routes']

def ip_to_asn(ip_address:str):
    
    URL = f"https://ip.guide/{ip_address}"
    response = requests.get(URL)
    ip_info = response.json()
    
    # CIDR yapınca response json yapısında değişiklik oluyor
    if '/' in ip_address:
        ASN = ip_info['autonomous_system']['asn']
    else:
        ASN = ip_info['network']['autonomous_system']['asn']
    
    return "AS"+str(ASN)

if __name__ == "__main__":
    
    ip = asn_to_ip("AS14421")
    asn = ip_to_asn("216.101.17.0/24")
    
    print(ip)
    print(asn)