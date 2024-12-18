import subprocess
from os import geteuid

def katana_scan(target: str, rate_limit:int = 10):
    
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
    return output_list

if __name__ == "__main__":
    result = katana_scan('balpars.com')
    print(result)