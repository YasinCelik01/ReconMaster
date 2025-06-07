import subprocess
import time
try:
	# # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('smap', 'modules/logs/smap.log')
except ModuleNotFoundError:
	# doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('smap', 'logs/smap.log')



def smap_scan(target: str)->list:
    start = time.time()
    logger.info(f"Starting SMAP scan for {target}")
    
    try:
        SMAP_COMMAND = [
            'smap',
            target,
        ]

        process = subprocess.Popen(
            SMAP_COMMAND,
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
        logger.debug(f"SMAP scan completed in {duration:.2f} seconds")
        logger.debug(f"SMAP result: {extracted_data}")
        
        return extracted_data
    except Exception as e:
        logger.exception(f"[ERROR] smap.py : {e}")
        return []

if __name__ == "__main__":
    result = smap_scan('balpars.com')
    logger.info(result)