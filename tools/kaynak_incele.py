
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://erzurum.kentkart.com/sefer"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

html = response.text
soup = BeautifulSoup(html, "html.parser")

print("HTTP DURUMU:", response.status_code)
print("SAYFA BAŞLIĞI:", soup.title.get_text(strip=True) if soup.title else "Bulunamadı")

print("\n--- JAVASCRIPT DOSYALARI ---")

for script in soup.find_all("script", src=True):
    print(urljoin(URL, script["src"]))

print("\n--- FORM VE ARAMA ALANLARI ---")

for form in soup.find_all("form"):
    print("Form:", form.get("action"))
    print("Method:", form.get("method"))

    for item in form.find_all(["input", "select", "button"]):
        print({
            "tag": item.name,
            "name": item.get("name"),
            "id": item.get("id"),
            "type": item.get("type"),
            "value": item.get("value")
        })

print("\n--- VERİ KAYNAĞI OLABİLECEK ADRESLER ---")

patterns = [
    r'https?://[^"\']+',
    r'[^"\']*(?:api|durak|hat|stop|route)[^"\']*'
]

bulunan = set()

for pattern in patterns:
    bulunan.update(re.findall(pattern, html, re.IGNORECASE))

for item in sorted(bulunan):
    print(item[:300])

# Ham HTML dosyasını incelemek için kaydet
with open("kentkart_sayfa.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\nİnceleme tamamlandı. HTML dosyası kaydedildi.")
