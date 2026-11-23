
import csv
from pathlib import Path
from collections import defaultdict


# GTFS dosyalarının bulunduğu klasör
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "gtfs"


def csv_oku(dosya_adi):
    """GTFS CSV dosyasını okuyup satırları liste olarak döndürür."""
    dosya_yolu = DATA_DIR / dosya_adi

    with open(dosya_yolu, "r", encoding="utf-8-sig", newline="") as dosya:
        okuyucu = csv.DictReader(dosya)
        return list(okuyucu)


def gtfs_verilerini_yukle():
    """GTFS verilerini okuyarak hat, durak ve güzergâh bilgilerini oluşturur."""

    # --------------------------------------------------
    # 1. GTFS dosyalarını oku
    # --------------------------------------------------
    routes = csv_oku("routes.txt")
    stops = csv_oku("stops.txt")
    trips = csv_oku("trips.txt")
    stop_times = csv_oku("stop_times.txt")

    # --------------------------------------------------
    # 2. Hat bilgilerini hazırla
    # --------------------------------------------------
    hat_sozlugu = {}

    for route in routes:
        route_id = route["route_id"]

        hat_sozlugu[route_id] = route

    hatlar = []

    for route_id, route in hat_sozlugu.items():
        hatlar.append({
            "kod": route.get("route_short_name", "").strip(),
            "ad": route.get("route_long_name", "").strip(),
            "route_id": route_id
        })

    # --------------------------------------------------
    # 3. Durak bilgilerini hazırla
    # --------------------------------------------------
    durak_sozlugu = {}

    for stop in stops:
        stop_id = stop["stop_id"]

        durak_sozlugu[stop_id] = {
            "durak_no": stop_id,
            "ad": stop.get("stop_name", "").strip(),
            "enlem": stop.get("stop_lat", ""),
            "boylam": stop.get("stop_lon", "")
        }

    duraklar = list(durak_sozlugu.values())

    # --------------------------------------------------
    # 4. Sefer bilgilerini hazırla
    # --------------------------------------------------
    sefer_sozlugu = {}

    for trip in trips:
        trip_id = trip["trip_id"]

        sefer_sozlugu[trip_id] = {
            "route_id": trip["route_id"],
            "direction_id": trip.get("direction_id", "0")
        }

    # --------------------------------------------------
    # 5. Durak geçişlerini sefer bazında sırala
    # --------------------------------------------------
    sefer_duraklari = defaultdict(list)

    for kayit in stop_times:
        trip_id = kayit["trip_id"]

        if trip_id not in sefer_sozlugu:
            continue

        sefer_duraklari[trip_id].append({
            "durak_id": kayit["stop_id"],
            "durak_sirasi": int(kayit["stop_sequence"])
        })

    # --------------------------------------------------
    # 6. Aynı güzergâha sahip seferleri grupla
    # --------------------------------------------------
    guzergah_gruplari = {}

    for trip_id, durak_kayitlari in sefer_duraklari.items():

        sefer_bilgisi = sefer_sozlugu[trip_id]

        route_id = sefer_bilgisi["route_id"]
        yon_id = sefer_bilgisi["direction_id"]

        sirali_duraklar = sorted(
            durak_kayitlari,
            key=lambda x: x["durak_sirasi"]
        )

        durak_idleri = tuple(
            kayit["durak_id"]
            for kayit in sirali_duraklar
        )

        grup_anahtari = (route_id, yon_id, durak_idleri)

        guzergah_gruplari[grup_anahtari] = True

    # --------------------------------------------------
    # 7. Güzergâh listesini oluştur
    # --------------------------------------------------
    guzergahlar = []

    for route_id, yon_id, durak_idleri in guzergah_gruplari:

        if route_id not in hat_sozlugu:
            continue

        route = hat_sozlugu[route_id]

        # GTFS içinde bulunmayan durakları atla
        if not all(durak_id in durak_sozlugu for durak_id in durak_idleri):
            continue

        guzergahlar.append({
            "kod": route.get("route_short_name", "").strip(),
            "ad": route.get("route_long_name", "").strip(),
            "route_id": route_id,
            "direction_id": yon_id,
            "durak_idleri": list(durak_idleri),
            "duraklar": [
                durak_sozlugu[durak_id]["ad"]
                for durak_id in durak_idleri
            ]
        })

    return hatlar, duraklar, guzergahlar


# --------------------------------------------------
# Dosya doğrudan çalıştırılırsa veri sayısını göster
# --------------------------------------------------
if __name__ == "__main__":

    hatlar, duraklar, guzergahlar = gtfs_verilerini_yukle()

    print("GTFS VERİLERİ YÜKLENDİ")
    print("---------------------")
    print("Hat sayısı:", len(hatlar))
    print("Durak sayısı:", len(duraklar))
    print("Güzergâh sayısı:", len(guzergahlar))

    if guzergahlar:
        print("\nÖrnek güzergâh:")
        print(guzergahlar[0])
