import streamlit as st
import pandas as pd
from config import AGE_GROUPS
from database import db_manager
from styles import inject_styles, page_header, section_title, COLORS

st.set_page_config(page_title="Ana Sayfa | TFF", layout="wide")
inject_styles()

# Başlık ve açıklama güncellendi
page_header("🏠", "ANA SAYFA", "Genç Milli Takımlarınızın atletik performans özetlerini inceleyin.")

st.divider()
section_title("YAŞ GRUBU SEÇİMİ", "📊")
cols = st.columns(len(AGE_GROUPS))

for idx, ag in enumerate(AGE_GROUPS):
    with cols[idx]:
        try:
            ag_data = db_manager.get_data_by_age_group(ag)
            if not ag_data.empty:
                pc = ag_data['player_name'].nunique()
                cc = ag_data['camp_id'].nunique()
                
                # Orijinal HTML yerine styles.py içindeki "metric-card" sınıfı kullanıldı (Hover efekti için)
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;
                                letter-spacing:3px;color:{COLORS['GRAY_900']};">{ag}</div>
                    <div style="font-size:14px;color:{COLORS['GRAY_700']};margin-top:10px;font-weight:800;">
                        <span style="color:{COLORS['RED']}">{pc}</span> OYUNCU &nbsp;·&nbsp;
                        <span style="color:{COLORS['RED']}">{cc}</span> KAMP
                    </div>
                    <div style="font-size:12px;color:{COLORS['GRAY_500']};margin-top:6px;font-weight:600;">
                        {len(ag_data)} TOPLAM KAYIT
                    </div>
                </div>""", unsafe_allow_html=True)
                
                # Buton yazısı büyütüldü
                st.write("") # Buton ile kart arasına ufak bir esneme payı
                if st.button(f"📊 {ag} ANALİZ ET", key=f"btn_{ag}", use_container_width=True):
                    st.session_state.selected_age_group = ag
                    st.switch_page("pages/02_Kamp_Analizi.py")
            else:
                st.markdown(f"""
                <div class="metric-card" style="background:{COLORS['GRAY_50']};border:2px dashed {COLORS['GRAY_300']};opacity:0.6;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;
                                letter-spacing:3px;color:{COLORS['GRAY_400']};">{ag}</div>
                    <div style="font-size:13px;color:{COLORS['GRAY_400']};margin-top:10px;font-weight:700;">VERİ BULUNAMADI</div>
                </div>""", unsafe_allow_html=True)
        except Exception:
            st.markdown(f"""
            <div class="metric-card" style="background:{COLORS['GRAY_50']};border:2px dashed {COLORS['GRAY_300']};opacity:0.6;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;
                            letter-spacing:3px;color:{COLORS['GRAY_400']};">{ag}</div>
                <div style="font-size:13px;color:{COLORS['GRAY_400']};margin-top:10px;font-weight:700;">VERİ BULUNAMADI</div>
            </div>""", unsafe_allow_html=True)

st.divider()
section_title("HIZLI ERİŞİM MENÜSÜ", "🚀")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("⚽ KAMP ANALİZİ",   use_container_width=True): st.switch_page("pages/02_Kamp_Analizi.py")
with c2:
    if st.button("🏃 OYUNCU PROFİLİ", use_container_width=True): st.switch_page("pages/03_Oyuncu_Profili.py")
with c3:
    if st.button("⚔️ KARŞILAŞTIRMA",  use_container_width=True): st.switch_page("pages/04_Karsilastirma.py")
with c4:
    if st.button("📊 SIRALAMALAR",    use_container_width=True): st.switch_page("pages/05_Siralamalar.py")
with c5:
    if st.button("🎯 SCATTER ANALİZİ",        use_container_width=True): st.switch_page("pages/06_Scatter.py")

st.divider()
try:
    all_data = db_manager.get_all_data()
    if not all_data.empty:
        section_title("SİSTEM GENEL DURUMU", "📈")
        c1, c2, c3, c4 = st.columns(4)
        
        # Basit st.metric'ler yerine özel UI kartlar kullandık
        with c1: 
            st.markdown(f"<div class='metric-card'><h4 style='color:{COLORS['GRAY_600']}; margin:0; font-size:12px; font-weight:800; text-transform:uppercase;'>TOPLAM OYUNCU</h4><h2 style='color:{COLORS['RED']}; font-family:Bebas Neue; font-size:38px; margin:8px 0 0 0; letter-spacing:2px;'>{all_data['player_name'].nunique()}</h2></div>", unsafe_allow_html=True)
        with c2: 
            st.markdown(f"<div class='metric-card'><h4 style='color:{COLORS['GRAY_600']}; margin:0; font-size:12px; font-weight:800; text-transform:uppercase;'>TOPLAM KAMP</h4><h2 style='color:{COLORS['RED']}; font-family:Bebas Neue; font-size:38px; margin:8px 0 0 0; letter-spacing:2px;'>{all_data['camp_id'].nunique()}</h2></div>", unsafe_allow_html=True)
        with c3: 
            st.markdown(f"<div class='metric-card'><h4 style='color:{COLORS['GRAY_600']}; margin:0; font-size:12px; font-weight:800; text-transform:uppercase;'>TOPLAM KAYIT (SEANS)</h4><h2 style='color:{COLORS['RED']}; font-family:Bebas Neue; font-size:38px; margin:8px 0 0 0; letter-spacing:2px;'>{len(all_data)}</h2></div>", unsafe_allow_html=True)
        with c4:
            mp = int((all_data['tip'].str.upper() == 'MATCH').sum())
            st.markdown(f"<div class='metric-card'><h4 style='color:{COLORS['GRAY_600']}; margin:0; font-size:12px; font-weight:800; text-transform:uppercase;'>TOPLAM MAÇ GÜNÜ</h4><h2 style='color:{COLORS['RED']}; font-family:Bebas Neue; font-size:38px; margin:8px 0 0 0; letter-spacing:2px;'>{mp}</h2></div>", unsafe_allow_html=True)
except Exception:
    pass

st.markdown('<div class="tff-footer"><p>TFF Atletik Performans Sistemi · Ana Sayfa</p></div>',
            unsafe_allow_html=True)