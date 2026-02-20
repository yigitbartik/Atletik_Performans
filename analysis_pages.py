"""
ATLETİK PERFORMANS SİSTEMİ - AŞAMA 2
Analiz & Vizüalizasyon Modülü
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
from scipy import stats

class AnalysisEngine:
    """Analiz ve sıralama işlemleri"""
    
    def __init__(self, db_path="athletic_performance.db"):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    # ========== VERİ FETCHING ==========
    def get_camp_players_data(self, kamp_id, metrik, tip="Training"):
        """Kamp oyuncularının belirli metrik verilerini getir"""
        conn = self.get_connection()
        query = '''
            SELECT 
                p.oyuncu_id,
                p.ad_soyad,
                p.pozisyon,
                p.kulup,
                t.''' + metrik + ''' as metrik_value,
                t.minutes,
                t.tarih,
                t.tip
            FROM training_match_data t
            JOIN player_info p ON t.oyuncu_id = p.oyuncu_id
            WHERE t.kamp_id = ?
        '''
        
        if tip != "Tümü":
            query += f" AND t.tip = '{tip}'"
        
        query += " ORDER BY t." + metrik + " DESC"
        
        df = pd.read_sql_query(query, conn, params=[kamp_id])
        conn.close()
        return df
    
    def get_player_profile_data(self, oyuncu_id, metrik):
        """Oyuncunun tüm kamplarındaki performansını getir"""
        conn = self.get_connection()
        query = '''
            SELECT 
                c.kamp_id,
                c.kamp_adi,
                c.baslangic_tarihi,
                c.yas_grubu,
                t.''' + metrik + ''' as metrik_value,
                t.minutes,
                t.tarih,
                t.tip,
                t.total_distance,
                t.smax_kmh,
                t.player_load
            FROM training_match_data t
            JOIN camp_info c ON t.kamp_id = c.kamp_id
            WHERE t.oyuncu_id = ?
            ORDER BY t.tarih
        '''
        
        df = pd.read_sql_query(query, conn, params=[oyuncu_id])
        conn.close()
        return df
    
    def get_age_group_data(self, yas_grubu, kamp_id, metrik, tip="Training"):
        """Yaş grubunun oyuncularının verilerini getir"""
        conn = self.get_connection()
        query = '''
            SELECT 
                p.oyuncu_id,
                p.ad_soyad,
                p.pozisyon,
                t.''' + metrik + ''' as metrik_value,
                t.minutes,
                t.smax_kmh,
                t.total_distance,
                t.player_load,
                t.tarih
            FROM training_match_data t
            JOIN player_info p ON t.oyuncu_id = p.oyuncu_id
            WHERE p.yaas_grubu = ? AND t.kamp_id = ?
        '''
        
        if tip != "Tümü":
            query += f" AND t.tip = '{tip}'"
        
        df = pd.read_sql_query(query, conn, params=[yas_grubu, kamp_id])
        conn.close()
        return df
    
    def calculate_team_stats(self, kamp_id, metrik, tip="Training"):
        """Takım istatistiklerini hesapla"""
        df = self.get_camp_players_data(kamp_id, metrik, tip)
        
        if df.empty:
            return None
        
        return {
            'mean': df['metrik_value'].mean(),
            'median': df['metrik_value'].median(),
            'std': df['metrik_value'].std(),
            'min': df['metrik_value'].min(),
            'max': df['metrik_value'].max(),
            'q1': df['metrik_value'].quantile(0.25),
            'q3': df['metrik_value'].quantile(0.75)
        }
    
    def calculate_percentiles(self, df, metrik_col):
        """Percentile hesapla"""
        return df[metrik_col].rank(pct=True) * 100

# ============================================================
# SAYFA 1: OYUNCU KARŞILAŞTIRMASI
# ============================================================

def page_player_comparison(dm, ae):
    """Oyuncu Karşılaştırması Sayfası"""
    
    st.markdown('<h2 class="section-header">⚽ Oyuncu Karşılaştırması</h2>', unsafe_allow_html=True)
    
    col_filters = st.columns(4)
    
    with col_filters[0]:
        camps = dm.get_all_camps()
        if camps.empty:
            st.error("Kamp yok!")
            return
        
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps['kamp_id'].values,
            format_func=lambda x: camps[camps['kamp_id']==x]['kamp_adi'].values[0]
        )
    
    with col_filters[1]:
        metrik = st.selectbox(
            "Metrik Seçiniz",
            ['total_distance', 'smax_kmh', 'player_load', 'dist_gt_25', 
             'n_gt_25', 'dist_20_25', 'n_20_25', 'amp', 'metrage', 'minutes'],
            format_func=lambda x: {
                'total_distance': '📏 Total Distance',
                'smax_kmh': '⚡ Max Speed',
                'player_load': '💪 Player Load',
                'dist_gt_25': '🔥 Dist > 25',
                'n_gt_25': '💨 N > 25',
                'dist_20_25': '📊 Dist 20-25',
                'n_20_25': '🏃 N 20-25',
                'amp': '📈 AMP',
                'metrage': '📐 Metrage',
                'minutes': '⏱️ Minutes'
            }.get(x, x)
        )
    
    with col_filters[2]:
        tip = st.selectbox("Tip", ["Training", "Match", "Tümü"])
    
    with col_filters[3]:
        min_dakika = st.slider("Min Dakika", 0, 120, 10)
    
    # Veri getir
    df = ae.get_camp_players_data(selected_camp, metrik, tip)
    
    if df.empty:
        st.warning("Veri yok!")
        return
    
    # Filtrele
    df = df[df['minutes'] >= min_dakika].copy()
    
    if df.empty:
        st.warning(f"Minimum {min_dakika} dakika kriterine uygun veri yok!")
        return
    
    # Takım istatistikleri
    team_stats = ae.calculate_team_stats(selected_camp, metrik, tip)
    
    # Sıralama ve percentile
    df['rank'] = df['metrik_value'].rank(ascending=False).astype(int)
    df['percentile'] = ae.calculate_percentiles(df, 'metrik_value')
    
    st.markdown("---")
    
    # TAB 1: BAR CHART (Sıralanmış)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Bar Chart", "🎯 Scatter Plot", "📋 Tablo", "📈 İstatistikler"])
    
    with tab1:
        # Renkler: Sıralamaya göre
        colors = ['#D32F2F' if rank <= 3 else '#FFC107' if rank <= 5 else '#4CAF50' 
                  for rank in df['rank']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['ad_soyad'],
            y=df['metrik_value'],
            marker=dict(color=colors),
            text=df['rank'].astype(str),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Değer: %{y:.2f}<extra></extra>'
        ))
        
        # Team average çizgisi
        if team_stats:
            fig.add_hline(
                y=team_stats['mean'],
                line_dash="dash",
                line_color="gray",
                annotation_text=f"Takım Ort.: {team_stats['mean']:.2f}",
                annotation_position="right"
            )
        
        fig.update_layout(
            title=f"<b>{metrik.upper()}</b> - Sıralı Performans",
            xaxis_title="Oyuncu",
            yaxis_title="Değer",
            hovermode='x unified',
            height=500,
            template="plotly_white",
            font=dict(family="Arial", size=11),
            plot_bgcolor='rgba(240,240,240,0.5)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Scatter: Total Distance vs Speed
        fig = px.scatter(
            df,
            x='total_distance',
            y='smax_kmh',
            size='player_load',
            color='pozisyon',
            hover_name='ad_soyad',
            hover_data={'total_distance': ':.0f', 'smax_kmh': ':.1f', 'player_load': ':.1f'},
            color_discrete_map={'Savunma': '#003366', 'Orta Saha': '#FFC107', 'Hücum': '#D32F2F'},
            title="<b>Mesafe vs Hız</b> (Boyut: Player Load)",
            labels={'total_distance': 'Total Distance (m)', 'smax_kmh': 'Max Speed (km/h)', 'pozisyon': 'Konum'}
        )
        
        fig.update_traces(marker=dict(size=12, opacity=0.7))
        fig.update_layout(height=500, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Tablo
        display_df = df[['rank', 'ad_soyad', 'pozisyon', 'kulup', 'metrik_value', 'minutes', 'percentile']].copy()
        display_df.columns = ['Sırası', 'Oyuncu', 'Konum', 'Kulüp', 'Değer', 'Dakika', '%tile']
        display_df = display_df.sort_values('Sırası')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab4:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        if team_stats:
            with col1:
                st.metric("Takım Ort.", f"{team_stats['mean']:.2f}")
            with col2:
                st.metric("Median", f"{team_stats['median']:.2f}")
            with col3:
                st.metric("Min", f"{team_stats['min']:.2f}")
            with col4:
                st.metric("Max", f"{team_stats['max']:.2f}")
            with col5:
                st.metric("Std Dev", f"{team_stats['std']:.2f}")
        
        # Box Plot
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=df['metrik_value'],
            name=metrik,
            boxmean='sd',
            marker_color='#003366'
        ))
        
        fig.update_layout(
            title="<b>Dağılım Analizi</b>",
            yaxis_title="Değer",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SAYFA 2: OYUNCU PROFİLİ
# ============================================================

def page_player_profile(dm, ae):
    """Oyuncu Profili Sayfası"""
    
    st.markdown('<h2 class="section-header">👤 Oyuncu Profili</h2>', unsafe_allow_html=True)
    
    # Oyuncu seç
    players = dm.get_all_players()
    if players.empty:
        st.error("Oyuncu yok!")
        return
    
    selected_player = st.selectbox(
        "Oyuncu Seçiniz",
        players['oyuncu_id'].values,
        format_func=lambda x: players[players['oyuncu_id']==x]['ad_soyad'].values[0]
    )
    
    oyuncu_id = selected_player
    oyuncu_adi = players[players['oyuncu_id']==oyuncu_id]['ad_soyad'].values[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        metrik = st.selectbox(
            "Metrik Seçiniz",
            ['total_distance', 'smax_kmh', 'player_load', 'dist_gt_25', 'n_gt_25'],
            format_func=lambda x: {
                'total_distance': '📏 Total Distance',
                'smax_kmh': '⚡ Max Speed',
                'player_load': '💪 Player Load',
                'dist_gt_25': '🔥 Dist > 25',
                'n_gt_25': '💨 N > 25'
            }.get(x, x)
        )
    
    with col2:
        tip = st.selectbox("Tip", ["Training", "Match", "Tümü"])
    
    # Oyuncu profili veri
    profile_data = ae.get_player_profile_data(oyuncu_id, metrik)
    
    if profile_data.empty:
        st.warning("Bu oyuncu için veri yok!")
        return
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📈 Zaman Serisi", "📋 Antrenman Kayıtları", "📊 İstatistikler"])
    
    with tab1:
        # Zaman serisi grafik
        profile_data['tarih'] = pd.to_datetime(profile_data['tarih'])
        profile_data = profile_data.sort_values('tarih')
        
        fig = go.Figure()
        
        # Oyuncu verisi
        fig.add_trace(go.Scatter(
            x=profile_data['tarih'],
            y=profile_data['metrik_value'],
            name=oyuncu_adi,
            mode='lines+markers',
            line=dict(color='#D32F2F', width=3),
            marker=dict(size=8)
        ))
        
        # Trend çizgisi
        z = np.polyfit(range(len(profile_data)), profile_data['metrik_value'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=profile_data['tarih'],
            y=p(range(len(profile_data))),
            name="Trend",
            mode='lines',
            line=dict(color='rgba(211,47,47,0.3)', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title=f"<b>{oyuncu_adi}</b> - {metrik} Gelişimi",
            xaxis_title="Tarih",
            yaxis_title="Değer",
            hovermode='x unified',
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Antrenman kayıtları
        records = profile_data[['tarih', 'tip', 'minutes', 'kamp_adi', 'metrik_value', 'total_distance', 'smax_kmh']].copy()
        records.columns = ['Tarih', 'Tip', 'Dakika', 'Kamp', 'Metrik', 'Mesafe (m)', 'Max Speed']
        records['Tarih'] = pd.to_datetime(records['Tarih']).dt.strftime('%d.%m.%Y')
        
        st.dataframe(records, use_container_width=True, hide_index=True)
    
    with tab3:
        # İstatistikler
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ort. Değer", f"{profile_data['metrik_value'].mean():.2f}")
        with col2:
            st.metric("Max", f"{profile_data['metrik_value'].max():.2f}")
        with col3:
            st.metric("Min", f"{profile_data['metrik_value'].min():.2f}")
        with col4:
            st.metric("Std Dev", f"{profile_data['metrik_value'].std():.2f}")
        
        st.markdown("---")
        
        # Kamp özetleri
        st.subheader("📍 Kamp Özetleri")
        camp_summary = profile_data.groupby('kamp_adi').agg({
            'metrik_value': ['mean', 'max', 'min'],
            'minutes': 'sum',
            'tarih': 'count'
        }).round(2)
        
        camp_summary.columns = ['Ort.', 'Max', 'Min', 'Toplam Dakika', 'Seanslar']
        st.dataframe(camp_summary)

# ============================================================
# SAYFA 3: YAŞ GRUBU ANALİZİ
# ============================================================

def page_age_group_analysis(dm, ae):
    """Yaş Grubu Analizi Sayfası"""
    
    st.markdown('<h2 class="section-header">👥 Yaş Grubu Analizi</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        yas_grubu = st.selectbox("Yaş Grubu", ["U15", "U16", "U17", "U19", "U20", "U21"])
    
    with col2:
        camps = dm.get_all_camps()
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps['kamp_id'].values,
            format_func=lambda x: camps[camps['kamp_id']==x]['kamp_adi'].values[0]
        )
    
    with col3:
        metrik = st.selectbox(
            "Metrik",
            ['total_distance', 'smax_kmh', 'player_load'],
            format_func=lambda x: {
                'total_distance': '📏 Total Distance',
                'smax_kmh': '⚡ Max Speed',
                'player_load': '💪 Player Load'
            }.get(x, x)
        )
    
    # Veri getir
    age_data = ae.get_age_group_data(yas_grubu, selected_camp, metrik)
    
    if age_data.empty:
        st.warning("Veri yok!")
        return
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dağılım", "🎯 Konum Karşılaştırması", "📈 Trend", "📋 Oyuncu Listesi"])
    
    with tab1:
        # Box plot
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=age_data['metrik_value'],
            name=metrik,
            boxmean='sd',
            marker_color='#003366'
        ))
        
        fig.update_layout(
            title=f"<b>{yas_grubu}</b> - Dağılım Analizi",
            yaxis_title="Değer",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Istatistikler
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Ort.", f"{age_data['metrik_value'].mean():.2f}")
        with col2:
            st.metric("Median", f"{age_data['metrik_value'].median():.2f}")
        with col3:
            st.metric("Min", f"{age_data['metrik_value'].min():.2f}")
        with col4:
            st.metric("Max", f"{age_data['metrik_value'].max():.2f}")
        with col5:
            st.metric("Std Dev", f"{age_data['metrik_value'].std():.2f}")
    
    with tab2:
        # Konum bazlı karşılaştırma
        position_data = age_data.groupby('pozisyon')['metrik_value'].apply(list)
        
        fig = go.Figure()
        
        for position in age_data['pozisyon'].unique():
            pos_values = age_data[age_data['pozisyon'] == position]['metrik_value']
            fig.add_trace(go.Box(
                y=pos_values,
                name=position,
                marker_color={'Savunma': '#003366', 'Orta Saha': '#FFC107', 'Hücum': '#D32F2F'}.get(position, 'gray')
            ))
        
        fig.update_layout(
            title=f"<b>Konum Bazlı Karşılaştırma</b>",
            yaxis_title="Değer",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Tarih bazlı trend
        age_data_sorted = age_data.sort_values('tarih')
        
        daily_avg = age_data_sorted.groupby('tarih')['metrik_value'].mean().reset_index()
        daily_avg['tarih'] = pd.to_datetime(daily_avg['tarih'])
        
        fig = px.line(
            daily_avg,
            x='tarih',
            y='metrik_value',
            title=f"<b>{yas_grubu} Grubu - Günlük Ortalama Trend</b>",
            labels={'tarih': 'Tarih', 'metrik_value': 'Ort. Değer'},
            markers=True
        )
        
        fig.update_traces(line_color='#D32F2F', marker_size=8)
        fig.update_layout(height=500, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Oyuncu listesi
        player_list = age_data.groupby(['ad_soyad', 'pozisyon']).agg({
            'metrik_value': ['mean', 'max', 'min'],
            'minutes': 'sum'
        }).round(2)
        
        player_list.columns = ['Ort.', 'Max', 'Min', 'Toplam Dakika']
        player_list = player_list.sort_values('Ort.', ascending=False)
        
        st.dataframe(player_list)

# ============================================================
# SAYFA 4: HEATMAP ANALİZİ
# ============================================================

def page_heatmap_analysis(dm, ae):
    """Heatmap Analizi Sayfası"""
    
    st.markdown('<h2 class="section-header">🔥 Heatmap Analizi</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        camps = dm.get_all_camps()
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps['kamp_id'].values,
            format_func=lambda x: camps[camps['kamp_id']==x]['kamp_adi'].values[0]
        )
    
    with col2:
        metrik = st.selectbox(
            "Metrik Seçiniz",
            ['total_distance', 'smax_kmh', 'player_load', 'dist_gt_25', 'n_gt_25'],
            format_func=lambda x: {
                'total_distance': '📏 Total Distance',
                'smax_kmh': '⚡ Max Speed',
                'player_load': '💪 Player Load',
                'dist_gt_25': '🔥 Dist > 25',
                'n_gt_25': '💨 N > 25'
            }.get(x, x)
        )
    
    # Kamp verisi
    conn = sqlite3.connect("athletic_performance.db")
    df = pd.read_sql_query('''
        SELECT 
            p.ad_soyad,
            t.tarih,
            t.''' + metrik + ''' as metrik_value,
            t.minutes
        FROM training_match_data t
        JOIN player_info p ON t.oyuncu_id = p.oyuncu_id
        WHERE t.kamp_id = ? AND t.minutes >= 20
        ORDER BY t.tarih, p.ad_soyad
    ''', conn, params=[selected_camp])
    conn.close()
    
    if df.empty:
        st.warning("Veri yok!")
        return
    
    st.markdown("---")
    
    # Pivot table
    pivot = df.pivot_table(
        values='metrik_value',
        index='ad_soyad',
        columns='tarih',
        aggfunc='mean'
    )
    
    # Normalize (0-1)
    pivot_normalized = (pivot - pivot.min().min()) / (pivot.max().max() - pivot.min().min())
    
    # Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_normalized.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        colorbar=dict(title="Normalized Value"),
        hovertemplate='<b>%{y}</b><br>%{x}<br>Value: %{customdata:.2f}<extra></extra>',
        customdata=pivot.values
    ))
    
    fig.update_layout(
        title=f"<b>Heatmap:</b> Oyuncu × Tarih ({metrik})",
        xaxis_title="Tarih",
        yaxis_title="Oyuncu",
        height=600,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Veri tablosu
    st.subheader("📊 Detaylı Veriler")
    st.dataframe(pivot.round(2), use_container_width=True)

# ============================================================
# MAIN FUNCTION
# ============================================================

def main(dm):
    """Analiz sayfaları main function"""
    
    ae = AnalysisEngine()
    
    st.markdown("""
    <style>
    .section-header {
        color: #003366;
        border-bottom: 3px solid #D32F2F;
        padding-bottom: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
        font-size: 1.8em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Alt menü
    analysis_page = st.radio(
        "📊 Analiz Sayfaları",
        ["⚽ Oyuncu Karşılaştırması", "👤 Oyuncu Profili", "👥 Yaş Grubu Analizi", "🔥 Heatmap Analizi"],
        horizontal=True
    )
    
    if analysis_page == "⚽ Oyuncu Karşılaştırması":
        page_player_comparison(dm, ae)
    
    elif analysis_page == "👤 Oyuncu Profili":
        page_player_profile(dm, ae)
    
    elif analysis_page == "👥 Yaş Grubu Analizi":
        page_age_group_analysis(dm, ae)
    
    elif analysis_page == "🔥 Heatmap Analizi":
        page_heatmap_analysis(dm, ae)

if __name__ == "__main__":
    from admin_panel import DataManager
    dm = DataManager()
    main(dm)
