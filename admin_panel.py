"""
ATLETİK PERFORMANS SİSTEMİ
Veri Girişi ve Yönetimi Modülü (Admin Panel)
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import numpy as np
from io import BytesIO
import openpyxl

DATABASE_PATH = "athletic_performance.db"

class DataManager:
    """Veritabanı işlemleri"""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    # ========== KAMP İŞLEMLERİ ==========
    def add_camp(self, kamp_adi, baslangic, bitis, toplanma_yeri, kamp_yeri, direktor, yas_grubu):
        """Yeni kamp ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO camp_info 
                (kamp_adi, baslangic_tarihi, bitis_tarihi, toplanma_yeri, kamp_yeri, teknik_direktor, yas_grubu)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (kamp_adi, baslangic, bitis, toplanma_yeri, kamp_yeri, direktor, yas_grubu))
            conn.commit()
            kamp_id = cursor.lastrowid
            conn.close()
            return kamp_id, True
        except Exception as e:
            conn.close()
            return str(e), False
    
    def get_all_camps(self):
        """Tüm kampları getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM camp_info ORDER BY baslangic_tarihi DESC', conn)
        conn.close()
        return df
    
    def get_camp_by_id(self, kamp_id):
        """Kamp detaylarını getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM camp_info WHERE kamp_id = ?', conn, params=[kamp_id])
        conn.close()
        return df.iloc[0] if not df.empty else None
    
    # ========== OYUNCU İŞLEMLERİ ==========
    def add_player(self, ad_soyad, dogum_tarihi=None, yas_grubu=None, kulup=None, pozisyon=None):
        """Yeni oyuncu ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO player_info 
                (ad_soyad, dogum_tarihi, yaas_grubu, kulup, pozisyon)
                VALUES (?, ?, ?, ?, ?)
            ''', (ad_soyad, dogum_tarihi, yas_grubu, kulup, pozisyon))
            conn.commit()
            oyuncu_id = cursor.lastrowid
            conn.close()
            return oyuncu_id, True
        except Exception as e:
            conn.close()
            return str(e), False
    
    def get_all_players(self):
        """Tüm oyuncuları getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM player_info ORDER BY ad_soyad', conn)
        conn.close()
        return df
    
    def get_camp_players(self, kamp_id):
        """Kampın oyuncularını getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT DISTINCT p.* 
            FROM player_info p
            JOIN training_match_data t ON p.oyuncu_id = t.oyuncu_id
            WHERE t.kamp_id = ?
            ORDER BY p.ad_soyad
        ''', conn, params=[kamp_id])
        conn.close()
        return df
    
    def get_players_by_age_group(self, yas_grubu):
        """Yaş grubunun oyuncularını getir"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM player_info WHERE yaas_grubu = ? ORDER BY ad_soyad', 
            conn, params=[yas_grubu]
        )
        conn.close()
        return df
    
    # ========== PERFORMANS VERİSİ İŞLEMLERİ ==========
    def add_performance_data(self, veri_dict):
        """Performans verisi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO training_match_data 
                (kamp_id, oyuncu_id, tarih, tip, minutes, total_distance, metrage,
                 dist_20_25, dist_gt_25, n_20_25, n_gt_25, smax_kmh, player_load, amp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                veri_dict['kamp_id'],
                veri_dict['oyuncu_id'],
                veri_dict['tarih'],
                veri_dict['tip'],
                veri_dict['minutes'],
                veri_dict['total_distance'],
                veri_dict['metrage'],
                veri_dict['dist_20_25'],
                veri_dict['dist_gt_25'],
                veri_dict['n_20_25'],
                veri_dict['n_gt_25'],
                veri_dict['smax_kmh'],
                veri_dict['player_load'],
                veri_dict['amp']
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return str(e)
    
    def get_camp_data(self, kamp_id):
        """Kampın tüm performans verilerini getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT t.*, p.ad_soyad
            FROM training_match_data t
            JOIN player_info p ON t.oyuncu_id = p.oyuncu_id
            WHERE t.kamp_id = ?
            ORDER BY t.tarih, p.ad_soyad
        ''', conn, params=[kamp_id])
        conn.close()
        return df
    
    # ========== TARİH PLANLAMASI ==========
    def add_date_schedule(self, kamp_id, tarih, gun_tipi, notlar=None):
        """Kamp tarih planlaması ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO date_schedule (kamp_id, tarih, gun_tipi, notlar)
                VALUES (?, ?, ?, ?)
            ''', (kamp_id, tarih, gun_tipi, notlar))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return str(e)
    
    def get_camp_schedule(self, kamp_id):
        """Kamp takvimini getir"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM date_schedule WHERE kamp_id = ? ORDER BY tarih',
            conn, params=[kamp_id]
        )
        conn.close()
        return df
    
    # ========== KATILIM DURUMU ==========
    def register_player_to_camp(self, kamp_id, oyuncu_id):
        """Oyuncuyu kampa kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO camp_player_registration (kamp_id, oyuncu_id)
                VALUES (?, ?)
            ''', (kamp_id, oyuncu_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return str(e)
    
    def add_absence(self, kamp_id, oyuncu_id, tarih, neden, notlar=None):
        """Katılmama kaydı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO training_absence (kamp_id, oyuncu_id, tarih, neden, notlar)
                VALUES (?, ?, ?, ?, ?)
            ''', (kamp_id, oyuncu_id, tarih, neden, notlar))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return str(e)
    
    def get_absences(self, kamp_id):
        """Kamp katılmama kayıtlarını getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT a.*, p.ad_soyad
            FROM training_absence a
            JOIN player_info p ON a.oyuncu_id = p.oyuncu_id
            WHERE a.kamp_id = ?
            ORDER BY a.tarih, p.ad_soyad
        ''', conn, params=[kamp_id])
        conn.close()
        return df
    
    # ========== EXPORT/IMPORT ==========
    def export_camp_to_excel(self, kamp_id):
        """Kampı Excel'e aktar"""
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Kamp bilgileri
            camp = self.get_camp_by_id(kamp_id)
            camp_df = pd.DataFrame([camp.to_dict()])
            camp_df.to_excel(writer, sheet_name='Camp_Info', index=False)
            
            # Performans verisi
            data_df = self.get_camp_data(kamp_id)
            data_df.to_excel(writer, sheet_name='Performance_Data', index=False)
            
            # Katılmama kayıtları
            absence_df = self.get_absences(kamp_id)
            if not absence_df.empty:
                absence_df.to_excel(writer, sheet_name='Absences', index=False)
        
        output.seek(0)
        return output

# ============================================================
# STREAMLIT ARAYÜZÜ
# ============================================================

def main():
    st.set_page_config(page_title="Admin Panel - Veri Yönetimi", layout="wide")
    
    # CSS Styling
    st.markdown("""
    <style>
    .header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #003366;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #D32F2F;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 2px solid #003366;
        padding-bottom: 10px;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">⚙️ Admin Panel - Veri Yönetimi</div>', unsafe_allow_html=True)
    
    dm = DataManager()
    
    # Sidebar menü
    menu = st.sidebar.radio(
        "📋 İşlemler",
        ["Kamplar", "Oyuncular", "Performans Verisi", "Katılım Durumu", "📥 Excel İmport", "📄 PDF Rapor", "Raporlar"],
        icons=["📍", "👥", "📊", "✅", "📥", "📄", "📋"]
    )
    
    # ====== KAMPLAR ======
    if menu == "Kamplar":
        st.markdown('<div class="section-header">🏕️ Kamp Yönetimi</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Yeni Kamp Ekle")
            with st.form("yeni_kamp_form"):
                kamp_adi = st.text_input("Kamp Adı *", placeholder="Örn: Ağustos U17 Kampı")
                
                col_dates = st.columns(2)
                with col_dates[0]:
                    baslangic = st.date_input("Başlangıç Tarihi *")
                with col_dates[1]:
                    bitis = st.date_input("Bitiş Tarihi *")
                
                col_yer = st.columns(2)
                with col_yer[0]:
                    toplanma_yeri = st.text_input("Toplanma Yeri", placeholder="Ankara, İstanbul, vb.")
                with col_yer[1]:
                    kamp_yeri = st.text_input("Kamp Yeri", placeholder="Antalya, Bodrum, vb.")
                
                col_info = st.columns(2)
                with col_info[0]:
                    direktor = st.text_input("Teknik Direktör")
                with col_info[1]:
                    yas_grubu = st.selectbox("Yaş Grubu *", ["U15", "U16", "U17", "U19", "U20", "U21"])
                
                if st.form_submit_button("➕ Kamp Ekle", use_container_width=True):
                    if kamp_adi and baslangic and bitis:
                        kamp_id, success = dm.add_camp(
                            kamp_adi, baslangic, bitis, toplanma_yeri, kamp_yeri, direktor, yas_grubu
                        )
                        if success:
                            st.success(f"✅ Kamp başarıyla eklendi! (ID: {kamp_id})")
                            st.rerun()
                        else:
                            st.error(f"❌ Hata: {kamp_id}")
                    else:
                        st.warning("⚠️ Zorunlu alanları doldurunuz!")
        
        with col2:
            st.subheader("Ayarlar")
            if st.button("🔄 Verileri Yenile"):
                st.rerun()
        
        st.markdown("---")
        st.subheader("Mevcut Kamplar")
        camps_df = dm.get_all_camps()
        
        if not camps_df.empty:
            # Görüntüleme formatı
            for idx, camp in camps_df.iterrows():
                with st.expander(f"📍 {camp['kamp_adi']} ({camp['yas_grubu']}) - {camp['baslangic_tarihi']} to {camp['bitis_tarihi']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Toplanma:** {camp['toplanma_yeri']}")
                        st.write(f"**Kamp Yeri:** {camp['kamp_yeri']}")
                    with col2:
                        st.write(f"**Teknik Direktör:** {camp['teknik_direktor']}")
                        st.write(f"**Kamp ID:** {camp['kamp_id']}")
                    with col3:
                        if st.button(f"📥 Export", key=f"export_{camp['kamp_id']}"):
                            excel_file = dm.export_camp_to_excel(camp['kamp_id'])
                            st.download_button(
                                label="⬇️ İndir",
                                data=excel_file,
                                file_name=f"{camp['kamp_adi']}.xlsx",
                                mime="application/vnd.ms-excel"
                            )
        else:
            st.info("📭 Henüz kamp kaydı yok")
    
    # ====== OYUNCULAR ======
    elif menu == "Oyuncular":
        st.markdown('<div class="section-header">👥 Oyuncu Yönetimi</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Yeni Oyuncu Ekle")
            with st.form("yeni_oyuncu_form"):
                ad_soyad = st.text_input("Ad Soyadı *", placeholder="Örn: Adem Yeşilyurt")
                
                col_info = st.columns(3)
                with col_info[0]:
                    dogum_tarihi = st.date_input("Doğum Tarihi")
                with col_info[1]:
                    yas_grubu = st.selectbox("Yaş Grubu", ["U15", "U16", "U17", "U19", "U20", "U21", "Diğer"])
                with col_info[2]:
                    pozisyon = st.selectbox("Pozisyon", ["Savunma", "Orta Saha", "Hücum"])
                
                kulup = st.text_input("Kulüp", placeholder="Örn: Fenerbahçe")
                
                if st.form_submit_button("➕ Oyuncu Ekle", use_container_width=True):
                    if ad_soyad:
                        oyuncu_id, success = dm.add_player(ad_soyad, dogum_tarihi, yas_grubu, kulup, pozisyon)
                        if success:
                            st.success(f"✅ Oyuncu başarıyla eklendi! (ID: {oyuncu_id})")
                            st.rerun()
                        else:
                            st.error(f"❌ Hata: {oyuncu_id}")
                    else:
                        st.warning("⚠️ Ad soyadını doldurunuz!")
        
        st.markdown("---")
        st.subheader("Oyuncu Listesi")
        
        players_df = dm.get_all_players()
        
        if not players_df.empty:
            # Filtreleme
            yas_filter = st.multiselect("Yaş Grubu Filtresi", players_df['yaas_grubu'].unique())
            if yas_filter:
                players_df = players_df[players_df['yaas_grubu'].isin(yas_filter)]
            
            # Tablo gösterimi
            st.dataframe(
                players_df[['oyuncu_id', 'ad_soyad', 'yaas_grubu', 'pozisyon', 'kulup']],
                use_container_width=True,
                hide_index=True
            )
            
            st.metric("Toplam Oyuncu", len(players_df))
        else:
            st.info("📭 Henüz oyuncu kaydı yok")
    
    # ====== PERFORMANS VERİSİ ======
    elif menu == "Performans Verisi":
        st.markdown('<div class="section-header">📊 Performans Verisi Girişi</div>', unsafe_allow_html=True)
        
        # Kamp seç
        camps_df = dm.get_all_camps()
        if camps_df.empty:
            st.error("❌ Önce bir kamp oluşturunuz!")
            return
        
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps_df['kamp_id'].values,
            format_func=lambda x: f"{camps_df[camps_df['kamp_id']==x]['kamp_adi'].values[0]} ({camps_df[camps_df['kamp_id']==x]['baslangic_tarihi'].values[0]})"
        )
        
        camp_data = dm.get_camp_by_id(selected_camp)
        
        # Oyuncu seç
        players = dm.get_all_players()
        if players.empty:
            st.error("❌ Önce oyuncu kaydet!")
            return
        
        # Veri girişi
        with st.form("performans_veri_formu"):
            col1, col2 = st.columns(2)
            
            with col1:
                oyuncu_adi = st.selectbox("Oyuncu", players['ad_soyad'].values)
                oyuncu_id = players[players['ad_soyad'] == oyuncu_adi]['oyuncu_id'].values[0]
                
                tarih = st.date_input("Tarih")
                tip = st.selectbox("Tip", ["Training", "Match"])
            
            with col2:
                minutes = st.number_input("Dakika (min)", min_value=0, max_value=120)
                total_distance = st.number_input("Toplam Mesafe (m)", min_value=0.0)
            
            st.write("---")
            st.write("**Yüksek Hız Metrikleri**")
            col_high_speed = st.columns(4)
            with col_high_speed[0]:
                dist_20_25 = st.number_input("Dist 20-25 (m)", min_value=0.0)
            with col_high_speed[1]:
                dist_gt_25 = st.number_input("Dist > 25 (m)", min_value=0.0)
            with col_high_speed[2]:
                n_20_25 = st.number_input("N 20-25", min_value=0)
            with col_high_speed[3]:
                n_gt_25 = st.number_input("N > 25", min_value=0)
            
            st.write("---")
            st.write("**Diğer Metrikler**")
            col_other = st.columns(4)
            with col_other[0]:
                smax_kmh = st.number_input("SMax (km/h)", min_value=0.0)
            with col_other[1]:
                player_load = st.number_input("Player Load", min_value=0.0)
            with col_other[2]:
                metrage = st.number_input("Metrage", min_value=0.0)
            with col_other[3]:
                amp = st.number_input("AMP", min_value=0.0)
            
            if st.form_submit_button("💾 Verini Kaydet", use_container_width=True):
                veri_dict = {
                    'kamp_id': selected_camp,
                    'oyuncu_id': oyuncu_id,
                    'tarih': tarih,
                    'tip': tip,
                    'minutes': minutes,
                    'total_distance': total_distance,
                    'metrage': metrage,
                    'dist_20_25': dist_20_25,
                    'dist_gt_25': dist_gt_25,
                    'n_20_25': n_20_25,
                    'n_gt_25': n_gt_25,
                    'smax_kmh': smax_kmh,
                    'player_load': player_load,
                    'amp': amp
                }
                
                result = dm.add_performance_data(veri_dict)
                if result is True:
                    st.success("✅ Veri başarıyla kaydedildi!")
                    st.rerun()
                else:
                    st.error(f"❌ Hata: {result}")
        
        # Mevcut veriler
        st.markdown("---")
        st.subheader("Kamp Verisi")
        camp_data_df = dm.get_camp_data(selected_camp)
        
        if not camp_data_df.empty:
            st.dataframe(camp_data_df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 Bu kamp için henüz veri yok")
    
    # ====== KATILIM DURUMU ======
    elif menu == "Katılım Durumu":
        st.markdown('<div class="section-header">✅ Katılım & Absans Yönetimi</div>', unsafe_allow_html=True)
        
        camps_df = dm.get_all_camps()
        if camps_df.empty:
            st.error("❌ Önce bir kamp oluşturunuz!")
            return
        
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps_df['kamp_id'].values,
            format_func=lambda x: f"{camps_df[camps_df['kamp_id']==x]['kamp_adi'].values[0]}"
        )
        
        with st.form("absans_formu"):
            players = dm.get_all_players()
            oyuncu_adi = st.selectbox("Oyuncu", players['ad_soyad'].values)
            oyuncu_id = players[players['ad_soyad'] == oyuncu_adi]['oyuncu_id'].values[0]
            
            tarih = st.date_input("Tarih")
            
            neden = st.selectbox(
                "Katılmama Nedeni",
                ["İnjüri", "Rejenerasyon", "Seçilmedi", "Hastalık", "Diğer"]
            )
            
            notlar = st.text_area("Notlar", max_chars=500)
            
            if st.form_submit_button("💾 Absans Kaydet", use_container_width=True):
                if dm.add_absence(selected_camp, oyuncu_id, tarih, neden, notlar):
                    st.success("✅ Absans kaydedildi!")
                    st.rerun()
                else:
                    st.error("❌ Hata oluştu")
        
        st.markdown("---")
        st.subheader("Absans Kayıtları")
        
        absence_df = dm.get_absences(selected_camp)
        if not absence_df.empty:
            st.dataframe(absence_df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 Bu kamp için henüz absans kaydı yok")
    
    # ====== RAPORLAR ======
    elif menu == "Raporlar":
        st.markdown('<div class="section-header">📄 Rapor ve İhraç</div>', unsafe_allow_html=True)
        
        camps_df = dm.get_all_camps()
        if camps_df.empty:
            st.error("❌ Henüz rapor yok!")
            return
        
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps_df['kamp_id'].values,
            format_func=lambda x: f"{camps_df[camps_df['kamp_id']==x]['kamp_adi'].values[0]}"
        )
        
        camp_info = dm.get_camp_by_id(selected_camp)
        camp_data = dm.get_camp_data(selected_camp)
        
        # Özet istatistikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Oyuncu", len(camp_data['ad_soyad'].unique()))
        with col2:
            st.metric("Toplam Seanslar", len(camp_data))
        with col3:
            avg_distance = camp_data['total_distance'].mean()
            st.metric("Ort. Mesafe (m)", f"{avg_distance:,.0f}")
        with col4:
            avg_speed = camp_data['smax_kmh'].mean()
            st.metric("Ort. Max Speed (km/h)", f"{avg_speed:.2f}")
        
        st.markdown("---")
        
        # Excel Export
        if st.button("📥 Excel'e Aktar"):
            excel_file = dm.export_camp_to_excel(selected_camp)
            st.download_button(
                label="⬇️ İndir",
                data=excel_file,
                file_name=f"{camp_info['kamp_adi']}_Raporu.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    # ====== EXCEL İMPORT ======
    elif menu == "📥 Excel İmport":
        from excel_import import excel_import_page
        excel_import_page(dm)
    
    # ====== PDF RAPOR ======
    elif menu == "📄 PDF Rapor":
        from pdf_report import pdf_report_page
        pdf_report_page(dm)

if __name__ == "__main__":
    main()
