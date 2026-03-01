# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - UI BİLEŞENLERİ
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
from config import COLORS

def player_card(name, age_group, stats, photo_url=None):
    """Oyuncu kartı"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if photo_url:
            st.image(photo_url, width=80)
        else:
            st.markdown(f'<div style="font-size: 60px; text-align: center;">👤</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**{name}**")
        st.caption(f"🇹🇷 {age_group} MİLLİ TAKIMI")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Kamplar", stats.get('camp_count', 0))
        with col_b:
            st.metric("Seanslar", stats.get('session_count', 0))

def metric_comparison(label, value1, value2, unit="", player1_name="Oyuncu 1", player2_name="Oyuncu 2"):
    """Renk-kodlu karşılaştırma"""
    if value1 > value2:
        color = COLORS['SUCCESS']
        icon = "✅"
    elif value1 < value2:
        color = COLORS['DANGER']
        icon = "❌"
    else:
        color = COLORS['GRAY_400']
        icon = "⚖️"
    
    st.markdown(f"""
    <div style="background: white; padding: 12px; border-left: 4px solid {color};
               border-radius: 6px; margin-bottom: 12px;">
        <div style="font-size: 12px; color: #666; margin-bottom: 8px;"><b>{label}</b></div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="text-align: center; background: #f5f5f5; padding: 8px; border-radius: 4px;">
                <div style="font-weight: 700; font-size: 13px; color: {COLORS['RED']};
                           margin-bottom: 2px;">{player1_name}</div>
                <div style="font-size: 16px; font-weight: 700;">{value1:.1f}</div>
                <div style="font-size: 10px; color: #999;">{unit}</div>
            </div>
            <div style="text-align: center; background: #f5f5f5; padding: 8px; border-radius: 4px;">
                <div style="font-weight: 700; font-size: 13px; color: {COLORS['GRAY_700']};
                           margin-bottom: 2px;">{player2_name}</div>
                <div style="font-size: 16px; font-weight: 700;">{value2:.1f}</div>
                <div style="font-size: 10px; color: #999;">{unit}</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 8px; font-weight: 700; color: {color};">
            {icon} {abs(value1 - value2):.1f} {unit}
        </div>
    </div>
    """, unsafe_allow_html=True)

print("✅ UI Bileşenleri Yüklendi")
