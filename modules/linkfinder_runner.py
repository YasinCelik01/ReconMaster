import requests
import subprocess
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# import json  
try:
	# # main.py'den çalıştırıldığında
	from modules.log_helper import setup_logger
	logger = setup_logger('linkfinder_runner', 'modules/logs/linkfinder_runner.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
	from log_helper import setup_logger
	logger = setup_logger('linkfinder_runner', 'logs/linkfinder_runner.log')


def run_linkfinder(url):
	import re

	start = time.time()
	logger.info(f"Starting JS endpoints scan for {url}")
	
	try:
		if "http" not in url:
			url = "http://" + url

		response = requests.get(url, timeout=10)
		soup = BeautifulSoup(response.text, 'html.parser')

		script_tags = soup.find_all('script')
		js_files = set()

		for tag in script_tags:
			src = tag.get('src')
			if src:
				full_url = urljoin(url, src)
				js_files.add(full_url)

		result_dict = {}
		for js_url in js_files:
			try:
				logger.debug(f"Analyzing {js_url}")
				resp = requests.get(js_url, timeout=10)
				if 'javascript' not in resp.headers.get('Content-Type', ''):
					continue

				with open('temp.js', 'w', encoding='utf-8') as f:
					f.write(resp.text)

				cmd = ['python3', 'linkfinder.py', '-i', 'temp.js', '-o', 'cli']
				proc = subprocess.run(cmd, capture_output=True, text=True)
				os.remove('temp.js')

				lines = proc.stdout.splitlines()
				endpoints = [line.strip() for line in lines if re.match(r'^https?://|^/', line)]
				result_dict[js_url] = endpoints

			except Exception as single_err:
				logger.warning(f"Skipped {js_url}: {single_err}")

		final_list = list(result_dict.keys())  # JS kaynakları
		final_list += [ep for v in result_dict.values() for ep in v]  # Endpoint'ler

		logger.debug(f"JS endpoints scan completed in {time.time() - start:.2f} seconds")
		return final_list

	except Exception as e:
		logger.exception(f"[ERROR] run_linkfinder: {e}")
		return []

 
if __name__ == "__main__":
	url = 'balpars.com'
	result = run_linkfinder(url)
	logger.info(result)