# KAMP ANALİZİ SAYFASI
import streamlit as st
import pandas as pd
from config import AGE_GROUPS, COLORS
from database import db_manager
from styles import inject_styles, page_header, section_title

st.set_page_config(page_title="Kamp Analizi | TFF", layout="wide")
inject_styles()

page_header("⚽", "KAMP ANALİZİ", "Kamplar bazında performans sıralamları ve günlük analiz")

c1, c2 = st.columns([1, 2])
with c1:
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="ka_age")

raw_data = db_manager.get_data_by_age_group(age_group)

if raw_data.empty:
    st.warning(f"❌ {age_group} için veri bulunamadı")
    st.stop()

camps_df = db_manager.get_camps(age_group)
camp_dict = {row['camp_name']: row['camp_id'] for _, row in camps_df.iterrows()}

with c2:
    sel_camp_label = st.selectbox("KAMP SEÇİMİ", list(camp_dict.keys()), key="ka_camp")

sel_camp_id = camp_dict[sel_camp_label]
camp_data = raw_data[raw_data['camp_id'] == sel_camp_id]

if camp_data.empty:
    st.warning("❌ Seçilen kamp için veri yok")
    st.stop()

st.divider()
section_title("KAMP ÖZET STATİSTİKLERİ", "📊")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card"><div class="sc-label">OYUNCU</div>
    <div class="sc-val">{camp_data['player_name'].nunique()}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card"><div class="sc-label">SEANS</div>
    <div class="sc-val">{len(camp_data)}</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card"><div class="sc-label">ORT. MESAFE</div>
    <div class="sc-val">{camp_data['total_distance'].mean():.0f} <span style="font-size:11px;">m</span></div></div>""", 
    unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card"><div class="sc-label">MAX HIZ</div>
    <div class="sc-val">{camp_data['smax_kmh'].max():.1f} <span style="font-size:11px;">km/h</span></div></div>""", 
    unsafe_allow_html=True)

st.divider()
section_title("OYUNCU PERFORMANSLARI", "🏆")

player_stats = camp_data.groupby('player_name').agg({
    'total_distance': 'mean',
    'smax_kmh': 'max',
    'player_load': 'mean',
    'tarih': 'count'
}).round(1)

player_stats.columns = ['ORT. MESAFE (m)', 'MAX HIZ (km/h)', 'ORT. YÜK', 'SEANS']
player_stats = player_stats.sort_values('ORT. MESAFE (m)', ascending=False).head(15)

st.dataframe(
    player_stats.style.background_gradient(cmap='Reds', subset=['ORT. MESAFE (m)']),
    use_container_width=True
)

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • Kamp Analizi</p></div>',
            unsafe_allow_html=True)
