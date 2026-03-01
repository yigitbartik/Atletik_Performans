import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import AGE_GROUPS, METRICS, RADAR_METRICS, PRIMARY_METRICS, DEFAULT_MINUTES
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box, COLORS
from utils import (render_export_buttons, plot_player_comparison,
                   plot_radar_comparison_multiple, plot_camp_comparison,
                   calculate_percentile_rank, calculate_composite_score,
                   percentile_color, PLAYER_PALETTE)

st.set_page_config(page_title="Karşılaştırma | TFF", layout="wide")
inject_styles()
page_header("⚔️", "KARŞILAŞTIRMA",
            "H2H (Kafa Kafaya) · Kamp Karşılaştırma · Çoklu Radar Analizi")

# ── Yaş Grubu Seçimi ──────────────────────────────────────────────────────────
age_group = st.selectbox("YAŞ GRUBU", AGE_GROUPS, key="cmp_age")

try:
    raw_age_data = db_manager.get_data_by_age_group(age_group)
    if raw_age_data.empty:
        st.warning(f"{age_group} için veri bulunamadı."); st.stop()

    players = db_manager.get_players(age_group)
    camps_df = db_manager.get_camps(age_group)
    camp_options = {row['camp_name']: row['camp_id'] for _, row in camps_df.iterrows()}

    if len(players) < 2:
        st.warning("Karşılaştırma yapmak için bu yaş grubunda en az 2 oyuncu bulunmalı."); st.stop()

    # ── Dakika Filtreleri (Veri Kirliliğini Önler) ───────────────────────────
    with st.expander("⚙️ DAKİKA VE VERİ FİLTRELERİ (Gelişmiş)", expanded=False):
        st.markdown("<div style='font-size:13px; color:#6B7280; margin-bottom:10px;'>Karşılaştırma adaletsizliğini önlemek için az süre alınan seansları filtreleyebilirsiniz.</div>", unsafe_allow_html=True)
        dk1, dk2 = st.columns(2)
        with dk1: min_train_dk = st.number_input("Minimum Antrenman Dakikası", value=DEFAULT_MINUTES['TRAINING'], step=5, key="cmp_dk_tr")
        with dk2: min_match_dk = st.number_input("Minimum Maç Dakikası", value=DEFAULT_MINUTES['MATCH'], step=5, key="cmp_dk_ma")

    def apply_minute_filter(df):
        if df.empty: return df
        is_tr = df['tip'].str.upper().str.contains('TRAINING')
        is_ma = df['tip'].str.upper().str.contains('MATCH')
        mask = (is_tr & (df['minutes'] >= min_train_dk)) | (is_ma & (df['minutes'] >= min_match_dk))
        return df[mask].copy()

    age_data = apply_minute_filter(raw_age_data)
    if age_data.empty:
        st.warning("Seçili dakika filtresine uygun veri kalmadı. Lütfen filtreyi düşürün."); st.stop()

    cmp_type = st.radio(
        "KARŞILAŞTIRMA TİPİ",
        ["👥 İKİ OYUNCU H2H", "🔁 KAMP KARŞILAŞTIRMA", "⚔️ ÇOKLU RADAR"],
        horizontal=True, key="cmp_type"
    )
    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # H2H (KAFA KAFAYA KARŞILAŞTIRMA)
    # ════════════════════════════════════════════════════════════════════════
    if cmp_type == "👥 İKİ OYUNCU H2H":
        section_title("İKİ OYUNCU H2H KARŞILAŞTIRMASI", "👥", tooltip="Seçilen iki oyuncunun aynı şartlar altındaki (aynı kamp, aynı seans tipi) performanslarını kafa kafaya kıyaslar.")
        
        c1, c2 = st.columns(2)
        with c1: p1 = st.selectbox("🔴 1. OYUNCU", players, key="cmp_p1")
        with c2: p2 = st.selectbox("⚫ 2. OYUNCU", players, index=min(1, len(players)-1), key="cmp_p2")

        if p1 == p2:
            st.warning("Lütfen farklı iki oyuncu seçin."); st.stop()

        f1, f2, f3 = st.columns(3)
        with f1: camp_filter = st.checkbox("Belirli bir kampa sınırla", key="cmp_cf")
        with f2: ses = st.radio("Seans Tipi", ["Tümü","TRAINING","MATCH"], horizontal=True, key="cmp_ses")
        with f3: show_team = st.checkbox("Takım ortalamasını grafikte göster", value=True, key="cmp_team")

        p1_raw = db_manager.get_data_by_player(p1)
        p2_raw = db_manager.get_data_by_player(p2)
        
        p1d = apply_minute_filter(p1_raw)
        p2d = apply_minute_filter(p2_raw)
        td  = age_data.copy()

        if camp_filter and camp_options:
            sc = st.selectbox("KAMP SEÇİMİ", list(camp_options.keys()), key="cmp_camp")
            sid = camp_options[sc]
            p1d = p1d[p1d['camp_id'] == sid]
            p2d = p2d[p2d['camp_id'] == sid]
            td  = td[td['camp_id'] == sid]

        if ses != "Tümü":
            p1d = p1d[p1d['tip'].str.upper() == ses]
            p2d = p2d[p2d['tip'].str.upper() == ses]
            td  = td[td['tip'].str.upper() == ses]

        if p1d.empty or p2d.empty:
            st.warning("Seçilen filtreler ve kamplar doğrultusunda bu iki oyuncunun ortak karşılaştırılabilecek verisi bulunamadı."); st.stop()

        # Bileşik skor
        s1 = calculate_composite_score(p1d, td)
        s2 = calculate_composite_score(p2d, td)

        # Fotoğraf ve Logoları Al
        p1_info = db_manager.get_player_info(p1)
        p2_info = db_manager.get_player_info(p2)
        p1_img = p1_info.get('photo_url') or "https://cdn-icons-png.flaticon.com/512/847/847969.png"
        p2_img = p2_info.get('photo_url') or "https://cdn-icons-png.flaticon.com/512/847/847969.png"

        # Özet header (Fotoğraflı)
        L, M, R = st.columns([5, 1, 5])
        def _player_box(name, color, score, img_url):
            c = percentile_color(score.get('composite', 50))
            bg = '#fff0f0' if color == COLORS['RED'] else '#f5f5f5'
            return f"""
            <div style="background:linear-gradient(135deg,{bg},white); border:2px solid {color}; border-radius:16px; padding:20px; text-align:center; position:relative; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                <img src="{img_url}" style="width:100px; height:100px; border-radius:50%; object-fit:cover; border:3px solid {color}; margin-bottom:10px; background:white;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:26px; letter-spacing:1.5px; color:{color}; line-height:1;">{name.upper()}</div>
                <div style="font-size:11px;color:#9CA3AF;margin:6px 0 10px; font-weight:bold; text-transform:uppercase;">Bileşik Skorlama</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;color:{c};line-height:1;">
                    {score.get('composite',0):.0f}%
                </div>
            </div>"""

        with L:
            st.markdown(_player_box(p1, COLORS['RED'], s1, p1_img), unsafe_allow_html=True)
            st.write("")
            c_L1, c_L2 = st.columns(2)
            with c_L1: st.markdown(f"<div class='metric-card' style='padding:10px;'><div class='sc-label'>GEÇERLİ SEANS</div><div class='sc-val' style='font-size:22px;'>{len(p1d)}</div></div>", unsafe_allow_html=True)
            with c_L2: st.markdown(f"<div class='metric-card' style='padding:10px;'><div class='sc-label'>ORT. MESAFE</div><div class='sc-val' style='font-size:22px;'>{p1d['total_distance'].mean():.0f} <span style='font-size:10px;color:#9CA3AF;'>m</span></div></div>", unsafe_allow_html=True)

        with M:
            st.markdown("""
            <div style="text-align:center;padding-top:70px;font-family:'Bebas Neue',sans-serif;
                        font-size:42px;font-weight:900;color:#D1D5DB;letter-spacing:2px;">VS</div>
            """, unsafe_allow_html=True)

        with R:
            st.markdown(_player_box(p2, COLORS['BLACK'], s2, p2_img), unsafe_allow_html=True)
            st.write("")
            c_R1, c_R2 = st.columns(2)
            with c_R1: st.markdown(f"<div class='metric-card' style='padding:10px;'><div class='sc-label'>GEÇERLİ SEANS</div><div class='sc-val' style='font-size:22px;'>{len(p2d)}</div></div>", unsafe_allow_html=True)
            with c_R2: st.markdown(f"<div class='metric-card' style='padding:10px;'><div class='sc-label'>ORT. MESAFE</div><div class='sc-val' style='font-size:22px;'>{p2d['total_distance'].mean():.0f} <span style='font-size:10px;color:#9CA3AF;'>m</span></div></div>", unsafe_allow_html=True)

        st.divider()

        # Percentile karşılaştırma barları
        section_title("SKORLAMA (PERCENTILE) KARŞILAŞTIRMASI", "📊")
        pct_m = [m for m in PRIMARY_METRICS if m in p1d.columns and m in p2d.columns
                 and p1d[m].dropna().any() and p2d[m].dropna().any()]
        labels = [METRICS.get(m,{}).get('display',m).upper() for m in pct_m]
        v1 = [s1.get(m, 50) for m in pct_m]
        v2 = [s2.get(m, 50) for m in pct_m]

        fig_pct = go.Figure()
        fig_pct.add_trace(go.Bar(
            name=p1.upper(), x=labels, y=v1,
            marker=dict(color=COLORS['RED'], opacity=0.9),
            text=[f"%{v:.0f}" for v in v1], textposition='outside',
            textfont=dict(family='DM Sans', size=11, weight='bold'),
        ))
        fig_pct.add_trace(go.Bar(
            name=p2.upper(), x=labels, y=v2,
            marker=dict(color=COLORS['BLACK'], opacity=0.9),
            text=[f"%{v:.0f}" for v in v2], textposition='outside',
            textfont=dict(family='DM Sans', size=11, weight='bold'),
        ))
        fig_pct.add_hline(y=50, line_dash='dash', line_color=COLORS['GRAY_500'],
                           annotation_text="TAKIM MEDYANI",
                           annotation_font=dict(size=10, color=COLORS['GRAY_600'], weight='bold'))
        fig_pct.update_layout(
            barmode='group', height=450,
            xaxis=dict(tickangle=-20, tickfont=dict(family='DM Sans', size=11, weight='bold')),
            yaxis=dict(title='Skor (%)', range=[0, 120], gridcolor='#F3F4F6'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(weight='bold')),
            plot_bgcolor='#FAFAFA', paper_bgcolor=COLORS['WHITE'],
            margin=dict(t=40),
        )
        st.plotly_chart(fig_pct, use_container_width=True)

        st.divider()
        section_title("GÖRSEL METRİK KARŞILAŞTIRMASI", "📈")
        avail = [m for m in PRIMARY_METRICS if m in p1d.columns and
                 p1d[m].notna().any() and p2d[m].notna().any()]
        cols = st.columns(2)
        for idx, metric in enumerate(avail):
            with cols[idx % 2]:
                fig = plot_player_comparison(p1d, p2d, metric,
                                             td if show_team else None, p1, p2)
                st.plotly_chart(fig, use_container_width=True)

        st.divider()
        section_title("DETAYLI İSTATİSTİK VE FARK TABLOSU", "📋", tooltip="Yeşil daireler o metrikte kimin daha yüksek ortalamaya sahip olduğunu gösterir.")
        
        rows = []
        for m in avail:
            p1v = p1d[m].mean(); p2v = p2d[m].mean()
            tv  = td[m].mean()  if not td.empty else 0
            mi  = METRICS.get(m, {})
            
            # Renkli ok ve sembol mantığı
            if p1v > p2v:
                p1_str = f"🟢 {p1v:.1f}"
                p2_str = f"🔴 {p2v:.1f}"
            elif p2v > p1v:
                p1_str = f"🔴 {p1v:.1f}"
                p2_str = f"🟢 {p2v:.1f}"
            else:
                p1_str = f"⚪ {p1v:.1f}"
                p2_str = f"⚪ {p2v:.1f}"

            rows.append({
                'METRİK': mi.get('display', m).upper(), 
                'BİRİM': mi.get('unit',''),
                f"{p1.upper()} (ORT)": p1_str,
                f'{p1.upper()} SKOR': f"%{s1.get(m,0):.0f}",
                f"{p2.upper()} (ORT)": p2_str,
                f'{p2.upper()} SKOR': f"%{s2.get(m,0):.0f}",
                'TAKIM ORT.': f"{tv:.1f}",
            })
        df_tbl = pd.DataFrame(rows)
        st.dataframe(df_tbl, use_container_width=True, hide_index=True)
        render_export_buttons(df=df_tbl, key_prefix="cmp_tbl",
                              filename=f"h2h_{p1}_vs_{p2}")

    # ════════════════════════════════════════════════════════════════════════
    # KAMP KARŞILAŞTIRMA
    # ════════════════════════════════════════════════════════════════════════
    elif cmp_type == "🔁 KAMP KARŞILAŞTIRMA":
        section_title("KAMP KARŞILAŞTIRMASI", "🔁")
        info_box("İki farklı kampı seçerek takımın veya oyuncuların kamp bazındaki performanslarını karşılaştırın.")

        if len(camp_options) < 2:
            st.warning("Karşılaştırma için en az 2 kamp gerekli."); st.stop()

        k1, k2, k3 = st.columns(3)
        with k1: camp1_name = st.selectbox("1. KAMP", list(camp_options.keys()), key="kc_k1")
        with k2: camp2_name = st.selectbox("2. KAMP", list(camp_options.keys()), index=min(1, len(camp_options)-1), key="kc_k2")
        with k3: ses = st.radio("SEANS TİPİ", ["Tümü","TRAINING","MATCH"], horizontal=True, key="kc_ses")

        if camp1_name == camp2_name:
            st.warning("Farklı iki kamp seçin."); st.stop()

        c1_id = camp_options[camp1_name]
        c2_id = camp_options[camp2_name]
        
        c1d_raw = db_manager.get_data_by_camp(c1_id)
        c2d_raw = db_manager.get_data_by_camp(c2_id)
        
        c1d = apply_minute_filter(c1d_raw)
        c2d = apply_minute_filter(c2d_raw)

        if ses != "Tümü":
            c1d = c1d[c1d['tip'].str.upper() == ses]
            c2d = c2d[c2d['tip'].str.upper() == ses]

        # Kamp özeti
        kk1, kk2 = st.columns(2)
        with kk1:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#fff0f0,white);
                        border:2px solid {COLORS['RED']};border-radius:16px;
                        padding:25px;text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                            letter-spacing:2px;color:{COLORS['RED']};">
                    🔴 {camp1_name.upper()}
                </div>
                <div style="font-size:14px;color:{COLORS['GRAY_700']};margin-top:10px; font-weight:bold;">
                    {c1d['player_name'].nunique()} OYUNCU &nbsp;·&nbsp; {c1d['tarih'].nunique()} GÜN
                </div>
            </div>""", unsafe_allow_html=True)
        with kk2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#f5f5f5,white);
                        border:2px solid {COLORS['BLACK']};border-radius:16px;
                        padding:25px;text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                            letter-spacing:2px;color:{COLORS['BLACK']};">
                    ⚫ {camp2_name.upper()}
                </div>
                <div style="font-size:14px;color:{COLORS['GRAY_700']};margin-top:10px; font-weight:bold;">
                    {c2d['player_name'].nunique()} OYUNCU &nbsp;·&nbsp; {c2d['tarih'].nunique()} GÜN
                </div>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # Metrik seçimi ve grafik
        kc_avail = [m for m in PRIMARY_METRICS if m in c1d.columns and m in c2d.columns
                    and c1d[m].dropna().any() and c2d[m].dropna().any()]
        
        kc_metric = st.selectbox("METRİK SEÇİMİ", kc_avail,
                                  format_func=lambda x: METRICS.get(x,{}).get('display',x).upper(),
                                  key="kc_metric")

        fig_kc = plot_camp_comparison(c1d, c2d, kc_metric, camp1_name, camp2_name)
        st.plotly_chart(fig_kc, use_container_width=True)

        # Karşılaştırma tablosu
        section_title("KAMP ÖZET TABLOSU", "📋")
        avail_m_kc = [m for m in PRIMARY_METRICS if m in c1d.columns and c1d[m].dropna().any()]
        rows = []
        for m in avail_m_kc:
            mi = METRICS.get(m, {'display':m, 'unit':''})
            v1 = c1d[m].mean(); v2 = c2d[m].mean()
            diff = v2 - v1 if (not pd.isna(v1) and not pd.isna(v2)) else None
            rows.append({
                'METRİK':       mi['display'].upper(),
                'BİRİM':        mi['unit'],
                camp1_name.upper(): f"{v1:.2f}" if not pd.isna(v1) else '—',
                camp2_name.upper(): f"{v2:.2f}" if not pd.isna(v2) else '—',
                'FARK':         f"+{diff:.2f}" if (diff and diff>0) else (f"{diff:.2f}" if diff else '—'),
                'DURUM':        '📈 ARTIŞ' if (diff and diff>0) else ('📉 DÜŞÜŞ' if (diff and diff<0) else '➡️ SABİT'),
            })
        kc_df = pd.DataFrame(rows)
        st.dataframe(kc_df, use_container_width=True, hide_index=True)
        render_export_buttons(fig=fig_kc, df=kc_df, key_prefix="kc",
                              filename=f"kamp_{camp1_name}_vs_{camp2_name}")

    # ════════════════════════════════════════════════════════════════════════
    # ÇOKLU RADAR
    # ════════════════════════════════════════════════════════════════════════
    else:
        section_title("ÇOKLU OYUNCU RADAR ANALİZİ", "⚔️")
        sel_players = st.multiselect(
            "OYUNCULAR (2–6 Seçim Yapabilirsiniz)", players,
            default=players[:min(2, len(players))], key="cmp_multi"
        )
        if len(sel_players) < 2:
            st.warning("En az 2 oyuncu seçin."); st.stop()
        if len(sel_players) > 6:
            st.warning("Grafiğin anlaşılabilir olması için en fazla 6 oyuncu seçebilirsiniz."); st.stop()

        r1, r2 = st.columns(2)
        with r1: ses = st.radio("SEANS TİPİ", ["Tümü","TRAINING","MATCH"], horizontal=True, key="cmp_rses")
        with r2: camp_filter_r = st.checkbox("Belirli bir kampa sınırla", key="cmp_rcf")

        td = age_data if ses == "Tümü" else age_data[age_data['tip'].str.upper() == ses]

        if camp_filter_r and camp_options:
            rsc = st.selectbox("KAMP SEÇİMİ", list(camp_options.keys()), key="cmp_rcamp")
            rsid = camp_options[rsc]
            td = td[td['camp_id'] == rsid]

        pd_dict = {}
        for p in sel_players:
            pdata_raw = db_manager.get_data_by_player(p)
            pdata = apply_minute_filter(pdata_raw)
            if ses != "Tümü":
                pdata = pdata[pdata['tip'].str.upper() == ses]
            if camp_filter_r and camp_options:
                pdata = pdata[pdata['camp_id'] == rsid]
            pd_dict[p] = pdata

        if td.empty:
            st.warning("Seçilen filtreler için takım verisi yok."); st.stop()

        fig_r = plot_radar_comparison_multiple(pd_dict, td)
        st.plotly_chart(fig_r, use_container_width=True)
        render_export_buttons(fig=fig_r, key_prefix="cmp_radar", filename="radar_karsilastirma")

        st.markdown("""
        <div style="text-align:center;font-size:12px;color:#9CA3AF;margin-top:8px; font-weight:bold;">
            📌 İndeks = (Oyuncu Ort. / Takım Max) × 100 &nbsp;|&nbsp; Merkezden uzaklaştıkça performans artar.
        </div>""", unsafe_allow_html=True)

        st.divider()
        section_title("ÇOKLU PERCENTILE (SKOR) TABLOSU", "📊")
        pct_rows = []
        for p in sel_players:
            pdata = pd_dict[p]
            sc = calculate_composite_score(pdata, td)
            row = {'OYUNCU': p.upper()}
            for m in PRIMARY_METRICS:
                if m in pdata.columns and pdata[m].dropna().any():
                    mi = METRICS.get(m, {})
                    row[mi.get('display', m).upper()] = f"%{sc.get(m, 50):.0f}"
            row['BİLEŞİK SKOR'] = f"%{sc.get('composite', 50):.0f}"
            pct_rows.append(row)
        pct_df = pd.DataFrame(pct_rows)
        st.dataframe(pct_df, use_container_width=True, hide_index=True)
        render_export_buttons(df=pct_df, key_prefix="cmp_ptbl", filename="coklu_percentile")

        st.divider()
        section_title("DETAYLI METRİK TABLOSU", "📋")
        avail = [m for m in PRIMARY_METRICS if m in td.columns and td[m].notna().any()]
        rows = []
        for p in sel_players:
            pdata = pd_dict[p]
            for m in avail:
                pv = pdata[m].mean() if pdata[m].notna().any() else 0
                tv = td[m].mean()    if td[m].notna().any()    else 0
                rows.append({
                    'OYUNCU': p.upper(),
                    'METRİK': METRICS.get(m,{}).get('display',m).upper(),
                    'OYUNCU ORT.': f"{pv:.1f}",
                    'TAKIM ORT.':  f"{tv:.1f}",
                    'PERFORMANS İNDEKSİ': f"%{pv/tv*100:.0f}" if tv>0 else '—',
                })
        tbl = pd.DataFrame(rows)
        st.dataframe(tbl, use_container_width=True, hide_index=True)
        render_export_buttons(df=tbl, key_prefix="cmp_mtbl", filename="coklu_karsilastirma")

except Exception as e:
    st.error(f"❌ Hata: {str(e)}")
    import traceback; st.code(traceback.format_exc())

st.markdown('<div class="tff-footer"><p>Türkiye Futbol Federasyonu · Karşılaştırma Analizi</p></div>', unsafe_allow_html=True)