import subprocess, time, re, os
try:
    from modules.log_helper import setup_logger
    logger = setup_logger('waf_scan','modules/logs/waf_scan.log')
except ModuleNotFoundError:
    from log_helper import setup_logger
    logger = setup_logger('waf_scan','logs/waf_scan.log')


# ANSI escape kodlarını temizleyen regex
ANSI_RE = re.compile(r'\x1B\[\d+(?:;\d+)*m')

# "[+] The site ... is behind Fastly (Fastly CDN) WAF." satırından
# "Fastly (Fastly CDN)" kısmını çekecek regex
BEHIND_RE = re.compile(r'\[\+\]\s+The site .+ is behind (.+?) WAF\.')

def strip_ansi(line: str) -> str:
    return ANSI_RE.sub('', line)


def run_wafw00f(target: str, timeout: float = 30.0) -> str:
    start = time.time()
    logger.info(f"Starting WAF scan for {target}")

    cmd = ['wafw00f', target]
    try:
        # subprocess.run ile hem stderr'i yakalayalım, hem timeout kullanalım
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        logger.error(f"WAF scan timed out after {timeout}s for {target}")
        return "Unknown"
    except subprocess.CalledProcessError as e:
        err = (e.stderr or '').strip()
        logger.error(f"WAF scan failed (code {e.returncode}): {err}")
        return "Unknown"

    # stdout satırlarını alın, ANSI kodlarını temizleyin
    lines = [strip_ansi(l) for l in res.stdout.splitlines()]
    logger.debug("wafw00f output (cleaned):\n" + "\n".join(lines))

    waf = "Unknown"
    # regex ile "[+] ... is behind XXX WAF." satırını yakala
    for line in lines:
        m = BEHIND_RE.match(line)
        if m:
            waf = m.group(1)
            break

    duration = time.time() - start
    logger.debug(f"WAF scan completed in {duration:.2f} seconds, detected: {waf!r}")
    logger.info(f"WAF scan result: {waf}")
    return waf


if __name__ == '__main__':
    print(run_wafw00f('https://balpars.com'))
