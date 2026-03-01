import streamlit as st
import pandas as pd
from config import AGE_GROUPS, METRICS, PRIMARY_METRICS, DEFAULT_MINUTES
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box, COLORS
from utils import (plot_player_performance_with_band, plot_player_radar,
                   calculate_player_stats, calculate_composite_score,
                   plot_percentile_gauge, build_stats_table,
                   generate_player_report_html, render_export_buttons, percentile_color)

st.set_page_config(page_title="Oyuncu Profili | TFF", layout="wide")
inject_styles()

page_header("🏃", "OYUNCU PROFİLİ",
            "Bireysel performans · Min/Ort/Max · Atletik Performans Skorlaması · Rapor Kartı")

c1, c2 = st.columns([1, 2])
with c1:
    default_age = st.session_state.get('pp_age', AGE_GROUPS[0])
    age_index = AGE_GROUPS.index(default_age) if default_age in AGE_GROUPS else 0
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, index=age_index, key="pp_age_sel")

with c2:
    players = db_manager.get_players(age_group)
    if not players:
        st.warning(f"{age_group} için oyuncu bulunamadı."); st.stop()
    default_player = st.session_state.get('pp_player', players[0])
    player_index = players.index(default_player) if default_player in players else 0
    selected_player = st.selectbox("OYUNCU SEÇİMİ", players, index=player_index, key="pp_player_sel")

# ── Dakika Filtreleri (Veri Kirliliğini Önler) ───────────────────────────────
with st.expander("⚙️ DAKİKA VE VERİ FİLTRELERİ", expanded=False):
    st.markdown("<div style='font-size:13px; color:#6B7280; margin-bottom:10px;'>Oyuncunun az süre aldığı seansların genel ortalamasını (Percentile) düşürmemesi için minimum dakika sınırlarını belirleyin.</div>", unsafe_allow_html=True)
    dk1, dk2 = st.columns(2)
    with dk1:
        min_train_dk = st.number_input("Minimum Antrenman Dakikası", value=DEFAULT_MINUTES['TRAINING'], step=5, key="pp_dk_tr")
    with dk2:
        min_match_dk = st.number_input("Minimum Maç Dakikası", value=DEFAULT_MINUTES['MATCH'], step=5, key="pp_dk_ma")

raw_age_data    = db_manager.get_data_by_age_group(age_group)
raw_player_data = db_manager.get_data_by_player(selected_player)

if raw_player_data.empty:
    st.warning("Oyuncuya ait veri bulunamadı."); st.stop()

# Filtreyi Uygula
def apply_minute_filter(df):
    if df.empty: return df
    is_tr = df['tip'].str.upper().str.contains('TRAINING')
    is_ma = df['tip'].str.upper().str.contains('MATCH')
    mask = (is_tr & (df['minutes'] >= min_train_dk)) | (is_ma & (df['minutes'] >= min_match_dk))
    return df[mask].copy()

age_data = apply_minute_filter(raw_age_data)
player_data = apply_minute_filter(raw_player_data)

if player_data.empty:
    st.warning("Belirlenen dakika filtrelerine uygun oyuncu verisi bulunamadı. Lütfen filtreyi düşürün.")
    st.stop()

stats = calculate_player_stats(player_data)

player_info = db_manager.get_player_info(selected_player)
photo_url = player_info.get('photo_url') if player_info.get('photo_url') else "https://cdn-icons-png.flaticon.com/512/847/847969.png"
club_logo_url = player_info.get('club_logo_url') if player_info.get('club_logo_url') else "https://upload.wikimedia.org/wikipedia/tr/b/b9/T%C3%BCrkiye_Futbol_Federasyonu_logo.png"

# ── Oyuncu Üst Kartı (Hero Section) ───────────────────────────────────────────
st.markdown(f"""
<div style="display: flex; align-items: center; background: #FFFFFF; border: 1px solid {COLORS['GRAY_200']}; border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
    <div style="position: relative; width: 140px; height: 140px; flex-shrink: 0;">
        <img src="{photo_url}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%; border: 4px solid #E30A17; background: #FAFAFA;">
        <div style="position: absolute; bottom: -5px; right: -5px; width: 48px; height: 48px; background: white; border-radius: 50%; padding: 5px; box-shadow: 0 3px 10px rgba(0,0,0,0.2); border: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: center;">
            <img src="{club_logo_url}" style="width: 100%; height: 100%; object-fit: contain;">
        </div>
    </div>
    <div style="margin-left: 35px; flex-grow: 1;">
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 42px; color: {COLORS['GRAY_900']}; letter-spacing: 1.5px; line-height: 1.1;">
            {selected_player.upper()}
        </div>
        <div style="font-size: 15px; color: {COLORS['GRAY_500']}; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px;">
            🇹🇷 {age_group} MİLLİ TAKIMI
        </div>
        <div style="display: flex; gap: 15px; margin-top: 15px;">
            <div style="background: {COLORS['GRAY_50']}; border: 1px solid {COLORS['GRAY_200']}; border-radius: 10px; padding: 10px 20px;">
                <div style="font-size: 11px; color: {COLORS['GRAY_500']}; font-weight: 800; text-transform: uppercase;">Toplam Kamp</div>
                <div style="font-size: 22px; font-family:'Bebas Neue'; color: {COLORS['GRAY_800']}; letter-spacing: 1px;">{int(stats.get('camp_count', 0))}</div>
            </div>
            <div style="background: {COLORS['GRAY_50']}; border: 1px solid {COLORS['GRAY_200']}; border-radius: 10px; padding: 10px 20px;">
                <div style="font-size: 11px; color: {COLORS['GRAY_500']}; font-weight: 800; text-transform: uppercase;">Geçerli Gün</div>
                <div style="font-size: 22px; font-family:'Bebas Neue'; color: {COLORS['GRAY_800']}; letter-spacing: 1px;">{int(stats.get('session_count', 0))}</div>
            </div>
            <div style="background: {COLORS['GRAY_50']}; border: 1px solid {COLORS['GRAY_200']}; border-radius: 10px; padding: 10px 20px;">
                <div style="font-size: 11px; color: {COLORS['GRAY_500']}; font-weight: 800; text-transform: uppercase;">Max Hız (Genel)</div>
                <div style="font-size: 22px; font-family:'Bebas Neue'; color: #E30A17; letter-spacing: 1px;">{stats.get('max_speed', 0):.1f} <span style="font-size:12px; font-family:'DM Sans';">km/h</span></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

camps_df  = db_manager.get_camps(age_group)
camp_dict = {}
for _, row in camps_df.iterrows():
    if row['camp_id'] in raw_player_data['camp_id'].values:
        label = row['camp_name']
        if pd.notna(row.get('start_date')):
            label += f"  ({str(row['start_date'])[:7]})"
        camp_dict[label] = row['camp_id']

cc1, cc2, cc3 = st.columns([2, 1, 1])
with cc1: sel_camp_label = st.selectbox("KAMP SEÇİMİ", list(camp_dict.keys()), key="pp_camp")
with cc2: ses = st.radio("SEANS TİPİ (GÖRÜNÜM İÇİN)", ["Tümü","TRAINING","MATCH"], horizontal=True, key="pp_ses")
with cc3: score_ses = st.radio("SKORLAMA BAZI (PERCENTILE)", ["Tümü","TRAINING","MATCH"], horizontal=True, key="pp_score_ses")

sel_camp_id      = camp_dict[sel_camp_label]
camp_player_data = player_data[player_data['camp_id'] == sel_camp_id].copy()
camp_team_data   = age_data[age_data['camp_id'] == sel_camp_id].copy()

if ses != "Tümü":
    camp_player_data = camp_player_data[camp_player_data['tip'].str.upper() == ses]
    camp_team_data   = camp_team_data[camp_team_data['tip'].str.upper() == ses]

score_dict = calculate_composite_score(camp_player_data, camp_team_data, session_filter=score_ses if score_ses != "Tümü" else "ALL")
composite  = score_dict.get('composite', 0)

safe_player_name = selected_player.replace(" ", "_")
safe_camp_name = sel_camp_label.split(" ")[0].replace(".", "_")

st.divider()

# ── Seçili Kamp Performansı ───────────────────────────────────────────────────
section_title("SEÇİLİ KAMP PERFORMANSI", "📊")
m1,m2,m3,m4,m5,m6,m7 = st.columns(7)
m_data = camp_player_data[camp_player_data['tip'].str.upper().str.contains('MATCH')]
t_data = camp_player_data[camp_player_data['tip'].str.upper().str.contains('TRAINING')]

with m1: st.markdown(f"<div class='metric-card' style='padding:12px;'><div class='sc-label'>GÜN</div><div class='sc-val' style='font-size:24px;'>{camp_player_data['tarih'].nunique()}</div></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card' style='padding:12px;'><div class='sc-label'>SEANS</div><div class='sc-val' style='font-size:24px;'>{len(camp_player_data)}</div></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='metric-card' style='padding:12px;'><div class='sc-label'>MAÇ GÜNÜ</div><div class='sc-val' style='font-size:24px;'>{m_data['tarih'].nunique() if not m_data.empty else 0}</div></div>", unsafe_allow_html=True)
with m4: st.markdown(f"<div class='metric-card' style='padding:12px;'><div class='sc-label'>ANTRENMAN</div><div class='sc-val' style='font-size:24px;'>{t_data['tarih'].nunique() if not t_data.empty else 0}</div></div>", unsafe_allow_html=True)
with m5: st.markdown(f"<div class='metric-card' style='padding:12px;'><div class='sc-label'>ORT. MESAFE</div><div class='sc-val' style='font-size:24px;'>{camp_player_data['total_distance'].mean():.0f} <span style='font-size:10px;color:#9CA3AF;'>m</span></div></div>", unsafe_allow_html=True)
with m6: st.markdown(f"<div class='metric-card' style='padding:12px;'><div class='sc-label'>MAX HIZ</div><div class='sc-val' style='font-size:24px;'>{camp_player_data['smax_kmh'].max():.1f} <span style='font-size:10px;color:#9CA3AF;'>km/h</span></div></div>", unsafe_allow_html=True)
with m7:
    c = percentile_color(composite)
    st.markdown(f"""
    <div style="background:white;border:1px solid {COLORS['GRAY_200']};border-radius:12px;
                padding:12px 10px;text-align:center;border-top:4px solid {c}; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
        <div style="font-size:10px;font-weight:800;text-transform:uppercase; color:{COLORS['GRAY_500']};">BİLEŞİK SKOR</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:26px; color:{c}; margin-top:2px; letter-spacing: 1px;">{composite:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈  PERFORMANS", "📊  MİN/ORT/MAX", "🎯  ATLETİK SKORLAMA", "🔵  RADAR", "📄  RAPOR KARTI"])

# ── TAB 1: Performans Serisi (Tüm Metrikler Eklendi) ──────────────────────────
with tab1:
    avail_m = [m for m in PRIMARY_METRICS if m in camp_player_data.columns and camp_player_data[m].notna().any()]
    for i in range(0, len(avail_m), 2):
        cols = st.columns(2)
        for j, metric in enumerate(avail_m[i:i+2]):
            with cols[j]:
                fig = plot_player_performance_with_band(camp_player_data, camp_team_data, metric)
                st.plotly_chart(fig, use_container_width=True)

# ── TAB 2: Min / Ort / Max Tablosu ───────────────────────────────────────────
with tab2:
    # utils içerisindeki güncellenmiş ve Min=0 hataları giderilmiş tablo
    mm_df = build_stats_table(camp_player_data, camp_team_data)
    st.dataframe(mm_df, use_container_width=True, hide_index=True)
    render_export_buttons(df=mm_df, key_prefix="pp_mm", filename=f"{safe_player_name}_{safe_camp_name}_MinOrtMax")

# ── TAB 3: Percentile & Yapay Zeka Yorumu ────────────────────────────────────
with tab3:
    section_title("ATLETİK PERFORMANS SKORLAMASI (PERCENTILE)", "🎯", 
                  tooltip="Oyuncunun her bir metrikteki performansı...")

    pct_metrics = [m for m in PRIMARY_METRICS if m in camp_player_data.columns and camp_player_data[m].dropna().any()]
    
    # HATA ÖNLEYİCİ: Eğer hiç metrik yoksa kullanıcıyı uyar ve dur
    if not pct_metrics:
        st.warning("Bu oyuncu için skorlanabilecek metrik verisi bulunamadı.")
    else:
        # AI Yorum Kutusu kısmı buraya gelecek...
        # (Mevcut AI yorum kodların...)

        st.divider()

        # Dinamik sütun yapısı - Artık en az 1 sütun olacağı garanti
        cols_count = min(len(pct_metrics), 4)
        gauge_cols = st.columns(cols_count)
        
        for i, m in enumerate(pct_metrics):
            with gauge_cols[i % 4]:
                pct = score_dict.get(m, 50)
                label = METRICS.get(m, {}).get('display', m)
                fig = plot_percentile_gauge(pct, label)
                st.plotly_chart(fig, use_container_width=True)

# ── TAB 4: Radar Grafiği ─────────────────────────────────────────────────────
with tab4:
    if not camp_team_data.empty:
        fig_r = plot_player_radar(camp_player_data, camp_team_data)
        st.plotly_chart(fig_r, use_container_width=True)
        render_export_buttons(fig=fig_r, key_prefix="pp_radar", filename=f"{safe_player_name}_{safe_camp_name}_Radar")

# ── TAB 5: Çoklu Kamp Rapor Kartı (PDF/HTML) ─────────────────────────────────
with tab5:
    report_camps = st.multiselect("RAPORA DAHİL EDİLECEK KAMPLAR", options=list(camp_dict.keys()), default=[sel_camp_label], key="report_camps")
    if report_camps:
        report_camp_ids = [camp_dict[c] for c in report_camps]
        # Rapor için veriyi tekrar dakika filtreli ana setten (player_data) çekiyoruz
        report_p_data = player_data[player_data['camp_id'].isin(report_camp_ids)].copy()
        report_t_data = age_data[age_data['camp_id'].isin(report_camp_ids)].copy()
        rep_stats = calculate_player_stats(report_p_data)
        rep_score_dict = calculate_composite_score(report_p_data, report_t_data, session_filter=score_ses if score_ses != "Tümü" else "ALL")

        html_report = generate_player_report_html(
            player_name=selected_player, age_group=age_group, stats=rep_stats, score_dict=rep_score_dict,
            player_data=report_p_data, team_data=report_t_data,
            camp_name=" + ".join([c.split(" ")[0] for c in report_camps]),
            photo_url=photo_url, club_logo_url=club_logo_url
        )
        render_export_buttons(html_report=html_report, key_prefix="pp_report", filename=f"{age_group}_{safe_player_name}_Rapor")
        
        with st.expander("📄 RAPOR ÖNİZLEMESİ", expanded=True):
            st.components.v1.html(html_report, height=700, scrolling=True)

st.markdown('<div class="tff-footer"><p>Türkiye Futbol Federasyonu · Oyuncu Profili Analizi</p></div>', unsafe_allow_html=True)