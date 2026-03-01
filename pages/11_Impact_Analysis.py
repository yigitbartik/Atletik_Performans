# IMPACT ANALİZİ SAYFASI
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import AGE_GROUPS, COLORS
from database import db_manager
from styles import inject_styles, page_header, section_title
from utils import calculate_impact_score_engine, render_export_buttons

st.set_page_config(page_title="Impact Analizi | TFF", layout="wide")
inject_styles()

page_header("⚡", "IMPACT (ETKİ) ANALİZİ",
            "Tüm metriklerin Z-Skoru ile hesaplanmış objektif günlük ve kamp performansı")

with st.expander("📌 İMPACT MODELİ METODOLOJİSİ"):
    st.markdown("""
    **Hesaplama Adımları:**
    1. **Dakikaya Oranlama:** Tüm veriler oyuncunun sahada kaldığı dakikaya bölünür
    2. **Z-Skoru:** Oyuncunun performansı takım ortalamasıyla karşılaştırılır
    3. **Ağırlıklı Skorlama:** 
       - %25 Yüksek Hızlı Koşu (25+ km/h)
       - %20 Patlayıcı Aksiyon (Acc + Dec)
       - %20 Oyuncu Yükü
       - %15 Toplam Mesafe
       - %10 Maksimum Hız
       - %10 Metabolik Güç
    4. **Ölçekleme:** 0-100 arasında anlaşılır puan
    """)

c1, c2, c3 = st.columns(3)

with c1:
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="ia_age")

raw_age_data = db_manager.get_data_by_age_group(age_group)

if raw_age_data.empty:
    st.warning(f"❌ {age_group} için veri bulunamadı")
    st.stop()

camps_df = db_manager.get_camps(age_group)
camp_options = {row['camp_name']: row['camp_id'] for _, row in camps_df.iterrows()}

with c2:
    sel_camp_label = st.selectbox("KAMP", list(camp_options.keys()), key="ia_camp") if camp_options else None

with c3:
    ses = st.radio("SEANS", ["Tümü", "TRAINING", "MATCH"], horizontal=True, key="ia_ses")

if not camp_options:
    st.warning(f"❌ {age_group} için kamp bulunamadı")
    st.stop()

sel_camp_id = camp_options[sel_camp_label]
raw_camp_data = raw_age_data[raw_age_data['camp_id'] == sel_camp_id]

if ses != "Tümü":
    raw_camp_data = raw_camp_data[raw_camp_data['tip'].str.upper() == ses]

camp_data = calculate_impact_score_engine(raw_camp_data)

if camp_data.empty:
    st.warning("❌ Hesaplanabilir veri yok")
    st.stop()

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 GÜNLÜK SIRALAMA", "🏆 KAMP LİDERLERİ", "📈 TRENDİ"])

# TAB 1: GÜNLÜK SIRALAMA
with tab1:
    unique_dates = sorted(camp_data['tarih'].unique(), reverse=True)
    sel_date = st.selectbox("SEANS TARİHİ", unique_dates, 
                           format_func=lambda x: pd.to_datetime(x).strftime('%d.%m.%Y'),
                           key="ia_daily_date")
    
    day_data = camp_data[camp_data['tarih'] == sel_date].sort_values('impact_score', ascending=False)
    
    st.markdown("### TAKIM SIRAMASI")
    
    display_cols = ['player_name', 'impact_score', 'dist_25_plus_pm', 'player_load_pm']
    show_df = day_data[display_cols].copy()
    show_df.columns = ['OYUNCU', 'IMPACT SKOR', '25+ HIZ (m/dk)', 'YÜK (Load/dk)']
    show_df.index = range(1, len(show_df) + 1)
    
    st.dataframe(show_df.style.background_gradient(cmap='Reds', subset=['IMPACT SKOR']),
                use_container_width=True)
    
    render_export_buttons(df=show_df.reset_index(drop=True), key_prefix="ia_daily",
                         filename=f"Gunluk_Impact_{sel_date}")

# TAB 2: KAMP LİDERLERİ
with tab2:
    section_title("KAMP GENEL ORTALAMASI VE LİDERLİK", "🏆")
    
    camp_impact = camp_data.groupby('player_name').agg({
        'impact_score': 'mean',
        'smax_kmh': 'max',
        'tarih': 'count'
    }).reset_index().sort_values('impact_score', ascending=False)
    
    camp_impact.columns = ['OYUNCU', 'KAMP ORT. IMPACT', 'KAMP MAX HIZ (km/h)', 'SEANS']
    camp_impact.index = range(1, len(camp_impact) + 1)
    
    st.dataframe(camp_impact.style.background_gradient(cmap='Greys', subset=['KAMP ORT. IMPACT']),
                use_container_width=True)

# TAB 3: TREND
with tab3:
    section_title("KAMP İÇİ ETKİ TRENDİ", "📉")
    
    players = sorted(camp_data['player_name'].unique())
    sel_player = st.selectbox("OYUNCU", players, key="ia_trend_player")
    
    player_trend = camp_data[camp_data['player_name'] == sel_player].sort_values('tarih')
    
    if len(player_trend) >= 2:
        daily_impact = player_trend[['tarih', 'impact_score']].copy()
        daily_impact['tarih_str'] = daily_impact['tarih'].dt.strftime('%d.%m')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_impact['tarih_str'], y=daily_impact['impact_score'],
            mode='lines+markers',
            line=dict(color=COLORS['RED'], width=3, shape='spline'),
            marker=dict(size=10, color='white', line=dict(color=COLORS['RED'], width=2))
        ))
        
        mean_impact = daily_impact['impact_score'].mean()
        fig.add_hline(y=mean_impact, line_dash="dash", line_color='gray',
                     annotation_text=f"Ort: {mean_impact:.1f}",
                     annotation_position="top left")
        
        fig.update_layout(template='plotly_white', height=450,
                         xaxis_title="Tarih", yaxis_title="Impact Score (0-100)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Trend için en az 2 seans verisi gereklidir")

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • Impact Analizi</p></div>',
            unsafe_allow_html=True)
