import subprocess
import time
from os import geteuid
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('katana', 'modules/logs/katana.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('katana', 'logs/katana.log')



def katana_scan(target: str, rate_limit: int = 10, crawl_duration = 300):
    start = time.time()
    logger.info(f"Starting Katana scan for {target}")
    try:

        KATANA_COMMAND = [
                'katana',
                '-u', target,

                # HEADLESS ve JS CRAWL zaten var
                '-headless',
                '-js-crawl',
            

                # Tarama derinliği
                '-d', '3',

                # Rate‐limit
                '-rate-limit', str(rate_limit),

                # Maksimum tarama süresi her bir hedef için
                '-ct', str(crawl_duration),

                # Bilinen dosyaları (sitemap, robots.txt) da ekle
                '-kf', 'all',

                # Sistem Chrome'unu kullan
                '-system-chrome',

                # Zaten docker'da güncel hali olması garanti
                '-disable-update-check',
                
                '-headless-options',
                #'--proxy-server=http://127.0.0.1:3128,--ignore-certificate-errors,--allow-insecure-localhost,--no-sandbox,--disable-gpu'
                '--no-sandbox,--disable-gpu'
            ]

        if geteuid() == 0:
            KATANA_COMMAND.append('-no-sandbox')

        logger.debug(f"Katana komutu: {' '.join(KATANA_COMMAND)}")

        process = subprocess.Popen(
            KATANA_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        if stderr:
            logger.debug(f"Katana stderr: {stderr.strip()}")

        output_list = stdout.splitlines()
        # katana güncelleme yapıyorsa bununla ilgili stringler outputa karışmasın
        filtered_list = [s for s in output_list if "[launcher.Browser]" not in s]
    

        end = time.time()
        duration = end - start
        logger.debug(f"Katana scan completed in {duration:.2f} seconds")
        logger.debug(f"Returning {len(filtered_list)} URLs")

        return filtered_list

    except Exception as e:
        logger.exception(f"Katana error: {e}")
        return []
    finally:
        logger.info("Katana scan ended.")

if __name__ == "__main__":
    result = katana_scan('balpars.com')
    logger.info(result)
