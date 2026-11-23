# 🚌 Erzurum Otobüs Hattı Bulucu

## Hangi problemi çözüyor? Kimin için?
Bir Endüstri Mühendisliği öğrencisi olarak Erzurum'daki duraklarda saha gözlemi yaptım. Birçok durakta hat listesinin yırtık, eksik veya okunamaz olduğunu, bazı duraklarda ise durak adı ve numarasının hiç bulunmadığını gördüm. Bu durumda yolcu, hangi durakta olduğunu ve gideceği yere hangi hatla ulaşabileceğini öğrenemiyor.

Sorun en çok Erzurum'a yeni gelen öğrencileri, ziyaretçileri ve şehri tanımayan yolcuları etkiliyor. Gözlemime göre mevcut uygulamalar ilk kullanımda anlaşılması zor olabiliyor, özellikle hattın hangi yönde gittiği (gidiş/dönüş) yeni gelen biri için net değil.

**Erzurum Otobüs Hattı Bulucu**, bu kullanıcılar için sade bir araçtır:
- **Şu an:** durak adı veya numarasıyla o duraktan geçen hatları bulma, GPS ile yakındaki durakları görme, "nereden-nereye" aramasıyla aktarmasız hat bulma.
- **Planlanan:** gidiş/dönüş yönlerinin ayrı gösterimi, harita üzerinde güzergâh, eksik veya hatalı durak bilgisi bildirme ([panoya git](https://github.com/users/sabirenurtunc06/projects/1)

## 📋 İş takip panosu
👉 **Pano:** https://github.com/users/sabirenurtunc06/projects/1
Görev listesi ve kabul kriterleri: [PANO.md](PANO.md)

## Teknolojiler
Python 3.10+, FastAPI, GTFS verisi (`data/gtfs/`), tek sayfalık HTML/JS arayüz.

## Projeyi çalıştırma
```bash
git clone https://github.com/sabirenurtunc06/erzurum-hat-bulucu.git
cd erzurum-hat-bulucu
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```
Tarayıcıda http://127.0.0.1:8000 adresini aç. API dokümantasyonu: http://127.0.0.1:8000/docs

## Geliştirilen iki özelliği deneme

### Özellik 1 — Duraktan geçen hatları listeleme
1. Ana sayfada **Durak Bul → Durak Adıyla Bul** seçeneğini aç.
2. Kutuya `Üniversite` yaz ve **Ara**'ya bas.
3. Beklenen: G1, G4/A ve K3 dahil en az 3 hat listelenir. `xyztuv` gibi anlamsız bir arama için "Sonuç bulunamadı" mesajı çıkar.
4. API ile: `GET /api/durak?q=üniversite`

### Özellik 2 — Nereden-nereye aktarmasız hat bulma
1. **Nereden Nereye** sekmesine geç.
2. Nereden: `İstasyon`, Nereye: `Üniversite` yaz ve **Bul**'a bas.
3. Beklenen: G4/A dahil en az bir hat önerilir. Çözümü olmayan bir arama için "aktarmasız hat bulunamadı" mesajı gösterilir.
4. API ile: `GET /api/guzergah?nereden=istasyon&nereye=üniversite`

## Testler
```bash
python -m pytest -q
```

## Veri kaynağı
GTFS dosyaları Erzurum Kentkart sefer verisinden alınmıştır. `tools/` klasöründeki betikler veri kaynağını incelemek için kullanılmıştır, uygulamanın çalışması için gerekli değildir.


## Docker ile çalıştırma (isteğe bağlı)
```bash
docker compose up --build
```
Ardından http://localhost:8000 adresini aç.
