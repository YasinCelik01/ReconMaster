import subprocess
from dotenv import load_dotenv
import os

def run_shosubgo(target: str, key):
    
    if not key:
        print("[INFO] No Shodan Key, skipping shosubgo")
        return []

    COMMAND = [
        'shosubgo',
        '-d', target,
        '-s',
        key
    ]
    process = subprocess.Popen(
        COMMAND,
        stdout=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate()
    output_list = stdout.splitlines()
    return output_list

if __name__ == "__main__":
    load_dotenv()
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
    result = run_shosubgo('balpars.com', SHODAN_API_KEY)
    print(result)