import subprocess

def smap_scan(target: str):
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
        
        return extracted_data
    except Exception as e:
        print(f"[ERROR] smap.py : {e}")
        return []

if __name__ == "__main__":
    result = smap_scan('balpars.com')
    print(result)