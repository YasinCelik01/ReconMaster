import subprocess
import time
from os import geteuid
from modules.log_helper import setup_logger

logger = setup_logger('katana', 'modules/logs/katana.log')

def katana_scan(target: str, rate_limit: int = 10):
    start = time.time()
    logger.info(f"Starting Katana scan for {target}")
    try:
        KATANA_COMMAND = [
            'katana', '-u', target,
            '-headless', '-js-crawl',
            '-rate-limit', str(rate_limit)
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
        filtered_list = [s for s in output_list if "[launcher.Browser]" not in s]
        logger.debug(f"Katana output {filtered_list}")

        end = time.time()
        duration = end - start
        logger.debug(f"Katana scan completed in {duration:.2f} seconds")

        return filtered_list

    except Exception as e:
        logger.exception(f"Katana error: {e}")
        return []
    finally:
        logger.info("Katana scan ended.")

if __name__ == "__main__":
    katana_scan('balpars.com')
