# Wafw00f WAF tespit
# Domain alır, wafı döndürür

import os
import time
import subprocess
from modules.log_helper import setup_logger

logger = setup_logger('waf_scan', 'modules/logs/waf_scan.log')

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
            text=True,
            cwd=current_folder
        )
        
        stdout, stderr = process.communicate()

        output_lines = stdout.splitlines()
        
        # Örnek: [+] The site https://balpars.com is behind Fastly (Fastly CDN) WAF
        waf = output_lines[-2].split("behind")[1].removesuffix('.')
        
        end = time.time()
        duration = end - start
        logger.debug(f"WAF scan completed in {duration:.2f} seconds")
        
        return waf
    except Exception as e:
        logger.exception(f"[ERROR] waf_scan.py : {e}")
        return "Unknown WAF"

if __name__ == "__main__":
    result = run_wafw00f('balpars.com')
    logger.info(result)