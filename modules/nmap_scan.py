import subprocess

def scan_with_nmap(target):
	if not target:
		return {"error": "No IP addresses provided for scanning"}

	NMAP_COMMAND = [
				'nmap',
				'-F',
				target
			]

	# DEMO İÇİN TEK IP BAKILIYOR, SONRASINDA TÜM IP'LERE BAKILACAK
	# scan_results = {}
	# for ip in target:
	# 	# result = subprocess.run(['nmap', '-p-','-sV',ip], capture_output=True, text=True)
	# 	# FOR DEMO
	# 	result = subprocess.run(['nmap', '-F',ip], capture_output=True, text=True)
	# 	scan_results[ip] = result.stdout.strip()

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
		
	return extracted_data
		

def main():
	print(scan_with_nmap("balpars.com"))



if __name__ == "__main__":
    main()