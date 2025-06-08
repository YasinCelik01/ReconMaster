import subprocess
import tempfile
import json
import os
import logging

try:
    # main.py'den çalıştırıldığında
    from modules.log_helper import setup_logger
    logger = setup_logger('httpx_runner', 'modules/logs/httpx_runner.log')
except ModuleNotFoundError:
    # doğrudan modül çalıştırıldığında
    from log_helper import setup_logger
    logger = setup_logger('httpx_runner', 'logs/httpx_runner.log')


def run_httpx(targets: list[str]) -> list[dict]:
    """
    Given a list of domains or endpoints, run httpx with predefined flags
    and return a list of parsed JSON results.

    :param targets: List of hostnames or URLs to scan
    :return: List of dictionaries parsed from httpx JSON output
    """
    if not targets:
        return []

    # Write targets to a temporary input file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_in:
        tmp_in.write("\n".join(targets))
        tmp_input_path = tmp_in.name

    tmp_output_path = tmp_input_path + '.json'

    # Build httpx command
    cmd = [
        "httpx",
        "-silent",
        "-json",
        "-probe",      # include probe errors/status in JSON
        "-location",   # include redirect location header
        "-l", tmp_input_path,
        # Core probes
        "-sc",    # status-code
        "-ct",    # content-type
        "-cl",    # content-length
        "-title",
        "-ip",
        "-server",
        "-cdn",
        "-td",        # tech-detect (Wappalyzer)
        "-favicon",
        "-jarm",
        # Output
        "-o", tmp_output_path
    ]

    results: list[dict] = []
    try:
        logger.info(f"Running httpx on {len(targets)} targets")
        # stdout/stderr to console for error visibility
        subprocess.run(cmd, check=True)

        # Read and parse JSONL output
        with open(tmp_output_path, 'r') as f:
            for line in f:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError as je:
                    logger.warning(f"Failed to parse line as JSON: {je}")
    except subprocess.CalledProcessError as cpe:
        logger.error(f"httpx process failed: {cpe}")
    except Exception as e:
        logger.exception(f"Unexpected error running httpx: {e}")
    finally:
        # Cleanup temp files
        try:
            os.remove(tmp_input_path)
        except OSError:
            pass
        try:
            os.remove(tmp_output_path)
        except OSError:
            pass
    
    # En başta erişebildikleri olucak listede
    results.sort(key=lambda r: r.get("failed", False))
    return results


if __name__ == '__main__':
    targets = ['nc.balpars.com', 'nextcloud.balpars.com','www.balpars.com']
    result = run_httpx(targets)
    print("<<<<<<<<<<<<<<<<<<")
    print(result)