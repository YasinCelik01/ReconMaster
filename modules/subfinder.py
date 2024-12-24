import subprocess
import json

def run_subfinder(domain):
    command = ['subfinder', '-d', domain, '-oJ', '-silent']
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running Subfinder: {e.stderr}")
        return []

    subdomains = []
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                host = data.get('host')
                if host:
                    subdomains.append(host)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                continue
    
    return subdomains

if __name__ == "__main__":
    result = run_subfinder("balpars.com")
    print(result)