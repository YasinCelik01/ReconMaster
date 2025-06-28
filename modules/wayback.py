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
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            url_200 = f"https://web.archive.org/cdx/search/cdx?url=*.{target}%2F*&output=text&fl=original&collapse=urlkey&filter=statuscode%3A200"
            response = requests.get(url_200, timeout=240)
            response.raise_for_status()
            
            # Process results
            result_200 = response.content.decode('utf-8').split('\n')
            str_list = list(filter(None, result_200))
            
            url_300 = f"https://web.archive.org/cdx/search/cdx?url=*.{target}%2F*&output=text&fl=original&collapse=urlkey&filter=statuscode%3A30*"
            response = requests.get(url_300, timeout=240)
            response.raise_for_status()
            result_300 = response.content.decode('utf-8').split('\n')
            str_list.extend(list(filter(None, result_300)))


            end = time.time()
            duration = end - start
            logger.info(f"Wayback Machine scan completed in {duration:.2f} seconds, {len(str_list)} results found")
            return str_list
            
        except requests.RequestException as e:
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} attempts failed: {str(e)}")
                return []
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return []




if __name__ == "__main__":
    TARGET = "balpars.com"
    result = fetch_wayback_200(TARGET)
    logger.info(f"Found {len(result)} URLs")
	
