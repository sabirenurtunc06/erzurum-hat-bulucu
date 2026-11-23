
import re
import requests
from urllib.parse import urljoin

BASE_URL = "https://erzurum.kentkart.com/sefer"

JS_FILES = [
    "https://erzurum.kentkart.com/scripts.dc30bdbae7c6dccef0c1.js",
    "https://erzurum.kentkart.com/main-es2015.19ef324f49968f58b7e9.js",
    "https://erzurum.kentkart.com/main-es5.19ef324f49968f58b7e9.js",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS = [
    "api",
    "durak",
    "hat",
    "stop",
    "route",
    "sefer",
    "baseurl",
    "base_url",
    "kentkart"
]

bulunanlar = set()

for js_url in JS_FILES:

    print("\n" + "=" * 70)
    print("DOSYA:", js_url)
    print("=" * 70)

    try:
        response = requests.get(
            js_url,
            headers=HEADERS,
            timeout=40
        )

        response.raise_for_status()
        kod = response.text

        print("HTTP:", response.status_code)
        print("Dosya boyutu:", len(kod), "karakter")

        # URL ve API adreslerini ara
        stringler = re.findall(
            r"""["']([^"'\\]{3,300})["']""",
            kod
        )

        for ifade in stringler:

            ifade_kucuk = ifade.lower()

            if any(k in ifade_kucuk for k in KEYWORDS):

                if ifade not in bulunanlar:
                    bulunanlar.add(ifade)
                    print("BULUNDU:", ifade[:250])

        # JavaScript içindeki tam URL'leri ara
        urls = re.findall(
            r'https?://[^\s"\'<>]+',
            kod
        )

        for url in urls:
            if url not in bulunanlar:
                bulunanlar.add(url)
                print("URL:", url[:250])

    except requests.RequestException as hata:
        print("İndirme hatası:", hata)


with open(
    "kentkart_api_adaylari.txt",
    "w",
    encoding="utf-8"
) as f:

    for ifade in sorted(bulunanlar):
        f.write(ifade + "\n")

print("\n" + "=" * 70)
print("İNCELEME TAMAMLANDI")
print("Bulunan ifade sayısı:", len(bulunanlar))
print("Sonuçlar kentkart_api_adaylari.txt dosyasına kaydedildi.")
