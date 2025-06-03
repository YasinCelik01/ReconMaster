import requests
import time
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('asn_query', 'modules/logs/asn_query.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('asn_query', 'logs/asn_query.log')


def asn_to_ip(asn_number:str):
    start = time.time()
    logger.info(f"Starting ASN to IP conversion for {asn_number}")
    
    try:
        URL = f"https://ip.guide/{asn_number}"
        response = requests.get(URL)
        asn_info = response.json()
        
        end = time.time()
        duration = end - start
        logger.debug(f"ASN to IP conversion completed in {duration:.2f} seconds")
        logger.debug(f"Routes found: {asn_info['routes']}")
        
        return asn_info['routes']
    except Exception as e:
        logger.exception(f"[ERROR] asn_query.py : {e}")
        return []

def ip_to_asn(ip_address:str):
    start = time.time()
    logger.info(f"Starting IP to ASN conversion for {ip_address}")
    
    try:
        URL = f"https://ip.guide/{ip_address}"
        response = requests.get(URL)
        ip_info = response.json()
        
        # CIDR yapınca response json yapısında değişiklik oluyor
        if '/' in ip_address:
            ASN = ip_info['autonomous_system']['asn']
        else:
            ASN = ip_info['network']['autonomous_system']['asn']
        
        end = time.time()
        duration = end - start
        logger.debug(f"IP to ASN conversion completed in {duration:.2f} seconds")
        logger.debug(f"Found ASN: AS{ASN}")
        
        return "AS"+str(ASN)
    except Exception as e:
        logger.exception(f"[ERROR] asn_query.py : {e}")
        return 0

if __name__ == "__main__":
    ip = asn_to_ip("AS14421")
    asn = ip_to_asn("216.101.17.0/24")
    
    logger.info(ip)
    logger.info(asn)