"""
ATLETİK PERFORMANS SİSTEMİ
Excel Veri İmport Modülü (Otomatik Algılama)
"""

import pandas as pd
import sqlite3
from datetime import datetime
import streamlit as st
from io import BytesIO

class ExcelImporter:
    """Excel dosyasından veri import ve otomatik algılama"""
    
    def __init__(self, db_path="athletic_performance.db"):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def detect_excel_structure(self, excel_file):
        """Excel dosyasının yapısını otomatik algıla"""
        
        try:
            # Tüm sheet'leri oku
            xls = pd.ExcelFile(excel_file)
            sheets_info = {}
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheets_info[sheet_name] = {
                    'data': df,
                    'columns': df.columns.tolist(),
                    'rows': len(df)
                }
            
            return sheets_info, True, "Excel dosyası başarıyla algılandı"
        
        except Exception as e:
            return None, False, str(e)
    
    def import_camp_info(self, df):
        """Camp_Info sheet'ini import et"""
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Sütunları normalize et
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT OR IGNORE INTO camp_info 
                    (kamp_adi, baslangic_tarihi, bitis_tarihi, toplanma_yeri, 
                     kamp_yeri, teknik_direktor, yas_grubu)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('kamp_adi') or row.get('kamp_adı'),
                    pd.to_datetime(row.get('baslangic_tarihi') or row.get('başlangıç_tarihi')),
                    pd.to_datetime(row.get('bitis_tarihi') or row.get('bitiş_tarihi')),
                    row.get('toplanma_yeri'),
                    row.get('kamp_yeri'),
                    row.get('teknik_direktor'),
                    row.get('yas_grubu') or row.get('yaş_grubu')
                ))
            
            conn.commit()
            conn.close()
            return True, f"{len(df)} kamp kaydı eklendi"
        
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def import_player_info(self, df):
        """Player_Info sheet'ini import et"""
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            for _, row in df.iterrows():
                oyuncu_adi = row.get('oyuncu_adı') or row.get('oyuncu_adi') or row.get('ad_soyad') or row.get('name')
                
                # Oyuncuyu ekle
                cursor.execute('''
                    INSERT OR IGNORE INTO player_info 
                    (ad_soyad, dogum_tarihi, yaas_grubu, kulup, pozisyon)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    oyuncu_adi,
                    pd.to_datetime(row.get('dogum_tarihi') or row.get('doğum_tarihi')),
                    row.get('yas_grubu') or row.get('yaş_grubu'),
                    row.get('kulup') or row.get('kulüp'),
                    row.get('pozisyon')
                ))
            
            conn.commit()
            conn.close()
            return True, f"{len(df)} oyuncu kaydı eklendi"
        
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def import_training_data(self, df):
        """Training_Match_Data sheet'ini import et"""
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Oyuncu ve kamp ID'lerini bul
            for _, row in df.iterrows():
                oyuncu_adi = row.get('name') or row.get('ad_soyad') or row.get('oyuncu_adı')
                
                # Oyuncu ID'sini bul
                cursor.execute('SELECT oyuncu_id FROM player_info WHERE ad_soyad = ?', (oyuncu_adi,))
                oyuncu_result = cursor.fetchone()
                
                if not oyuncu_result:
                    # Oyuncu varsa ekle
                    cursor.execute('''
                        INSERT OR IGNORE INTO player_info (ad_soyad)
                        VALUES (?)
                    ''', (oyuncu_adi,))
                    oyuncu_id = cursor.lastrowid
                else:
                    oyuncu_id = oyuncu_result[0]
                
                kamp_id = int(row.get('kamp_id') or row.get('camp_id') or 1)
                
                cursor.execute('''
                    INSERT OR IGNORE INTO training_match_data 
                    (kamp_id, oyuncu_id, tarih, tip, minutes, total_distance, 
                     metrage, dist_20_25, dist_gt_25, n_20_25, n_gt_25, 
                     smax_kmh, player_load, amp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    kamp_id,
                    oyuncu_id,
                    pd.to_datetime(row.get('tarih') or row.get('date')),
                    row.get('tip') or row.get('type') or 'Training',
                    int(row.get('minutes') or 0),
                    float(row.get('total_distance') or row.get('total_distance') or 0),
                    float(row.get('metrage') or 0),
                    float(row.get('dist_20_25') or row.get('dist_20_25') or 0),
                    float(row.get('dist_>_25') or row.get('dist_gt_25') or row.get('dist > 25') or 0),
                    int(row.get('n_20_25') or 0),
                    int(row.get('n_>_25') or row.get('n_gt_25') or row.get('n > 25') or 0),
                    float(row.get('smax_(kmh)') or row.get('smax_kmh') or row.get('speed_max') or 0),
                    float(row.get('player_load') or 0),
                    float(row.get('amp') or 0)
                ))
            
            conn.commit()
            conn.close()
            return True, f"{len(df)} performans kaydı eklendi"
        
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def import_date_schedule(self, df):
        """Date_Info sheet'ini import et"""
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT OR IGNORE INTO date_schedule 
                    (kamp_id, tarih, gun_tipi, notlar)
                    VALUES (?, ?, ?, ?)
                ''', (
                    int(row.get('kamp_id') or row.get('camp_id') or 1),
                    pd.to_datetime(row.get('date') or row.get('tarih')),
                    row.get('day_type') or row.get('gun_tipi') or row.get('day'),
                    row.get('notes') or row.get('notlar')
                ))
            
            conn.commit()
            conn.close()
            return True, f"{len(df)} tarih kaydı eklendi"
        
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def auto_import(self, excel_file):
        """Otomatik import - tüm sheet'leri algılayıp içe aktar"""
        
        sheets_info, success, message = self.detect_excel_structure(excel_file)
        
        if not success:
            return False, message
        
        results = {}
        
        # Her sheet'i kontrol et ve uygun tabloyu import et
        for sheet_name, info in sheets_info.items():
            sheet_lower = sheet_name.lower()
            
            # Camp Info
            if 'camp' in sheet_lower or 'kamp' in sheet_lower:
                success, msg = self.import_camp_info(info['data'])
                results['Camp Info'] = msg
            
            # Player Info
            elif 'player' in sheet_lower or 'oyuncu' in sheet_lower:
                success, msg = self.import_player_info(info['data'])
                results['Player Info'] = msg
            
            # Training Data
            elif 'training' in sheet_lower or 'performance' in sheet_lower or 'athletik' in sheet_lower:
                success, msg = self.import_training_data(info['data'])
                results['Training Data'] = msg
            
            # Date Info
            elif 'date' in sheet_lower or 'tarih' in sheet_lower:
                success, msg = self.import_date_schedule(info['data'])
                results['Date Schedule'] = msg
        
        return True, results

# ============================================================
# STREAMLIT UI FUNCTION
# ============================================================

def excel_import_page(dm):
    """Excel Import UI Sayfası"""
    
    st.markdown('<h2 class="section-header">📥 Excel Veri İçe Aktarma</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Excel dosyasını yükleyin ve sistem otomatik olarak algılar ve içe aktarır.
    
    **Desteklenen Sheet'ler:**
    - 📍 Camp_Info (Kamplar)
    - 👥 Player_Info (Oyuncular)
    - 📊 Training_Match_Data (Performans)
    - 📅 Date_Info (Takvim)
    """)
    
    uploaded_file = st.file_uploader(
        "Excel dosyası seçiniz",
        type=['xlsx', 'xls'],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        st.markdown("---")
        
        # Dosya bilgileri
        st.subheader("📋 Dosya Bilgileri")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Dosya Adı:** {uploaded_file.name}")
        with col2:
            st.write(f"**Dosya Boyutu:** {uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.write(f"**Yükleme Zamanı:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Yapı algılama
        st.subheader("🔍 Dosya Yapısı Algılanıyor...")
        
        importer = ExcelImporter()
        sheets_info, success, message = importer.detect_excel_structure(uploaded_file)
        
        if success:
            st.success(message)
            
            # Sheet'leri göster
            st.subheader("📊 Algılanan Sheet'ler")
            
            for sheet_name, info in sheets_info.items():
                with st.expander(f"📄 {sheet_name} ({info['rows']} satır)"):
                    st.write(f"**Sütunlar:** {', '.join(info['columns'])}")
                    st.dataframe(info['data'].head(3), use_container_width=True)
            
            # Import butonu
            st.markdown("---")
            
            if st.button("📥 Verileri İçe Aktar", type="primary", use_container_width=True):
                with st.spinner("Veriler içe aktarılıyor..."):
                    success, results = importer.auto_import(uploaded_file)
                    
                    if success:
                        st.success("✅ Veriler başarıyla içe aktarıldı!")
                        
                        st.subheader("📊 İçe Aktarma Sonuçları")
                        for sheet_type, message in results.items():
                            st.info(f"✅ {sheet_type}: {message}")
                        
                        st.balloons()
                    else:
                        st.error(f"❌ Hata: {results}")
        
        else:
            st.error(f"❌ Hata: {message}")
