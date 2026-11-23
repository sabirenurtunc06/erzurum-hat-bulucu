"""API kabul kriterlerini doğrulayan testler. Çalıştırmak için: python -m pytest -v"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def kodlar(cevap):
    return [h["kod"] for h in cevap.json()["hatlar"]]


def test_durak_arama_universite():
    """Görev 2: 'üniversite' aramasında G1, G4/A ve K3 dahil en az 3 hat döner."""
    cevap = client.get("/api/durak", params={"q": "üniversite"})
    assert cevap.status_code == 200
    assert cevap.json()["sonuc_sayisi"] >= 3
    assert {"G1", "G4/A", "K3"} <= set(kodlar(cevap))


def test_durak_arama_turkce_karakter():
    """İ/ı, I/i farkı arama sonucunu bozmamalı."""
    assert "G4/A" in kodlar(client.get("/api/durak", params={"q": "İSTASYON"}))
    assert "G4/A" in kodlar(client.get("/api/durak", params={"q": "istasyon"}))


def test_durak_arama_sonuc_yok():
    cevap = client.get("/api/durak", params={"q": "xyztuv"})
    assert cevap.status_code == 200
    assert cevap.json()["sonuc_sayisi"] == 0
    assert cevap.json()["hatlar"] == []


def test_guzergah_istasyon_universite():
    """Görev 4: İstasyon → Üniversite için G4/A döner."""
    cevap = client.get(
        "/api/guzergah", params={"nereden": "İstasyon", "nereye": "Üniversite"}
    )
    assert cevap.json()["sonuc_sayisi"] >= 1
    assert "G4/A" in kodlar(cevap)


def test_guzergah_bulunamadi():
    cevap = client.get(
        "/api/guzergah", params={"nereden": "Yakutiye 132", "nereye": "xyztuv"}
    )
    veri = cevap.json()
    assert veri["sonuc_sayisi"] == 0
    assert "bulunamadı" in veri["mesaj"]


def test_hat_detay():
    """Görev 3: hat koduyla duraklar sırayla döner."""
    veri = client.get("/api/hat", params={"kod": "G4/A"}).json()
    assert veri["kod"] == "G4/A"
    assert len(veri["duraklar"]) > 5
    assert veri["duraklar"][0] == "İSTASYON SEVK İDARE MERKEZİ"


def test_hat_detay_bulunamadi():
    assert client.get("/api/hat", params={"kod": "YOK"}).json().get("hata")


def test_tum_hatlar():
    assert client.get("/api/hatlar").json()["hat_sayisi"] >= 10


def test_durak_hatlari_132():
    veri = client.get("/api/durak-hatlari", params={"q": "132"}).json()
    assert veri["sonuc_sayisi"] > 0
    assert any("132" in d["ad"] for d in veri["duraklar"])


def test_hedef_ara_universite():
    veri = client.get("/api/hedef-ara", params={"q": "Üniversite"}).json()
    assert veri["sonuc_sayisi"] > 0
    assert any("ÜNİVERSİTE" in d["ad"] for d in veri["hedefler"])


def test_yakindaki_duraklar():
    veri = client.get("/api/yakindaki-duraklar", params={"lat": 39.9, "lon": 41.27}).json()
    assert veri["durak_sayisi"] == 5
    mesafeler = [d["mesafe_metre"] for d in veri["duraklar"]]
    assert mesafeler == sorted(mesafeler)
