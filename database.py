# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - VERİTABANı YÖNETICISI
# ═══════════════════════════════════════════════════════════════════════════════

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="tff_performans.db"):
        self.db_path = db_path
        self._init_db()
    
    # ─── VERİTABANı BAŞLATMA ────────────────────────────────────────────────────
    def _init_db(self):
        """Veritabanı tablolarını oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ana veri tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            age_group TEXT NOT NULL,
            tarih DATE NOT NULL,
            camp_id INTEGER NOT NULL,
            tip TEXT,
            minutes REAL,
            total_distance REAL,
            metrage REAL,
            smax_kmh REAL,
            dist_25_plus REAL,
            player_load REAL,
            amp REAL,
            hsr REAL,
            acc_over_3 REAL,
            dec_under_minus_3 REAL,
            high_accel_count REAL,
            quick_change_of_direction REAL,
            is_match_day INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Kamp tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS camps (
            camp_id INTEGER PRIMARY KEY,
            age_group TEXT NOT NULL,
            camp_name TEXT NOT NULL,
            start_date DATE,
            end_date DATE,
            location TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Oyuncu bilgileri tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_info (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT UNIQUE NOT NULL,
            age_group TEXT,
            club TEXT,
            position TEXT,
            photo_url TEXT,
            club_logo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Audit Log tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            user TEXT DEFAULT 'system',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Sistem ayarları
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_name TEXT PRIMARY KEY,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    # ─── EXCEL'DEN VERİTABANıNA IMPORT ──────────────────────────────────────────
    def excel_to_db(self, file_obj, age_group):
        """Excel dosyasını veritabanına aktarır"""
        try:
            df = pd.read_excel(file_obj)
            
            # Sütun isimlerini küçük harfe çevir
            df.columns = [col.lower().strip() for col in df.columns]
            
            # Tarih dönüşümü
            if 'tarih' in df.columns:
                df['tarih'] = pd.to_datetime(df['tarih'], errors='coerce')
            
            # Yaş grubu ekle
            df['age_group'] = age_group
            
            # NaN değerleri 0 yap
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)
            
            # Veritabanına yaz
            conn = sqlite3.connect(self.db_path)
            df.to_sql('performance_data', conn, if_exists='append', index=False)
            
            # Kamp bilgisini çıkar ve ekle
            if 'camp_id' in df.columns:
                camps = df[['camp_id']].drop_duplicates()
                for _, row in camps.iterrows():
                    camp_id = int(row['camp_id'])
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT OR IGNORE INTO camps (camp_id, age_group, camp_name) VALUES (?, ?, ?)",
                        (camp_id, age_group, f"Kamp {camp_id}")
                    )
                conn.commit()
            
            # Oyuncu bilgisini çıkar ve ekle
            if 'player_name' in df.columns:
                players = df[['player_name']].drop_duplicates()
                cursor = conn.cursor()
                for _, row in players.iterrows():
                    cursor.execute(
                        "INSERT OR IGNORE INTO player_info (player_name, age_group) VALUES (?, ?)",
                        (row['player_name'], age_group)
                    )
                conn.commit()
            
            # Audit log
            self._log_action("excel_import", f"{age_group} grubu - {len(df)} kayıt yüklendi")
            
            conn.close()
            return {'status': 'success', 'message': f'✅ {len(df)} kayıt başarıyla yüklendi!'}
        
        except Exception as e:
            self._log_action("excel_import_error", str(e))
            return {'status': 'error', 'message': f'❌ Hata: {str(e)}'}
    
    # ─── VERİ SORGULAMA ─────────────────────────────────────────────────────────
    def get_all_data(self):
        """Tüm veriyi çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM performance_data", conn)
        df['tarih'] = pd.to_datetime(df['tarih'])
        conn.close()
        return df
    
    def get_data_by_age_group(self, age_group):
        """Yaş grubuna göre veri çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM performance_data WHERE age_group = ?",
            conn,
            params=(age_group,)
        )
        df['tarih'] = pd.to_datetime(df['tarih'])
        conn.close()
        return df
    
    def get_data_by_player(self, player_name):
        """Oyuncuya göre veri çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM performance_data WHERE player_name = ?",
            conn,
            params=(player_name,)
        )
        df['tarih'] = pd.to_datetime(df['tarih'])
        conn.close()
        return df
    
    def get_players(self, age_group):
        """Yaş grubundaki oyuncu listesini çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT DISTINCT player_name FROM performance_data WHERE age_group = ? ORDER BY player_name",
            conn,
            params=(age_group,)
        )
        conn.close()
        return df['player_name'].tolist()
    
    def get_players_with_info(self, age_group):
        """Oyuncu bilgileriyle birlikte oyuncuları çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT DISTINCT p.player_name as name, i.photo_url, i.club_logo_url
            FROM performance_data p
            LEFT JOIN player_info i ON p.player_name = i.player_name
            WHERE p.age_group = ?
            ORDER BY p.player_name
        """, conn, params=(age_group,))
        conn.close()
        return df.to_dict('records')
    
    def get_camps(self, age_group):
        """Yaş grubundaki kampları çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM camps WHERE age_group = ? ORDER BY camp_name",
            conn,
            params=(age_group,)
        )
        conn.close()
        return df
    
    def get_player_info(self, player_name):
        """Oyuncu bilgisini çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM player_info WHERE player_name = ?",
            conn,
            params=(player_name,)
        )
        conn.close()
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}
    
    # ─── SİLME İŞLEMLERİ ────────────────────────────────────────────────────────
    def delete_excel_import(self, age_group, camp_id=None):
        """Yüklenen Excel verilerini siler"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if camp_id:
                cursor.execute(
                    "DELETE FROM performance_data WHERE age_group = ? AND camp_id = ?",
                    (age_group, camp_id)
                )
                self._log_action("delete_camp", f"{age_group} - Kamp {camp_id} silindi")
            else:
                cursor.execute(
                    "DELETE FROM performance_data WHERE age_group = ?",
                    (age_group,)
                )
                self._log_action("delete_age_group", f"{age_group} grubu verileri silindi")
            
            conn.commit()
            conn.close()
            return {'status': 'success', 'message': '✅ Veriler başarıyla silindi!'}
        except Exception as e:
            self._log_action("delete_error", str(e))
            return {'status': 'error', 'message': f'❌ Hata: {str(e)}'}
    
    def delete_player(self, player_name):
        """Oyuncunun tüm kayıtlarını siler"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM performance_data WHERE player_name = ?", (player_name,))
            cursor.execute("DELETE FROM player_info WHERE player_name = ?", (player_name,))
            
            self._log_action("delete_player", f"{player_name} oyuncusu silindi")
            conn.commit()
            conn.close()
            return {'status': 'success', 'message': f'✅ {player_name} başarıyla silindi!'}
        except Exception as e:
            self._log_action("delete_error", str(e))
            return {'status': 'error', 'message': f'❌ Hata: {str(e)}'}
    
    # ─── OYUNCU GÜNCELLEME ──────────────────────────────────────────────────────
    def update_player_images(self, player_name, photo_url, club_logo_url):
        """Oyuncu fotoğraf ve logosu günceller"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE player_info
                SET photo_url = ?, club_logo_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE player_name = ?
            """, (photo_url, club_logo_url, player_name))
            
            conn.commit()
            conn.close()
            self._log_action("update_player_images", f"{player_name} görselleri güncellendi")
            return True
        except:
            return False
    
    # ─── AUDIT LOG ───────────────────────────────────────────────────────────────
    def _log_action(self, action, details):
        """Yapılan işlemleri log'a kaydeder"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_log (action, details) VALUES (?, ?)",
                (action, details)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_audit_log(self, limit=50):
        """Audit log'u çeker"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
            conn,
            params=(limit,)
        )
        conn.close()
        return df if not df.empty else None

# Global instance
db_manager = DatabaseManager()

print("✅ Veritabanı bağlantısı başarılı | TFF Performans")
