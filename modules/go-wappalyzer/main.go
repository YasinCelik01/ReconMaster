package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"

	wappalyzer "github.com/projectdiscovery/wappalyzergo"
)

func main() {
	target := flag.String("url", "", "target URL (include http:// or https://)")
	flag.Parse()

	if *target == "" {
		log.Fatal("–url parametresi gerekli")
	}

	resp, err := http.Get(*target)
	if err != nil {
		log.Fatalf("HTTP isteği başarısız: %v", err)
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Response body okunamadı: %v", err)
	}

	client, err := wappalyzer.New()
	if err != nil {
		log.Fatalf("Wappalyzer client oluşturulamadı: %v", err)
	}

	fps := client.Fingerprint(resp.Header, body)

	// JSON çıktısı
	out, err := json.MarshalIndent(fps, "", "  ")
	if err != nil {
		log.Fatalf("JSON serileştirme hatası: %v", err)
	}
	fmt.Println(string(out))
}
