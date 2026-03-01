import streamlit as st
import pandas as pd
from config import AGE_GROUPS, METRICS, SCATTER_PRESETS, PRIMARY_METRICS, DEFAULT_MINUTES
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box, COLORS
from utils import plot_scatter, render_export_buttons

st.set_page_config(page_title="Scatter Analizi | TFF", layout="wide")
inject_styles()
page_header("🎯", "SCATTER ANALİZİ",
            "İki metrik bazlı oyuncu dağılımı · Filtreli · İnteraktif Korelasyon")

section_title("FİLTRELER", "⚙️")
f1, f2, f3 = st.columns(3)
with f1:
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="sc_age")

raw_age_data = db_manager.get_data_by_age_group(age_group)
if raw_age_data.empty:
    st.warning(f"{age_group} için veri bulunamadı.")
    st.stop()

camps_df = db_manager.get_camps(age_group)
camp_options = {"Tüm Kamplar": None}
camp_options.update({row['camp_name']: row['camp_id'] for _, row in camps_df.iterrows()})

with f2:
    sel_camp = st.selectbox("KAMP SEÇİMİ", list(camp_options.keys()), key="sc_camp")
with f3:
    ses = st.multiselect("SEANS TİPİ", ['TRAINING', 'MATCH'],
                         default=['TRAINING', 'MATCH'], key="sc_ses")

# ── Dakika Filtreleri (Veri Kirliliğini Önler) ───────────────────────────────
with st.expander("⚙️ DAKİKA VE VERİ FİLTRELERİ", expanded=False):
    st.markdown("<div style='font-size:13px; color:#6B7280; margin-bottom:10px;'>Grafikteki sapmaları ve sol alttaki kümelenmeleri önlemek için az oynanan seansları filtreleyebilirsiniz.</div>", unsafe_allow_html=True)
    dk1, dk2 = st.columns(2)
    with dk1: min_train_dk = st.number_input("Minimum Antrenman Dakikası", value=DEFAULT_MINUTES['TRAINING'], step=5, key="sc_dk_tr")
    with dk2: min_match_dk = st.number_input("Minimum Maç Dakikası", value=DEFAULT_MINUTES['MATCH'], step=5, key="sc_dk_ma")

def apply_minute_filter(df):
    if df.empty: return df
    is_tr = df['tip'].str.upper().str.contains('TRAINING')
    is_ma = df['tip'].str.upper().str.contains('MATCH')
    mask = (is_tr & (df['minutes'] >= min_train_dk)) | (is_ma & (df['minutes'] >= min_match_dk))
    return df[mask].copy()

if camp_options[sel_camp] is not None:
    data_filtered_camp = raw_age_data[raw_age_data['camp_id'] == camp_options[sel_camp]].copy()
else:
    data_filtered_camp = raw_age_data.copy()

if ses:
    data_filtered_camp = data_filtered_camp[data_filtered_camp['tip'].isin(ses)]

# Dakika filtresini uygula
data = apply_minute_filter(data_filtered_camp)

if data.empty:
    st.warning("Seçilen filtrelere (Kamp/Seans/Dakika) uygun veri yok. Lütfen esnetin.")
    st.stop()

st.divider()
section_title("EKSEN VE GÖRSEL AYARLARI", "🎨")

# Sadece PRIMARY_METRICS'i kullanarak 11 metriği garantiliyoruz
avail_m = [m for m in PRIMARY_METRICS if m in data.columns and data[m].dropna().any()]

e1, e2, e3, e4 = st.columns(4)
with e1:
    x_metric = st.selectbox("X EKSENİ", avail_m,
                             format_func=lambda x: METRICS.get(x, {}).get('display', x).upper(),
                             key="sc_x")
with e2:
    y_default_idx = min(avail_m.index(x_metric) + 1, len(avail_m) - 1) if x_metric in avail_m else 0
    y_metric = st.selectbox("Y EKSENİ", avail_m, index=y_default_idx,
                             format_func=lambda x: METRICS.get(x, {}).get('display', x).upper(),
                             key="sc_y")
with e3:
    color_by = st.radio("RENKLENDİRME", ["Oyuncu", "Seans Tipi"],
                        horizontal=True, key="sc_color")
with e4:
    show_avg = st.checkbox("Ortalama Çizgilerini Göster", value=True, key="sc_avg")

highlight_player = None
if color_by == "Oyuncu":
    players_in_data = sorted(data['player_name'].unique())
    hl_sel = st.selectbox("VURGULANACAK OYUNCU (Opsiyonel)", ["Yok"] + players_in_data, key="sc_hl")
    if hl_sel != "Yok":
        highlight_player = hl_sel

agg_mode = st.radio(
    "VERİ GRANÜLARİTESİ",
    ["Ham Veri (Gün Bazlı Noktalar)", "Oyuncu Ortalaması (Kamp/Filtre Bazlı Tek Nokta)"],
    horizontal=True, key="sc_agg"
)

if agg_mode == "Oyuncu Ortalaması (Kamp/Filtre Bazlı Tek Nokta)":
    plot_data = data.groupby('player_name')[[x_metric, y_metric, 'tip']].agg(
        {x_metric: 'mean', y_metric: 'mean', 'tip': 'first'}
    ).reset_index()
else:
    plot_data = data.copy()

st.divider()

x_label = METRICS.get(x_metric, {}).get('display', x_metric).upper()
y_label = METRICS.get(y_metric, {}).get('display', y_metric).upper()
section_title(f"{x_label} vs {y_label}", "🎯")

col_by = 'tip' if color_by == "Seans Tipi" else 'player_name'
fig = plot_scatter(
    data=plot_data, x_metric=x_metric, y_metric=y_metric,
    color_by=col_by, highlight_player=highlight_player, show_avg_lines=show_avg,
)
st.plotly_chart(fig, width='stretch')

# Sıfır değerlerini dışlayarak Min hesaplıyoruz
x_valid = plot_data[x_metric].replace(0, pd.NA).dropna()
y_valid = plot_data[y_metric].replace(0, pd.NA).dropna()

x_min = x_valid.min() if not x_valid.empty else 0.0
y_min = y_valid.min() if not y_valid.empty else 0.0

info_box(
    f"📊 <b>VERİ NOKTASI:</b> {len(plot_data)} &nbsp;|&nbsp; "
    f"<b>{x_label}:</b> MİN {x_min:.1f} · "
    f"ORT {plot_data[x_metric].mean():.1f} · MAX {plot_data[x_metric].max():.1f} &nbsp;|&nbsp; "
    f"<b>{y_label}:</b> MİN {y_min:.1f} · "
    f"ORT {plot_data[y_metric].mean():.1f} · MAX {plot_data[y_metric].max():.1f}"
)

render_export_buttons(
    fig=fig, df=plot_data[['player_name', 'tip', x_metric, y_metric]].round(2),
    key_prefix="sc", filename=f"scatter_{x_metric}_vs_{y_metric}"
)

st.divider()
section_title("HAZIR EKSEN ÇİFTLERİ (ŞABLONLAR)", "⚡")
info_box("Spor bilimlerinde en sık kullanılan metrik kombinasyonlarını tek tıkla görselleştirin.")

# Sadece mevcut veri kolonlarında olan preset'leri göster
valid_presets = [
    (px_m, py_m) for px_m, py_m in SCATTER_PRESETS
    if px_m in avail_m and py_m in avail_m
    and px_m in plot_data.columns and py_m in plot_data.columns
]

if valid_presets:
    preset_cols = st.columns(min(len(valid_presets), 3))
    for i, (px_m, py_m) in enumerate(valid_presets[:3]):
        with preset_cols[i]:
            lbl = f"{METRICS.get(px_m,{}).get('display',px_m).upper()} VS {METRICS.get(py_m,{}).get('display',py_m).upper()}"
            if st.button(lbl, key=f"preset_{i}", width='stretch'):
                fig_p = plot_scatter(plot_data, px_m, py_m, color_by=col_by, show_avg_lines=show_avg)
                st.plotly_chart(fig_p, width='stretch')
                render_export_buttons(fig=fig_p, key_prefix=f"sc_preset_{i}",
                                      filename=f"scatter_{px_m}_vs_{py_m}")
else:
    st.info("Mevcut veri için hazır eksen çifti bulunamadı.")

st.divider()
with st.expander("📋 HAM VERİYİ GÖSTER"):
    show_cols = ['player_name', 'tip', x_metric, y_metric]
    if 'tarih' in plot_data.columns:
        show_cols = ['tarih'] + show_cols
    disp = plot_data[show_cols].copy()
    if 'tarih' in disp.columns:
        disp['tarih'] = pd.to_datetime(disp['tarih']).dt.strftime('%d.%m.%Y')
    
    # Tablo Başlıklarını Düzenle
    rename_dict = {
        'player_name': 'OYUNCU',
        'tip': 'SEANS TİPİ',
        'tarih': 'TARİH',
        x_metric: x_label,
        y_metric: y_label
    }
    disp = disp.rename(columns=rename_dict)
    
    st.dataframe(disp.round(2), width='stretch', hide_index=True)

st.markdown('<div class="tff-footer"><p>Türkiye Futbol Federasyonu · Scatter Analizi</p></div>',
            unsafe_allow_html=True)