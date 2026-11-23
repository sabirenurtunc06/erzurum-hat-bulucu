
"""
Erzurum Otobüs Hattı Bulucu — FastAPI uygulaması.

Kullanıcı bir durak adı yazarak o duraktan geçen hatları,
ya da nereden-nereye yazarak iki durağı da güzergâhına alan hatları sorgular.
"""
import math
from pathlib import Path

from app.gtfs_loader import gtfs_verilerini_yukle

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# FastAPI uygulaması
app = FastAPI(
    title="Erzurum Otobüs Hattı Bulucu",
    version="1.0.0"
)


# Türkçe karakter uyumlu normalizasyon
def normalize(text: str) -> str:
    """Türkçe karakterlere duyarlı, büyük/küçük harf bağımsız arama yapar."""

    text = text.replace("İ", "i").replace("I", "ı")
    return text.lower().strip()

# GTFS dosyalarından gerçek hat ve durak verilerini yükle
HATLAR, DURAKLAR, GUZERGAHLAR = gtfs_verilerini_yukle()


# Bir duraktan geçen hatları bulma
def duraktan_gecen_hatlar(sorgu: str) -> list[dict]:

    q = normalize(sorgu)
    sonuc = []
    eklenen_hatlar = {}

    # Aranan durakları DURAKLAR listesinden bul.
    eslesen_duraklar = {
        str(d["durak_no"]): d["ad"]
        for d in DURAKLAR
        if all(
            kelime in normalize(d["ad"])
            for kelime in q.split()
        )
    }

    # Gerçek güzergâhları kontrol et.
    for hat in GUZERGAHLAR:

        eslesen_hat_duraklari = []

        for durak_id, durak_adi in zip(
            hat["durak_idleri"],
            hat["duraklar"]
        ):
            if durak_id in eslesen_duraklar:
                if durak_adi not in eslesen_hat_duraklari:
                    eslesen_hat_duraklari.append(durak_adi)

        if not eslesen_hat_duraklari:
            continue

        route_id = hat["route_id"]

        if route_id not in eklenen_hatlar:
            yeni_hat = {
                "kod": hat["kod"],
                "ad": hat["ad"],
                "eslesen_duraklar": []
            }

            eklenen_hatlar[route_id] = yeni_hat
            sonuc.append(yeni_hat)

        mevcut_hat = eklenen_hatlar[route_id]

        for durak in eslesen_hat_duraklari:
            if durak not in mevcut_hat["eslesen_duraklar"]:
                mevcut_hat["eslesen_duraklar"].append(durak)

    return sonuc
# Ana sayfa
@app.get("/")
def ana_sayfa():

    return FileResponse(
        Path(__file__).parent / "static" / "index.html"
    )


# Bütün hatları listeleme
@app.get("/api/hatlar")
def tum_hatlar():
    """Tüm hatları listeler."""

    return {
        "hat_sayisi": len(HATLAR),
        "hatlar": HATLAR
    }


# Durak adına göre hat arama
@app.get("/api/durak")
def durak_ara(
    q: str = Query(
        ...,
        min_length=2,
        description="Durak veya mahalle adı"
    )
):

    sonuc = duraktan_gecen_hatlar(q)

    return {
        "sorgu": q,
        "sonuc_sayisi": len(sonuc),
        "hatlar": sonuc
    }


# Hat koduna göre güzergâh görüntüleme
@app.get("/api/hat")
def hat_detay(
    kod: str = Query(
        ...,
        description="Hat kodu, ör. G4/A"
    )
):
    """Hat kodunu alır, hattın duraklarını sırayla döndürür."""

    q = normalize(kod)

    for hat in HATLAR:

        if normalize(hat["kod"]) != q:
            continue

        # Bu hatta ait güzergâhlar (yönler).
        yonler = [
            {
                "yon_id": g["direction_id"],
                "duraklar": g["duraklar"]
            }
            for g in GUZERGAHLAR
            if g["route_id"] == hat["route_id"]
        ]

        # En uzun güzergâhı ana durak listesi olarak göster.
        ana = max(yonler, key=lambda y: len(y["duraklar"]), default=None)

        return {
            **hat,
            "duraklar": ana["duraklar"] if ana else [],
            "yonler": yonler
        }

    return {
        "hata": f"'{kod}' kodlu hat bulunamadı"
    }


@app.get("/api/guzergah")
def guzergah_ara(
    nereden: str = Query(
        ...,
        min_length=2,
        description="Bulunulan durak"
    ),
    nereye: str = Query(
        ...,
        min_length=2,
        description="Gidilecek durak veya bölge"
    )
):
    """İki durak arasında doğru sırayla ilerleyen aktarmasız hatları bulur."""

    nereden_q = normalize(nereden)
    nereye_q = normalize(nereye)

    sonuc = []
    hat_indeksleri = {}

    for hat in GUZERGAHLAR:
        duraklar = hat["duraklar"]

        kalkis_indeksleri = [
            i for i, durak in enumerate(duraklar)
            if nereden_q in normalize(durak)
        ]

        varis_indeksleri = [
            i for i, durak in enumerate(duraklar)
            if nereye_q in normalize(durak)
        ]

        for kalkis_i in kalkis_indeksleri:
            for varis_i in varis_indeksleri:

                # Varış durağı kalkıştan sonra gelmeli.
                if kalkis_i >= varis_i:
                    continue

                kalkis = duraklar[kalkis_i]
                varis = duraklar[varis_i]

                route_id = hat["route_id"]

                # Aynı hat daha önce eklendiyse mevcut sonuca ulaş.
                if route_id not in hat_indeksleri:
                    hat_indeksleri[route_id] = len(sonuc)

                    sonuc.append({
                        "kod": hat["kod"],
                        "ad": hat["ad"],
                        "yon_id": hat["direction_id"],
                        "nereden_durak": kalkis,
                        "nereye_durak": varis,
                        "durak_eslesmeleri": []
                    })

                mevcut_hat = sonuc[hat_indeksleri[route_id]]

                eslesme = {
                    "nereden_durak": kalkis,
                    "nereye_durak": varis
                }

                # Aynı durak eşleşmesini tekrar ekleme.
                if eslesme not in mevcut_hat["durak_eslesmeleri"]:
                    mevcut_hat["durak_eslesmeleri"].append(eslesme)

    mesaj = (
        f"{nereden} → {nereye} için {len(sonuc)} farklı hat bulundu."
        if sonuc
        else f"{nereden} → {nereye} için aktarmasız hat bulunamadı."
    )

    return {
        "nereden": nereden,
        "nereye": nereye,
        "sonuc_sayisi": len(sonuc),
        "hatlar": sonuc,
        "mesaj": mesaj
    }


# Durak numarasına veya adına göre durak arama
@app.get("/api/durak-hatlari")
def durak_hatlari(
    q: str = Query(
        ...,
        min_length=1,
        description="Durak numarası veya durak adı"
    )
):
    """Durak numarası veya adına göre durakları listeler."""

    q_norm = normalize(q)
    sonuc = []

    for durak in DURAKLAR:

        durak_no = str(durak.get("durak_no", ""))
        durak_adi = durak.get("ad", "")

        if (
            q_norm in normalize(durak_no)
            or q_norm in normalize(durak_adi)
        ):
            sonuc.append(durak)

    mesaj = (
        f"{q} için {len(sonuc)} durak bulundu."
        if sonuc
        else f"{q} için durak bulunamadı."
    )

    return {
        "sorgu": q,
        "sonuc_sayisi": len(sonuc),
        "duraklar": sonuc,
        "mesaj": mesaj
    }


# Hedef adına veya mahalleye göre durak arama
@app.get("/api/hedef-ara")
def hedef_ara(
    q: str = Query(
        ...,
        min_length=2,
        description="Hedef yeri veya bölge"
    )
):
    """Hedef adına göre uygun durakları listeler."""

    q_norm = normalize(q)
    sonuc = []

    for durak in DURAKLAR:

        durak_adi = durak.get("ad", "")
        mahalle = durak.get("mahalle", "")

        if (
            q_norm in normalize(durak_adi)
            or q_norm in normalize(mahalle)
        ):
            sonuc.append(durak)

    mesaj = (
        f"{q} için {len(sonuc)} hedef bulundu."
        if sonuc
        else f"{q} için uygun hedef bulunamadı."
    )

    return {
        "sorgu": q,
        "sonuc_sayisi": len(sonuc),
        "hedefler": sonuc,
        "mesaj": mesaj
    }

# İki koordinat arasındaki mesafeyi metre cinsinden hesaplama
def mesafe_hesapla(lat1, lon1, lat2, lon2):
    yaricap = 6371000

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    return 2 * yaricap * math.asin(math.sqrt(a))


# Kullanıcının konumuna en yakın durakları bulma
@app.get("/api/yakindaki-duraklar")
def yakindaki_duraklar(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    limit: int = Query(5, ge=1, le=20)
):
    sonuc = []

    for durak in DURAKLAR:
        try:
            mesafe = mesafe_hesapla(
                lat, lon,
                durak["enlem"],
                durak["boylam"]
            )

            sonuc.append({
                **durak,
                "mesafe_metre": round(mesafe)
            })

        except (ValueError, TypeError, KeyError):
            continue

    sonuc.sort(key=lambda x: x["mesafe_metre"])

    return {
        "durak_sayisi": min(len(sonuc), limit),
        "duraklar": sonuc[:limit]
    }


# Durak numarasına göre o duraktan geçen hatları bulma
@app.get("/api/durak-no-hatlari")
def durak_no_hatlari(
    durak_no: str = Query(..., min_length=1)
):
    secilen_durak = next(
        (
            d for d in DURAKLAR
            if str(d["durak_no"]) == str(durak_no)
        ),
        None
    )

    if secilen_durak is None:
        return {
            "durak": None,
            "sonuc_sayisi": 0,
            "hatlar": [],
            "mesaj": "Durak bulunamadı."
        }

    sonuc = []
    eklenen_hatlar = {}

    for hat in GUZERGAHLAR:
        if str(durak_no) not in [
            str(d) for d in hat["durak_idleri"]
        ]:
            continue

        route_id = hat["route_id"]

        if route_id not in eklenen_hatlar:
            yeni_hat = {
                "kod": hat["kod"],
                "ad": hat["ad"],
                "eslesen_duraklar": []
            }

            eklenen_hatlar[route_id] = yeni_hat
            sonuc.append(yeni_hat)

        mevcut_hat = eklenen_hatlar[route_id]

        if secilen_durak["ad"] not in mevcut_hat["eslesen_duraklar"]:
            mevcut_hat["eslesen_duraklar"].append(
                secilen_durak["ad"]
            )

    return {
        "durak": secilen_durak,
        "sonuc_sayisi": len(sonuc),
        "hatlar": sonuc,
        "mesaj": (
            f"{secilen_durak['ad']} durağından "
            f"{len(sonuc)} farklı hat geçiyor."
            if sonuc
            else "Bu duraktan geçen hat bulunamadı."
        )
    }
# Statik dosyaları bağlama
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static"
)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
