import subprocess
import os
import json
import time
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('wappalyzer_runner', 'modules/logs/wappalyzer_runner.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('wappalyzer_runner', 'logs/wappalyzer_runner.log')


def run_wappalyzer(url: str):
    start = time.time()
    logger.info(f"Starting Wappalyzer scan for {url}")
    
    # ensure scheme
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # yeni Go‑based CLI
    cmd = ["wappalyzergo-cli", "-url", url]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc.communicate()
        if proc.returncode != 0:
            logger.exception(f"[ERROR] WappalyzerGo :\n{err}")
            return {}

        # JSON parse
        result = json.loads(out)


        end = time.time()
        duration = end - start
        logger.debug(f"Wappalyzer scan completed in {duration:.2f} seconds")
        tech_names = list(result.keys())
        logger.debug(f"Wappalyzer result: {tech_names}")
        return tech_names
        
    except Exception as e:
        logger.exception(f"[ERROR] WappalyzerGo exception: {e}")
        return {}


if __name__ == "__main__":
    result=run_wappalyzer('balpars.com')
    logger.info(result)
