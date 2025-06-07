FROM python:3.10

# Tüm sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    wget \
    git \
    dnsutils \
    nmap \
    ca-certificates \
    libnss3 \
    xvfb \
    x11vnc \
    xauth \
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
    && go install github.com/s0md3v/smap/cmd/smap@latest \
    && go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest \
    && go install -v github.com/projectdiscovery/wappalyzergo/cmd/update-fingerprints@latest


# Go‑Wappalyzer CLI
COPY modules/go-wappalyzer /go-wappalyzer
RUN cd /go-wappalyzer && \
     go get github.com/projectdiscovery/wappalyzergo@latest && \
     go mod tidy && \
     go build -o /usr/local/bin/wappalyzergo-cli ./main.go

# Python bağımlılıkları
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set display environment variable
ENV DISPLAY=:99

COPY . .

# 8) Tek satır ENTRYPOINT ile:
#    - IP’den timezone al
#    - /etc/localtime ve /etc/timezone güncelle
#    - Xvfb’yi başlat, google dork için
#    - Uygulamayı çalıştır
ENTRYPOINT ["sh","-c", "\
   TZ=$(curl -sf --connect-timeout 3 -m 5 https://ipapi.co/timezone || echo 'Europe/Istanbul')  && \
   ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
   echo \"$TZ\" > /etc/timezone && \
   dpkg-reconfigure -f noninteractive tzdata >/dev/null 2>&1 && \
   exec python -u main.py \"$@\" \
"]
# Web arayüzü için port açıklığı
EXPOSE 5000
