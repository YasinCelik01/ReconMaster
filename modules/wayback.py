
# https://medium.com/@gguzelkokar.mdbf15/from-wayback-machine-to-aws-metadata-uncovering-ssrf-in-a-production-system-within-5-minutes-2d592875c9ab
# Wayback machine'den subdomainler, directory'ler getirir, liste olarak döndürür.
# Büyük hedefler için yavaş, tee gibi bir komut gerek


import requests

# Main'den çağırılacak Fonskiyon
# Wayback machine'de 200 response'u ile arşivlenmiş adresleri getirir
def fetch_wayback_200(target: str):
    url = f"""
    https://web.archive.org/cdx/search/cdx?url=*.{target}%2F*&output=text&fl=original&collapse=urlkey&filter=statuscode%3A200
    """
    # İsteği gönderip sonucu string listesine çevirme
    result = requests.get(url).content.decode('utf-8').split('\n')
    # Boş elemanları filtreleme
    str_list = list(filter(None, result))
    return str_list

if __name__ == "__main__":
    TARGET = "balpars.com"
    result = fetch_wayback_200(TARGET)
    print(result)
	
