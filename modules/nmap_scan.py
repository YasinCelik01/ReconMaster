import subprocess

def scan_with_nmap(ip_addresses):
	if not ip_addresses:
		return {"error": "No IP addresses provided for scanning"}

	scan_results = {}
	for ip in ip_addresses:
		# result = subprocess.run(['nmap', '-p-','-sV',ip], capture_output=True, text=True)
		# FOR DEMO
		result = subprocess.run(['nmap', '-F','-sV',ip], capture_output=True, text=True)
		scan_results[ip] = result.stdout.strip()
  

	return scan_results

