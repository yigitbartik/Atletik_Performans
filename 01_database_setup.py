"""
YENİ MILLI TAKIMLAR ATLETİK PERFORMANS SİSTEMİ
Database Kurulum ve İnitiyalizasyon
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_PATH = "athletic_performance.db"

def init_database():
    """SQLite database'i oluştur ve tabloları başlat"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 1. CAMP_INFO Tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS camp_info (
        kamp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_adi TEXT NOT NULL UNIQUE,
        baslangic_tarihi DATE NOT NULL,
        bitis_tarihi DATE NOT NULL,
        toplanma_yeri TEXT,
        kamp_yeri TEXT,
        teknik_direktor TEXT,
        yas_grubu TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. PLAYER_INFO Tablosu (Oyuncu bilgileri)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_info (
        oyuncu_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT NOT NULL,
        dogum_tarihi DATE,
        yaas_grubu TEXT,
        kulup TEXT,
        pozisyon TEXT,
        tc_numarasi TEXT,
        uluslararasi_tecrube INTEGER DEFAULT 0,
        en_yuksek_hiz REAL,
        en_yuksek_load REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. CAMP_PLAYER_REGISTRATION (Oyuncu-Kamp İlişkisi)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS camp_player_registration (
        kayit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_id INTEGER NOT NULL,
        oyuncu_id INTEGER NOT NULL,
        katilim_durumu TEXT,
        antrenman_sayisi INTEGER DEFAULT 0,
        mac_sayisi INTEGER DEFAULT 0,
        toplam_dakika INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (kamp_id) REFERENCES camp_info(kamp_id),
        FOREIGN KEY (oyuncu_id) REFERENCES player_info(oyuncu_id),
        UNIQUE(kamp_id, oyuncu_id)
    )
    ''')
    
    # 4. DATE_SCHEDULE (Kamp içi gün planlaması)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS date_schedule (
        takvim_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_id INTEGER NOT NULL,
        tarih DATE NOT NULL,
        gun_tipi TEXT NOT NULL,
        notlar TEXT,
        FOREIGN KEY (kamp_id) REFERENCES camp_info(kamp_id),
        UNIQUE(kamp_id, tarih)
    )
    ''')
    
    # 5. TRAINING_MATCH_DATA (Ana performans verileri)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_match_data (
        veri_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_id INTEGER NOT NULL,
        oyuncu_id INTEGER NOT NULL,
        tarih DATE NOT NULL,
        tip TEXT NOT NULL,
        
        -- Dakika ve Mesafe
        minutes INTEGER,
        total_distance REAL,
        metrage REAL,
        
        -- Yüksek Hız Metrikler
        dist_20_25 REAL,
        dist_gt_25 REAL,
        n_20_25 INTEGER,
        n_gt_25 INTEGER,
        
        -- Diğer Metrikler
        smax_kmh REAL,
        player_load REAL,
        amp REAL,
        
        -- Sistem
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (kamp_id) REFERENCES camp_info(kamp_id),
        FOREIGN KEY (oyuncu_id) REFERENCES player_info(oyuncu_id),
        UNIQUE(kamp_id, oyuncu_id, tarih, tip)
    )
    ''')
    
    # 6. TEAM_STATS_DAILY (Günlük takım istatistikleri - cache)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_stats_daily (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_id INTEGER NOT NULL,
        tarih DATE NOT NULL,
        tip TEXT NOT NULL,
        
        minutes_min REAL, minutes_max REAL, minutes_avg REAL,
        distance_min REAL, distance_max REAL, distance_avg REAL,
        smax_min REAL, smax_max REAL, smax_avg REAL,
        player_load_min REAL, player_load_max REAL, player_load_avg REAL,
        amp_min REAL, amp_max REAL, amp_avg REAL,
        
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kamp_id) REFERENCES camp_info(kamp_id),
        UNIQUE(kamp_id, tarih, tip)
    )
    ''')
    
    # 7. TRAINING_ABSENCE (Antrenman/Maç katılmama nedenleri)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_absence (
        absence_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_id INTEGER NOT NULL,
        oyuncu_id INTEGER NOT NULL,
        tarih DATE NOT NULL,
        neden TEXT,
        notlar TEXT,
        FOREIGN KEY (kamp_id) REFERENCES camp_info(kamp_id),
        FOREIGN KEY (oyuncu_id) REFERENCES player_info(oyuncu_id),
        UNIQUE(kamp_id, oyuncu_id, tarih)
    )
    ''')
    
    # 8. SCOUTING_SCORES (Scout puanlaması - ağırlıklı skorlar)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scouting_scores (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kamp_id INTEGER NOT NULL,
        oyuncu_id INTEGER NOT NULL,
        tarih_baslangic DATE,
        tarih_bitis DATE,
        
        -- Metrik skorları (0-100)
        speed_score REAL,
        distance_score REAL,
        high_speed_score REAL,
        load_score REAL,
        consistency_score REAL,
        overall_score REAL,
        
        -- Detaylar
        toplam_minutes INTEGER,
        toplam_mac INTEGER,
        toplam_antrenman INTEGER,
        
        ranking_position INTEGER,
        notes TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kamp_id) REFERENCES camp_info(kamp_id),
        FOREIGN KEY (oyuncu_id) REFERENCES player_info(oyuncu_id)
    )
    ''')
    
    # İndeksleri oluştur (sorgu performansı için)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_training_match_kamp_tarih ON training_match_data(kamp_id, tarih)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_training_match_oyuncu ON training_match_data(oyuncu_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_yas_grubu ON player_info(yaas_grubu)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_camp_dates ON camp_info(baslangic_tarihi, bitis_tarihi)')
    
    conn.commit()
    print("✅ Database başarıyla oluşturuldu!")
    print(f"📁 Dosya: {DATABASE_PATH}")
    
    conn.close()

def import_excel_to_db(excel_path):
    """Excel dosyasından verileri database'e aktar"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Camp Info
        camps_df = pd.read_excel(excel_path, sheet_name='Camp_Info')
        camps_df.columns = ['kamp_id', 'kamp_adi', 'baslangic_tarihi', 'bitis_tarihi', 
                           'toplanma_yeri', 'kamp_yeri', 'teknik_direktor', 'yas_grubu']
        camps_df.to_sql('camp_info', conn, if_exists='append', index=False)
        print(f"✅ {len(camps_df)} kamp kaydı eklendi")
        
        # Player Info
        players_df = pd.read_excel(excel_path, sheet_name='Player_Info')
        players_df.columns = ['ad_soyad', 'dogum_tarihi', 'yaas_grubu', 'kamp_id', 'kulup']
        players_df.to_sql('player_info', conn, if_exists='append', index=False)
        print(f"✅ {len(players_df)} oyuncu kaydı eklendi")
        
        # Date Info
        dates_df = pd.read_excel(excel_path, sheet_name='Date_Info')
        dates_df.columns = ['tarih', 'gun_tipi', 'yas_grubu', 'kamp_id']
        dates_df.to_sql('date_schedule', conn, if_exists='append', index=False)
        print(f"✅ {len(dates_df)} tarih kaydı eklendi")
        
        # Training Match Data
        data_df = pd.read_excel(excel_path, sheet_name='Training_Match_Data')
        data_df.columns = ['ad_soyad', 'tarih', 'minutes', 'total_distance', 'metrage',
                          'dist_20_25', 'dist_gt_25', 'n_20_25', 'n_gt_25', 'smax_kmh',
                          'player_load', 'amp', 'tip', 'kamp_id']
        
        # Oyuncu ID'lerini bul ve ekle
        players_lookup = pd.read_sql('SELECT oyuncu_id, ad_soyad FROM player_info', conn)
        data_df = data_df.merge(players_lookup, left_on='ad_soyad', right_on='ad_soyad', how='left')
        
        # Sütunları düzenle
        data_df = data_df[['kamp_id', 'oyuncu_id', 'tarih', 'tip', 'minutes', 'total_distance',
                          'metrage', 'dist_20_25', 'dist_gt_25', 'n_20_25', 'n_gt_25',
                          'smax_kmh', 'player_load', 'amp']]
        
        data_df.to_sql('training_match_data', conn, if_exists='append', index=False)
        print(f"✅ {len(data_df)} performans kaydı eklendi")
        
        print("\n✅ Tüm veriler başarıyla içe aktarıldı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    print("🚀 Veritabanı başlatılıyor...\n")
    
    # Database'i oluştur
    init_database()
    
    # Excel'den veri aktar (varsa)
    if os.path.exists('/mnt/user-data/uploads/Work_Data.xlsx'):
        print("\n📊 Excel dosyası bulundu. Veriler aktarılıyor...\n")
        import_excel_to_db('/mnt/user-data/uploads/Work_Data.xlsx')
    else:
        print("⚠️ Excel dosyası bulunamadı. Manuel girişle kullanabilirsiniz.")
