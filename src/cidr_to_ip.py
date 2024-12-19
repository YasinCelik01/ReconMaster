import ipaddress

def cidr_to_ip(cidr:str):
    return [str(ip) for ip in ipaddress.IPv4Network(cidr)]

if __name__ == "__main__":
    print(cidr_to_ip("192.168.1.0/24"))