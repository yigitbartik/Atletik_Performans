# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - ANA SAYFA (app.py)
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import AGE_GROUPS, COLORS
from database import db_manager
from styles import inject_styles, sidebar_brand, section_title, page_header

st.set_page_config(
    page_title="TFF Performans Sistemi",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit timeout sorunu çözmesi
st.set_page_config(client={'maxMessageSize': 5 * 1024 * 1024})

inject_styles()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    
    st.markdown('<div class="sidebar-label">📂 VERİ YÜKLE</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Excel Dosyası", type=['xlsx'], label_visibility='collapsed')
    
    if uploaded_file:
        age_group = st.selectbox("Yaş Grubu Seçin", AGE_GROUPS, key="upload_age")
        if st.button("✅ VERİTABANıNA AKTAR", use_container_width=True, type="primary"):
            with st.spinner("⏳ Yükleniyor..."):
                result = db_manager.excel_to_db(uploaded_file, age_group)
                if result['status'] == 'success':
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
    
    st.divider()
    
    st.markdown('<div class="sidebar-label">📊 SİSTEM ÖZETİ</div>', unsafe_allow_html=True)
    try:
        all_data = db_manager.get_all_data()
        if not all_data.empty:
            col1, col2 = st.columns(2)
            match_data = all_data[all_data['tip'].str.upper() == 'MATCH']
            training_data = all_data[all_data['tip'].str.upper() == 'TRAINING']
            
            with col1:
                st.metric("🏃 Oyuncu", all_data['player_name'].nunique())
                st.metric("⚽ Kamp", all_data['camp_id'].nunique())
            
            with col2:
                st.metric("📋 Kayıt", len(all_data))
                st.metric("🎯 Maç Günü", match_data['tarih'].nunique() if not match_data.empty else 0)
    except:
        pass
    
    st.divider()
    
    st.markdown('<div class="sidebar-label">⚙️ YÖNETİM</div>', unsafe_allow_html=True)
    if st.button("🔐 Admin Paneline Git", use_container_width=True):
        st.switch_page("pages/09_Admin_Panel.py")

# ─── HEADER ──────────────────────────────────────────────────────────────────
page_header("⚽", "TFF PERFORMANS SİSTEMİ",
            "Türkiye Futbol Federasyonu • Genç Milli Takımlar Atletik Veri Platformu")

st.divider()

# ─── NAVİGASYON KARTLARI ─────────────────────────────────────────────────────
section_title("HIZLI ERİŞİM MENÜSÜ", "🚀")

nav_items = [
    ("02_Kamp_Analizi.py", "⚽", "KAMP ANALİZİ", "Günlük & kamp bazlı sıralamalar"),
    ("03_Oyuncu_Profili.py", "🏃", "OYUNCU PROFİLİ", "Bireysel performans & radar"),
    ("04_Karsilastirma.py", "⚔️", "KARŞILAŞTIRMA", "H2H · Kamp karşılaştırması"),
    ("05_Siralamalar.py", "📊", "SIRALAMALAR", "Günlük · Kamp · Percentile"),
    ("06_Scatter.py", "🎯", "SCATTER ANALİZİ", "İki metrik dağılımı"),
]

cols = st.columns(5)
for i, (page, icon, title, desc) in enumerate(nav_items):
    with cols[i]:
        border = COLORS['RED']
        shadow = "0 4px 16px rgba(227,10,23,0.2)"
        
        st.markdown(f"""
        <div style="background: white; border: 2px solid {border}; border-radius: 14px;
                   padding: 20px 14px 14px; text-align: center; box-shadow: {shadow};
                   height: 130px; transition: all 0.3s ease; cursor: pointer;">
            <div style="font-size: 28px; margin-bottom: 8px;">{icon}</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 14px;
                       letter-spacing: 1.5px; color: {COLORS['GRAY_900']};
                       font-weight: 700; margin-bottom: 4px;">
                {title}
            </div>
            <div style="font-size: 10px; color: {COLORS['GRAY_500']};">
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"GİT →", key=f"nav_{i}", use_container_width=True):
            st.switch_page(f"pages/{page}")

st.divider()

# ─── YAŞ GRUBU DURUMU ────────────────────────────────────────────────────────
try:
    all_data = db_manager.get_all_data()
    
    if not all_data.empty:
        section_title("YAŞ GRUBU DURUMU", "📈")
        
        ag_cols = st.columns(len(AGE_GROUPS))
        for i, ag in enumerate(AGE_GROUPS):
            ag_data = all_data[all_data['age_group'] == ag]
            has = not ag_data.empty
            
            with ag_cols[i]:
                if has:
                    pc = ag_data['player_name'].nunique()
                    cc = ag_data['camp_id'].nunique()
                    rc = len(ag_data)
                    
                    st.markdown(f"""
                    <div class="ag-card has-data">
                        <div class="ag-label">{ag}</div>
                        <div class="ag-stat"><b>{pc}</b> Oyuncu · <b>{cc}</b> Kamp</div>
                        <div class="ag-stat" style="font-size: 11px; color: {COLORS['GRAY_400']};
                                                   margin-top: 4px;">{rc} kayıt</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Detaylar →", key=f"ag_{i}", use_container_width=True):
                        st.session_state['selected_age_group'] = ag
                        st.switch_page("pages/02_Kamp_Analizi.py")
                else:
                    st.markdown(f"""
                    <div class="ag-card no-data">
                        <div class="ag-label">{ag}</div>
                        <div class="ag-stat" style="color: {COLORS['GRAY_400']};">VERİ YOK</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        
        # ─── GENEL İSTATİSTİKLER ─────────────────────────────────────────────
        section_title("GENEL İSTATİSTİKLER", "📊")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        
        match_df = all_data[all_data['tip'].str.upper() == 'MATCH']
        training_df = all_data[all_data['tip'].str.upper() == 'TRAINING']
        
        metrics_data = [
            (k1, "🏃", "TOPLAM OYUNCU", all_data['player_name'].nunique()),
            (k2, "⚽", "TOPLAM KAMP", all_data['camp_id'].nunique()),
            (k3, "📋", "TOPLAM KAYIT", len(all_data)),
            (k4, "🎯", "TOPLAM MAÇ GÜNÜ", match_df['tarih'].nunique() if not match_df.empty else 0),
            (k5, "📏", "ORT. MESAFE", f"{all_data['total_distance'].mean():.0f} m"),
            (k6, "⚡", "MAX HIZ (GENEL)", f"{all_data['smax_kmh'].max():.1f} km/h"),
        ]
        
        for col, icon, label, value in metrics_data:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 16px; margin-bottom: 8px;">{icon}</div>
                    <div class="sc-label">{label}</div>
                    <div class="sc-val">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # ─── TOP PERFORMANSLAR ────────────────────────────────────────────────
        section_title("EN YÜKSEK 10 MESAFE PERFORMANSI", "🏆")
        
        top10 = all_data.nlargest(10, 'total_distance')[[
            'player_name', 'age_group', 'tarih', 'tip', 'total_distance', 'smax_kmh', 'player_load'
        ]].copy()
        
        top10['tarih'] = top10['tarih'].dt.strftime('%d.%m.%Y')
        top10.columns = ['OYUNCU', 'YAŞ GRUBU', 'TARİH', 'SEANS TİPİ', 'MESAFE (m)', 'MAX HIZ (km/h)', 'YÜK']
        
        st.dataframe(
            top10.style.background_gradient(cmap='Reds', subset=['MESAFE (m)'], vmin=top10['MESAFE (m)'].min()),
            use_container_width=True, hide_index=True, height=450
        )
        
        st.divider()
        
        # ─── TOP 10 KAMPLAR ──────────────────────────────────────────────────
        col1, col2, col3 = st.columns(3)
        
        with col1:
            section_title("EN ÇOK KAMPA ÇIKAN OYUNCULAR", "📊")
            top_camps = all_data.groupby('player_name').size().nlargest(10).reset_index(name='Seans Sayısı')
            st.dataframe(top_camps.rename(columns={'player_name': 'OYUNCU'}), use_container_width=True, hide_index=True)
        
        with col2:
            section_title("EN ÇOK ANTRENMANA ÇIKAN", "💪")
            top_training = training_df.groupby('player_name').size().nlargest(10).reset_index(name='Antrenman Sayısı')
            st.dataframe(top_training.rename(columns={'player_name': 'OYUNCU'}), use_container_width=True, hide_index=True)
        
        with col3:
            section_title("EN ÇOK MAÇA ÇIKAN", "⚽")
            top_matches = match_df.groupby('player_name').size().nlargest(10).reset_index(name='Maç Sayısı')
            st.dataframe(top_matches.rename(columns={'player_name': 'OYUNCU'}), use_container_width=True, hide_index=True)
    
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 80px 20px; background: {COLORS['GRAY_50']};
                   border-radius: 16px; border: 2px dashed {COLORS['GRAY_300']};
                   margin-top: 40px;">
            <div style="font-size: 52px; margin-bottom: 16px;">📂</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 30px;
                       letter-spacing: 2px; color: {COLORS['GRAY_700']};">
                HENÜZ VERİ YÜKLENMEDİ
            </div>
            <div style="font-size: 13px; color: {COLORS['GRAY_500']}; margin-top: 12px;">
                Sol panelden Excel dosyanızı yükleyerek sistemi başlatın
            </div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Hata oluştu: {str(e)}")

st.divider()

st.markdown(f"""
<div class="tff-footer">
    <p><strong>Türkiye Futbol Federasyonu</strong></p>
    <p>Genç Milli Takımlar Atletik Performans Sistemi • v5.0</p>
    <p style="margin-top: 10px; font-size: 10px;">© 2026 TFF · Tüm hakları saklıdır</p>
</div>
""", unsafe_allow_html=True)
