# Github üzerinde subdomain araması, doğruluk oranı yüksek değil
import os
import subprocess

def run_gh_subdomains(target: str, key):
    try:
        if not key:
            print("[ERROR] No Github Token is given, skipping github-subdomains module")
            return []

        current_folder = os.path.abspath(os.path.dirname(__file__))
        COMMAND = [
            'github-subdomains', '-d', target, '-t', key, '-o', 'gh_subdomains.txt'
        ]
    
        process = subprocess.Popen(
            COMMAND,
            stdout=subprocess.PIPE,
            text=True,
            cwd=current_folder
        )
        
        stdout, stderr = process.communicate()

        output_file = os.path.join(current_folder, 'gh_subdomains.txt')
        
        
        domains = []
        with open(output_file) as f:
            domains = f.read().splitlines()
            
        os.remove(output_file)
        return domains
    except Exception as e:
        print(f"[ERROR] github_subdomains.py : {e}")
        return []
    
if __name__ == "__main__":
    result = run_gh_subdomains('balpars.com')
    print(result)