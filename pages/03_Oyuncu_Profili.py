# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - OYUNCU PROFİLİ
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
from config import AGE_GROUPS, METRICS, PRIMARY_METRICS, DEFAULT_MINUTES, COLORS
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box
from utils import (plot_player_performance_with_band, plot_player_radar,
                   calculate_player_stats, calculate_composite_score,
                   plot_percentile_gauge, build_stats_table,
                   calculate_player_clustering, get_similarity_score,
                   render_export_buttons)

st.set_page_config(page_title="Oyuncu Profili | TFF", layout="wide")
inject_styles()

page_header("🏃", "OYUNCU PROFİLİ",
            "Bireysel performans · Min/Ort/Max · Atletik Performans Skorlaması · Benzer Oyuncular")

# ─── OYUNCU SEÇİMİ ──────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 2])

with c1:
    default_age = st.session_state.get('pp_age', AGE_GROUPS[0])
    age_index = AGE_GROUPS.index(default_age) if default_age in AGE_GROUPS else 0
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, index=age_index, key="pp_age_sel")

with c2:
    players = db_manager.get_players(age_group)
    if not players:
        st.warning(f"❌ {age_group} için oyuncu bulunamadı")
        st.stop()
    default_player = st.session_state.get('pp_player', players[0])
    player_index = players.index(default_player) if default_player in players else 0
    selected_player = st.selectbox("OYUNCU SEÇİMİ", players, index=player_index, key="pp_player_sel")

# ─── DAKİKA FİLTRELERİ ──────────────────────────────────────────────────────
with st.expander("⚙️ DAKİKA VE VERİ FİLTRELERİ", expanded=False):
    st.markdown(f"""
    <div class="info-box">
        ℹ️ <b>Nedir?</b> Oyuncunun az süre aldığı seanslar ortalamasını olumsuz etkileyebilir.
        Bu filtreyle minimum dakika sınırları belirleyerek daha net analiz yapabilirsiniz.
    </div>
    """, unsafe_allow_html=True)
    dk1, dk2 = st.columns(2)
    with dk1:
        min_train_dk = st.number_input("Minimum Antrenman Dakikası", value=DEFAULT_MINUTES['TRAINING'], step=5, key="pp_dk_tr")
    with dk2:
        min_match_dk = st.number_input("Minimum Maç Dakikası", value=DEFAULT_MINUTES['MATCH'], step=5, key="pp_dk_ma")

# ─── VERİ ÇEKİŞİ ────────────────────────────────────────────────────────────
raw_age_data = db_manager.get_data_by_age_group(age_group)
raw_player_data = db_manager.get_data_by_player(selected_player)

if raw_player_data.empty:
    st.warning("❌ Oyuncuya ait veri bulunamadı")
    st.stop()

def apply_minute_filter(df):
    if df.empty:
        return df
    is_tr = df['tip'].str.upper().str.contains('TRAINING')
    is_ma = df['tip'].str.upper().str.contains('MATCH')
    mask = (is_tr & (df['minutes'] >= min_train_dk)) | (is_ma & (df['minutes'] >= min_match_dk))
    return df[mask].copy()

age_data = apply_minute_filter(raw_age_data)
player_data = apply_minute_filter(raw_player_data)

if player_data.empty:
    st.warning("⚠️ Seçilen filtrelere uygun veri bulunamadı. Filtreyi düşürmeyi deneyin.")
    st.stop()

stats = calculate_player_stats(player_data)

# ─── OYUNCU BİLGİLERİ ───────────────────────────────────────────────────────
player_info = db_manager.get_player_info(selected_player)
photo_url = player_info.get('photo_url') or "https://cdn-icons-png.flaticon.com/512/847/847969.png"
club_logo_url = player_info.get('club_logo_url') or "https://upload.wikimedia.org/wikipedia/tr/b/b9/Türkiye_Futbol_Federasyonu_logo.png"

# ─── OYUNCU BAŞLIK KARTI ────────────────────────────────────────────────────
st.markdown(f"""
<div style="display: flex; align-items: center; background: white;
           border: 1px solid {COLORS['GRAY_200']}; border-radius: 16px;
           padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
    
    <div style="position: relative; width: 140px; height: 140px; flex-shrink: 0;">
        <img src="{photo_url}" style="width: 100%; height: 100%; object-fit: cover;
                                     border-radius: 50%; border: 4px solid {COLORS['RED']};
                                     background: {COLORS['GRAY_50']};">
        <div style="position: absolute; bottom: -5px; right: -5px; width: 48px;
                   height: 48px; background: white; border-radius: 50%; padding: 5px;
                   box-shadow: 0 3px 10px rgba(0,0,0,0.2); border: 1px solid {COLORS['GRAY_200']};
                   display: flex; align-items: center; justify-content: center;">
            <img src="{club_logo_url}" style="width: 100%; height: 100%; object-fit: contain;">
        </div>
    </div>
    
    <div style="margin-left: 35px; flex-grow: 1;">
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 42px;
                   color: {COLORS['GRAY_900']}; letter-spacing: 1.5px; line-height: 1;">
            {selected_player.upper()}
        </div>
        <div style="font-size: 14px; color: {COLORS['GRAY_500']}; font-weight: 800;
                   text-transform: uppercase; letter-spacing: 1.5px; margin-top: 8px;">
            🇹🇷 {age_group} MİLLİ TAKIMI
        </div>
        <div style="display: flex; gap: 12px; margin-top: 15px;">
            <div style="background: {COLORS['GRAY_50']}; border: 1px solid {COLORS['GRAY_200']};
                       border-radius: 10px; padding: 10px 16px;">
                <div style="font-size: 10px; color: {COLORS['GRAY_500']}; font-weight: 800;">
                    TOPLAM KAMP</div>
                <div style="font-size: 22px; font-family: 'Bebas Neue'; color: {COLORS['RED']};
                           letter-spacing: 1px;">{int(stats.get('camp_count', 0))}</div>
            </div>
            <div style="background: {COLORS['GRAY_50']}; border: 1px solid {COLORS['GRAY_200']};
                       border-radius: 10px; padding: 10px 16px;">
                <div style="font-size: 10px; color: {COLORS['GRAY_500']}; font-weight: 800;">
                    GEÇERLİ GÜN</div>
                <div style="font-size: 22px; font-family: 'Bebas Neue'; color: {COLORS['RED']};
                           letter-spacing: 1px;">{int(stats.get('session_count', 0))}</div>
            </div>
            <div style="background: {COLORS['GRAY_50']}; border: 1px solid {COLORS['GRAY_200']};
                       border-radius: 10px; padding: 10px 16px;">
                <div style="font-size: 10px; color: {COLORS['GRAY_500']}; font-weight: 800;">
                    MAX HIZ (GENEL)</div>
                <div style="font-size: 22px; font-family: 'Bebas Neue'; color: {COLORS['RED']};
                           letter-spacing: 1px;">{stats.get('max_speed', 0):.1f}</div>
                <div style="font-size: 9px; color: {COLORS['GRAY_400']};">km/h</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KAMP SEÇİMİ ────────────────────────────────────────────────────────────
camps_df = db_manager.get_camps(age_group)
camp_dict = {}
for _, row in camps_df.iterrows():
    if row['camp_id'] in raw_player_data['camp_id'].values:
        label = row['camp_name']
        if pd.notna(row.get('start_date')):
            label += f"  ({str(row['start_date'])[:7]})"
        camp_dict[label] = row['camp_id']

if not camp_dict:
    st.warning("❌ Oyuncunun katıldığı kamp bulunamadı")
    st.stop()

cc1, cc2, cc3 = st.columns([2, 1, 1])

with cc1:
    sel_camp_label = st.selectbox("KAMP SEÇİMİ", list(camp_dict.keys()), key="pp_camp")

with cc2:
    ses = st.radio("GÖRÜNÜM SESANSI", ["Tümü", "TRAINING", "MATCH"], horizontal=True, key="pp_ses")

with cc3:
    score_ses = st.radio("SKOR BAZLAMA", ["Tümü", "TRAINING", "MATCH"], horizontal=True, key="pp_score_ses")

sel_camp_id = camp_dict[sel_camp_label]
camp_player_data = player_data[player_data['camp_id'] == sel_camp_id].copy()
camp_team_data = age_data[age_data['camp_id'] == sel_camp_id].copy()

if ses != "Tümü":
    camp_player_data = camp_player_data[camp_player_data['tip'].str.upper() == ses]
    camp_team_data = camp_team_data[camp_team_data['tip'].str.upper() == ses]

score_dict = calculate_composite_score(camp_player_data, camp_team_data, 
                                        session_filter=score_ses if score_ses != "Tümü" else "ALL")
composite = score_dict.get('composite', 0)

safe_player_name = selected_player.replace(" ", "_")
safe_camp_name = sel_camp_label.split(" ")[0].replace(".", "_")

st.divider()

# ─── SEÇİLİ KAMP PERFORMANSI ────────────────────────────────────────────────
section_title("SEÇİLİ KAMP PERFORMANSI", "📊")

m1, m2, m3, m4, m5, m6, m7 = st.columns(7)

m_data = camp_player_data[camp_player_data['tip'].str.upper().str.contains('MATCH')]
t_data = camp_player_data[camp_player_data['tip'].str.upper().str.contains('TRAINING')]

metrics_list = [
    (m1, "GÜN", camp_player_data['tarih'].nunique()),
    (m2, "SEANS", len(camp_player_data)),
    (m3, "MAÇ GÜNÜ", m_data['tarih'].nunique() if not m_data.empty else 0),
    (m4, "ANTRENMAN", t_data['tarih'].nunique() if not t_data.empty else 0),
    (m5, "ORT. MESAFE", f"{camp_player_data['total_distance'].mean():.0f} m"),
    (m6, "MAX HIZ", f"{camp_player_data['smax_kmh'].max():.1f} km/h"),
]

for col, label, value in metrics_list:
    with col:
        st.markdown(f"""
        <div class="metric-card" style="padding: 12px; text-align: center;">
            <div class="sc-label">{label}</div>
            <div class="sc-val" style="font-size: 22px;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

with m7:
    color = '#059669' if composite >= 80 else '#10B981' if composite >= 65 else '#F59E0B' if composite >= 50 else '#EF4444'
    st.markdown(f"""
    <div style="background: white; border: 1px solid {COLORS['GRAY_200']};
               border-radius: 12px; padding: 12px 10px; text-align: center;
               border-top: 4px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
        <div style="font-size: 9px; font-weight: 800; text-transform: uppercase;
                   color: {COLORS['GRAY_500']};">ATLETİK SKOR</div>
        <div style="font-family: 'Bebas Neue'; font-size: 26px; color: {color};
                   margin-top: 2px; letter-spacing: 1px;">{composite:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─── TABLETLER ──────────────────────────────────────────────────────────────
section_title("DETAYLI ANALIZ SEKMELEERI", "📈")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 PERFORMANS SERISI",
    "📊 MIN/ORT/MAX",
    "🎯 ATLETİK SKORLAMA",
    "🔵 RADAR PROFILI",
    "🧑🤝🧑 BENZER OYUNCULAR"
])

# ─── TAB 1: PERFORMANS SERİSİ ───────────────────────────────────────────────
with tab1:
    st.markdown(f"""
    <div class="info-box">
        📈 <b>Bu Nedir?</b> Oyuncunun seçili kamptaki günlük performans grafiğidir.
        Kırmızı çizgi takım ortalaması, gri bölge ±1 standart sapma aralığıdır.
        Yeşil nokta oyuncunun performansını gösterir.
    </div>
    """, unsafe_allow_html=True)
    
    avail_m = [m for m in PRIMARY_METRICS if m in camp_player_data.columns and camp_player_data[m].notna().any()]
    
    if avail_m:
        for i in range(0, len(avail_m), 2):
            cols = st.columns(2)
            for j, metric in enumerate(avail_m[i:i+2]):
                with cols[j]:
                    fig = plot_player_performance_with_band(camp_player_data, camp_team_data, metric)
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 Bu seçim için performans verisi bulunamadı")

# ─── TAB 2: MIN/ORT/MAX ──────────────────────────────────────────────────────
with tab2:
    st.markdown(f"""
    <div class="info-box">
        📊 <b>Bu Nedir?</b> Her metriğin minimum, ortalama ve maksimum değerleridir.
        Takım Ort. sütunu, takımın genel ortalaması ile karşılaştırma yapmanızı sağlar.
    </div>
    """, unsafe_allow_html=True)
    
    mm_df = build_stats_table(camp_player_data, camp_team_data)
    st.dataframe(mm_df, use_container_width=True, hide_index=True)
    render_export_buttons(df=mm_df, key_prefix="pp_mm", filename=f"{safe_player_name}_{safe_camp_name}")

# ─── TAB 3: ATLETİK SKORLAMA ────────────────────────────────────────────────
with tab3:
    st.markdown(f"""
    <div class="info-box">
        🎯 <b>Atletik Performans Skoru (Percentile) Nedir?</b><br>
        Oyuncunun her metrikteki performansını takım içinde yüzdesel olarak gösterir.
        %80+ Mükemmel · %65-80 İyi · %50-65 Orta · <50 Düşük anlamına gelir.
    </div>
    """, unsafe_allow_html=True)
    
    pct_metrics = [m for m in PRIMARY_METRICS if m in camp_player_data.columns and camp_player_data[m].dropna().any()]
    
    if pct_metrics:
        cols_count = min(len(pct_metrics), 4)
        gauge_cols = st.columns(cols_count)
        
        for i, m in enumerate(pct_metrics):
            with gauge_cols[i % 4]:
                pct = score_dict.get(m, 50)
                label = METRICS.get(m, {}).get('display', m)
                fig = plot_percentile_gauge(pct, label)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("📭 Skorlanabilecek metrik bulunamadı")

# ─── TAB 4: RADAR PROFİLİ ───────────────────────────────────────────────────
with tab4:
    st.markdown(f"""
    <div class="info-box">
        🔵 <b>Radar Profili Nedir?</b><br>
        Oyuncunun tüm metriklerdeki performansını radar şeklinde gösterir.
        Her eksendeki uzunluk oyuncunun o metrikteki percentile puanıdır (0-100%).
    </div>
    """, unsafe_allow_html=True)
    
    if not camp_team_data.empty:
        fig_r = plot_player_radar(camp_player_data, camp_team_data)
        st.plotly_chart(fig_r, use_container_width=True)
        render_export_buttons(fig=fig_r, key_prefix="pp_radar", filename=f"{safe_player_name}_{safe_camp_name}")
    else:
        st.warning("📭 Radar profili oluşturamadı")

# ─── TAB 5: BENZER OYUNCULAR (KÜMLEMEv) ──────────────────────────────────────
with tab5:
    st.markdown(f"""
    <div class="info-box">
        🧑🤝🧑 <b>Benzer Oyuncular Nedir?</b><br>
        K-Means kümeleme algoritması kullanarak oyuncuyu tüm metriklerine göre karşılaştırır.
        Aynı kümede yer alan oyuncular atletik özellikler bakımından benzerdir.
        Benzerlik Skoru 0-100% arasında gösterilir (100% = Aynı).
    </div>
    """, unsafe_allow_html=True)
    
    similar_players, all_players_clustered = calculate_player_clustering(age_data, selected_player)
    
    if similar_players is not None and not similar_players.empty:
        st.success(f"✅ {len(similar_players)} benzer oyuncu bulundu!")
        
        # Benzerlik skorlarını hesapla
        selected_stats = all_players_clustered.loc[selected_player]
        
        similarity_data = []
        for player_name in similar_players.index:
            similarity_score = get_similarity_score(selected_stats, similar_players.loc[player_name])
            similarity_data.append({
                'OYUNCU': player_name,
                'BENZERLİK SKORU (%)': similarity_score
            })
        
        sim_df = pd.DataFrame(similarity_data).sort_values('BENZERLİK SKORU (%)', ascending=False)
        
        # Renk kodlaması
        st.dataframe(
            sim_df.style.background_gradient(cmap='Greens', subset=['BENZERLİK SKORU (%)']),
            use_container_width=True, hide_index=True
        )
        
        # Detaylı karşılaştırma
        st.markdown("### 📊 Detaylı Metrik Karşılaştırması")
        
        if len(sim_df) > 0:
            comp_player = st.selectbox(
                "Karşılaştırılacak Oyuncu Seçin",
                sim_df['OYUNCU'].tolist(),
                key="comp_player"
            )
            
            st.markdown(f"**{selected_player} vs {comp_player}**")
            
            comp_cols = st.columns(4)
            
            for i, metric in enumerate(PRIMARY_METRICS[:8]):
                col_idx = i % 4
                with comp_cols[col_idx]:
                    selected_val = selected_stats.get(metric, 0)
                    comp_val = similar_players.loc[comp_player, metric] if metric in similar_players.columns else 0
                    
                    if selected_val > comp_val:
                        color = COLORS['SUCCESS']
                        arrow = "▲"
                    elif selected_val < comp_val:
                        color = COLORS['DANGER']
                        arrow = "▼"
                    else:
                        color = COLORS['GRAY_400']
                        arrow = "▬"
                    
                    metric_label = METRICS.get(metric, {}).get('display', metric)
                    
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid {COLORS['GRAY_200']};
                               border-radius: 8px; padding: 12px; text-align: center;">
                        <div style="font-size: 9px; color: {COLORS['GRAY_600']};
                                   font-weight: 800; margin-bottom: 8px;">
                            {metric_label}
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                            <div style="background: {COLORS['GRAY_50']}; padding: 6px;
                                       border-radius: 4px; font-size: 13px;
                                       font-weight: 700; color: {COLORS['RED']};">
                                {selected_val:.1f}
                            </div>
                            <div style="background: {COLORS['GRAY_50']}; padding: 6px;
                                       border-radius: 4px; font-size: 13px;
                                       font-weight: 700; color: {COLORS['GRAY_700']};">
                                {comp_val:.1f}
                            </div>
                        </div>
                        <div style="margin-top: 6px; font-size: 14px; color: {color};
                                   font-weight: 700;">
                            {arrow}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📭 Benzer oyuncu bulunamadı veya veri yetersiz")

st.divider()

st.markdown(f"""
<div class="tff-footer">
    <p>Türkiye Futbol Federasyonu • Oyuncu Profili Analizi</p>
</div>
""", unsafe_allow_html=True)
