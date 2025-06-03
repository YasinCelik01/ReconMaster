import subprocess
import json
import time

try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger

logger = setup_logger('subfinder', 'modules/logs/subfinder.log')

def run_subfinder(domain):
    start = time.time()
    logger.info(f"Starting subfinder scan for {domain}")
    
    command = ['subfinder', '-d', domain, '-oJ', '-silent']
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Subfinder execution failed: {e.stderr}")
        return []

    subdomains = []
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                host = data.get('host')
                if host:
                    subdomains.append(host)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                continue
    
    end = time.time()
    duration = end - start
    logger.debug(f"Subfinder found {len(subdomains)} subdomains in {duration:.2f} seconds")
    logger.debug(f"{subdomains}")
    return subdomains

if __name__ == "__main__":
    result = run_subfinder("balpars.com")
    logger.info(result)