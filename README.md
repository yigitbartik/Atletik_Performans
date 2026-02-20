# 🏆 TFF Genç Milli Takımlar - Atletik Performans Sistemi

Türkiye Futbol Federasyonu Genç Milli Takımları için profesyonel atletik performans yönetim sistemi.

## ✨ Özellikler

- ✅ **Excel Veri Import** - Otomatik algılama
- ✅ **Performans Analizi** - 4 detaylı analiz sayfası
- ✅ **Scout Sistemi** - Ağırlıklı puanlama modeli
- ✅ **PDF Rapor** - Profesyonel rapor oluşturma
- ✅ **Güvenlik** - Kullanıcı yönetimi (SHA256)
- ✅ **10 Performans Metriği** - Minutes, Distance, Speed, Load, vb.

## 🚀 Kurulum

### 1. Python Paketlerini Yükle
```bash
pip install -r requirements.txt
```

### 2. Veritabanını Başlat
```bash
python 01_database_setup.py
```

### 3. Uygulamayı Çalıştır
```bash
streamlit run app.py
```

### 4. Tarayıcıya Git
```
http://localhost:8501
```

## 🔐 Varsayılan Giriş

| Alan | Değer |
|------|-------|
| **Username** | admin |
| **Password** | admin123 |

⚠️ **ÖNEMLİ:** İlk giriş yaptığında şifreyi değiştiriniz!

## 📊 Ana Özellikler

### 1. Admin Panel
- 🏕️ Kamp yönetimi
- 👥 Oyuncu yönetimi
- 📊 Performans verisi girişi
- 📥 Excel veri import
- 📄 PDF rapor oluşturma

### 2. Analiz & Raporlar
- ⚽ Oyuncu karşılaştırması
- 👤 Oyuncu profili
- 👥 Yaş grubu analizi
- 🔥 Heatmap analizi

### 3. Scout Sistemi
- 🏆 Scout sıralaması
- 📊 Oyuncu radar karşılaştırması
- ⭐ Yetenekli oyuncu bulma

## 📁 Dosya Yapısı

```
athletic-performance-system/
├── app.py                      # Main uygulamasi
├── admin_panel.py              # Admin yönetim paneli
├── analysis_pages.py           # Analiz sayfaları
├── scout_pages.py              # Scout sistemi
├── excel_import.py             # Excel import
├── pdf_report.py               # PDF rapor
├── security_module.py          # Güvenlik sistemi
├── 01_database_setup.py        # Database kurulumu
├── requirements.txt            # Python bağımlılıkları
└── .gitignore                  # Git ignore kuralları
```

## 🛠️ Teknoloji Stack

| Teknoloji | Sürüm | Amaç |
|-----------|-------|------|
| **Streamlit** | 1.28.1 | Frontend framework |
| **Pandas** | 2.0.3 | Veri işleme |
| **SQLite** | 3 | Veritabanı |
| **Plotly** | 5.17.0 | İnteraktif grafikler |
| **FPDF2** | 2.7.0 | PDF oluşturma |
| **Matplotlib** | 3.8.0 | Görselleştirme |

## 📊 Performans Metrikleri

### 10 Ana Metrik

1. **Minutes** - Oynanılan dakika
2. **Total Distance** - Toplam koşu mesafesi (m)
3. **Speed Max** - Maksimum hız (km/h)
4. **Dist 20-25** - 20-25 km/h arası mesafe (m)
5. **Dist > 25** - 25+ km/h mesafe (m)
6. **N 20-25** - 20-25 km/h sprint sayısı
7. **N > 25** - 25+ km/h sprint sayısı
8. **Player Load** - Oyuncu beden yükü
9. **Metrage** - Mesafe metraji
10. **AMP** - Accelerometer metriği

## 🎯 Scout Puanlama Modeli

```
Overall Score = 
  Speed (20%) + 
  Distance (20%) + 
  High Speed (20%) + 
  Load (15%) + 
  Consistency (15%)
```

## 🌐 Deployment

### Streamlit Cloud
1. GitHub'a push et
2. https://streamlit.io/cloud'a git
3. Repository seç
4. app.py dosyasını seç
5. Deploy!

### Yerel Çalıştırma
```bash
streamlit run app.py
```

## 📖 Dokümantasyon

- **DEPLOYMENT_STEP_BY_STEP.md** - 20 dakikalık video talimatı
- **GITHUB_STREAMLIT_REHBERI.md** - Detaylı deployment rehberi
- **HIZLI_BASLAMA.md** - 5 dakikalık hızlı başlama
- **KURULUM_REHBERI.md** - Teknik kurulum detayları

## 🔄 Veri Akışı

```
Excel → Import → SQLite Database → Analiz → Raporlar → PDF/Excel
```

## ✅ Kullanıcı Rolleri

| Rol | İzinler |
|-----|---------|
| **Admin** | Tüm özellikler + Yönetim |
| **Editor** | Veri girişi + Analiz |
| **Viewer** | Raporları görüntüle |

## 🐛 Sorun Giderme

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Database locked"
Uygulamayı yeniden başlat

### Streamlit yavaş
Cache'i temizle:
```bash
streamlit cache clear
```

## 📞 Destek

- 📧 Email: admin@tff.org.tr
- 🌐 GitHub: [Repository]
- 💬 Streamlit: [Live App]

## 📜 Lisans

© 2025 Türkiye Futbol Federasyonu - Tüm Hakları Saklıdır

---

**🚀 Başlangıç:** `streamlit run app.py`

**Sorular?** GitHub Issues'de oluştur.
