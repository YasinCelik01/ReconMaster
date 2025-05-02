import subprocess
from os import geteuid

def katana_scan(target: str, rate_limit:int = 10):
    try:
        KATANA_COMMAND = [
            'katana',
            '-u', target,
            '-headless', # Sayfa yüklendikten sonra ortaya çıkan bağlantılar vs.
            '-js-crawl', # javascript dosyalarını inceleme
            '-rate-limit', str(rate_limit) 
        ]

        # root kullanıcısı için bu argüman gerekiyor
        if geteuid() == 0:
            KATANA_COMMAND.append('-no-sandbox')
        
        process = subprocess.Popen(
            KATANA_COMMAND,
            stdout=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        output_list = stdout.splitlines()
        filtered_list = [s for s in output_list if "[launcher.Browser]" not in s]
        return filtered_list
    except Exception as e:
        print(f"[ERROR] katana.py : {e}")
        return []

if __name__ == "__main__":
    result = katana_scan('balpars.com')
    print(result)