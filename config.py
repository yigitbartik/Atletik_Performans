# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - YAPILANDIRMA
# ═══════════════════════════════════════════════════════════════════════════════

# ─── YAŞ GRUPLARI ───────────────────────────────────────────────────────────────
AGE_GROUPS = ["U17", "U19", "U20", "U21"]

# ─── METRILER ───────────────────────────────────────────────────────────────────
METRICS = {
    'total_distance': {
        'display': 'Toplam Mesafe',
        'unit': 'm',
        'description': 'Oyuncunun koştuğu toplam mesafe (metre cinsinden)'
    },
    'metrage': {
        'display': 'Metabolik Güç',
        'unit': 'W/kg',
        'description': 'Harcanan metabolik enerji (İvmelenme, Yavaşlama, Çaprazzlık)'
    },
    'smax_kmh': {
        'display': 'Maksimum Hız',
        'unit': 'km/h',
        'description': 'Kaydedilen en yüksek hız'
    },
    'dist_25_plus': {
        'display': '25+ km/h Koşu',
        'unit': 'm',
        'description': 'Yüksek hızda (25 km/h ve üzeri) koşulan mesafe'
    },
    'player_load': {
        'display': 'Oyuncu Yükü',
        'unit': 'Load',
        'description': 'Vücut tarafından hissedilen toplam mekanik yük'
    },
    'amp': {
        'display': 'Metabolik Toparlanma',
        'unit': 'J/kg',
        'description': 'Yüksek hızlı eylemlerin tekrarlanma yoğunluğu'
    },
    'hsr': {
        'display': 'Yüksek Hızlı Koşular',
        'unit': 'sayı',
        'description': '25 km/h ve üzerindeki koşu sayısı'
    },
    'acc_over_3': {
        'display': 'İvmelenme (>3 m/s²)',
        'unit': 'sayı',
        'description': '3 m/s² üzerindeki ivmelenme sayısı'
    },
    'dec_under_minus_3': {
        'display': 'Yavaşlama (<-3 m/s²)',
        'unit': 'sayı',
        'description': '-3 m/s² altındaki yavaşlama sayısı'
    },
    'high_accel_count': {
        'display': 'Yüksek İvmelenme',
        'unit': 'sayı',
        'description': 'Patlayıcı hareketler (Acc > 4 m/s²)'
    },
    'quick_change_of_direction': {
        'display': 'Hızlı Çaprazzlık',
        'unit': 'sayı',
        'description': 'Anlık yön değiştirme sayısı'
    }
}

# ─── BİRİNCİL METRİKLER (GRAFIK VE SKORLAMADA KULLANILAN) ─────────────────────
PRIMARY_METRICS = [
    'total_distance',
    'smax_kmh',
    'dist_25_plus',
    'player_load',
    'metrage',
    'hsr',
    'acc_over_3',
    'dec_under_minus_3',
    'high_accel_count',
    'quick_change_of_direction',
    'amp'
]

# ─── SCATTER ANALİZİ ÖNCEDENTANıMLI EKSENLERİ ────────────────────────────────
SCATTER_PRESETS = [
    ('total_distance', 'smax_kmh'),
    ('dist_25_plus', 'player_load'),
    ('hsr', 'metrage'),
    ('acc_over_3', 'dec_under_minus_3'),
    ('player_load', 'total_distance')
]

# ─── DİĞER AYARLAR ──────────────────────────────────────────────────────────
DEFAULT_MINUTES = {
    'TRAINING': 30,  # Antrenman minimum dakika
    'MATCH': 30      # Maç minimum dakika
}

# ─── POZISYONLAR (GELECEĞİ İÇİN) ────────────────────────────────────────────
POSITIONS = [
    'Kaleci',
    'Sağ Bek',
    'Sol Bek',
    'Merkez Bek',
    'Sağ Orta Saha',
    'Sol Orta Saha',
    'Merkez Orta Saha',
    'Sağ Kanat',
    'Sol Kanat',
    'Forvet'
]

# ─── VERİTABANı DÖNEMLERİ ────────────────────────────────────────────────────
IMPACT_WEIGHTS = {
    'dist_25_plus_pm': 0.25,        # %25 Yüksek Hızlı Koşu
    'patlayici': 0.20,              # %20 Patlayıcı Aksiyon (Acc + Dec)
    'player_load_pm': 0.20,         # %20 Oyuncu Yükü
    'total_distance_pm': 0.15,      # %15 Toplam Mesafe Hacmi
    'smax_kmh': 0.10,               # %10 Maksimum Hız
    'metabolik_pm': 0.10            # %10 Metabolik Güç (AMP + Metrage)
}

# ─── RENK PALETİ ────────────────────────────────────────────────────────────────
COLORS = {
    'RED': '#E30A17',           # TFF Kırmızısı
    'DARK': '#0D0D0D',          # Siyah
    'GRAY_900': '#111827',      # Koyu Gri
    'GRAY_800': '#1F2937',
    'GRAY_700': '#374151',
    'GRAY_600': '#4B5563',
    'GRAY_500': '#6B7280',
    'GRAY_400': '#9CA3AF',
    'GRAY_300': '#D1D5DB',
    'GRAY_200': '#E5E7EB',
    'GRAY_100': '#F3F4F6',
    'GRAY_50': '#F9FAFB',
    'SUCCESS': '#10B981',        # Yeşil
    'WARNING': '#F59E0B',        # Sarı
    'DANGER': '#EF4444',         # Kırmızı
    'INFO': '#3B82F6',           # Mavi
    'EXCELLENT': '#059669',      # Koyu Yeşil
    'GOOD': '#10B981',
    'MEDIUM': '#F59E0B',
    'LOW': '#EF4444',
    'WHITE': '#FFFFFF',
    'WIN': '#10B981',
    'LOSS': '#EF4444',
    'TIE': '#6B7280'
}

# ─── TESTER MOD (GELİŞTİRME) ────────────────────────────────────────────────
DEBUG_MODE = False
ADMIN_PASSWORD = "tff2024"

print("✅ Konfigürasyon yüklendi | TFF Performans Sistemi v5.0")
