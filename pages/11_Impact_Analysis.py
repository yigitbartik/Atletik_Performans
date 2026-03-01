import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from config import AGE_GROUPS
from database import db_manager
from styles import inject_styles, page_header, section_title, COLORS
from utils import calculate_impact_score_engine, calculate_development_stats, render_export_buttons

st.set_page_config(page_title="Impact Analizi | TFF", layout="wide")
inject_styles()

page_header("⚡", "IMPACT (ETKİ) ANALİZİ",
            "Tüm atletik değişkenlerin Z-Skoru ile hesaplanmış objektif günlük ve kamp performansı.")

# ── Model Açıklaması (Expander) ───────────────────────────────────────────────
with st.expander("📌 İMPACT MODELİ METODOLOJİSİ (SİSTEM NASIL ÇALIŞIR?)"):
    st.markdown("""
    **Hesaplama Adımları:**
    1. **Dakikaya Oranlama (Normalization):** Max hız hariç tüm veriler (Mesafe, HSR, İvmelenme, Load vb.) oyuncunun sahada kaldığı dakikaya bölünerek *Birim Dakika* verisi elde edilir.
    2. **Z-Skoru Dağılımı:** Oyuncunun birim dakika verisi, o günkü takımın ortalamasından çıkarılıp standart sapmaya bölünür. Böylece oyuncunun takıma göre kaç standart sapma saptığı (Z-Score) bulunur.
    3. **Ağırlıklı İndeks (Impact Score):** Z-Skorları TFF atletik standartlarına göre ağırlıklandırılır:
       * **%25** Yüksek Hızlı Koşu (25+ km/h)
       * **%20** Patlayıcı Aksiyon (Acc > 3 + Dec < -3)
       * **%20** Oyuncu Yükü (Player Load)
       * **%15** Toplam Mesafe (Volume)
       * **%10** Maksimum Hız (Smax)
       * **%10** Metabolik Güç (AMP & Metrage)
    4. **Ölçekleme:** Elde edilen toplam sapma değeri 0 ile 100 arasında anlaşılır bir endekse dönüştürülür.
    """, unsafe_allow_html=True)

# ── Filtreler ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="ia_age")

raw_age_data = db_manager.get_data_by_age_group(age_group)
if raw_age_data.empty:
    st.warning(f"{age_group} için veri bulunamadı.")
    st.stop()

camps_df = db_manager.get_camps(age_group)
camp_options = {row['camp_name']: row['camp_id'] for _, row in camps_df.iterrows()}

with c2:
    if camp_options:
        sel_camp_label = st.selectbox("KAMP SEÇİMİ", list(camp_options.keys()), key="ia_camp")
        sel_camp_id = camp_options[sel_camp_label]
    else:
        st.warning(f"{age_group} için kamp bulunamadı.")
        st.stop()

with c3:
    ses = st.radio("SEANS TİPİ", ["Tümü", "TRAINING", "MATCH"], horizontal=True, key="ia_ses")

# ── Veri İşleme (Impact Engine) ───────────────────────────────────────────────
raw_camp_data = raw_age_data[raw_age_data['camp_id'] == sel_camp_id].copy()

if raw_camp_data.empty:
    st.warning("Seçilen kamp için veri yok.")
    st.stop()

if ses != "Tümü":
    raw_camp_data = raw_camp_data[raw_camp_data['tip'].str.upper() == ses]

# utils.py içindeki yenilenmiş objektif motoru çalıştır
camp_data = calculate_impact_score_engine(raw_camp_data)

if camp_data.empty:
    st.warning("Hesaplanabilir veri bulunamadı (dakikası 0 olan hatalı veriler filtrelenmiştir).")
    st.stop()

st.divider()

# ── TAB YAPISI ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 GÜNLÜK TAKIM SIRALAMASI",
    "📋 KAMP LİDERLERİ (TÜM KADRO)", 
    "📈 GEÇMİŞ KAMPLARA GÖRE GELİŞİM",
    "📉 KAMP İÇİ TREND"
])

# ── TAB 1: GÜNLÜK SIRALAMA (Full Kadro) ──────────────────────────────────────
with tab1:
    unique_dates = sorted(camp_data['tarih'].unique(), reverse=True)
    sel_date = st.selectbox("SEANS TARİHİ", unique_dates, format_func=lambda x: pd.to_datetime(x).strftime('%d.%m.%Y'), key="ia_daily_date")
    
    day_data = camp_data[camp_data['tarih'] == sel_date].sort_values('impact_score', ascending=False)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        section_title("TAKIM SIRALAMASI TABLOSU", "📋")
        display_cols = ['player_name', 'impact_score', 'status_tag', 'dist_25_plus', 'player_load', 'smax_kmh']
        show_df = day_data[display_cols].copy()
        show_df.columns = ['OYUNCU', 'IMPACT SKOR', 'İSTATİSTİKSEL DURUM', '25+ HIZ (m)', 'YÜK (Load)', 'MAX KM/H']
        show_df.index = np.arange(1, len(show_df) + 1)
        
        # Profesyonel kırmızı tonlamasıyla tüm oyuncuları basıyoruz
        st.dataframe(show_df.style.background_gradient(cmap='Reds', subset=['IMPACT SKOR'], vmin=20, vmax=90), 
                     use_container_width=True, height=600)
        
        render_export_buttons(df=show_df.reset_index(drop=True), key_prefix="ia_daily", filename=f"Gunluk_Impact_{sel_date}")
                     
    with col_b:
        section_title("İMPACT SKOR DAĞILIMI", "📊")
        # Profesyonel Plotly Bar Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=day_data['player_name'].str.upper(),
            x=day_data['impact_score'],
            orientation='h',
            marker=dict(
                color=day_data['impact_score'],
                colorscale='Reds',
                cmin=30, cmax=90,
                line=dict(color='rgba(0,0,0,0.1)', width=1)
            ),
            text=[f"{v:.1f}" for v in day_data['impact_score']],
            textposition='outside',
            textfont=dict(family="DM Sans", size=11, color=COLORS['GRAY_800'], weight="bold")
        ))
        fig.update_layout(
            template='plotly_white',
            height=max(600, len(day_data) * 25),
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(title="Impact Score (0-100)", gridcolor='#F3F4F6'),
            yaxis=dict(autorange="reversed", tickfont=dict(weight="bold", color=COLORS['GRAY_800']))
        )
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 2: KAMP LİDERLERİ (Full Kadro) ────────────────────────────────────────
with tab2:
    section_title("KAMP GENEL ORTALAMASI VE LİDERLİK TABLOSU", "🏆")
    st.markdown("<p style='color: gray; font-size: 13px;'>Kamp boyunca tüm oyuncuların günlük Impact skorlarının ve değişkenlerinin genel ortalaması alınarak oluşturulmuş objektif sıralamadır.</p>", unsafe_allow_html=True)
    
    camp_impact = camp_data.groupby('player_name').agg(
        avg_impact=('impact_score', 'mean'),
        avg_high_speed=('dist_25_plus_pm', 'mean'),
        avg_load=('player_load_pm', 'mean'),
        max_speed=('smax_kmh', 'max'),
        session_count=('tarih', 'count')
    ).reset_index().sort_values('avg_impact', ascending=False)
    
    camp_impact.index = np.arange(1, len(camp_impact) + 1)
    camp_impact.columns = ['OYUNCU', 'KAMP ORT. İMPACT', 'ORT. 25+ HIZ (m/dk)', 'ORT. YÜK (Load/dk)', 'KAMP MAX HIZ (km/h)', 'KATILDIĞI SEANS']
    
    st.dataframe(
        camp_impact.style.format(precision=1)\
            .background_gradient(cmap='Greys', subset=['KAMP ORT. İMPACT'], vmin=40, vmax=80)\
            .highlight_max(subset=['KAMP MAX HIZ (km/h)'], color='#fee2e2'),
        use_container_width=True, height=650
    )
    
    render_export_buttons(df=camp_impact.reset_index(drop=True), key_prefix="ia_camp", filename=f"Kamp_Liderleri_{sel_camp_label}")

# ── TAB 3: GELİŞİM ANALİZİ ────────────────────────────────────────────────────
with tab3:
    section_title("GEÇMİŞ KAMPLARA GÖRE BİREYSEL GELİŞİM", "📈")
    
    historical_raw = raw_age_data[raw_age_data['camp_id'] != sel_camp_id]
    
    if historical_raw.empty:
        st.info("Bu yaş grubu için veritabanında kıyaslama yapılacak geçmiş kamp verisi bulunmamaktadır.")
    else:
        players = sorted(camp_data['player_name'].unique())
        sel_player = st.selectbox("OYUNCU SEÇİNİZ", players, key="ia_dev_player")
        
        historical_processed = calculate_impact_score_engine(historical_raw)
        dev_stats = calculate_development_stats(camp_data, historical_processed)
        
        if sel_player in dev_stats.index:
            player_dev = dev_stats.loc[sel_player]
            
            # Kart tasarımı: Minimalist ve net veri gösterimi
            cols = st.columns(4)
            metrics_dict = {
                'impact_score': 'İMPACT SKOR DEĞİŞİMİ',
                'dist_25_plus_pm': 'YÜKSEK HIZLI KOŞU (25+)',
                'player_load_pm': 'MEKANİK YÜK (Load)',
                'total_distance_pm': 'TOPLAM MESAFE HACMİ'
            }
            
            for idx, (key, label) in enumerate(metrics_dict.items()):
                change = player_dev[key] if key in player_dev else np.nan
                color = COLORS['RED'] if change < 0 else COLORS['SUCCESS'] if change > 0 else COLORS['GRAY_500']
                arrow = "▼" if change < 0 else "▲" if change > 0 else "▬"
                
                with cols[idx]:
                    st.markdown(f"""
                    <div style="border: 1px solid #E5E7EB; border-radius: 6px; padding: 20px; background: white; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="font-size: 11px; color: #6B7280; font-weight: 800; letter-spacing: 1px;">{label}</div>
                        <div style="font-size: 32px; font-family: 'Bebas Neue'; color: {color}; margin-top: 5px;">
                            {arrow} {abs(change):.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Seçili oyuncunun geçmiş kamp verisi bulunmuyor.")

# ── TAB 4: TREND ANALİZİ ──────────────────────────────────────────────────────
with tab4:
    section_title("KAMP İÇİ ETKİ (IMPACT) TRENDİ", "📉")
    st.markdown("<p style='color: gray; font-size: 13px;'>Oyuncunun kampın ilk gününden son gününe kadar gösterdiği performans dalgalanması.</p>", unsafe_allow_html=True)
    
    sel_player_trend = st.selectbox("OYUNCU SEÇİNİZ", sorted(camp_data['player_name'].unique()), key="ia_trend_player")
    player_trend_data = camp_data[camp_data['player_name'] == sel_player_trend].sort_values('tarih')
    
    if len(player_trend_data) >= 2:
        daily_impact = player_trend_data[['tarih', 'impact_score']].copy()
        daily_impact['tarih_str'] = daily_impact['tarih'].dt.strftime('%d.%m')
        
        # Profesyonel Trend Grafiği (Spline Curve)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_impact['tarih_str'], y=daily_impact['impact_score'],
            mode='lines+markers',
            name='Impact Score',
            line=dict(color=COLORS['RED'], width=3, shape='spline'),
            marker=dict(size=10, color='white', line=dict(color=COLORS['RED'], width=2))
        ))
        
        # Ortalama Çizgisi
        mean_impact = daily_impact['impact_score'].mean()
        fig.add_hline(y=mean_impact, line_dash="dash", line_color=COLORS['GRAY_400'], 
                      annotation_text=f"Kamp Ortalaması: {mean_impact:.1f}",
                      annotation_position="top left",
                      annotation_font=dict(size=11, color=COLORS['GRAY_600']))
                      
        fig.update_layout(
            template="plotly_white", 
            height=450, 
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(title="Tarih", gridcolor='#F3F4F6', tickfont=dict(weight="bold")),
            yaxis=dict(title="Impact Score (0-100)", gridcolor='#F3F4F6')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend analizi grafiği çizebilmek için oyuncunun bu kampta en az 2 seans verisi gereklidir.")

st.markdown('<div class="tff-footer"><p>Türkiye Futbol Federasyonu · Performans Analiz Departmanı</p></div>', unsafe_allow_html=True)