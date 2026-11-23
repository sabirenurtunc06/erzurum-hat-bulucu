# 📋 Pano Görevleri ve Kabul Kriterleri

Pano sütunları: **Yapılacak → Devam Ediyor → Tamamlandı**. Kart güncellendiğinde ilgili commit/PR bağlantısı karta yorum olarak eklenir; kabul kriteri doğrulanınca kart "Tamamlandı"ya taşınır.

## ✅ Tamamlandı

### 1. Duraktan geçen hatları listeleme
**Açıklama:** Kullanıcı durak veya mahalle adı yazınca o duraktan geçen hatlar listelensin (web arayüzü + API).
**Kabul kriteri:** "Üniversite" araması G1, G4/A ve K3 dahil en az 3 hat döndürür; sonuç yoksa anlamlı mesaj gösterilir.
**Test:** `test_durak_arama_universite`, `test_durak_arama_sonuc_yok`

### 2. Nereden-nereye hat bulma
**Açıklama:** Başlangıç ve varış yeri yazılınca iki durağı da doğru sırayla geçen aktarmasız hatlar önerilsin.
**Kabul kriteri:** "İstasyon → Üniversite" en az bir hat (G4/A) döndürür; çözüm yoksa "aktarmasız hat bulunamadı" mesajı gösterilir.
**Test:** `test_guzergah_istasyon_universite`, `test_guzergah_bulunamadi`

## 📝 Yapılacak

### 3. Gidiş ve dönüş yönlerinin ayrıştırılması
**Açıklama:** Aynı hattın gidiş ve dönüş güzergâhları ayrı listelensin.
**Kabul kriteri:** Kullanıcı seçtiği hattın iki yöndeki durak sıralamasını arayüzde ayrı ayrı görebilir.

### 4. Harita üzerinde güzergâh gösterimi
**Açıklama:** Seçilen hattın durakları ve güzergâhı harita üzerinde gösterilsin.
**Kabul kriteri:** Hat seçilince o hatta ait duraklar haritada işaretli görünür.

### 5. Eksik veya hatalı durak bilgisi bildirme
**Açıklama:** Kullanıcılar eksik durak adı, numarası veya hat bilgisini bildirebilsin.
**Kabul kriteri:** Gönderilen bildirim kaydedilir ve sonradan görüntülenebilir.
