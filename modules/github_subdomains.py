# Github üzerinde subdomain araması, doğruluk oranı yüksek değil
import os
import time
import subprocess
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('github_subdomains', 'modules/logs/github_subdomains.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('github_subdomains', 'logs/github_subdomains.log')




def run_gh_subdomains(target: str, key):
    start = time.time()
    logger.info(f"Starting GitHub subdomains scan for {target}")
    
    try:
        if not key:
            logger.warning("No Github Token is given, skipping github-subdomains module")
            return []

        current_folder = os.path.abspath(os.path.dirname(__file__))
        COMMAND = [
            'github-subdomains', '-d', target, '-t', key, '-o', 'gh_subdomains.txt'
        ]
    
        process = subprocess.Popen(
            COMMAND,
            stdout=subprocess.PIPE,
            text=True,
            cwd=current_folder
        )
        
        stdout, stderr = process.communicate()

        output_file = os.path.join(current_folder, 'gh_subdomains.txt')
        
        domains = []
        with open(output_file) as f:
            domains = f.read().splitlines()
            
        os.remove(output_file)
        
        end = time.time()
        duration = end - start
        logger.debug(f"GitHub subdomains scan completed in {duration:.2f} seconds")
        logger.debug(f"Found subdomains: {domains}")
        
        return domains
    except Exception as e:
        logger.exception(f"[ERROR] github_subdomains.py : {e}")
        return []
    
if __name__ == "__main__":
    result = run_gh_subdomains('balpars.com')
    logger.info(f"GH Subdomains found: {result}")