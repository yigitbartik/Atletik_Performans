# OYUNCU GALERİSİ SAYFASI
import streamlit as st
import pandas as pd
from config import AGE_GROUPS, COLORS
from database import db_manager
from styles import inject_styles, page_header

st.set_page_config(page_title="Oyuncu Galerisi | TFF", layout="wide")
inject_styles()

page_header("👥", "OYUNCU GALERİSİ", "Takım kadrosunu ve oyuncu bilgilerini görüntüleyin")

age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="gal_age")

players_info = db_manager.get_players_with_info(age_group)

if not players_info:
    st.warning(f"❌ {age_group} grubu için veri bulunamadı")
    st.stop()

st.divider()

st.markdown(f"""<h3 style='font-family: Bebas Neue; letter-spacing: 1px; color: {COLORS['GRAY_900']};'>
🇹🇷 {age_group} KADROSU ({len(players_info)} Oyuncu)</h3>""", unsafe_allow_html=True)

st.markdown("""
<style>
.player-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 20px 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    transition: all 0.3s ease;
}
.player-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 20px rgba(227,10,23,0.15);
}
.p-name {
    font-family: 'Bebas Neue';
    font-size: 18px;
    color: #111827;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

DEFAULT_PHOTO = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
DEFAULT_LOGO = "https://upload.wikimedia.org/wikipedia/tr/b/b9/Türkiye_Futbol_Federasyonu_logo.png"

cols_per_row = 5
for i in range(0, len(players_info), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        idx = i + j
        if idx < len(players_info):
            p_data = players_info[idx]
            name = p_data['name']
            photo = p_data.get('photo_url') or DEFAULT_PHOTO
            logo = p_data.get('club_logo_url') or DEFAULT_LOGO
            
            with cols[j]:
                st.markdown(f"""
                <div class="player-card">
                    <img src="{photo}" style="width: 100px; height: 100px; 
                         border-radius: 50%; border: 3px solid #E30A17;">
                    <div class="p-name">{name}</div>
                    <div style="font-size: 10px; color: #999;">Milli Oyuncu</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📈 PROFİLE GİT", key=f"gal_{idx}", use_container_width=True):
                    st.session_state['pp_player'] = name
                    st.session_state['pp_age'] = age_group
                    st.switch_page("pages/03_Oyuncu_Profili.py")

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • Oyuncu Galerisi</p></div>',
            unsafe_allow_html=True)
