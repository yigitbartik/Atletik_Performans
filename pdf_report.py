"""
ATLETİK PERFORMANS SİSTEMİ
PDF Rapor Generator (Profesyonel Raporlar)
"""

import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

class PDFReportGenerator:
    """PDF rapor oluşturma"""
    
    def __init__(self, db_path="athletic_performance.db"):
        self.db_path = db_path
        self.width = 210  # A4 width mm
        self.height = 297  # A4 height mm
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_player_info(self, oyuncu_id):
        """Oyuncu bilgilerini getir"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM player_info WHERE oyuncu_id = ?',
            conn, params=[oyuncu_id]
        )
        conn.close()
        return df.iloc[0] if not df.empty else None
    
    def get_player_camp_data(self, oyuncu_id, kamp_id):
        """Oyuncunun kamp verilerini getir"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT 
                t.*,
                c.kamp_adi,
                c.baslangic_tarihi,
                c.bitis_tarihi
            FROM training_match_data t
            JOIN camp_info c ON t.kamp_id = c.kamp_id
            WHERE t.oyuncu_id = ? AND t.kamp_id = ?
            ORDER BY t.tarih
        ''', conn, params=[oyuncu_id, kamp_id])
        conn.close()
        return df
    
    def create_pdf_report(self, oyuncu_id, kamp_ids, background_image=None):
        """
        Oyuncu PDF raporu oluştur
        
        Parameters:
        - oyuncu_id: Oyuncu ID
        - kamp_ids: List of kamp IDs
        - background_image: Arka plan görsel yolu
        """
        
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        
        oyuncu = self.get_player_info(oyuncu_id)
        if oyuncu is None:
            return None
        
        # ========== SAYFA 1: KAPAK ==========
        pdf.add_page()
        
        # Arka plan
        if background_image:
            try:
                pdf.image(background_image, x=0, y=0, w=self.width, h=self.height)
            except:
                pass
        
        # Başlık
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(0, 51, 102)  # Lacivert
        pdf.ln(60)
        pdf.cell(0, 15, "ATLETİK PERFORMANS RAPORU", ln=True, align='C')
        
        # Oyuncu adı
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(211, 47, 47)  # Kırmızı
        pdf.ln(10)
        pdf.cell(0, 15, str(oyuncu['ad_soyad']), ln=True, align='C')
        
        # Oyuncu bilgileri
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(100, 100, 100)
        pdf.ln(20)
        
        info_text = f"""
Yaş Grubu: {oyuncu['yaas_grubu']}
Konum: {oyuncu['pozisyon']}
Kulüp: {oyuncu['kulup']}
Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y')}
        """
        pdf.multi_cell(0, 8, info_text, align='C')
        
        # TFF Logo
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(150, 150, 150)
        pdf.ln(40)
        pdf.cell(0, 10, "Türkiye Futbol Federasyonu", ln=True, align='C')
        pdf.cell(0, 8, "Genç Milli Takımlar", ln=True, align='C')
        
        # ========== VERİ SAYFALARI ==========
        for kamp_id in kamp_ids:
            camp_data = self.get_player_camp_data(oyuncu_id, kamp_id)
            
            if camp_data.empty:
                continue
            
            camp_name = camp_data.iloc[0]['kamp_adi']
            
            # Sayfa ekle
            pdf.add_page()
            
            # Başlık
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, f"📍 {camp_name}", ln=True)
            
            # Tarih aralığı
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(100, 100, 100)
            start_date = camp_data.iloc[0]['baslangic_tarihi']
            end_date = camp_data.iloc[0]['bitis_tarihi']
            pdf.cell(0, 5, f"{start_date} - {end_date}", ln=True)
            
            pdf.ln(5)
            
            # İstatistikler
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, "KAMP İSTATİSTİKLERİ", ln=True)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.set_fill_color(240, 240, 240)
            
            stats = {
                'Toplam Seanslar': len(camp_data),
                'Toplam Dakika': int(camp_data['minutes'].sum()),
                'Ort. Dakika': f"{camp_data['minutes'].mean():.1f}",
                'Ort. Mesafe': f"{camp_data['total_distance'].mean():.0f} m",
                'Max Hız': f"{camp_data['smax_kmh'].max():.1f} km/h",
                'Ort. Speed Max': f"{camp_data['smax_kmh'].mean():.1f} km/h",
                'Ort. Player Load': f"{camp_data['player_load'].mean():.1f}",
                'Ort. Dist > 25': f"{camp_data['dist_gt_25'].mean():.0f} m"
            }
            
            # İstatistikleri 2 sütunda göster
            col_width = (self.width - 30) / 2
            col1_x = 15
            col2_x = 15 + col_width + 5
            
            x_pos = 0
            for i, (label, value) in enumerate(stats.items()):
                if i % 2 == 0:
                    x_pos = col1_x
                    y_pos = pdf.get_y()
                else:
                    x_pos = col2_x
                    pdf.set_y(y_pos)
                
                pdf.set_x(x_pos)
                pdf.cell(col_width - 5, 8, f"{label}: {value}", ln=(i % 2 == 1))
            
            pdf.ln(5)
            
            # Detaylı veriler tablosu
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 8, "GÜNLÜK VERİLER", ln=True)
            
            # Tablo başlığı
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(0, 51, 102)
            
            headers = ['Tarih', 'Tip', 'Min', 'Mesafe', 'Speed', 'Load', 'Dist>25']
            col_widths = [25, 20, 15, 20, 20, 18, 20]
            
            for header, width in zip(headers, col_widths):
                pdf.cell(width, 7, header, fill=True, border=1, align='C')
            pdf.ln()
            
            # Tablo verileri
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(245, 245, 245)
            
            fill = False
            for _, row in camp_data.iterrows():
                pdf.cell(col_widths[0], 7, str(row['tarih'])[:10], border=1, fill=fill)
                pdf.cell(col_widths[1], 7, row['tip'][:7], border=1, fill=fill)
                pdf.cell(col_widths[2], 7, f"{int(row['minutes'])}", border=1, fill=fill, align='C')
                pdf.cell(col_widths[3], 7, f"{row['total_distance']:.0f}", border=1, fill=fill, align='C')
                pdf.cell(col_widths[4], 7, f"{row['smax_kmh']:.1f}", border=1, fill=fill, align='C')
                pdf.cell(col_widths[5], 7, f"{row['player_load']:.0f}", border=1, fill=fill, align='C')
                pdf.cell(col_widths[6], 7, f"{row['dist_gt_25']:.0f}", border=1, fill=fill, align='C')
                pdf.ln()
                
                fill = not fill
        
        # ========== SON SAYFA: ÖZET ==========
        pdf.add_page()
        
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "GENEL ÖZET", ln=True)
        
        # Tüm kamplar için genel istatistikler
        conn = self.get_connection()
        all_data = pd.read_sql_query('''
            SELECT * FROM training_match_data
            WHERE oyuncu_id = ?
        ''', conn, params=[oyuncu_id])
        conn.close()
        
        if not all_data.empty:
            pdf.set_font("Helvetica", "", 11)
            pdf.ln(5)
            
            summary = f"""
Toplam Seanslar: {len(all_data)}
Toplam Dakika: {int(all_data['minutes'].sum())}
Ortalama Dakika/Seans: {all_data['minutes'].mean():.1f}
Ortalama Mesafe: {all_data['total_distance'].mean():.0f} m
Ortalama Max Hız: {all_data['smax_kmh'].mean():.1f} km/h
Maksimum Hız: {all_data['smax_kmh'].max():.1f} km/h
Ortalama Player Load: {all_data['player_load'].mean():.1f}
Ortalama Dist > 25: {all_data['dist_gt_25'].mean():.0f} m
Toplam Dist > 25: {all_data['dist_gt_25'].sum():.0f} m

Training Seansları: {len(all_data[all_data['tip'] == 'Training'])}
Match Seansları: {len(all_data[all_data['tip'] == 'Match'])}
            """
            
            pdf.multi_cell(0, 7, summary)
        
        # İmza alanı
        pdf.ln(20)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, "_____________________", ln=True)
        pdf.cell(0, 5, "Teknik Direktör", ln=True)
        
        pdf.ln(10)
        pdf.cell(0, 5, "_____________________", ln=True)
        pdf.cell(0, 5, "Analiz Sorumlusu", ln=True)
        
        return pdf.output(dest='S').encode('latin-1')

# ============================================================
# STREAMLIT UI FUNCTION
# ============================================================

def pdf_report_page(dm):
    """PDF Rapor UI Sayfası"""
    
    st.markdown('<h2 class="section-header">📄 PDF Rapor Oluşturucu</h2>', unsafe_allow_html=True)
    
    # Oyuncu seç
    players = dm.get_all_players()
    if players.empty:
        st.error("Oyuncu yok!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_player = st.selectbox(
            "Oyuncu Seçiniz",
            players['oyuncu_id'].values,
            format_func=lambda x: players[players['oyuncu_id']==x]['ad_soyad'].values[0]
        )
    
    oyuncu_adi = players[players['oyuncu_id']==selected_player]['ad_soyad'].values[0]
    
    st.markdown("---")
    
    # Kampları seç
    conn = sqlite3.connect("athletic_performance.db")
    camps_df = pd.read_sql_query('''
        SELECT DISTINCT c.kamp_id, c.kamp_adi, c.yas_grubu
        FROM training_match_data t
        JOIN camp_info c ON t.kamp_id = c.kamp_id
        WHERE t.oyuncu_id = ?
        ORDER BY c.baslangic_tarihi DESC
    ''', conn, params=[selected_player])
    conn.close()
    
    if camps_df.empty:
        st.warning(f"{oyuncu_adi} için veri yok!")
        return
    
    st.subheader("📍 Raporlanacak Kampları Seçiniz")
    
    selected_camps = st.multiselect(
        "Kamplar",
        camps_df['kamp_id'].values,
        format_func=lambda x: camps_df[camps_df['kamp_id']==x]['kamp_adi'].values[0],
        default=camps_df['kamp_id'].values[:1]  # İlk kamı default seç
    )
    
    if not selected_camps:
        st.warning("En az bir kamp seçiniz!")
        return
    
    st.markdown("---")
    
    # Arka plan görsel
    st.subheader("🎨 Arka Plan Ayarları")
    
    use_background = st.checkbox("Arka plan görsel kullan", value=True)
    
    background_image = None
    if use_background:
        col1, col2 = st.columns(2)
        
        with col1:
            bg_option = st.radio("Arka Plan Tipi", ["TFF Logosu", "Özel Görsel"])
        
        with col2:
            if bg_option == "Özel Görsel":
                bg_file = st.file_uploader("Görsel yükleyin", type=['png', 'jpg', 'jpeg'])
                if bg_file:
                    background_image = bg_file
            else:
                # Varsayılan TFF logosu
                background_image = "/mnt/user-data/uploads/grey.png" if use_background else None
    
    st.markdown("---")
    
    # PDF Oluştur
    if st.button("📄 PDF Rapor Oluştur", type="primary", use_container_width=True):
        with st.spinner("Rapor oluşturuluyor..."):
            generator = PDFReportGenerator()
            
            try:
                pdf_data = generator.create_pdf_report(
                    selected_player,
                    selected_camps,
                    background_image
                )
                
                if pdf_data:
                    # Download butonu
                    st.success("✅ Rapor başarıyla oluşturuldu!")
                    
                    filename = f"{oyuncu_adi}_Raporu_{datetime.now().strftime('%d_%m_%Y')}.pdf"
                    
                    st.download_button(
                        label="📥 PDF'i İndir",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Rapor özeti
                    st.markdown("---")
                    st.subheader("📊 Rapor Özeti")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Kamp Sayısı", len(selected_camps))
                    with col2:
                        st.metric("Dosya Adı", filename.split('.')[0][:30])
                    with col3:
                        st.metric("Oluşturma Tarihi", datetime.now().strftime('%d.%m.%Y'))
                
                else:
                    st.error("Rapor oluşturulurken hata oluştu!")
            
            except Exception as e:
                st.error(f"Hata: {str(e)}")
