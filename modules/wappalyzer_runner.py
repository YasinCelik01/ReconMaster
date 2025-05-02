import subprocess
import os

def run_wappalyzer(url: str):
    # ensure scheme
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # yeni Go‑based CLI
    cmd = ["wappalyzergo-cli", "-url", url]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc.communicate()
        if proc.returncode != 0:
            print(f"[-] WappalyzerGo hata:\n{err}")
            return {}
        # JSON parse
        import json
        return json.loads(out)
    except Exception as e:
        print(f"[-] WappalyzerGo exception: {e}")
        return {}


if __name__ == "__main__":
    result=run_wappalyzer('balpars.com')
    print(result)
