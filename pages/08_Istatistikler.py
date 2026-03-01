# İSTATİSTİKLER SAYFASI
import streamlit as st
import pandas as pd
import plotly.express as px
from config import AGE_GROUPS, METRICS
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box

st.set_page_config(page_title="İstatistikler | TFF", layout="wide")
inject_styles()

page_header("📈", "İSTATİSTİKLER & TRENDLER", "Dağılım, korelasyon ve trend analizi")

age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="stat_age")

df = db_manager.get_data_by_age_group(age_group)

if df.empty:
    st.warning(f"❌ {age_group} için veri bulunamadı")
    st.stop()

numeric_cols = [c for c in METRICS.keys() if c in df.columns and df[c].notna().any()]

tabs = st.tabs(["📊 DAĞILIM (BOX-PLOT)", "📉 KORELASYON", "📈 TREND"])

# TAB 1: DAĞILIM
with tabs[0]:
    section_title("DAĞILIM ANALİZİ", "📊")
    
    metric = st.selectbox("METRİK", numeric_cols, 
                         format_func=lambda x: METRICS.get(x, {}).get('display', x),
                         key="box_metric")
    
    fig = px.box(df, y=metric, color='tip',
                labels={metric: METRICS.get(metric, {}).get('display', metric)},
                title=f"{age_group} - {METRICS.get(metric, {}).get('display', metric)} Dağılımı")
    
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: KORELASYON
with tabs[1]:
    section_title("KORELASYON MATRİSİ", "📉")
    
    corr_metrics = st.multiselect("METRİKLER",
        numeric_cols,
        default=[numeric_cols[0], numeric_cols[1]] if len(numeric_cols) > 1 else numeric_cols,
        key="corr_metrics")
    
    if len(corr_metrics) > 1:
        corr_df = df[corr_metrics].corr().round(2)
        
        fig = px.imshow(corr_df, text_auto=True, color_continuous_scale='RdBu_r',
                       title="Korelasyon Isı Haritası", zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)

# TAB 3: TREND
with tabs[2]:
    section_title("TREND ANALİZİ", "📈")
    
    metric = st.selectbox("METRİK", numeric_cols,
                         format_func=lambda x: METRICS.get(x, {}).get('display', x),
                         key="trend_metric")
    
    trend_df = df.groupby('tarih')[metric].mean().reset_index()
    trend_df['tarih_str'] = trend_df['tarih'].dt.strftime('%d.%m')
    
    fig = px.line(trend_df, x='tarih_str', y=metric, markers=True,
                 labels={'tarih_str': 'Tarih'},
                 title=f"Günlük Trend - {METRICS.get(metric, {}).get('display', metric)}")
    
    fig.update_traces(line_color='#E30A17', marker_color='#0D0D0D')
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • İstatistikler</p></div>',
            unsafe_allow_html=True)
