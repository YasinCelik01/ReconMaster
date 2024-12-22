import ipaddress

def cidr_to_ip(cidr:str):
    """CIDR formatından üretilebilecek IP adreslerinin listesini döndürür.
       "192.168.1.0/24" -> ["192.168.1.0", "192.168.1.1", ... ,"192.168.1.255"]
    """
    
    return [str(ip) for ip in ipaddress.IPv4Network(cidr)]

if __name__ == "__main__":
    print(cidr_to_ip("192.168.1.0/24"))