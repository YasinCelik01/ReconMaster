# src/subfinder_runner.py

import os
import platform
import subprocess
import json

def get_subfinder_binary():
    system = platform.system().lower()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bin_path = os.path.join(base_dir, '..', 'bin', 'subfinder')

    if system == 'windows':
        binary = os.path.join(bin_path, 'windows', 'subfinder.exe')
    elif system == 'linux':
        binary = os.path.join(bin_path, 'linux', 'subfinder')
    elif system == 'darwin':
        binary = os.path.join(bin_path, 'macos', 'subfinder')
    else:
        raise OSError('Unsupported operating system')

    if not os.path.isfile(binary):
        raise FileNotFoundError(f"Subfinder binary not found for {system} at {binary}")

    return binary

def run_subfinder(domain):
    binary = get_subfinder_binary()
    command = [binary, '-d', domain, '-oJ', '-silent']
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

    print(result.stdout)

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
