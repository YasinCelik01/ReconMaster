import requests
import subprocess
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# import json  

#Mainden cagrılacak fonksiyon
def linkfinder(url):
	js_files = []
	result_dict = {}

	if "http" not in url:
		url = "http://" + url
	print(url)
	response = requests.get(url)
	html_content = response.text

	content = BeautifulSoup(html_content, 'html.parser')

	script_tags = content.find_all('script')

	for tag in script_tags:
		script_url = tag.get('src')
		if script_url:
			script_url = urljoin(url, script_url)
			js_files.append(script_url)

	for js_url in js_files:
		response = requests.get(js_url)
		js_content = response.text

		with open('temp.js', 'w', encoding='utf-8') as file:
			file.write(js_content)

		result = subprocess.run(['python3', 'linkfinder.py', '-i', 'temp.js', '-o', 'cli'], capture_output=True, text=True)
		endpoints = result.stdout.splitlines()
		result_dict[js_url] = endpoints
		os.remove('temp.js')

	# DEMO için
	# json_result = json.dumps(result_dict, indent=4)
	# return json_result
	# 
	endpoints = []
	endpoints.extend(result_dict.keys())  # Add JS file URLs
	endpoints.extend([item for sublist in result_dict.values() for item in sublist])  # Flattened values
	return endpoints
 
 
if __name__ == "__main__":
	url = 'balpars.com'
	x = linkfinder(url)
	print(x)