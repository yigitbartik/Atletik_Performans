# SCATTER ANALİZİ SAYFASI
import streamlit as st
import pandas as pd
from config import AGE_GROUPS, METRICS, PRIMARY_METRICS
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box
from utils import plot_scatter, render_export_buttons

st.set_page_config(page_title="Scatter Analizi | TFF", layout="wide")
inject_styles()

page_header("🎯", "SCATTER ANALİZİ", "İki metrik bazlı oyuncu dağılımı ve korelasyon")

section_title("FİLTRELER", "⚙️")
f1, f2, f3 = st.columns(3)

with f1:
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="sc_age")

raw_data = db_manager.get_data_by_age_group(age_group)

if raw_data.empty:
    st.warning(f"❌ {age_group} için veri bulunamadı")
    st.stop()

avail_m = [m for m in PRIMARY_METRICS if m in raw_data.columns and raw_data[m].dropna().any()]

st.divider()
section_title("EKSEN SEÇİMİ", "🎨")

e1, e2 = st.columns(2)
with e1:
    x_metric = st.selectbox("X EKSENİ", avail_m,
                            format_func=lambda x: METRICS.get(x, {}).get('display', x),
                            key="sc_x")

with e2:
    y_idx = min(avail_m.index(x_metric) + 1, len(avail_m) - 1) if x_metric in avail_m else 0
    y_metric = st.selectbox("Y EKSENİ", avail_m, index=y_idx,
                            format_func=lambda x: METRICS.get(x, {}).get('display', x),
                            key="sc_y")

st.divider()

x_label = METRICS.get(x_metric, {}).get('display', x_metric)
y_label = METRICS.get(y_metric, {}).get('display', y_metric)

section_title(f"{x_label} vs {y_label}", "🎯")

fig = plot_scatter(raw_data, x_metric, y_metric)
st.plotly_chart(fig, use_container_width=True)

info_box(f"📊 <b>VERİ:</b> {len(raw_data)} veri noktası")

render_export_buttons(fig=fig, key_prefix="sc", filename=f"scatter_{x_metric}_vs_{y_metric}")

st.markdown(f'<div class="tff-footer"><p>Türkiye Futbol Federasyonu • Scatter Analizi</p></div>',
            unsafe_allow_html=True)
