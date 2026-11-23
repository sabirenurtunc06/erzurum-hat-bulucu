
import requests

URL = "https://service.kentkart.com/rl1/web/nearest/find"

parametreler = {
    "region": "038",
    "lang": "tr"
}

basliklar = {
    "User-Agent": "KentkartGTFSGenerator/1.0",
    "Accept": "application/json"
}

try:
    cevap = requests.get(
        URL,
        params=parametreler,
        headers=basliklar,
        timeout=30
    )

    print("HTTP DURUMU:", cevap.status_code)
    print("İSTEK URL:", cevap.url)
    print("CONTENT TYPE:", cevap.headers.get("Content-Type"))
    print("SUNUCU YANITI:", cevap.text[:1500])

    if cevap.status_code == 200:
        veri = cevap.json()

        print("\nGELEN VERİNİN TAMAMI:")
        print(veri)

        print("\nVERİ TİPİ:", type(veri))

        if isinstance(veri, dict):
            print("\nANAHTARLAR:", list(veri.keys()))

    else:
        print("\nİstek reddedildi. Henüz veri alınamadı.")

except requests.RequestException as hata:
    print("BAĞLANTI HATASI:", hata)
