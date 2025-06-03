import ipaddress
import time
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('cidr_to_ip', 'modules/logs/cidr_to_ip.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('cidr_to_ip', 'logs/cidr_to_ip.log')


# CIDR formatından üretilebilecek IP adreslerinin listesini döndürür.
# 192.168.1.0/24" -> ["192.168.1.0", "192.168.1.1", ... ,"192.168.1.255"]
def cidr_to_ip(cidr:str):
    start = time.time()
    logger.info(f"Starting CIDR to IP conversion for {cidr}")
    
    try:
        ip_list = [str(ip) for ip in ipaddress.IPv4Network(cidr)]
        end = time.time()
        duration = end - start
        logger.debug(f"Generated {len(ip_list)} IP addresses in {duration:.2f} seconds")
        logger.debug(f"IP list: {ip_list}")
        return ip_list
    except Exception as e:
        logger.exception(f"[ERROR] cidr_to_ip.py : {e}")
        return []

if __name__ == "__main__":
    result = cidr_to_ip("192.168.1.0/24")
    logger.info(result)