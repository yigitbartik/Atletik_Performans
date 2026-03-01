import streamlit as st
import pandas as pd
import plotly.express as px
from config import AGE_GROUPS, METRICS
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box

st.set_page_config(page_title="İstatistikler & Trendler | TFF", layout="wide")
inject_styles()

page_header("📈", "İstatistikler & Trendler", "Yaş grubunun genel dağılımı, metrik korelasyonları ve kamp kıyaslamaları")

# ── Üst Filtreler ─────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 3])
with c1:
    age_group = st.selectbox("Yaş Grubu Seçin", AGE_GROUPS)

# Veriyi Çek
df = db_manager.get_data_by_age_group(age_group)

if df.empty:
    st.warning(f"{age_group} için veritabanında henüz veri bulunmuyor.")
    st.stop()

# Kamp İsimlerini Merge Et (Tablolarda ID yerine İsim yazsın)
camps_df = db_manager.get_camps(age_group)
if not camps_df.empty:
    df = df.merge(camps_df[['camp_id', 'camp_name']], on='camp_id', how='left')
else:
    df['camp_name'] = "Kamp " + df['camp_id'].astype(str)

# Metrik Listesini Hazırla
numeric_cols = [c for c in METRICS.keys() if c in df.columns and df[c].notna().any()]

tabs = st.tabs(["📊 Dağılım (Box-Plot)", "📉 Korelasyon Matrisi", "📈 Zaman Serisi (Trend)"])

# ── TAB 1: DAĞILIM (KUTU GRAFİĞİ) ─────────────────────────────────────────────
with tabs[0]:
    section_title("Kamp Zorluk ve Dağılım Analizi", "📊")
    info_box("Kutu grafiği (Box-plot), bir kamptaki değerlerin nasıl dağıldığını gösterir. Ortadaki çizgi medyanı, kutunun sınırları ise oyuncuların %50'sinin yığıldığı alanı temsil eder.")
    
    sel_dist_metric = st.selectbox("Dağılımı İncelenecek Metrik:", numeric_cols, format_func=lambda x: METRICS.get(x, {}).get('display', x), key="dist_metric")
    
    fig_box = px.box(
        df, 
        x='camp_name', 
        y=sel_dist_metric, 
        color='tip',
        color_discrete_map={'MATCH': '#0D0D0D', 'TRAINING': '#E30A17'},
        labels={'camp_name': 'Kamp Adı', sel_dist_metric: METRICS.get(sel_dist_metric, {}).get('display', sel_dist_metric), 'tip': 'Seans Tipi'},
        title=f"{age_group} - Kamplara Göre {METRICS.get(sel_dist_metric, {}).get('display', sel_dist_metric)} Dağılımı"
    )
    fig_box.update_layout(template="plotly_white", xaxis={'categoryorder':'category ascending'})
    st.plotly_chart(fig_box, use_container_width=True)

# ── TAB 2: KORELASYON MATRİSİ ─────────────────────────────────────────────────
with tabs[1]:
    section_title("Metrikler Arası Korelasyon", "📉")
    info_box("Hangi metriklerin birbiriyle doğrudan ilişkili olduğunu gösterir. +1'e yaklaşan değerler doğru orantıyı (biri artarken diğeri artar), -1'e yaklaşan değerler ters orantıyı ifade eder.")
    
    corr_metrics = st.multiselect(
        "Korelasyona Dahil Edilecek Metrikler:", 
        numeric_cols, 
        default=[m for m in ['total_distance', 'metrage', 'smax_kmh', 'player_load', 'amp'] if m in numeric_cols]
    )
    
    if len(corr_metrics) > 1:
        corr_df = df[corr_metrics].corr().round(2)
        
        # Etiketleri anlaşılır isimlere çevir
        corr_df.columns = [METRICS.get(c, {}).get('display', c) for c in corr_df.columns]
        corr_df.index = corr_df.columns
        
        fig_corr = px.imshow(
            corr_df, 
            text_auto=True, 
            aspect="auto",
            color_continuous_scale='RdBu_r', 
            zmin=-1, zmax=1,
            title="Korelasyon Isı Haritası"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Korelasyon oluşturmak için en az 2 metrik seçmelisiniz.")

# ── TAB 3: TREND (ZAMAN SERİSİ) ───────────────────────────────────────────────
with tabs[2]:
    section_title("Takım Ortalaması Trend Analizi", "📈")
    info_box("Zaman içinde takımın genel performans ortalamasının nasıl değiştiğini izleyin.")
    
    sel_trend_metric = st.selectbox("Trendi İzlenecek Metrik:", numeric_cols, format_func=lambda x: METRICS.get(x, {}).get('display', x), key="trend_metric")
    
    # Tarihe göre takım ortalamasını al
    trend_df = df.groupby('tarih')[sel_trend_metric].mean().reset_index()
    trend_df['tarih_str'] = trend_df['tarih'].dt.strftime('%d.%m.%Y')
    
    fig_trend = px.line(
        trend_df, 
        x='tarih_str', 
        y=sel_trend_metric, 
        markers=True,
        labels={'tarih_str': 'Tarih', sel_trend_metric: 'Takım Ortalaması'},
        title=f"Günlük Takım Ortalaması - {METRICS.get(sel_trend_metric, {}).get('display', sel_trend_metric)}"
    )
    fig_trend.update_traces(line=dict(color='#E30A17', width=3), marker=dict(size=8, color='#0D0D0D'))
    fig_trend.update_layout(template="plotly_white", xaxis_tickangle=-45)
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown('<div class="tff-footer"><p>TFF Performans Sistemi · İstatistikler</p></div>', unsafe_allow_html=True)