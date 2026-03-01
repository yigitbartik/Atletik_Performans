# TFF Performans Sistemi - Konfigürasyon v4.0

AGE_GROUPS = ['U16', 'U17', 'U19', 'U21']

DATE_FORMAT    = '%d.%m.%Y'
DATE_FORMAT_DB = '%Y-%m-%d'

DATAFRAME_KWARGS = {'use_container_width': True, 'hide_index': True}

# ─── Metrik tanımları ────────────────────────────────────────────────────────
METRICS_BASE = {
    'minutes':        {'display': 'Minutes',                 'unit': 'min',  'group': 'A', 'icon': '⏱'},
    'total_distance': {'display': 'Total Distance',          'unit': 'm',    'group': 'A', 'icon': '📏'},
    'metrage':        {'display': 'High Speed Running',      'unit': 'm',    'group': 'A', 'icon': '🔥'},
    'dist_20_25':     {'display': 'Distance 20-25 km/h',     'unit': 'm',    'group': 'A', 'icon': '💨'},
    'dist_25_plus':   {'display': 'Distance 25+ km/h',       'unit': 'm',    'group': 'A', 'icon': '⚡'},
    'smax_kmh':       {'display': 'Maximum Speed',           'unit': 'km/h', 'group': 'A', 'icon': '🚀'},
    'player_load':    {'display': 'Player Load',             'unit': '',     'group': 'A', 'icon': '💪'},
    'amp':            {'display': 'Average Metabolic Power', 'unit': '',     'group': 'A', 'icon': '📊'},
}

METRICS_ACC_DEC = {
    'dist_acc_3':     {'display': 'Acceleration Distance > 3 m/s²', 'unit': 'm', 'group': 'B', 'icon': '▲'},
    'dist_dec_3':     {'display': 'Deceleration Distance < -3 m/s²', 'unit': 'm', 'group': 'B', 'icon': '▼'},
}

METRICS_N = {
    'n_20_25':        {'display': 'Number of Runs 20-25 km/h', 'unit': 'n', 'group': 'C', 'icon': '🏃'},
    'n_25_plus':      {'display': 'Number of Runs 25+ km/h',   'unit': 'n', 'group': 'C', 'icon': '🏃'},
}

METRICS = {**METRICS_BASE, **METRICS_ACC_DEC, **METRICS_N}

# ─── Bileşik skor metrikleri ─────────────────────────────────────────────────
# Dakika (minutes) hariç TÜM DEĞİŞKENLER analize ve radar grafiklere eklendi!
PRIMARY_METRICS = [
    'total_distance', 'metrage', 'dist_20_25', 'dist_25_plus',
    'smax_kmh', 'player_load', 'amp', 'dist_acc_3', 'dist_dec_3',
    'n_20_25', 'n_25_plus'
]

# ─── Metrik ağırlıkları ──────────────────────────────────────────────────────
# İstenildiği gibi TÜM KATSAYILAR EŞİTLENDİ (1.0)
METRIC_WEIGHTS = {
    'total_distance': 1.0,
    'metrage':        1.0,
    'dist_20_25':     1.0,
    'dist_25_plus':   1.0,
    'smax_kmh':       1.0,
    'player_load':    1.0,
    'amp':            1.0,
    'dist_acc_3':     1.0,
    'dist_dec_3':     1.0,
    'n_20_25':        1.0,
    'n_25_plus':      1.0,
}

# ─── Radar grafiği metrikleri ────────────────────────────────────────────────
RADAR_METRICS = PRIMARY_METRICS.copy()

# ─── Scatter plot öneri çiftleri ─────────────────────────────────────────────
SCATTER_PRESETS = [
    ('total_distance', 'smax_kmh'),
    ('total_distance', 'player_load'),
    ('metrage',        'dist_25_plus'),
    ('dist_20_25',     'dist_25_plus'),
    ('player_load',    'amp'),
]

# ─── Çoklu oyuncu grafik paleti ──────────────────────────────────────────────
PLAYER_PALETTE = ['#E30A17', '#0D0D0D', '#059669', '#2563EB', '#D97706', '#7C3AED']

# ─── Renk Paleti (tek kaynak) ────────────────────────────────────────────────
COLORS = {
    # Marka
    'RED':          '#E30A17',
    'RED_DARK':     '#B5000E',
    'RED_LIGHT':    '#FFF0F0',
    'RED_MID':      'rgba(227,10,23,0.12)',
    'BLACK':        '#0D0D0D',
    # Gri skalası
    'GRAY_900':     '#111827',
    'GRAY_800':     '#1F2937',
    'GRAY_700':     '#374151',
    'GRAY_600':     '#4B5563',
    'GRAY_500':     '#6B7280',
    'GRAY_400':     '#9CA3AF',
    'GRAY_300':     '#D1D5DB',
    'GRAY_200':     '#E5E7EB',
    'GRAY_100':     '#F3F4F6',
    'GRAY_50':      '#F9FAFB',
    'WHITE':        '#FFFFFF',
    # Durum
    'SUCCESS':      '#059669',
    'WARNING':      '#D97706',
    'DANGER':       '#DC2626',
    'INFO':         '#2563EB',
    # Grafik
    'TRAINING':     '#E30A17',
    'MATCH':        '#0D0D0D',
    'TEAM_AVG':     '#6B7280',
    'BAND_FILL':    'rgba(107,114,128,0.12)',
    # Karşılaştırma (components.py)
    'WIN':          '#059669',
    'LOSS':         '#DC2626',
    'TIE':          '#D97706',
    # Percentile seviyeleri (components.py)
    'EXCELLENT':    '#059669',
    'GOOD':         '#2563EB',
    'MEDIUM':       '#D97706',
    'LOW':          '#DC2626',
}

# ─── Pozisyonlar (components.py) ─────────────────────────────────────────────
POSITIONS = {
    'GK':  {'display': 'Kaleci',        'short': 'KL',  'color': '#F59E0B'},
    'CB':  {'display': 'Stoper',        'short': 'ST',  'color': '#3B82F6'},
    'LB':  {'display': 'Sol Bek',       'short': 'SB',  'color': '#3B82F6'},
    'RB':  {'display': 'Sağ Bek',       'short': 'SğB', 'color': '#3B82F6'},
    'DM':  {'display': 'Defansif Orta', 'short': 'DO',  'color': '#8B5CF6'},
    'CM':  {'display': 'Orta Saha',     'short': 'OS',  'color': '#8B5CF6'},
    'LM':  {'display': 'Sol Kanat',     'short': 'SK',  'color': '#EC4899'},
    'RM':  {'display': 'Sağ Kanat',     'short': 'SğK', 'color': '#EC4899'},
    'AM':  {'display': 'Ofansif Orta',  'short': 'OO',  'color': '#EC4899'},
    'LW':  {'display': 'Sol Açık',      'short': 'SA',  'color': '#10B981'},
    'RW':  {'display': 'Sağ Açık',      'short': 'SğA', 'color': '#10B981'},
    'CF':  {'display': 'Santrafor',     'short': 'SF',  'color': '#EF4444'},
    'SS':  {'display': 'İkinci Forvet', 'short': 'İF',  'color': '#EF4444'},
}
POSITION_LIST = list(POSITIONS.keys())

# ─── Performans eşik değerleri ───────────────────────────────────────────────
THRESHOLDS = {
    'anomaly_z':        2.5,
    'trend_min_days':   3,
    'elite_percentile': 80,
    'good_percentile':  65,
    'avg_percentile':   50,
    'smax_elite':       31.0,
    'smax_good':        28.0,
    'total_dist_match': 9500,
}

# ─── Dakika Filtreleri (Veri Temizliği İçin Eklendi) ─────────────────────────
DEFAULT_MINUTES = {
    'TRAINING': 45,
    'MATCH': 70
}

# ─── Tüm DB kolonları ────────────────────────────────────────────────────────
ALL_DB_COLUMNS = [
    'minutes', 'total_distance', 'metrage', 'dist_20_25', 'dist_25_plus',
    'dist_acc_3', 'dist_dec_3', 'n_20_25', 'n_25_plus',
    'smax_kmh', 'player_load', 'amp',
]

# ─── IMPACT SCORE MODEL ───────────────────────────────────────────────────────
# Fiziksel performans karar destek sistemi

# Bileşen ağırlıkları
IMPACT_WEIGHTS = {
    'high_speed': 0.25,      # distance > 25 km/h (High Speed Index)
    'explosive': 0.20,       # acceleration + deceleration (Explosive Index)
    'load': 0.20,            # player load intensity (Load Intensity)
    'volume': 0.15,          # total distance (Volume Index)
    'max_velocity': 0.10,    # smax (Max Velocity Indicator)
    'metabolic': 0.10        # AMP / metrage (Metabolic Power)
}

# Impact Score eşikleri
IMPACT_THRESHOLDS = {
    'high_impact_sigma': 1.0,              # 1 std üzeri "High Impact"
    'match_ready_high_speed': 0.7,         # Match Ready: yüksek high speed
    'match_ready_load': 0.6,               # Match Ready: yüksek load
    'finisher_volume': -0.3,               # Finisher: düşük volume
    'finisher_high_speed': 0.5,            # Finisher: yüksek high speed
    'load_risk_threshold': 0.8,            # Load Risk: yüksek load
    'elite_percentile': 75                 # Elite: En iyi %25
}

# Renk kodlama eşikleri (gelişim yüzdeleri)
DEVELOPMENT_COLOR_THRESHOLDS = {
    'excellent': 10,        # +10% ve üzeri → koyu yeşil
    'good': 5,              # +5% ile +10% → açık yeşil
    'stable_low': -5,       # -5% ile +5% → sarı (stabil)
    'declining': -10,       # -5% ile -10% → turuncu
    'critical': -10,        # -10% ve altı → kırmızı
}

# Renkler
IMPACT_COLORS = {
    'excellent_growth': '#059669',    # Koyu yeşil
    'good_growth': '#10B981',         # Açık yeşil
    'stable': '#FBBF24',              # Sarı
    'declining': '#F97316',           # Turuncu
    'critical': '#DC2626',            # Kırmızı
}