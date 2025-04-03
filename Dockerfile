FROM python:3.9

# Tüm sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    wget \
    git \
    dnsutils \
    nmap \
    ca-certificates \
    libnss3 \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Go kurulumu
RUN wget https://go.dev/dl/go1.22.4.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.22.4.linux-amd64.tar.gz \
    && rm go1.22.4.linux-amd64.tar.gz

# PATH ayarları
ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH=/go
ENV PATH="${GOPATH}/bin:${PATH}"

# Go araçları
RUN go install github.com/incogbyte/shosubgo@latest \
    && go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
    && go install github.com/projectdiscovery/katana/cmd/katana@latest \
    && go install github.com/gwen001/github-subdomains@latest \
    && go install github.com/s0md3v/smap/cmd/smap@latest

# Python bağımlılıkları
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]