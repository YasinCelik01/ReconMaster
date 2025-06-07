import subprocess
import time
from os import geteuid
try:
	# main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('httpx', 'modules/logs/httpx.log')
except ModuleNotFoundError:
	# doğrudan çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('httpx', 'logs/httpx.log')

# -duc, -disable-update-check  disable automatic httpx update check
#  -cl, -content-length   display response content-length
# -location              display response redirect location
# -ip -cdn
# -websocket             display server using websocket
# httpx -duc -title -status-code -cl -tech-detect -follow-redirects -location -ip -cdn -websocket -mc 200,204,301,302,304,,401,403,404,407,500 -l <filename>
# httpx -duc -title -status-code -cl -tech-detect -follow-redirects -location -ip -cdn -websocket -rl 10 -mc 200 -l <filename>


def run_httpx(target: str, rate_limit: int = 10):

    logger.info("HTTPX is WIP, so is disabled")
    return []
    ############################################
    start = time.time()
    logger.info(f"Starting httpx scan for {target}")
    

    try:
        HTTPX_COMMAND = [
            'httpx',
        ]

        logger.debug(f"httpx komutu: {' '.join(HTTPX_COMMAND)}")

        process = subprocess.Popen(
            HTTPX_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        if stderr:
            logger.debug(f"httpx stderr: {stderr.strip()}")

        output_list = stdout.splitlines()
        filtered_list = [s for s in output_list if "[launcher.Browser]" not in s]
        logger.debug(f"httpx output {filtered_list}")

        end = time.time()
        duration = end - start
        logger.debug(f"httpx scan completed in {duration:.2f} seconds")
        logger.debug(f"Returning {len(filtered_list)} URLs: {filtered_list}")

        return filtered_list

    except Exception as e:
        logger.exception(f"httpx error: {e}")
        return []
    finally:
        logger.info("httpx scan ended.")

if __name__ == "__main__":
    result = run_httpx('balpars.com')
    logger.info(result)
