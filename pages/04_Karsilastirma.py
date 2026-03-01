# KARŞILAŞTIRMA SAYFASI
import streamlit as st
import pandas as pd
from config import AGE_GROUPS, COLORS, PRIMARY_METRICS, METRICS
from database import db_manager
from styles import inject_styles, page_header, section_title, comparison_card

st.set_page_config(page_title="Karşılaştırma | TFF", layout="wide")
inject_styles()

page_header("⚔️", "KARŞILAŞTIRMA", "H2H karşılaştırma, kamp karşılaştırması, gün karşılaştırması")

c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="cmp_age")

players = db_manager.get_players(age_group)
if not players:
    st.warning(f"❌ {age_group} için oyuncu yok")
    st.stop()

with c2:
    player1 = st.selectbox("OYUNCU 1", players, key="cmp_p1")

with c3:
    player2 = st.selectbox("OYUNCU 2", players, key="cmp_p2")

if player1 == player2:
    st.warning("⚠️ Farklı oyuncuları seçiniz")
    st.stop()

st.divider()
section_title("H2H KARŞILAŞTIRMA", "⚔️")

data1 = db_manager.get_data_by_player(player1)
data2 = db_manager.get_data_by_player(player2)

if data1.empty or data2.empty:
    st.warning("❌ Oyuncu verisi bulunamadı")
    st.stop()

st.markdown(f"""
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    <div style="text-align: center;">
        <div style="font-family: 'Bebas Neue'; font-size: 28px; letter-spacing: 2px;
                   color: {COLORS['RED']};">{player1.upper()}</div>
    </div>
    <div style="text-align: center;">
        <div style="font-family: 'Bebas Neue'; font-size: 28px; letter-spacing: 2px;
                   color: {COLORS['GRAY_700']};">{player2.upper()}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# KARŞILAŞTIRMALAR
for metric in ['total_distance', 'smax_kmh', 'player_load', 'dist_25_plus']:
    if metric in data1.columns and metric in data2.columns:
        v1 = data1[metric].mean()
        v2 = data2[metric].mean()
        label = METRICS.get(metric, {}).get('display', metric)
        unit = METRICS.get(metric, {}).get('unit', '')
        
        st.markdown(comparison_card(label, v1, v2, unit, player1, player2), 
                   unsafe_allow_html=True)

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • Karşılaştırma Analizi</p></div>',
            unsafe_allow_html=True)
