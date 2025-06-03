# Wafw00f WAF tespit
# Domain alır, wafı döndürür
import re
import os
import time
import subprocess
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('waf_scan', 'modules/logs/waf_scan.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('waf_scan', 'logs/waf_scan.log')


def strip_ansi(o: str) -> str:    
    # pattern = re.compile(r'/(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]/')
    pattern = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
    stripped = pattern.sub('', o)
    return stripped


def run_wafw00f(target: str):
    start = time.time()
    logger.info(f"Starting WAF scan for {target}")
    
    try:
        current_folder = os.path.abspath(os.path.dirname(__file__))

        COMMAND = [
            'wafw00f', target
        ]
    
        process = subprocess.Popen(
            COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=current_folder
        )
        
        stdout, stderr = process.communicate()
        if stderr:
            logger.warning(f"wafw00f stderr: {stderr}")

        output_lines = stdout.splitlines()
        
        # Örnek: [+] The site https://balpars.com is behind Fastly (Fastly CDN) WAF
        waf = output_lines[-2].split("behind")[1].removesuffix('.')
        
        end = time.time()
        duration = end - start
        logger.debug(f"WAF scan completed in {duration:.2f} seconds")
        logger.debug(f"WAF {waf}")
        logger.debug(f"===")
        logger.debug(strip_ansi(waf))
        return strip_ansi(waf)
    except Exception as e:
        logger.exception(f"[ERROR] waf_scan.py : {e}")
        return "Unknown WAF"

if __name__ == "__main__":
    result = run_wafw00f('balpars.com')
    logger.info(result)