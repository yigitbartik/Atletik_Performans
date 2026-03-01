import streamlit as st
import pandas as pd
from config import AGE_GROUPS
from database import db_manager
from styles import inject_styles, sidebar_brand, section_title, page_header, COLORS

st.set_page_config(
    page_title="TFF Performans Sistemi",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    st.markdown('<div class="sidebar-label">📂 Veri Yükle</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Excel Dosyası Yükle", type=['xlsx'], label_visibility='collapsed')
    if uploaded_file:
        age_group = st.selectbox("Yaş Grubu", AGE_GROUPS, key="upload_age")
        if st.button("Veritabanına Aktar", use_container_width=True):
            with st.spinner("Yükleniyor..."):
                result = db_manager.excel_to_db(uploaded_file, age_group)
                if result['status'] == 'success':
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
    st.divider()
    st.markdown('<div class="sidebar-label">📊 Sistem Özeti</div>', unsafe_allow_html=True)
    try:
        all_data = db_manager.get_all_data()
        if not all_data.empty:
            c1, c2 = st.columns(2)
            match_data = all_data[all_data['tip'].str.upper()=='MATCH']
            with c1:
                st.metric("Oyuncu", all_data['player_name'].nunique())
                st.metric("Kayıt",  len(all_data))
            with c2:
                st.metric("Kamp",   all_data['camp_id'].nunique())
                # Satır sayısını değil, benzersiz maç gününü sayıyoruz
                st.metric("Maç Günü", match_data['tarih'].nunique() if not match_data.empty else 0)
    except:
        pass

# ── Header ────────────────────────────────────────────────────────────────────
page_header("⚽", "TFF Performans Sistemi",
            "Türkiye Futbol Federasyonu · Genç Milli Takımlar Atletik Veri Platformu")

# ── Nav Kartları ──────────────────────────────────────────────────────────────
nav_items = [
    ("02_Kamp_Analizi.py",   "⚽", "Kamp Analizi",    "Günlük & kamp bazlı sıralamalar"),
    ("03_Oyuncu_Profili.py", "🏃", "Oyuncu Profili",  "Bireysel performans & radar"),
    ("04_Karsilastirma.py",  "⚔️", "Karşılaştırma",   "H2H · Gün · Kamp karşılaştırma"),
    ("05_Siralamalar.py",    "📊", "Sıralamalar",      "Günlük · Kamp · Percentile skor"),
    ("06_Scatter.py",        "🎯", "Scatter Analizi",  "İki metrik bazlı oyuncu dağılımı"),
]

cols = st.columns(5)
for i, (page, icon, title, desc) in enumerate(nav_items):
    with cols[i]:
        active = (i == 0)
        border = COLORS['RED'] if active else COLORS['GRAY_300']
        shadow = "0 4px 16px rgba(227,10,23,0.15)" if active else "0 1px 4px rgba(0,0,0,0.05)"
        st.markdown(f"""
        <div style="background:white;border:2px solid {border};border-radius:14px;
                    padding:20px 14px 14px;text-align:center;box-shadow:{shadow};
                    height:120px;transition:all 0.2s;">
            <div style="font-size:24px;margin-bottom:8px;">{icon}</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:1.5px;
                        color:{COLORS['GRAY_900']};">{title}</div>
            <div style="font-size:10px;color:{COLORS['GRAY_400']};margin-top:4px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Git →", key=f"nav_{i}", use_container_width=True):
            st.switch_page(f"pages/{page}")

st.divider()

# ── Ana İçerik ────────────────────────────────────────────────────────────────
try:
    all_data = db_manager.get_all_data()
    if not all_data.empty:
        # Yaş grubu kartları
        section_title("Yaş Grubu Durumu", "📈")
        ag_cols = st.columns(len(AGE_GROUPS))
        for i, ag in enumerate(AGE_GROUPS):
            ag_data = all_data[all_data['age_group'] == ag]
            has = not ag_data.empty
            with ag_cols[i]:
                pc = ag_data['player_name'].nunique() if has else 0
                cc = ag_data['camp_id'].nunique()     if has else 0
                rc = len(ag_data)                     if has else 0
                cls = "ag-card has-data" if has else "ag-card no-data"
                st.markdown(f"""
                <div class="{cls}">
                    <div class="ag-label">{ag}</div>
                    <div class="ag-stat"><b>{pc}</b> Oyuncu · <b>{cc}</b> Kamp</div>
                    <div class="ag-stat" style="font-size:11px;color:{COLORS['GRAY_400']};margin-top:4px;">
                        {rc} kayıt
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # KPI satırı
        section_title("Genel İstatistikler", "📊")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        match_df = all_data[all_data['tip'].str.upper()=='MATCH']
        with k1: st.metric("Toplam Oyuncu",   all_data['player_name'].nunique())
        with k2: st.metric("Toplam Kamp",     all_data['camp_id'].nunique())
        with k3: st.metric("Toplam Kayıt",    len(all_data))
        with k4: st.metric("Toplam Maç Günü", match_df['tarih'].nunique() if not match_df.empty else 0)
        with k5: st.metric("Ort. Mesafe",     f"{all_data['total_distance'].mean():.0f} m")
        with k6: st.metric("Max Hız (Genel)", f"{all_data['smax_kmh'].max():.1f} km/h")

        st.divider()

        # Top 10
        section_title("En Yüksek 10 Mesafe Performansı", "🏆")
        top10 = all_data.nlargest(10, 'total_distance')[
            ['player_name','age_group','tarih','tip','total_distance','smax_kmh','player_load']
        ].copy()
        top10['tarih'] = top10['tarih'].dt.strftime('%d.%m.%Y')
        top10.columns  = ['Oyuncu','Yaş Gr.','Tarih','Tip','Mesafe (m)','Max Hız (km/h)','Pl. Load']
        st.dataframe(top10, use_container_width=True, hide_index=True)

    else:
        st.markdown(f"""
        <div style="text-align:center;padding:80px 20px;background:{COLORS['GRAY_50']};
                    border-radius:16px;border:2px dashed {COLORS['GRAY_300']};margin-top:20px;">
            <div style="font-size:52px;margin-bottom:16px;">📂</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:2px;
                        color:{COLORS['GRAY_700']};">HENÜZ VERİ YÜKLENMEDİ</div>
            <div style="font-size:13px;color:{COLORS['GRAY_400']};margin-top:8px;">
                Sol panelden Excel dosyanızı yükleyerek sistemi başlatın</div>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Hata: {e}")

st.markdown("""
<div class="tff-footer">
    <p><strong>Türkiye Futbol Federasyonu</strong> · Genç Milli Takımlar Atletik Performans Sistemi</p>
    <p>© 2026 TFF · Tüm hakları saklıdır</p>
</div>""", unsafe_allow_html=True)