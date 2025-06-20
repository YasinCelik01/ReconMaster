# ReconMaster

ReconMaster is a comprehensive reconnaissance tool that combines multiple passive and active scanning techniques to gather information about target domains. It provides both a web interface and command-line interface for ease of use.

## Features

### Passive Reconnaissance
- WHOIS information gathering
- DNS information
- Subdomain enumeration using multiple tools:
  - Subfinder
  - ShosubGo (Shodan-based)
  - GitHub subdomain discovery
  - Wayback Machine archives
- Port scanning via Shodan
- Google Dorks scanning
- HTTPX scanning for subdomains

### Active Reconnaissance
- Katana web crawling
- JavaScript endpoint discovery (LinkFinder)
- Nmap port scanning
- Wappalyzer technology detection
- WAF detection (WAFW00f)

### Additional Features
- Telegram notifications for scan results
- Parallel execution of modules
- Results saved in JSON format
- Web interface for easy interaction
- Command-line interface for automation

## Installation

### Docker Installation

This is the reccomended and most supported way to run our application.
Since docker installs everything for you, it's also the simplest.

```bash
# Clone the repository
git clone https://github.com/YasinCelik01/ReconMaster.git
cd ReconMaster

# Build and run with Docker Compose
docker-compose up --build
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/YasinCelik01/ReconMaster.git

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
This method also requires you to install Go binaries that are used in the project.
After installing and adding Go to path, you must run this command to install dependecies.

go install github.com/incogbyte/shosubgo@latest \
&& go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
&& go install github.com/projectdiscovery/katana/cmd/katana@latest \
&& go install github.com/gwen001/github-subdomains@latest \
&& go install github.com/s0md3v/smap/cmd/smap@latest \
&& go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest \
&& go install -v github.com/projectdiscovery/wappalyzergo/cmd/update-fingerprints@latest


## Configuration

Create a `.env` file in the project root with the following variables:
```
SHODAN_API_KEY=your_shodan_api_key
GITHUB_SEARCH_TOKEN=your_github_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```
If no key is set the modules that requires the key is be disabled.

## Usage

### Build and run with Docker Compose
1. ```docker-compose up --build```
2. Open your browser and navigate to `http://localhost:5000`
3. Enter the target domain and select desired modules
4. Click "Start Scan"

### Web Interface
1. Start the application:
```bash
python main.py
```
2. Open your browser and navigate to `http://localhost:5000`
3. Enter the target domain and select desired modules
4. Click "Start Scan"

### Command Line Interface
```bash
python main.py --url example.com --no-gui
```



## Module Selection

You can enable/disable specific modules for your scan. Available modules:
- whois: WHOIS information
- dns: DNS information
- subfinder: Subdomain enumeration
- shosubgo: Shodan-based subdomain discovery
- github: GitHub subdomain discovery
- wayback: Wayback Machine archives
- smap: Shodan port scanning
- googledorks: Google Dorks scanning
- katana: Web crawling
- linkfinder: JavaScript endpoint discovery
- nmap: Port scanning
- wappalyzer: Technology detection
- waf: WAF detection
- httpx: HTTPX scanning
- telegram: Telegram notifications

## Acknowledgments

This project uses several open-source tools and libraries:

- [Subfinder](https://github.com/projectdiscovery/subfinder) - Fast passive subdomain enumeration tool
- [Katana](https://github.com/projectdiscovery/katana) - Web crawling framework
- [LinkFinder](https://github.com/GerbenJavado/LinkFinder) - JavaScript endpoint discovery
- [Wappalyzer](https://github.com/wappalyzer/wappalyzer) - Technology detection
- [WAFW00f](https://github.com/EnableSecurity/wafw00f) - WAF detection
- [HTTPX](https://github.com/projectdiscovery/httpx) - Fast and multi-purpose HTTP toolkit
- [Flask](https://github.com/pallets/flask) - Web framework
- [nodriver](https://github.com/ultrafunkamsterdam/nodriver) - Chrome automation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.