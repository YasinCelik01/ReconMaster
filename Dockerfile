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
    # squid-openssl \
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

# --------------------Local-Proxy------------------------

# # Local Cache Proxy'imiz
# COPY squid.conf /etc/squid/squid.conf

# # HTTPS için SSL
# # --- CA key ve sertifikayı üret
# RUN mkdir -p /etc/squid/ssl_cert && \
#     cd /etc/squid/ssl_cert && \
#     openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
#         -keyout squid.key -out squid.crt \
#         -subj "/C=TR/ST=Istanbul/L=Istanbul/O=ReconMaster/OU=Proxy/CN=SquidCA" && \
#     cat squid.crt squid.key > squid.pem && \
#     chmod 600 squid.pem && \
#     chown proxy:proxy squid.pem

# RUN /usr/lib/squid/security_file_certgen -c -s /var/lib/ssl_db -M 4MB

# # Sisteme ekle (Debian tabanlıysa)
# RUN cp /etc/squid/ssl_cert/squid.crt /usr/local/share/ca-certificates/squid.crt && \
#     update-ca-certificates

# # Python için (requests, httpx vs)
# ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# ENTRYPOINT ile:
#    - önce squid’i başlat, sonra proxy’yi ayarla
#    - IP’den timezone al 5 saniyede alamazsa istanbul
#    - /etc/localtime ve /etc/timezone güncelle
#    - Uygulamayı çalıştır
# ENTRYPOINT ["sh","-c", "\
#     mkdir -p /var/spool/squid && \
#     chown -R proxy:proxy /var/spool/squid && \
#     squid -Nz && \
#     squid -NYCd 1 & \
#     export HTTP_PROXY=http://127.0.0.1:3128 HTTPS_PROXY=http://127.0.0.1:3128 && \
#     TZ=$(curl -sf --connect-timeout 3 -m 5 https://ipapi.co/timezone || echo 'Europe/Istanbul') && \
#     ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
#     echo \"$TZ\" > /etc/timezone && \
#     dpkg-reconfigure -f noninteractive tzdata >/dev/null 2>&1 && \
#     Xvfb :99 -screen 0 1920x1080x24 & \
#     exec python -u main.py \"$@\" \
# "]

ENTRYPOINT ["sh","-c", "\
    TZ=$(curl -sf --connect-timeout 3 -m 5 https://ipapi.co/timezone || echo 'Europe/Istanbul') && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo \"$TZ\" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata >/dev/null 2>&1 && \
    Xvfb :99 -screen 0 1920x1080x24 & \
    exec python -u main.py \"$@\" \
"]

# Web arayüzü için port açıklığı
EXPOSE 5000