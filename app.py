"""
ATLETİK PERFORMANS SİSTEMİ
Ana Uygulaması (app.py)
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from security_module import SecurityManager, require_login, logout, create_user_management_page, login_page
from admin_panel import DataManager
import os

# Sayfa ayarları
st.set_page_config(
    page_title="Atletik Performans Sistemi",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    /* Ana temalar */
    :root {
        --primary-color: #003366;
        --secondary-color: #D32F2F;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --info-color: #2196F3;
    }
    
    /* Header */
    .header-main {
        background: linear-gradient(90deg, #003366, #1a5490);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-main h1 {
        margin: 0;
        font-size: 2rem;
    }
    
    /* Section Headers */
    .section-header {
        color: #003366;
        border-bottom: 3px solid #D32F2F;
        padding-bottom: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    /* Cards */
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #003366;
    }
    
    /* Success/Error Messages */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Buttons */
    .btn-primary {
        background-color: #003366;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
    }
    
    .btn-secondary {
        background-color: #D32F2F;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f5f5f5;
    }
    
    /* Tables */
    table {
        font-size: 0.9em;
    }
    
    /* DataFrames */
    .dataframe {
        font-size: 0.85em !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Başlat
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_rol = None
    st.session_state.user_yas_grubu = None

if 'page' not in st.session_state:
    st.session_state.page = "Ana Sayfa"

# ============================================================
# GİRİŞ KONTROLÜ
# ============================================================

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ============================================================
# ÇIKTI YAPAN KULLANICI İÇİN ANA SAYFA
# ============================================================

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='color: #003366;'>🏆 TFF</h2>
        <p style='color: #666; font-size: 0.9em;'>Genç Milli Takımlar<br/>Atletik Performans Sistemi</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader(f"👤 {st.session_state.username}")
    st.write(f"**Rol:** {st.session_state.user_rol.upper()}")
    st.write(f"**Yaş Grubu:** {st.session_state.user_yas_grubu}")
    
    st.markdown("---")
    
    # Rol bazlı menü
    if st.session_state.user_rol == 'admin':
        menu_options = [
            "📊 Ana Sayfa",
            "⚙️ Admin Panel",
            "👥 Kullanıcı Yönetimi",
            "📈 Analiz & Raporlar",
            "🎯 Scout Analizi",
            "📋 Veri Yönetimi",
            "⚡ Sistem Ayarları"
        ]
    elif st.session_state.user_rol == 'editor':
        menu_options = [
            "📊 Ana Sayfa",
            "📈 Analiz & Raporlar",
            "🎯 Scout Analizi",
            "📋 Veri Girişi",
        ]
    else:  # viewer
        menu_options = [
            "📊 Ana Sayfa",
            "📈 Analiz & Raporlar",
            "🎯 Scout Analizi",
        ]
    
    selected_page = st.radio("📍 Sayfalar", menu_options, label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("🚪 Çıkış Yap", use_container_width=True, type="secondary"):
        logout()

# ============================================================
# SAYFA ROUTER
# ============================================================

dm = DataManager()

if selected_page == "📊 Ana Sayfa":
    st.markdown("""
    <div class="header-main">
        <h1>🏆 Genç Milli Takımlar Atletik Performans Sistemi</h1>
        <p style='margin-top: 10px; font-size: 1.1em;'>TFF Teknik Direktörlüğü - Akademik ve Bilimsel Destek</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hızlı İstatistikler
    st.markdown('<h3 class="section-header">📊 Genel İstatistikler</h3>', unsafe_allow_html=True)
    
    # Veri sayıları
    conn = sqlite3.connect("athletic_performance.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT kamp_id) FROM camp_info')
    total_camps = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT oyuncu_id) FROM player_info')
    total_players = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM training_match_data')
    total_sessions = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(total_distance) FROM training_match_data WHERE tip = "Training"')
    avg_distance_training = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📍 Toplam Kamplar", total_camps)
    with col2:
        st.metric("👥 Toplam Oyuncular", total_players)
    with col3:
        st.metric("⚽ Toplam Seanslar", total_sessions)
    with col4:
        st.metric("📏 Ort. Training Mesafesi", f"{avg_distance_training:,.0f} m")
    
    st.markdown("---")
    
    # Son Kamplar
    st.markdown('<h3 class="section-header">🏕️ Son Kamplar</h3>', unsafe_allow_html=True)
    
    camps = dm.get_all_camps()
    if not camps.empty:
        camps = camps.sort_values('baslangic_tarihi', ascending=False).head(5)
        
        for idx, camp in camps.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{camp['kamp_adi']}** ({camp['yas_grubu']})")
                st.caption(f"📅 {camp['baslangic_tarihi']} → {camp['bitis_tarihi']}")
            with col2:
                st.write(f"📍 {camp['kamp_yeri']}")
            with col3:
                st.write(f"👨‍🏫 {camp['teknik_direktor']}")
    else:
        st.info("Henüz kamp kaydı yok.")
    
    st.markdown("---")
    
    # Hoş Geldin Mesajı
    st.info(f"👋 Hoş geldiniz, {st.session_state.username}! Sistemin gücünü keşfetmek için menüdeki sayfaları ziyaret edin.")

elif selected_page == "⚙️ Admin Panel":
    if st.session_state.user_rol != 'admin':
        st.error("❌ Bu sayfaya erişim izniniz yok!")
    else:
        from admin_panel import main as admin_main
        st.markdown('<h2 class="section-header">⚙️ Admin Panel - Veri Yönetimi</h2>', unsafe_allow_html=True)
        admin_main()

elif selected_page == "👥 Kullanıcı Yönetimi":
    if st.session_state.user_rol != 'admin':
        st.error("❌ Bu sayfaya erişim izniniz yok!")
    else:
        st.markdown('<h2 class="section-header">👥 Kullanıcı Yönetimi</h2>', unsafe_allow_html=True)
        create_user_management_page()

elif selected_page == "📈 Analiz & Raporlar":
    from analysis_pages import main as analysis_main
    analysis_main(dm)

elif selected_page == "🎯 Scout Analizi":
    from scout_pages import main as scout_main
    scout_main(dm)

elif selected_page == "📋 Veri Girişi":
    st.markdown('<h2 class="section-header">📋 Veri Girişi</h2>', unsafe_allow_html=True)
    st.info("Performans verisi girmek için Admin Panel'den 'Performans Verisi' bölümünü kullanınız.")

elif selected_page == "⚡ Sistem Ayarları":
    if st.session_state.user_rol != 'admin':
        st.error("❌ Bu sayfaya erişim izniniz yok!")
    else:
        st.markdown('<h2 class="section-header">⚡ Sistem Ayarları</h2>', unsafe_allow_html=True)
        
        st.subheader("Veritabanı Bilgileri")
        
        conn = sqlite3.connect("athletic_performance.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        st.write("**Tablolar:**")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            st.write(f"- {table[0]}: {count} kayıt")
        
        cursor.close()
        conn.close()
        
        st.markdown("---")
        
        if st.button("🔄 Veritabanını Sıfırla (UYARI: TÜM VERİLER SİLİNECEK!)", type="secondary"):
            st.warning("Bu işlem tüm verileri silecektir! Lütfen yöneticiye başvurunuz.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em; padding: 20px 0;'>
    <p>🏆 <strong>Türkiye Futbol Federasyonu - Genç Milli Takımlar</strong></p>
    <p>📧 Sorular için: admin@tff.org.tr | 📞 Destek: +90 (555) 123-4567</p>
    <p>© 2025 - Tüm Hakları Saklıdır | Gizlilik Politikası</p>
</div>
""", unsafe_allow_html=True)
