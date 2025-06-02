import ipaddress
from modules.log_helper import setup_logger

logger = setup_logger('cidr_to_ip', 'modules/logs/cidr_to_ip.log')

# CIDR formatından üretilebilecek IP adreslerinin listesini döndürür.
# 192.168.1.0/24" -> ["192.168.1.0", "192.168.1.1", ... ,"192.168.1.255"]
def cidr_to_ip(cidr:str):
    return [str(ip) for ip in ipaddress.IPv4Network(cidr)]

if __name__ == "__main__":
    logger.info(cidr_to_ip("192.168.1.0/24"))