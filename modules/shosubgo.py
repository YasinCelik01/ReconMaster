import subprocess
import time
from dotenv import load_dotenv
import os
from modules.log_helper import setup_logger

logger = setup_logger('shosubgo', 'modules/logs/shosubgo.log')

def run_shosubgo(target: str, key):
    start = time.time()
    logger.info(f"Starting shosubgo scan for {target}")
    
    try:
        if not key:
            logger.info("[INFO] No Shodan Key, skipping shosubgo")
            return []

        COMMAND = [
            'shosubgo',
            '-d', target,
            '-s',
            key
        ]
        process = subprocess.Popen(
            COMMAND,
            stdout=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        output_list = stdout.splitlines()
        
        end = time.time()
        duration = end - start
        logger.debug(f"Shosubgo scan completed in {duration:.2f} seconds")
        
        return output_list
    except Exception as e:
        logger.exception(f"[ERROR] shosubgo.py : {e}")
        return []

if __name__ == "__main__":
    load_dotenv()
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
    result = run_shosubgo('balpars.com', SHODAN_API_KEY)
    logger.info(result)