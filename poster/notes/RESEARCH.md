# RESEARCH — kaynak tablosu (poster v1)

Okuma durumu etiketleri: READ_FULL (ilgili bölüm/tablo açılıp okundu), SNIPPET_ONLY (yalnız arama özeti),
NOT_ACCESSIBLE. Tür: MEASURED-field / MEASURED-lab / VENDOR / REGULATION / MODEL / ASSUMPTION.
Hiçbir satır "doğrulandı" anlamına gelmez; doğrulamayı kullanıcı yapar.

Okuma yöntemi notu: "READ_FULL (pdf)" = PDF indirildi, `pdftotext` ile ilgili bölüm metni okundu.
"READ_FULL (WF)" = sayfa WebFetch ile açıldı ve ilgili bölüm bir özetleyici model üzerinden okundu
(ham metni ben görmedim; kullanıcı kontrolünde öncelikli). "abstract" = yalnız özet sayfası okundu.
Tüm erişimler: 2026-10-06.

Sütunlar: parametre | değer+birim | kaynak | konum | tür | okuma | koşullar | P. brutia 868 MHz uygulanabilirlik | not

## R1 — Orman yol kaybı, gölgeleme (868/915 MHz; gövde ~2.5 m ve zemin ayrı)

| parametre | değer | kaynak | konum | tür | okuma | koşullar | uygulanabilirlik | not |
|---|---|---|---|---|---|---|---|---|
| Ormanda fazladan zayıflama modeli | A_ev = A_m[1 − exp(−dγ/A_m)] | ITU-R P.833-10 (09/2021), "Attenuation in vegetation", itu.int R-REC-P.833-10-202109-I | §2.1, Eq.(1) | MODEL (ölçüm derlemesi) | READ_FULL (pdf) | bir terminal orman DIŞINDA, diğeri içinde d metre | Düşük: bizim mesh'te iki terminal de orman içinde ve yere yakın; §2.1 bu geometriyi kapsamıyor | P.833-10 yürürlükte; poster P.833-9 diyor (#34) |
| γ, A_m @ 949 MHz | γ = 0.17 dB/m, A_m = 26.5 dB | ITU-R P.833-10 | §2.1, Tablo 1 | MEASURED-field (derleme) | READ_FULL (pdf) | St. Petersburg karışık iğne/geniş yapraklı orman, ağaç boyu ~16 m, yol 0.4–7 km, eğik polarizasyon | Orta-düşük: frekans yakın, orman tipi ve geometri farklı | |
| A_m = A1·f^α | Rio: A1=0.18, α=0.752 (Rx 2.4 m); Mulhouse: A1=1.15, α=0.43 (Rx 1.6 m, σ=8.7 dB); St. Petersburg: A1=1.37, α=0.42 (Rx 1.5 m) | ITU-R P.833-10 | §2.1, Eq.(2) ve maddeler | MEASURED-field (derleme) | READ_FULL (pdf) | 900–2200 MHz, Tx dışarıda (ör. 25 m) | Düşük (geometri) | f=868 MHz için A_m ≈ 0.18·868^0.752 ≈ 29 dB; 1.15·868^0.43 ≈ 21 dB (benim hesabım) |
| "10–15 dB arka gövde gölgesi" | — | ITU-R P.833-10 | tüm metinde "trunk" yalnız §2.1'de (dikey polarizasyonda gövde saçılması) geçiyor | — | READ_FULL (pdf) | — | — | **NOT FOUND in P.833-10**: posterdeki atıf (P.833 → 10–15 dB) desteklenmiyor (#21) |
| Gövde başına zayıflama | SF7 7.58, SF8 7.04, SF9 5.35, SF10 5.02, SF11 5.01, SF12 5.00 dB | Anzum ve ark., Sensors 22(14):5397, 2022, doi 10.3390/s22145397 | Tablo 5 | MEASURED-field | READ_FULL (WF) | 433 MHz, Malezya palmiye plantasyonu, Tx 3 m / Rx 1.5 m | Düşük (frekans, tür) | Kanopi başına 5.45–9.32 dB; LoS n = 2.34 (BW125/250), 2.9 (BW500), Tablo 4 |
| Orman yol kaybı üssü | n = 3.22 (orman), 2.31 (LoS); orman fazlası ~25 dB @1.2 km | Boonlom ve ark., Sensors 26(10):3192, 2026, doi 10.3390/s26103192 | Model denklemleri (sayfa özeti) | MEASURED-field | READ_FULL (WF) | 923 MHz, Tayland tropik orman (ağaç 5–8 m), Tx 1.7 m, gateway 8 m, SF10, 50 m–1.2 km | Orta-düşük: frekans yakın; ağaç tipi ve gateway yüksekliği farklı | Gövde montajlı düğüm ↔ yüksek gateway için en yakın veri |
| Orman menzili | SF12'de en fazla 250 m (RSSI −124 dBm); ilk 150 m'de keskin düşüş | Ferreira ve ark., Ann. Telecommun. 75:333–351, 2020, doi 10.1007/s12243-020-00789-w | §5.1.1 | MEASURED-field | READ_FULL (pdf) | 915 MHz, BW 500 kHz, 14 dBm, 7 dBi anten, Brezilya yağmur ormanı | Düşük | Anten yüksekliği metinde bulunamadı |
| Yere yakın 868 MHz | Yol kaybı üssü verilmiyor; model RMSE (orman, 868 MHz): ANFIS 1.46, optimize FITU-R 4.08, Okumura-Hata 6.32 dB | Hakim ve ark., Sensors 22(9):3267, 2022, doi 10.3390/s22093267 | Tablo 2–3 | MEASURED-field | READ_FULL (WF) | 433/868/920 MHz, anten < 30 cm, 5–100 m, Cakarta çevresi tropik orman | Düşük-orta (zemin geometrisi uygun, orman tipi farklı, 100 m ile sınırlı) | |
| Wu ve ark. 2020 (n ≈ 2.5–4.2, σ ≈ 5 dB, yükseklik 0.5–3 m; bib notu) | — | J. Sensors 2020:2687148, doi 10.1155/2020/2687148 | — | MEASURED-field | NOT_ACCESSIBLE (Wiley 403) | Doğu Çin karma orman; frekans doğrulanamadı (CN470 olabilir) | Bilinmiyor | Posterin n=3.5–4.5 dayanağı; kullanıcı kontrol etmeli |
| Azevedo & Santos 2011 (gövde seviyesi model) | yalnız özet: zayıflama, ağaç yoğunluğu × ortalama gövde çapına bağlı | IEEE TAP 59(6):2357–2367, doi 10.1109/TAP.2011.2143664 | özet | MEASURED-field | READ_FULL (abstract) | frekans/yükseklik özetten okunamadı | Potansiyel olarak yüksek (iki terminal orman içinde, gövde seviyesi) | Tam metin alınmalı |
| **P. brutia / Akdeniz çamı, 868 MHz, gövde 2.5 m veya zemin, yol kaybı üssü** | **NOT FOUND** | — | — | — | — | — | — | M1 iki senaryolu ASSUMPTION ile ilerler |

## R2 — Radyo/MCU değerleri ve düzenleme

| parametre | değer | kaynak | konum | tür | okuma | koşullar | uygulanabilirlik | not |
|---|---|---|---|---|---|---|---|---|
| LoRa duyarlılığı | SF7 −124 dBm, SF12 −137 dBm (BW 125 kHz); SF8–11 tabloda YOK | Semtech SX1261/2 Datasheet Rev 1.2 (June 2019), DS.SX1261-2.W.APP | Tablo 3-8 (s. 18) | VENDOR (datasheet) | READ_FULL (pdf, sparkfun aynası) | Rx Boosted gain, ayrık RF yolu, RF anahtar kaybı hariç | STM32WL'nin radyosu SX126x tabanlı; STM32WL datasheet'i ayrı değer verebilir | params SF7 = −124.5 (0.5 dB fark); SF8–11 enterpolasyon (2.5 dB/SF) kaynakta yok |
| TX akımı +14 dBm | 45 mA (SX1262, +14 dBm optimal ayar, 868/915 MHz) | SX1261/2 DS Rev 1.2 | Tablo 3-6 (s. 16) | VENDOR | READ_FULL (pdf) | PA VBAT'tan; DC-DC çekirdek | params I_TX14 = 45 mA ile aynı | +22 dBm ayarında 14 dBm: 90 mA |
| RX akımı | 4.6 mA (LoRa 125 kHz, DC-DC); Rx Boosted 5.3 mA; LDO 8.8 / 10.1 mA | SX1261/2 DS Rev 1.2 | Tablo 3-5 (s. 15) | VENDOR | READ_FULL (pdf) | | | Duyarlılık değerleri Boosted modda; tutarlılık için RX = 5.3 mA kullanılmalı |
| Uyku akımı (radyo) | 160 nA soğuk, 600 nA sıcak başlangıç | SX1261/2 DS Rev 1.2 | Tablo 3-5 | VENDOR | READ_FULL (pdf) | | | |
| CAD süresi | 1, 2, 4, 8 veya 16 sembol seçilebilir | SX1261/2 DS Rev 1.2 | §6.1.5 | VENDOR | READ_FULL (pdf) | | | SF7 sembolü 1.024 ms (BW125) |
| STM32WLE5 Stop2+RTC | 1.07 µA (VDD = 3 V) | STM32WLE5xx datasheet DS13105 Rev 2 (Jan 2020), kapak özellikleri | s. 1 | VENDOR | SNIPPET_ONLY (radiolocman önizleme, WF) | 25 °C varsayılır; sıcaklık bağımlılığı tablosu okunamadı | | st.com zaman aşımı → tam DS NOT_ACCESSIBLE; sıcaklıkla artış değeri NOT FOUND |
| STM32WLE5 TX akımı (kapak) | 15 mA @ 10 dBm, 87 mA @ 20 dBm (LoRa 125 kHz) | DS13105 Rev 2 kapak | s. 1 | VENDOR | SNIPPET_ONLY | | 14 dBm değeri kapakta yok | |
| STM32WL AES | AES 256-bit donanım (kapak); modlar ECB, CBC, CTR, GCM, GMAC, CCM; 128/256-bit anahtar | DS13105 kapak; Embassy HAL dokümanı (aes_v2) | — | VENDOR / ikincil | SNIPPET_ONLY | | | RM0461 NOT_ACCESSIBLE; AES akımı ve çevrim sayısı (#22: 5 mA, 280 cycle) NOT FOUND |
| TAMP, RDP seviyeleri (STM32WL) | — | RM0461 / DS13105 | — | VENDOR | NOT_ACCESSIBLE | | | Posterde yalnız kaynaklı iddia kalmalı |
| Bant M (EU) | 868.000–868.600 MHz: 25 mW e.r.p., ≤%1 görev çevrimi veya polite spectrum access | ETSI EN 300 220-2 V3.2.1 (2018-06) | Ek B, Tablo B.1, satır M (karar 2017/1483/EU bant 48) | REGULATION | READ_FULL (pdf) | | | Bant P 869.40–869.65: 500 mW, ≤%10; bant N 868.7–869.2: ≤%0.1 |
| Görev çevrimi gözlem süresi | T_obs = 1 saat (aksi belirtilmedikçe) | ETSI EN 300 220-1 V3.1.1 (2017-02) | §5.4.1, §5.4.2 | REGULATION | READ_FULL (pdf) | | | %1 = saatte 36 s TX. "Her yayından sonra 99× bekleme" kuralı ETSI'de değil (LoRaWAN uygulaması) → #3 ifadesini değiştirir |
| Türkiye 868.0–868.6 MHz | 25 mW e.r.p., ≤%1 görev çevrimi veya LBT+AFA (TS EN 300 220) | BTK, "Sınıf 1 cihaz kategorileri ve frekans bandları" (teknik ölçüt), btk.gov.tr/uploads/pages/sinif1-teknik-olcut.pdf | KET tablosu satır 20 | REGULATION | READ_FULL (pdf) | belgede yürürlük tarihi okunamadı; 27/11/2018 RG 30608 atfı var | Doğrudan uygulanır | satır 22: 869.4–869.65 MHz 500 mW, ≤%10; satır 16: 863–870 MHz ≤%0.1 |
| e.r.p. uyumu | 14 dBm iletim − 2 dBi anten − 2.15 = 9.85 dBm e.r.p. < 14 dBm e.r.p. | benim hesabım (params değerleriyle) | — | DERIVED | — | | | uyumlu |

## R3 — Gaz/VOC/H2/CO2 ile tespit mesafesi ve süresi; ısı sensörü

| parametre | değer | kaynak | konum | tür | okuma | koşullar | uygulanabilirlik | not |
|---|---|---|---|---|---|---|---|---|
| H2 sensörü saha tespiti | 0.5 m² içten yanan ateş: 5 m'de 8 sensörün 6'sı (rüzgâr yönü dışındakiler yok); 25 m'de 8'in 3'ü, sinyal ~24 mV "tespit sınırının hemen üstünde"; 2 m² ateş: 25 m ve 105 m'de 3 sensör, ~115 m'de zayıf etki | Nörthemann, Bienge, Müller, Moritz, J. Sens. Sens. Syst. 2:171–177, 2013, doi 10.5194/jsss-2-171-2013 | §3 (satır 194–248), Şekil 7–9 | MEASURED-field | READ_FULL (pdf) | Almanya ormanı, sensör 1–4 m yükseklik, rüzgâr ölçülmedi/tek yönlü değil | Orta: MEIS **hidrojen** sensörü, MOx/BME688 DEĞİL | İlk sinyal ateşlemeden 5–30 dk sonra (s. 265); rüzgâr hızı arttıkça uzak tespit kolaylaşıyor |
| "MOx sensörleri 15 dk tespit için ateşe ≤25 m" önerisi | 25 m / 15 dk | Chan ve ark., "IoT Ground Sensing Systems for Early Wildfire Detection", arXiv 2312.10919v1 (2023, ©IEEE) | §(MoS sensörler), refs [70],[71] | MODEL/öneri (ikincil) | READ_FULL (pdf) | — | — | Atıf yapılan [71] Nörthemann 2013 metninde 25 m/15 dk önerisi bulunamadı (yukarı); [70] Roque & Padilla, IEEE Access 8:114900–114909, 2020 NOT_ACCESSIBLE |
| CO2 NDIR ağ, kontrollü yakma | Eşik modeli 40 m ötesinde uyarı yok; LSTM ~70 m'deki sensöre kadar; 44 sensörün 16'sı (eşik) / 26'sı (LSTM) uyarı; 10 dk içinde 3 (eşik) / 9 (LSTM) | De Rango, Furnari, Cortale, Senatore, Mendicino, Sensors 25(7):2012, 2025, doi 10.3390/s25072012 | §2.1–2.2, §3, Şekil 8–9 | MEASURED-field | READ_FULL (WF, PMC) | İtalya (Dipignano), zeytin/meşe dalı yığını ~8 m³, 110 dk yanma, rüzgâr ≤6.4 km/sa, sensör 1.5 m, 2 dk örnekleme, Milesight EM500-CO2 | Orta: Akdeniz, ama yığın ateşi (büyük kaynak) ve CO2 | |
| Ortam sensörü saha denemesi | sıcaklık/nem sensörleri 10 m'de belirgin değişim göstermedi; CO2 ve TVOC 30 m'de yanıt verdi | Chan ve ark. arXiv 2312.10919v1 | deneysel yakma bölümü | MEASURED-field | READ_FULL (WF) | 0.7 m² ateş çukuru, ~1.6 kg okaliptüs yaprağı, 10 dk + 5 dk için için yanma | Orta | r_T için önemli: 10 m'de ısı yok |
| Düğüm algılama menzili "5 m" | "after conducting many tests, the maximum sensing range of a sensor node is determined to be five meters" | Dampage ve ark., Sci. Rep. 12, 2022 (makale no. okunmadı), doi 10.1038/s41598-021-03882-9 | "Sensor node deployment" bölümü; "Results" (Fig. 14 civarı) | MEASURED-field (yöntem gösterilmemiş) | READ_FULL (pdf) | Sri Lanka tropik orman; DHT22 + LDR + CO sensörlü **çok-sensörlü** düğüm, 1 m yükseklik; veri toplama ateşleri 1 m², düğüm ateşe 1 m | Düşük-orta | "Isı 5 m'de algılanır" ifadesi kısmen destekleniyor: 5 m düğüm (T+RH+ışık+CO) menzili; nasıl ölçüldüğü gösterilmemiş (#10) |
| BME688 ULP akımı | 0.09 mA ortalama, güncelleme 300 s | Bosch BME688 Datasheet, BST-BME688-DS000-03 Rev 1.3 (Feb 2024) | Tablo 2; §(BSEC power modes) | VENDOR | READ_FULL (pdf) | VDD ≤ 1.8 V, 25 °C | params Q_GAS ile eşleşir; 3.3 V beslemede güç farklı olabilir | Isıtıcı sabit çalışmada 9–13 mA, tepe 15–18 mA |
| BME688 yanıt süresi | τ33–63%: ULP 92 s, LP 1.4 s, sürekli 0.75 s | BME688 DS Rev 1.3 | Tablo 2 | VENDOR (lab) | READ_FULL (pdf) | yeni, lehimlenmemiş sensör; EtOH/b-VOC basamağı, 20 °C, %50 RH | | ULP'de ~1.5 dk ek gecikme modele girmeli |
| Dryad tespit iddiası | "Detection within minutes from ignition (100m, 2kg fuel)"; tespit aralığı "up to 300m … or more for larger fires" | Dryad Silvanet Wildfire Sensor sayfası, dryad.net/wildfiresensor | ürün sayfası | VENDOR | READ_FULL (WF) | — | — | bib notundaki "60 dk / 2×2 m" ifadesi güncel sayfada yok |
| **BME688/MOx için ölçülmüş saha r_G (Akdeniz çamı)** | **NOT FOUND** | — | — | — | — | — | — | M3: r_G = 25/50/100 m ASSUMPTION senaryoları |
| **Isı sensörü r_T ölçümü (yalnız sıcaklık)** | **NOT FOUND** (en yakın: Chan 10 m'de yok; Dampage 5 m çok-sensörlü) | — | — | — | — | — | — | M3: r_T = 1/2/5 m ASSUMPTION |

## R4 — Yayılma hızı

| parametre | değer | kaynak | konum | tür | okuma | koşullar | uygulanabilirlik | not |
|---|---|---|---|---|---|---|---|---|
| Yüzey yangını ROS | 0.3–3.75 m/dk (aralık), alev boyu 5–55 cm, rüzgâr varyansın %72'si | Küçük ve ark., 2012 (künye REVIEW.md/bib'den, kaynak sayfasından alınmadı) ("Rates of surface fire spread in a young calabrian pine plantation") | özet | MEASURED-field | SNIPPET_ONLY (özet arama sonucu) | 35 çizgi-ateşleme deneyi, genç P. brutia plantasyonu | Yüksek (tür) ama genç plantasyon ve çizgi ateşleme | REVIEW #11: kullanıcı aralığı doğruladı; "median" yok |
| Taç yangını ROS | ~2–34 m/dk, hat şiddeti ~700–16000 kW/m | 24 deneysel ateş, 20 yaşında P. brutia plantasyonu, Meriç/Edirne, Ağustos 2007 (künye arama sonucunda yok) | özet | MEASURED-field | SNIPPET_ONLY | | Yüksek (tür) | Künye bulunmalı; Bilgili ve ark. 2006 FEM ("Fire behaviour in immature calabrian pine plantations") ayrı çalışma, ROS sayısı sayfada yok |
| Rüzgârla sürülen büyük yangın ROS | Kuyucak (İzmir) ilk dönem ortalama 5.00 km/sa (min 4.27, maks 5.71; ≈83 m/dk), sonraki dönem 0.24 km/sa; Kavakdere 1.6 km/sa; diğer ölçümler 1.99 ve 0.41 km/sa | Coskuner, Papavasileiou, Giannaros, Benali, Bilgili, Fire 9:86, 2026, doi 10.3390/fire9020086 | §3.1, Şekil 8 | MEASURED-field (uydu/ilerleme poligonu) | READ_FULL (pdf) | 29–30 Haziran 2025, KD rüzgâr 40–50 km/sa, ölü ince yakıt nemi <%6, P. brutia | Yüksek (tür, bölge) ama gelişmiş yangın, erken faz değil | Modelin erken-faz rejiminin dışında; posterde sınırlama olarak |
| Manavgat 2021 | ~60.000 ha; 28 Tem 2021 akşamı 4 ayrı noktada tutuşma; "could barely be contained after 10 days" ve "contained 2 weeks later" (iki ifade de metinde) | Ekberzade, Görüm, Karabacak, Akay, Şen, npj Natural Hazards, 2025, doi 10.1038/s44304-025-00120-4 | Özet ve Giriş | MEASURED (olay raporu) | READ_FULL (pdf) | | | ROS verilmiyor; poster "ten days" ifadesi için bu kaynak "~10 gün / 2 hafta" belirsizliği taşıyor (R11 [1][2]) |
| **Nokta ateşleme ivmelenmesi (P. brutia)** | **NOT FOUND** | — | — | — | — | — | — | Modelde sabit hız varsayımı Limitations'a |

## R5 — Satıcı/saha dağıtım parametreleri (hepsi VENDOR)

| parametre | değer | kaynak | konum | tür | okuma | not |
|---|---|---|---|---|---|---|
| Dryad aralık | "Up to 300m (depending on risk)" | dryad.net/wildfiresensor | ürün sayfası | VENDOR | READ_FULL (WF) | 300 m aralık ≈ 0.11/ha (kare ızgara) |
| Dryad gateway yükü | "Up to 100 Wildfire Sensors per Gateway" | aynı | | VENDOR | READ_FULL (WF) | |
| Dryad güç/ömür | 8×8 cm güneş paneli, süperkapasite, pilsiz; "maintenance-free for 10–15 years" | aynı | | VENDOR | READ_FULL (WF) | |
| Dryad sensörler | T, RH, basınç, CO (0–10 ppm), VOC, PM2.5/PM10; LoRaWAN + uydu | aynı | | VENDOR | READ_FULL (WF) | Montaj yüksekliği sayfada yok (bib notunda 2.5–3 m) |
| Dryad Mada (Lübnan) | 91 sensör / 78 ha (≈1.17/ha), 2 gateway; 11 Ara 2023 alarm, 30 dk içinde ekip | dryad.net/case-studies/mada | vaka sayfası | VENDOR | READ_FULL (WF) | |
| N5 Sensors | Sayfada orman yangınına özgü sayısal iddia yok | n5sensors.com | ana sayfa | VENDOR | READ_FULL (WF) | |
| ForestGuard | "Minutes, not hours"; "€0.006 / m² / year" (koridor yoğunluğunda kapsama); İstanbul OBM vaka | nowildfire.com | ana sayfa | VENDOR | READ_FULL (WF) | €0.006/m²/yıl = €60/ha/yıl |

## R6 — Fiyatlar (dağıtıcı sayfaları; hepsi arama özeti, 2026-10-06 anlık)

| kalem | değer | kaynak | okuma | not |
|---|---|---|---|---|
| Wio-E5 modül (STM32WLE5JC) | DigiKey $6.83; Mouser $9.11; LCSC $7.52; üretici $6.49 (adet 1) | arama özeti (Seeed/DigiKey/Mouser) | SNIPPET_ONLY | |
| BME688 | DigiKey $6.52 (500 adet, kesik bant), $5.76 (3000, makara); Mouser $8.65 (1 adet) | arama özeti | SNIPPET_ONLY | |
| Li-SOCl2 AA (Saft LS14500, 2.6 Ah) | RS FR €13.13 (1 adet); RS UK £10.15 | arama özeti | SNIPPET_ONLY | |
| PM sensörü | Sensirion SPS30 DigiKey $36.63 (1 adet); Plantower PMS7003 ~$17–22 | arama özeti | SNIPPET_ONLY | |
| PV hücre | ANYSOLAR KXOB25-02X8F (26.3 mW) €2.93; 0.5 W 55×70 mm panel £3.74 (RS UK) | arama özeti | SNIPPET_ONLY | |
| LoRa gateway (dış mekân) | RAK7289V2/CV2 (WisGate Edge Pro): $372–525; LTE'li 16 kanal AUD 1021.90 | arama özeti | SNIPPET_ONLY | Güneş+akü kiti NOT FOUND |
| Bulut (AWS IoT Core) | mesaj $1.00 / 1 milyon (ilk 1 milyar; AB-İrlanda örneği); bağlantı $0.08 / milyon bağlantı-dakika | arama özeti | SNIPPET_ONLY | Frankfurt bölgesi NOT FOUND |
| Süperkapasite, kutu, anten, PCB | NOT FOUND | — | — | M7'de ESTIMATE |
| Elle montaj işçiliği (M) | NOT FOUND | — | — | ESTIMATE |
| Havadan saçma maliyeti (S) | NOT FOUND (drone tohum saçma için <$1000/ha "öngörü" var; sensör saçma için uygulanamaz) | arama özeti | SNIPPET_ONLY | ESTIMATE |

## R7 — Kanopi altı güneş ve süperkapasite

| parametre | değer | kaynak | okuma | koşullar | not |
|---|---|---|---|---|---|
| Kanopi altı PV tepe güç | 0.5 W mono PV, yüksek kanopi kapalılığı, 200–1800 lux: tepe 0.105–2.145 mW | "A Hybrid Microenergy Storage System for Power Supply of Forest Wireless Sensor Nodes", Electronics 8(12):1409, 2019 | SNIPPET_ONLY (MDPI erişim engelli) | orman tipi/ülke okunamadı | params 0.4–2.0 mW ile aynı mertebe; günlük saat sayısı yok |
| P. brutia meşceresi altı PAR geçirgenliği | NOT FOUND | — | — | — | |
| Etkin günlük hasat saati (5 h) | NOT FOUND | — | — | — | ASSUMPTION olarak kalır |
| Süperkapasite ömrü | sıcaklık her 10 °C düştükçe ömür ~2 katı (sektör kuralı); 70–85 °C'de 2.5 V → 1.8 V önerilir | Eaton supercapacitor application guidelines (ikincil kopya) | SNIPPET_ONLY | | |

## R8 — Çok sekmeli LoRa

| parametre | değer | kaynak | konum | okuma | not |
|---|---|---|---|---|---|
| Asenkron önsöz örneklemeli mesh | Alıcı her önsöz süresinde ≥2 kez CAD; önsöz SF7'de 16 s'ye kadar uzatılmış (varsayılan 6.2 ms, BW250); sürekli dinlemede 2 gün, 6 saatte bir yayında 4 yıla kadar ömür; birleştirme ile röle enerjisi %8–61 azalma | Leenders, Callebaut, Ottoy, Van der Perre, De Strycker, Sensors 23(11):4994, 2023, doi 10.3390/s23114994 | §2 (CAD), Şekil 4–5, Tablo 3–4 | READ_FULL (Europe PMC tam metin XML) | SX1276 + ATmega328p; 2500 mAh; birleştirme zamanlayıcısı 0–5 dk (sekme başı ek gecikme) |
| Sekme başına gecikme (senkron TDMA) | NOT FOUND (sayısal) | — | — | — | M4'te ASSUMPTION |

## R9 — Güvenlik

| parametre | değer | kaynak | konum | okuma | not |
|---|---|---|---|---|---|
| CCM etiket uzunluğu | t ∈ {4,6,8,10,12,14,16} B; Tlen < 32 bit geçersiz | NIST SP 800-38C (May 2004) | §5.3 (s. 7), Ek A.2 | READ_FULL (pdf) | etiketsiz CCM yok → tag=0 satırı "kimlik doğrulama yok" (#27) |
| CCM nonce | n ∈ {7..13} B, n + q = 15; anahtar ömrü boyunca tekrar etmemeli, rastgele olması gerekmez | SP 800-38C | §5.3, Ek A.2 | READ_FULL (pdf) | |
| Sahtecilik olasılığı | tek deneme ≤ 2^−Tlen; çok deneme olasılığı artırır | SP 800-38C | Ek B.1 | READ_FULL (pdf) | başarısız doğrulama sayacı gerekçesi |
| Ascon-AEAD128 | 128-bit anahtar, 128-bit nonce, 128-bit etiket, 128-bit güvenlik gücü | NIST SP 800-232 (Aug 2025), doi 10.6028/NIST.SP.800-232 | §4.1, §4.3 | READ_FULL (pdf) | |
| Kısaltılmış etiket ve hata sınırı | R4: ≥32 bit; <64 bit yalnız dikkatli risk analiziyle. R5: 64 ≤ λ ≤ 128 için anahtar başına ≤ 2^(λ−32) başarısız çözme; λ < 64 için 1 ile sınırlanmalı | SP 800-232 | §4.3 R4–R5 | READ_FULL (pdf) | Ascon'a özgü; CCM için benzetme olarak kullanılmalı |
| PQ güvenlik kategorileri | AES-128 = Kat. 1, AES-192 = Kat. 3, AES-256 = Kat. 5; ≥128-bit klasik güvenlikli onaylı simetrik ilkel en az Kat. 1 sayılır | NIST IR 8547 ipd (Nov 2024), Moody, Perlner, Regenscheid ve ark. | §4.1.3, Tablo 1 ve 6 | READ_FULL (pdf) | Taslak (ipd) |
| Grover | sırasız aramada O(√N) | Grover, "A fast quantum mechanical algorithm for database search", Proc. 28th ACM STOC, 1996, s. 212–219; arXiv quant-ph/9605043 | özet | READ_FULL (abstract, arXiv sayfası) | "simetrik anahtar marjını yaklaşık yarıya indirir" ifadesi bunun sonucu (benim çıkarımım) |
| STM32 RDP zayıflıkları | STM32F0: RDP1'de Cold-Boot Stepping, RDP downgrade, debug arayüzü yarış durumu; düşük maliyetli ekipman | Obermaier & Tatschner, "Shedding too much Light on a Microcontroller's Firmware Protection", USENIX WOOT 2017 | özet | READ_FULL (abstract) | STM32WL için bulgu NOT FOUND |
| STM32 donanım AES yan-kanal | STM32F415 donanım AES ~6000 iz ile CPA (konferans konuşması) | O'Flynn, Black Hat USA 2018 slaytları | SNIPPET_ONLY | hakemli değil; STM32WL için NOT FOUND → posterde direnç iddiası yok |
| Düğüm başına anahtar | K_u = f_{K_m}(u) (PRF; ana anahtar yalnız denetleyicide) | Zhu, Setia, Jajodia, LEAP, ACM CCS 2003 | §(Establishing Individual Node Keys) | READ_FULL (pdf, UMBC kopyası) | LEAP+ (ACM TOSN 2(4):500–528, 2006, doi 10.1145/1218556.1218559) özeti: dört anahtar türü (bireysel, ikili, küme, global) — READ_FULL (abstract) |
| LEAP+ ve "epoch ratcheting" | LEAP+ özetinde zaman tabanlı yerel anahtar ilerletme yok | yukarıdaki | özet | READ_FULL (abstract) | #8: posterdeki kullanım desteklenmiyor |

## R10 — Konum (yalnız future-work cümlesi)

| parametre | değer | kaynak | okuma | not |
|---|---|---|---|---|
| LoRa RSSI parmak izi konumlama | ortalama 358 m, medyan 204 m hata (kentsel LoRaWAN veri seti, sinir ağı) | arXiv 1908.05085 ("A Reproducible Comparison of RSSI Fingerprinting Localization Methods Using LoRaWAN") | SNIPPET_ONLY | orman değil |
| Ormanda RSSI konumlama doğruluğu | NOT FOUND | — | — | posterde sayı verilmeyecek |

## R11 — Mevcut atıf şüpheleri (REVIEW §9) — ara durum

| atıf | bulgu | okuma |
|---|---|---|
| [1],[2] Manavgat 60.000 ha / 10 gün | Ekberzade ve ark. 2025 (npj Nat. Hazards) ~60.000 ha'yı doğrudan veriyor; süre için hem "10 gün" hem "2 hafta"; ersoy2025/camalan2023 açılmadı | READ_FULL (Ekberzade); diğerleri bekliyor |
| [31] Dampage "heat 5 m" | Kısmen: 5 m çok-sensörlü düğüm menzili (yöntem gösterilmemiş), yalnız ısı değil | READ_FULL (pdf) |
| [35] LEAP+ | Düğüm başına anahtar türetme için uygun; epoch ratcheting için değil | READ_FULL (CCS'03 pdf + TOSN özeti) |
| P.833 "10–15 dB gövde" | P.833-10'da yok | READ_FULL (pdf) |
| [4] MODIS ~1000 m² | "MODIS can routinely detect both flaming and smoldering fires ∼1000 m2"; çok iyi koşulda ~1/10'u, kusursuz koşulda ~50 m² alevli. Kaynak: Giglio, Schroeder, Hall, Justice, *MODIS C6 and C6.1 Active Fire Product User's Guide* v1.0 (May 2021; C6 Rev C'den uyarlanmış), §8.3.2. Bib'deki Rev C (2020) ile aynı ifade olduğu varsayılmamalı → kullanıcı kontrolü | READ_FULL (pdf, modis-fire.umd.edu) |
| [4]/[5] "3 h latency" | bakılmadı (FIRMS sayfası) | — |
| [14] VIIRS 375 m | açılmadı; MODIS ile aynı "~1000 m²" kovasında göstermek yanıltıcı olabilir (REVIEW) | NOT_ACCESSIBLE (denenmedi, bütçe) |
| [29]/[30] "L/B ≥ 2.5" | FARSITE, Anderson (1983) L/B modelini orta alev yüksekliği rüzgârına bağlı kullanır ve 0.397 çıkarır; sabit "≥2.5" ifadesi bulunamadı. Rothermel 1972 tek boyutlu yayılma denklemidir, şekil vermez → posterdeki "L/B≥2.5 [Rothermel, Finney]" desteklenmiyor | READ_FULL (WF, firenet.gov FARSITE teknik yardım "Elliptical Dimensions"); FARSITE raporu rmrs_rp004 NOT_ACCESSIBLE (403) |
| [32] Briggs 1969 | açılmadı; baca dumanı için; kanopi altı küçük kaynak için uygunluk tartışmalı (REVIEW). Posterde yalnız nitel kullanılmalı veya kaldırılmalı | NOT_ACCESSIBLE (denenmedi) |

## İlgili çalışmalar (#1 kapsam iddiası için)

| çalışma | ne yapıyor | künye kaynağı | okuma |
|---|---|---|---|
| Fierens, "Number of sensors versus time to detection in wildfires", Int. J. Wildland Fire 18(7):825–829, 2009, doi 10.1071/WF07137 | Rastgele (düzgün) yerleşimde tespit anındaki yanan alanın dağılımı yaklaşık üstel; sonuç tutuşma sayısı ve yayılma modelinden bağımsız | Crossref API kaydı (künye); arXiv 0810.5763 özeti (içerik; başlık arXiv'de "Number of wireless sensors needed to detect a wildfire") | READ_FULL (abstract) |
| Hefeeda & Bagheri, Ad Hoc & Sensor Wireless Networks 7(3–4):169–224, 2009 | FWI'ye dayalı yangın modeli; tespit = düğüm k-kapsama problemi; yaklaşık algoritmalar | arama özeti (bib ile tutarlı) | SNIPPET_ONLY |
| Pandey & Gupta, arXiv 1810.07511 (2018; bib: IEEE ANTS 2018) | Poisson (PPP) yerleşimde genişleyen yangının tespit olasılığı ve gerekli yoğunluk; rüzgârın etkisi | arXiv özeti | READ_FULL (abstract) |
| Lloret ve ark., Sensors 9(11):8722–8747, 2009 | Kırsal/orman yangını tespiti ve doğrulaması için WSN dağıtımı (kamera + sensör) | bib (açılmadı) | NOT_ACCESSIBLE (denenmedi) |

Sonuç: "açık, hakemli model yok" iddiası yanlış; Fierens ve Pandey & Gupta Poisson yerleşim + tespit süresi/yoğunluk ilişkisini zaten kuruyor.
Savunulabilir katkı: aynı açık modelde RF menzili × çok sekmeli bağlantı × algılama × enerji × maliyet, P. brutia / 868 MHz parametreleriyle.

## Faz 1 özeti (2026-10-06)

- Radyo (R1): P. brutia/Akdeniz çamı için 868 MHz ölçülmüş yol kaybı üssü **bulunamadı**. En yakın veri 923 MHz tropik orman
  (n = 3.22, Tx 1.7 m, gateway 8 m). P.833-10 iki terminalin de orman içinde olduğu yere yakın bağlantıyı kapsamıyor ve
  "10–15 dB gövde gölgesi" ifadesini içermiyor. → M1 iki senaryolu ASSUMPTION.
- Düzenleme (R2): AB bant M ve Türkiye (BTK satır 20) 868.0–868.6 MHz: 25 mW e.r.p., ≤%1 görev çevrimi; görev çevrimi
  1 saatlik pencerede tanımlı (EN 300 220-1 §5.4.1) → tek bir alarm için "6 s bekleme" zorunlu değil; asıl kısıt gateway
  çevresindeki rölelerin saatlik 36 s bütçesi.
- Algılama (R3): MOx/BME688 için saha r_G **bulunamadı**. H2 sensörü (Nörthemann 2013) 0.5 m² ateşi 25 m'de tespit sınırında,
  2 m² ateşi 105 m'de algıladı; CO2 NDIR (De Rango 2025) eşik yöntemiyle ≤40 m. Isı için ölçülmüş r_T yok; Dampage'in 5 m'si
  çok-sensörlü düğüm için, yöntemi gösterilmemiş; Chan ve ark. 10 m'de sıcaklık değişimi görmemiş.
- Yayılma (R4): yüzey 0.3–3.75 m/dk (Küçük 2012, deney aralığı); rüzgârlı büyük yangın 5 km/sa (Coskuner 2026). Nokta ateşleme
  ivmelenmesi bulunamadı.
- Enerji (R7): kanopi altı küçük PV için tek veri arama özeti (0.105–2.145 mW tepe). P. brutia altı ışık **bulunamadı**.
- Güvenlik (R9): SP 800-38C, SP 800-232, IR 8547 ipd tam okundu; STM32WL'ye özgü yan-kanal/RDP çalışması bulunamadı.
- Erişilemeyen: STM32WL datasheet/RM (st.com zaman aşımı), MDPI sayfaları (403), Wu 2020 (403).

## Kullanıcının birincil kaynaktan kontrol etmesi gereken ilk 15 değer

| # | değer | kaynak ve konum | neden kritik |
|---|---|---|---|
| 1 | LoRa duyarlılığı SF7 −124 / SF12 −137 dBm (Rx Boosted) | SX1261/2 DS Rev 1.2, Tablo 3-8 | tüm menzil sonuçları; SF8–11 kaynakta yok |
| 2 | TX 45 mA @ +14 dBm (SX1262 optimal ayar) | SX1261/2 DS Rev 1.2, Tablo 3-6 | enerji; STM32WL'nin kendi değeri farklı olabilir |
| 3 | RX 4.6 mA (DC-DC) / 5.3 mA (Boosted) | SX1261/2 DS Rev 1.2, Tablo 3-5 | röle dinleme enerjisi |
| 4 | STM32WLE5 Stop2+RTC 1.07 µA @3 V ve sıcaklıkla artışı | DS13105 (güncel rev.), Stop2 akım tablosu | uyku bütçesi, 50 °C senaryosu (erişemedim) |
| 5 | Bant M 25 mW e.r.p., ≤%1; T_obs = 1 h | EN 300 220-2 V3.2.1 Tablo B.1; EN 300 220-1 V3.1.1 §5.4.1 | gecikme modeli |
| 6 | BTK 868–868.6 MHz: 25 mW e.r.p., ≤%1 veya LBT+AFA | BTK Sınıf 1 teknik ölçüt, satır 20 (güncel sürüm/tarih) | yasal uyum |
| 7 | BME688 ULP 0.09 mA @ 300 s (VDD ≤1.8 V, 25 °C); τ33–63% = 92 s | BME688 DS Rev 1.3, Tablo 2 | gaz enerjisi ve gecikme |
| 8 | H2 sensörü: 25 m'de 3/8 (tespit sınırında), 2 m² ateşte 105 m | Nörthemann 2013, §3, Şekil 8–9 | r_G senaryolarının tek saha dayanağı |
| 9 | CO2 NDIR: eşik yöntemi ≤40 m, LSTM ~70 m | De Rango 2025, Şekil 8 | r_G senaryoları |
| 10 | Düğüm algılama menzili 5 m (yöntem?) | Dampage 2022, "Sensor node deployment" | r_T (#10) |
| 11 | ROS 0.3–3.75 m/dk (35 çizgi ateşleme) | Küçük ve ark. 2012, Sonuçlar | yayılma senaryoları (#11) |
| 12 | 5.0 km/sa (4.27–5.71) rüzgârlı P. brutia yangını | Coskuner 2026, §3.1 | kapsam sınırı |
| 13 | P.833-10 Tablo 1 (949 MHz: γ 0.17 dB/m, A_m 26.5 dB) ve "10–15 dB gövde" ifadesinin yokluğu | ITU-R P.833-10 §2.1 | #21, #34 |
| 14 | Orman n = 3.22 (923 MHz) | Boonlom 2026 Sensors 26(10):3192 | gövde senaryosu kalibrasyonu |
| 15 | Etiket kuralları: CCM t ∈ {4..16} B; Ascon R5 (λ ≥ 64 → 2^(λ−32) hata); AES-256 = PQ Kat. 5 | SP 800-38C Ek A/B; SP 800-232 §4.3; IR 8547 ipd Tablo 1, 6 | güvenlik metni (#6, #16, #27) |

## Ek (WIP kaydı, 2026-10-06)

| parametre | değer | kaynak | konum | tür | okuma | not |
|---|---|---|---|---|---|---|
| SX1262 sentezleyici uyanma | 40 µs (STDBY_XOSC'tan) | SX1261/2 DS Rev 1.2 | Tablo 3-7 | VENDOR | READ_FULL (pdf) | CAD/dinleme enerjisi ek yükü için |
| SX1262 kristal osilatör uyanma | 150 µs (STDBY_RC'den) | SX1261/2 DS Rev 1.2 | Tablo 3-7 | VENDOR | READ_FULL (pdf) | |
| SX1262 STDBY_RC / STDBY_XOSC akımı | 0.6 mA / 0.8 mA | SX1261/2 DS Rev 1.2 | Tablo 3-5 | VENDOR | READ_FULL (pdf) | |
| SX1262 TX +10 dBm (SX1261, 3.3 V) | 18 mA (+14 dBm PA match) | SX1261/2 DS Rev 1.2 | Tablo 3-6 | VENDOR | READ_FULL (pdf) | yalnız SX1261 satırı |
| BME688 TPH akımları | 2.1 µA (1 Hz H+T), 3.7 µA (1 Hz H+P+T), uyku 0.15 µA; LP 0.9 mA; standart tarama 3.9 mA, 10.8 s/tarama | BME688 DS Rev 1.3 | s. 1 özellik listesi | VENDOR | READ_FULL (pdf) | |
| Not: Boonlom 2026 n=3.22 | modelin kesişimi RSSI = −16.62 dBm @1 m (kendi Tx/anten düzeni); biz yalnız üssü ödünç alıyoruz, FSPL(1 m) kesişimiyle | Boonlom 2026 | model denklemi | — | READ_FULL (WF) | iyimser M menzilini büyük olasılıkla abartır |

## R13 — STM32WLE5xx datasheet DS13105 Rev 6 (July 2020) — READ_FULL (pdf; Farnell aynası farnell.com/datasheets/3093895.pdf, erişim 2026-10-06)
Not: daha önce st.com zaman aşımı nedeniyle NOT_ACCESSIBLE idi; bu sürüm tam metin.

| parametre | değer | konum | tür | not |
|---|---|---|---|---|
| Stop2 + RTC (LSI) akımı, VDD 3.0 V | tipik 0.715 µA @0 °C, 1.00 µA @25 °C, 2.90 µA @55 °C, 9.70 µA @85 °C; maks 2.80 µA @25 °C, 26.0 µA @85 °C | Tablo 42 (s. 83) | VENDOR (karakterizasyon) | 50 °C için tablo değeri yok (25 ve 55 °C arası); kapakta 1.07 µA @3 V |
| Stop2 RTC kapalı, 3.0 V | 0.885 µA @25 °C, 2.80 µA @55 °C | Tablo 42 | VENDOR | |
| Stop2'de bellek korunumu | "Only SRAM1, SRAM2, CPU and some peripherals preserve their contents" | §3 (güç modları) | VENDOR | sayaç RAM'de tutulabilir |
| Flash dayanıklılığı | 10 kcycle (TA −40…+105 °C) | Tablo 66 (s. 103) | VENDOR | |
| Flash veri saklama | 10 kcycle sonrası 30 yıl @55 °C, 15 yıl @85 °C | Tablo 66 | VENDOR | |
| AES | FIPS 197; ECB, CBC, CTR, GCM, GMAC, CCM; 128 veya 256-bit anahtar | §3.21 | VENDOR | önceki ikincil kaynağı doğrudan karşılıyor |
| AES1 çevre birimi akımı | 2.50 / 2.13 / 1.80 µA/MHz (üç sütun; sütun başlıkları okunmadı) | çevre birimi akım tablosu (s. ~92) | VENDOR | 48 MHz'de ~0.1 mA; params.AES_I_A = 5 mA varsayımı çok yüksek; çevrim sayısı (RM) hâlâ NOT FOUND |
| Yedek kayıtlar / tamper | 20×32-bit yedek kayıt tüm düşük güç modlarında ve VBAT'ta korunur, tamper algılamayla korunur; 3 harici + 4 dahili tamper | §3.24 | VENDOR | |
| RDP | Level 0/1/2; Level 2 JTAG/SWD, SRAM'den boot ve bootloader'ı kapatır, "irreversible" | §3 (bellek koruması) | VENDOR | |

## R14 — Örtü altı rüzgâr hızı (A6) — 2026-10-06
| parametre | değer | kaynak | okuma | not |
|---|---|---|---|---|
| Örtü altı / üstü rüzgâr | çam ormanında 4 m'de ≤0.8 m/s iken 40 m'de 5 m/s (oran ~0.16) | arama özeti; olası kaynak Lohou ve ark., "VENFOR" 2003 (hal.inrae.fr/hal-02762196) | SNIPPET_ONLY | açılmadı; A6 duyarlılığında U = 0.5 ve 2 m/s ASSUMPTION |
| Orta-alev rüzgâr düzeltmesi | Baughman & Albini 1980 (frames.gov PDF) | arama sonucu başlığı | NOT_ACCESSIBLE (açılmadı) | |

## R15 — GNSS (A7), 2026-10-06 (6 erişim sınırı içinde)
| parametre | değer | kaynak | konum | tür | okuma | not |
|---|---|---|---|---|---|---|
| Soğuk başlangıç TTFF | 24–29 s (konstelasyon setine göre; GPS+GAL 29 s); sinyal −130 dBm açık gökyüzü | u-blox MAX-M10S Data sheet UBX-20035208 R02 (20-Apr-2021, "Advance information"), sparkfun aynası | Tablo 1 | VENDOR | READ_FULL (pdf) | kanopi altı TTFF yok |
| Edinim akımı | VCC 6.5–10.5 mA + V_IO 2.2–2.3 mA (GPS+GAL: 7.0 + 2.2 mA); tepe 25 mA | aynı | Tablo 13 ("indicative", soğuk başlangıç örnekleri) | VENDOR | READ_FULL (pdf) | gerilim koşulu tabloda okunamadı; 3.3 V varsayıldı |
| Yedek akımlar | donanım yedek 32 µA, yazılım bekleme 46 µA | aynı | Tablo 14 | VENDOR | READ_FULL (pdf) | tek seferlik kullanımda modül güç kesilerek kapatılmalı (ASSUMPTION) |
| Modül fiyatı | MAX-M10S-00B 21.00 USD (DigiKey, tek adet, kesik bant; stokta yok) | arama özeti | — | VENDOR | SNIPPET_ONLY | miktar kademesi görülmedi |
| Yama anten 25×25 mm | Taoglas: 5.00–19.00 USD (embeddedworks) | arama özeti | — | VENDOR | SNIPPET_ONLY | |
| Kanopi altı doğruluk | Pixel 5 ~1.5 m, ZED-F9P desimetre altı medyan; 20 dk statik, çift frekans, RTKLIB son işleme | Tomaštík & Everett, Sensors 23(6):3136, 2023, doi 10.3390/s23063136 | Özet, Yöntem | MEASURED-field | READ_FULL (Europe PMC XML) | tek seferlik L1 fix için uygulanamaz |
| Kanopi altı tek seferlik L1 fix başarı oranı / süresi / doğruluğu | NOT FOUND | — | — | — | — | A7'de p_fix ve fix süresi ASSUMPTION |
| GNSS spoofing | sivil sinyaller kimliksiz; UT Austin gösterimleri (yat, drone) | IEEE Spectrum, MIT Tech Review, PBS haberleri (arama özeti) | — | — | SNIPPET_ONLY | hakemli kaynak açılmadı → posterde atıfsız, gerekçeyle |

## R16 — NSW kamera ağı ([14] nsw_pano), 2026-10-06 — READ_FULL (WF)
| parametre | değer | konum | tür | not |
|---|---|---|---|---|
| Yatırım | "up to $1.4 million over 5 years" (A$) | bakanlık duyurusu, 18 Sep 2025 | GOVERNMENT (duyuru) | |
| Kapsam | 22 konum, 1.2 milyon ha (Forestry Corporation NSW + Pano AI) | aynı | GOVERNMENT | A$1.4M / 5 yıl / 1.2 Mha ≈ A$0.23/ha/yıl (benim hesabım; işletme dahil mi belirtilmemiş) |
| Zaman vurgusu | "critical edge in the crucial first 30 minutes after ignition" | aynı | GOVERNMENT | tespit süresi sayısı yok |
| "10–15 min alert", "20–35 km" | sayfada YOK | — | — | 20–35 km ve 1 dk tarama yalnız sources/companies.csv'de (vendor, bu oturumda açılmadı); "10–15 min" için kaynak NOT FOUND → posterden çıkarıldı |

## R17 — Yazılım Ascon enerjisi (E9), 2026-10-06
| kaynak | durum | okunan | enerji? | not |
|---|---|---|---|---|
| weatherley_lwc (rweather.github.io/lwc-finalists/performance.html) | READ_FULL (WebFetch, model özeti) | Arduino Due Cortex-M3 84 MHz ve ESP32 240 MHz; hız "ChaChaPoly Units" cinsinden göreli. Cortex-M3, 128 B: ASCON-128 şifreleme 1.54, AES-128-GCM 0.36 birim (yazılım) | YOK (yalnız hız) | Sayfada "Generated on Mon Jun 21 2021"; bib'de year = 2023 → TODO-VERIFY (bib değiştirilmedi, posterde atıf yok) |
| renner2020hil (ICICS 2020, LNCS 12282, doi 10.1007/978-3-030-61078-4_28) | NOT_ACCESSIBLE (Springer kimlik doğrulama yönlendirmesi; OTH Regensburg OPUS sayfasında PDF yok); özet SNIPPET_ONLY | özet: hız ve bellek, birden çok MCU | özette YOK | atıf eklenmedi |
| Yazılım Ascon-AEAD128 çerçeve başına enerji (STM32WL veya benzeri) | NOT FOUND | — | — | posterde "software Ascon not measured" |
| Model değerleri (kaynak değil) | TX/çerçeve = 45 mA × 3.3 V × ToA(SF7; 19 B → 51.5 ms, 27 B → 66.8 ms) = 7.6–9.9 mJ; AES = 5 mA × 3.3 V × 280/48 MHz ≈ 0.1 µJ (params AES_* ASSUMPTION #22; R? satırı: AES1 akımı ~2.5 µA/MHz → 5 mA varsayımı muhafazakâr yüksek) | | | |
