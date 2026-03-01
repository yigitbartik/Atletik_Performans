# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - ANA SAYFA
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
from config import AGE_GROUPS, COLORS
from database import db_manager
from styles import inject_styles, page_header, section_title

st.set_page_config(page_title="Ana Sayfa | TFF", layout="wide")
inject_styles()

page_header("🏠", "ANA SAYFA", "Genç Milli Takımlarınızın atletik performans özetlerini inceleyin")

st.divider()

# ─── YAŞ GRUBU SEÇİMİ ───────────────────────────────────────────────────────
section_title("YAŞ GRUBU SEÇİMİ", "📊")

cols = st.columns(len(AGE_GROUPS))

for idx, ag in enumerate(AGE_GROUPS):
    with cols[idx]:
        try:
            ag_data = db_manager.get_data_by_age_group(ag)
            
            if not ag_data.empty:
                pc = ag_data['player_name'].nunique()
                cc = ag_data['camp_id'].nunique()
                rc = len(ag_data)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-family: 'Bebas Neue', sans-serif; font-size: 44px;
                               letter-spacing: 3px; color: {COLORS['GRAY_900']};">
                        {ag}
                    </div>
                    <div style="font-size: 14px; color: {COLORS['GRAY_700']};
                               margin-top: 10px; font-weight: 800;">
                        <span style="color: {COLORS['RED']}">{pc}</span> OYUNCU &nbsp;·&nbsp;
                        <span style="color: {COLORS['RED']}">{cc}</span> KAMP
                    </div>
                    <div style="font-size: 12px; color: {COLORS['GRAY_500']};
                               margin-top: 6px; font-weight: 600;">
                        {rc} TOPLAM KAYIT
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                
                if st.button(f"📊 {ag} ANALİZ ET", key=f"btn_{ag}", use_container_width=True):
                    st.session_state.selected_age_group = ag
                    st.switch_page("pages/02_Kamp_Analizi.py")
            else:
                st.markdown(f"""
                <div class="metric-card" style="background: {COLORS['GRAY_50']};
                           border: 2px dashed {COLORS['GRAY_300']}; opacity: 0.6;">
                    <div style="font-family: 'Bebas Neue', sans-serif; font-size: 44px;
                               letter-spacing: 3px; color: {COLORS['GRAY_400']};">
                        {ag}
                    </div>
                    <div style="font-size: 13px; color: {COLORS['GRAY_400']};
                               margin-top: 10px; font-weight: 700;">
                        VERİ BULUNAMADI
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            st.markdown(f"""
            <div class="metric-card" style="background: {COLORS['GRAY_50']};
                       border: 2px dashed {COLORS['GRAY_300']}; opacity: 0.6;">
                <div style="font-family: 'Bebas Neue', sans-serif; font-size: 44px;
                           letter-spacing: 3px; color: {COLORS['GRAY_400']};">
                    {ag}
                </div>
                <div style="font-size: 13px; color: {COLORS['GRAY_400']};
                           margin-top: 10px; font-weight: 700;">
                    VERİ BULUNAMADI
                </div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ─── HIZLI ERİŞİM MENÜSÜ ─────────────────────────────────────────────────────
section_title("HIZLI ERİŞİM MENÜSÜ", "🚀")

c1, c2, c3, c4, c5 = st.columns(5)

menu_items = [
    (c1, "⚽ KAMP ANALİZİ", "pages/02_Kamp_Analizi.py"),
    (c2, "🏃 OYUNCU PROFİLİ", "pages/03_Oyuncu_Profili.py"),
    (c3, "⚔️ KARŞILAŞTIRMA", "pages/04_Karsilastirma.py"),
    (c4, "📊 SIRALAMALAR", "pages/05_Siralamalar.py"),
    (c5, "🎯 SCATTER ANALİZİ", "pages/06_Scatter.py"),
]

for col, label, page in menu_items:
    with col:
        if st.button(label, use_container_width=True):
            st.switch_page(page)

st.divider()

# ─── SİSTEM GENEL DURUMU ─────────────────────────────────────────────────────
try:
    all_data = db_manager.get_all_data()
    
    if not all_data.empty:
        section_title("SİSTEM GENEL DURUMU", "📈")
        
        c1, c2, c3, c4 = st.columns(4)
        
        match_data = all_data[all_data['tip'].str.upper() == 'MATCH']
        
        metrics = [
            (c1, "🏃", "TOPLAM OYUNCU", all_data['player_name'].nunique()),
            (c2, "⚽", "TOPLAM KAMP", all_data['camp_id'].nunique()),
            (c3, "📋", "TOPLAM KAYIT (SEANS)", len(all_data)),
            (c4, "🎯", "TOPLAM MAÇ GÜNÜ", match_data['tarih'].nunique() if not match_data.empty else 0),
        ]
        
        for col, icon, label, value in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
                    <h4 style="color: {COLORS['GRAY_600']}; margin: 0; font-size: 11px;
                              font-weight: 800; text-transform: uppercase;">
                        {label}
                    </h4>
                    <h2 style="color: {COLORS['RED']}; font-family: 'Bebas Neue';
                              font-size: 38px; margin: 8px 0 0 0;
                              letter-spacing: 2px;">
                        {value}
                    </h2>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.warning(f"⚠️ Hata: {e}")

st.markdown(f"""
<div class="tff-footer">
    <p>Türkiye Futbol Federasyonu · Ana Sayfa</p>
</div>
""", unsafe_allow_html=True)
