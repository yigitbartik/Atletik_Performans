# SIRALAMALAR SAYFASI
import streamlit as st
import pandas as pd
from config import AGE_GROUPS
from database import db_manager
from styles import inject_styles, page_header, section_title

st.set_page_config(page_title="Sıralamalar | TFF", layout="wide")
inject_styles()

page_header("📊", "SIRALAMALAR", "Günlük, kamp ve genel sıralamalar")

age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="sr_age")

data = db_manager.get_data_by_age_group(age_group)

if data.empty:
    st.warning(f"❌ {age_group} için veri bulunamadı")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📈 GENEL SIRALAMA", "⚽ KAMP SIRAMASI", "📅 GÜNLÜK SIRALAMA"])

# TAB 1: GENEL SIRALAMA
with tab1:
    section_title("GENEL MESAFE SIRAMASI", "🏆")
    
    general_ranking = data.groupby('player_name').agg({
        'total_distance': 'mean',
        'smax_kmh': 'max',
        'player_load': 'mean',
        'camp_id': 'nunique',
        'tarih': 'count'
    }).round(1)
    
    general_ranking.columns = ['ORT. MESAFE', 'MAX HIZ', 'ORT. YÜK', 'KAMP', 'SEANS']
    general_ranking = general_ranking.sort_values('ORT. MESAFE', ascending=False).head(20)
    general_ranking.index = range(1, len(general_ranking) + 1)
    
    st.dataframe(general_ranking.style.background_gradient(cmap='Reds', subset=['ORT. MESAFE']),
                use_container_width=True)

# TAB 2: KAMP SIRAMASI
with tab2:
    section_title("KAMP BAZLI SIRALAMA", "⚽")
    
    camps_df = db_manager.get_camps(age_group)
    camp_dict = {row['camp_name']: row['camp_id'] for _, row in camps_df.iterrows()}
    
    sel_camp = st.selectbox("KAMP SEÇİN", list(camp_dict.keys()), key="sr_camp")
    
    camp_data = data[data['camp_id'] == camp_dict[sel_camp]]
    
    camp_ranking = camp_data.groupby('player_name').agg({
        'total_distance': 'mean',
        'smax_kmh': 'max'
    }).round(1)
    
    camp_ranking.columns = ['ORT. MESAFE', 'MAX HIZ']
    camp_ranking = camp_ranking.sort_values('ORT. MESAFE', ascending=False).head(15)
    camp_ranking.index = range(1, len(camp_ranking) + 1)
    
    st.dataframe(camp_ranking.style.background_gradient(cmap='Reds', subset=['ORT. MESAFE']),
                use_container_width=True)

# TAB 3: GÜNLÜK SIRALAMA
with tab3:
    section_title("GÜNLÜK SIRALAMA", "📅")
    
    unique_dates = sorted(data['tarih'].unique(), reverse=True)
    sel_date = st.selectbox("TARİH SEÇİN", 
                            [pd.to_datetime(d).strftime('%d.%m.%Y') for d in unique_dates],
                            key="sr_date")
    
    sel_date_obj = pd.to_datetime(sel_date, format='%d.%m.%Y')
    day_data = data[data['tarih'] == sel_date_obj]
    
    day_ranking = day_data.groupby('player_name').agg({
        'total_distance': 'first',
        'smax_kmh': 'max',
        'player_load': 'first'
    }).round(1)
    
    day_ranking.columns = ['MESAFE (m)', 'MAX HIZ (km/h)', 'YÜK']
    day_ranking = day_ranking.sort_values('MESAFE (m)', ascending=False)
    day_ranking.index = range(1, len(day_ranking) + 1)
    
    st.dataframe(day_ranking.style.background_gradient(cmap='Reds', subset=['MESAFE (m)']),
                use_container_width=True)

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • Sıralamalar</p></div>',
            unsafe_allow_html=True)
