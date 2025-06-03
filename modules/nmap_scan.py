import subprocess
import time
try:
	# # main.py'den çalıştırıldığında
	from modules.log_helper import setup_logger
	logger = setup_logger('nmap_scan', 'modules/logs/nmap_scan.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
	from log_helper import setup_logger
	logger = setup_logger('nmap_scan', 'logs/nmap_scan.log')


def scan_with_nmap(target):
	start = time.time()
	logger.info(f"Starting Nmap scan for {target}")
	
	try:
		if not target:
			return {"error": "No IP addresses provided for scanning"}

		NMAP_COMMAND = [
					'nmap',
					'-F',
					target
				]

		output_list = []
		process = subprocess.Popen(
		NMAP_COMMAND,
		stdout=subprocess.PIPE,
		text=True
		)

		stdout, stderr = process.communicate()
		output_list = stdout.splitlines()
	 
		extracted_data = []
		for line in output_list:
			if any(proto in line for proto in ['tcp', 'udp']):  # Check if the line contains protocol info

				parts = line.split()  # Split the line by whitespace
				if len(parts) >= 3:
					port_protocol = parts[0]  # First item (e.g., "80/tcp")
				# state = parts[1] # Open durumu
					service = parts[2]        # Third item (e.g., "http")
					version = " ".join(parts[3:]) if len(parts) > 3 else "N/A"  # Kalanlar versiyon bilgisi
					extracted_data.append(f"{port_protocol} {service} {version.strip()}")
		
		end = time.time()
		duration = end - start
		logger.debug(f"Nmap results: {extracted_data}")
		logger.debug(f"Nmap scan completed in {duration:.2f} seconds")
		
		return extracted_data
	except Exception as e:
		logger.exception(f"[ERROR] nmap_scan.py : {e}")
		return []

def main():
	logger.info(scan_with_nmap("balpars.com"))


if __name__ == "__main__":
    main()