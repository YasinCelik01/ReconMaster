import subprocess
import os

def run_wappalyzer(url):
    if "http" not in url:
        url = "http://" + url
    script_path = "/home/yasin/wappalyzer/src/drivers/npm/cli.js"
    print(url)
    command = ["node", script_path, url]

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("[+] Wappalyzer Çıktısı:")
            return stdout
        else:
            print("[-] Hata oluştu:")
            return stderr
    except Exception as e:
            return str(e)

if __name__ == "__main__":
    result=run_wappalyzer('balpars.com')
    print(result)
