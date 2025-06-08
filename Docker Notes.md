# Recon Tool Docker Kılavuzu

## 📋 Ön Koşullar
- [Docker Desktop](https://www.docker.com/products/docker-desktop) kurulu olmalı
- Proje kökünde `.env` dosyası (yoksa shodan ve github aramaları atlanır)

## ⚙️ Komut Referansı

| Komut                             | Açıklama                                                       |
|-----------------------------------|----------------------------------------------------------------|
| `docker-compose up --build`       | Build et ve çalıştır                                           |
| `docker-compose build --no-cache` | Cache kullanmadan build, yeni program eklendiyse kullan        |
| `docker-compose down`             | Tüm konteynırları durdur ve sil                                |


`sudo docker compose run --rm recon -- --no-gui --url example.com`
No GUI modda çalıştırmak için araya "--" koymak gerekiyor

## Uyarılar

Apt ile program kurmak gerekiyorsa ilgili run komutunu genişlet, yeni RUN açma.
Sebepleri:
- Layer Yönetimi:
Her RUN komutu yeni bir katman oluşturur. Paket güncellemeleri ve kurulumları tek bir katmanda toplandığında, imaj boyutu küçülür ve gereksiz cache kalıntılarından kaçınılır.
- Güncelleme Tutarlılığı:
Tek bir RUN apt-get update && apt-get install ... komutunda, paket listeleri güncel kalırken kuruluma geçilir. Ayrı komutlarda, güncelleme sonrasında paket listeleri eskiyebilir.
- Temizlik:
Kurulumdan sonra apt cache'in temizlenmesi, imaj boyutunu azaltır. Bu temizleme işlemini tek bir komut içerisinde yapmak daha etkili olur.
