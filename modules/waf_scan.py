# Wafw00f WAF tespit
# Domain alır, wafı döndürür

import os
import subprocess

def run_wafw00f(target: str):
    try:
        current_folder = os.path.abspath(os.path.dirname(__file__))

        COMMAND = [
            'wafw00f', target
        ]
    
        process = subprocess.Popen(
            COMMAND,
            stdout=subprocess.PIPE,
            text=True,
            cwd=current_folder
        )
        
        stdout, stderr = process.communicate()

        output_lines = stdout.splitlines()
        
        # Örnek: [+] The site https://balpars.com is behind Fastly (Fastly CDN) WAF
        waf = output_lines[-2].split("behind")[1].removesuffix('.')
        return waf
    except Exception as e:
        print(f"[ERROR] waf_scan.py : {e}")
        return "Unknown WAF"

if __name__ == "__main__":
    result = run_wafw00f('balpars.com')
    print(result)