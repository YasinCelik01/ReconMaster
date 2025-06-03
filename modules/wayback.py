# https://medium.com/@gguzelkokar.mdbf15/from-wayback-machine-to-aws-metadata-uncovering-ssrf-in-a-production-system-within-5-minutes-2d592875c9ab
# Wayback machine'den subdomainler, directory'ler getirir, liste olarak döndürür.
# Büyük hedefler için yavaş, tee gibi bir komut gerek
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('wayback', 'modules/logs/wayback.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('wayback', 'logs/wayback.log')
import time
import requests




# Main'den çağırılacak Fonskiyon
# Wayback machine'de 200 response'u ile arşivlenmiş adresleri getirir
def fetch_wayback_200(target: str):
    start = time.time()
    logger.info(f"Starting Wayback Machine scan for {target}")
    
    try:
        url = f"""
        https://web.archive.org/cdx/search/cdx?url=*.{target}%2F*&output=text&fl=original&collapse=urlkey&filter=statuscode%3A200
        """
        # İsteği gönderip sonucu string listesine çevirme
        result = requests.get(url).content.decode('utf-8').split('\n')
        # Boş elemanları filtreleme
        str_list = list(filter(None, result))
        
        end = time.time()
        duration = end - start
        logger.debug(f"Wayback Machine found:\n{str_list}")
        logger.debug(f"Wayback Machine scan completed in {duration:.2f} seconds")
        return str_list
    except Exception as e:
        logger.exception(f"[ERROR] wayback.py : {e}")
        return []

if __name__ == "__main__":
    TARGET = "balpars.com"
    result = fetch_wayback_200(TARGET)
    logger.info(result)
	
