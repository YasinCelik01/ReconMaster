# Recon Tool Docker Kılavuzu

## 📋 Ön Koşullar
- [Docker Desktop](https://www.docker.com/products/docker-desktop) kurulu olmalı
- Proje kökünde `.env` dosyası (yoksa shodan ve github aramaları atlanır)

## ⚙️ Komut Referansı

| Komut                             | Açıklama                                                       |
|-----------------------------------|----------------------------------------------------------------|
| `docker-compose up`               | Çalıştırmak                                                    |
| `docker-compose up --build`       | Build et ve çalıştır, script'teki değişiklik yansımadıysa      |
| `docker-compose build`            | Normal build, çalıştırmadan                                    |
| `docker-compose build --no-cache` | Cache kullanmadan build, yeni program eklendiyse kullan        |
| `docker-compose down`             | Tüm konteynırları durdur ve sil                                |

