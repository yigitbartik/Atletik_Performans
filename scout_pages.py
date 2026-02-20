"""
ATLETİK PERFORMANS SİSTEMİ - AŞAMA 3
Scout Sistemi & Ağırlıklı Puanlama
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from scipy import stats

class ScoutEngine:
    """Scout analizi ve ağırlıklı puanlama"""
    
    def __init__(self, db_path="athletic_performance.db"):
        self.db_path = db_path
        self.default_weights = {
            'speed_max': 0.20,
            'total_distance': 0.20,
            'dist_gt_25': 0.20,
            'n_gt_25': 0.10,
            'player_load': 0.15,
            'consistency': 0.15
        }
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_player_metrics(self, oyuncu_id, kamp_id, min_dakika=300):
        """Oyuncunun kamp performans metriklerini getir"""
        conn = self.get_connection()
        query = '''
            SELECT 
                oyuncu_id,
                AVG(smax_kmh) as speed_max,
                AVG(total_distance) as total_distance,
                AVG(dist_gt_25) as dist_gt_25,
                SUM(n_gt_25) as n_gt_25,
                AVG(player_load) as player_load,
                SUM(minutes) as total_minutes,
                COUNT(*) as seans_sayisi
            FROM training_match_data
            WHERE oyuncu_id = ? AND kamp_id = ? AND minutes >= 20
            GROUP BY oyuncu_id
        '''
        
        df = pd.read_sql_query(query, conn, params=[oyuncu_id, kamp_id])
        conn.close()
        
        if df.empty or df['total_minutes'].values[0] < min_dakika:
            return None
        
        return df.iloc[0]
    
    def calculate_consistency(self, oyuncu_id, kamp_id):
        """Tutarlılık metriği hesapla (Min/Max farkı)"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT total_distance, smax_kmh, player_load
            FROM training_match_data
            WHERE oyuncu_id = ? AND kamp_id = ?
        ''', conn, params=[oyuncu_id, kamp_id])
        conn.close()
        
        if df.empty:
            return 0
        
        # Coefficient of variation
        consistency = 100 - (
            (df['total_distance'].std() / df['total_distance'].mean() * 100) +
            (df['smax_kmh'].std() / df['smax_kmh'].mean() * 100) +
            (df['player_load'].std() / df['player_load'].mean() * 100)
        ) / 3
        
        return max(0, min(100, consistency))
    
    def normalize_percentile(self, value, all_values):
        """Değeri percentile'a dönüştür (0-100)"""
        if len(all_values) == 0 or np.isnan(value):
            return 0
        
        return (np.sum(np.array(all_values) <= value) / len(all_values)) * 100
    
    def calculate_weighted_score(self, oyuncu_id, kamp_id, weights=None, min_dakika=300):
        """Ağırlıklı scout skorunu hesapla"""
        
        if weights is None:
            weights = self.default_weights
        
        metrics = self.get_player_metrics(oyuncu_id, kamp_id, min_dakika)
        if metrics is None:
            return None
        
        # Consistency ekle
        consistency = self.calculate_consistency(oyuncu_id, kamp_id)
        
        return {
            'oyuncu_id': oyuncu_id,
            'speed_max': metrics['speed_max'],
            'total_distance': metrics['total_distance'],
            'dist_gt_25': metrics['dist_gt_25'],
            'n_gt_25': metrics['n_gt_25'],
            'player_load': metrics['player_load'],
            'consistency': consistency,
            'total_minutes': metrics['total_minutes'],
            'seans_sayisi': metrics['seans_sayisi']
        }
    
    def get_camp_scout_rankings(self, kamp_id, weights=None, min_dakika=300, min_mac=0, min_antrenman=0):
        """Kampın scout sıralamasını hesapla"""
        
        conn = self.get_connection()
        
        # Tüm oyuncuları getir
        oyuncular_df = pd.read_sql_query('''
            SELECT DISTINCT 
                p.oyuncu_id,
                p.ad_soyad,
                p.pozisyon,
                p.kulup
            FROM training_match_data t
            JOIN player_info p ON t.oyuncu_id = p.oyuncu_id
            WHERE t.kamp_id = ?
        ''', conn, params=[kamp_id])
        
        conn.close()
        
        scores = []
        
        for _, oyuncu in oyuncular_df.iterrows():
            score_data = self.calculate_weighted_score(
                oyuncu['oyuncu_id'],
                kamp_id,
                weights,
                min_dakika
            )
            
            if score_data is not None:
                score_data['ad_soyad'] = oyuncu['ad_soyad']
                score_data['pozisyon'] = oyuncu['pozisyon']
                score_data['kulup'] = oyuncu['kulup']
                scores.append(score_data)
        
        if not scores:
            return None
        
        scores_df = pd.DataFrame(scores)
        
        # Filtrele
        if min_mac > 0:
            scores_df = scores_df[scores_df['seans_sayisi'] >= min_mac]
        
        # Percentile hesapla ve weighted score
        if weights is None:
            weights = self.default_weights
        
        # Her metrik için percentile
        scores_df['speed_percentile'] = scores_df['speed_max'].rank(pct=True) * 100
        scores_df['distance_percentile'] = scores_df['total_distance'].rank(pct=True) * 100
        scores_df['high_speed_percentile'] = scores_df['dist_gt_25'].rank(pct=True) * 100
        scores_df['load_percentile'] = scores_df['player_load'].rank(pct=True) * 100
        scores_df['consistency_percentile'] = scores_df['consistency'].rank(pct=True) * 100
        
        # Weighted score
        scores_df['overall_score'] = (
            scores_df['speed_percentile'] * weights['speed_max'] +
            scores_df['distance_percentile'] * weights['total_distance'] +
            scores_df['high_speed_percentile'] * weights['dist_gt_25'] +
            scores_df['load_percentile'] * weights['player_load'] +
            scores_df['consistency_percentile'] * weights['consistency']
        )
        
        # Sıralama
        scores_df['ranking'] = scores_df['overall_score'].rank(ascending=False).astype(int)
        
        return scores_df.sort_values('overall_score', ascending=False)

# ============================================================
# SAYFA 1: SCOUT SIRLAMASI
# ============================================================

def page_scout_ranking(se, dm):
    """Scout Sıralaması Sayfası"""
    
    st.markdown('<h2 class="section-header">🎯 Scout Sıralaması</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        camps = dm.get_all_camps()
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps['kamp_id'].values,
            format_func=lambda x: camps[camps['kamp_id']==x]['kamp_adi'].values[0]
        )
    
    with col2:
        st.write("**Filtreler**")
        min_dakika = st.slider("Min Dakika", 0, 600, 300)
        min_mac = st.slider("Min Seanslar", 0, 10, 1)
    
    st.markdown("---")
    
    # Ağırlık ayarları
    st.subheader("⚙️ Ağırlık Ayarları")
    
    col_w1, col_w2, col_w3 = st.columns(3)
    
    with col_w1:
        w_speed = st.slider("Speed Max (%)", 0, 50, 20) / 100
        w_distance = st.slider("Total Distance (%)", 0, 50, 20) / 100
    
    with col_w2:
        w_high_speed = st.slider("Dist > 25 (%)", 0, 50, 20) / 100
        w_load = st.slider("Player Load (%)", 0, 50, 15) / 100
    
    with col_w3:
        w_consistency = st.slider("Consistency (%)", 0, 50, 15) / 100
        # Normalleştir
        total_w = w_speed + w_distance + w_high_speed + w_load + w_consistency
        if total_w != 1.0:
            st.warning(f"⚠️ Ağırlıklar {total_w*100:.0f}% toplam ({int((total_w-1)*100):+d}%)")
    
    weights = {
        'speed_max': w_speed,
        'total_distance': w_distance,
        'dist_gt_25': w_high_speed,
        'n_gt_25': 0,  # n_gt_25 dist_gt_25'e dahil
        'player_load': w_load,
        'consistency': w_consistency
    }
    
    # Scout ranking
    scores = se.get_camp_scout_rankings(selected_camp, weights, min_dakika, min_mac)
    
    if scores is None or scores.empty:
        st.warning("Filtre kriterlerine uygun oyuncu yok!")
        return
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Sıralama", "📊 Top 5 Radar", "🔥 Heatmap", "📋 Detaylı Tablo"])
    
    with tab1:
        # Sıralama tablosu
        display_df = scores[['ranking', 'ad_soyad', 'pozisyon', 'kulup', 'overall_score', 
                             'speed_max', 'total_distance', 'consistency']].head(20).copy()
        display_df.columns = ['Sırası', 'Oyuncu', 'Konum', 'Kulüp', 'Score', 'Speed', 'Distance', 'Consistency']
        
        # Renklendir
        styled_df = display_df.style.highlight_max(subset=['Score'], color='lightgreen')
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Top 3 metrikler
        st.subheader("🥇 Top 3 Oyuncular")
        top_3 = scores.head(3)
        
        cols = st.columns(3)
        for idx, (_, player) in enumerate(top_3.iterrows()):
            with cols[idx]:
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉"
                st.metric(
                    f"{medal} #{player['ranking']:.0f} - {player['ad_soyad']}",
                    f"{player['overall_score']:.1f}",
                    f"Speed: {player['speed_max']:.1f} km/h"
                )
    
    with tab2:
        # Top 5 radar karşılaştırması
        top_5 = scores.head(5)
        
        if len(top_5) > 0:
            fig = go.Figure()
            
            categories = ['Speed', 'Distance', 'High Speed', 'Load', 'Consistency']
            
            for _, player in top_5.iterrows():
                values = [
                    player['speed_percentile'],
                    player['distance_percentile'],
                    player['high_speed_percentile'],
                    player['load_percentile'],
                    player['consistency_percentile']
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=f"{player['ranking']:.0f}. {player['ad_soyad']}"
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="<b>Top 5 Oyuncu Radar Karşılaştırması</b>",
                height=600,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Heatmap
        heatmap_data = scores.head(15)[['ad_soyad', 'speed_percentile', 'distance_percentile', 
                                         'high_speed_percentile', 'load_percentile', 'consistency_percentile']].copy()
        
        heatmap_data_values = heatmap_data.iloc[:, 1:].values
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_values,
            x=['Speed', 'Distance', 'High Speed', 'Load', 'Consistency'],
            y=heatmap_data['ad_soyad'],
            colorscale='RdYlGn',
            colorbar=dict(title="Percentile")
        ))
        
        fig.update_layout(
            title="<b>Top 15 Oyuncu - Metrik Heatmap</b>",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Detaylı tablo
        detailed = scores[['ranking', 'ad_soyad', 'pozisyon', 'overall_score', 
                          'speed_max', 'total_distance', 'dist_gt_25', 
                          'player_load', 'consistency', 'total_minutes', 'seans_sayisi']].copy()
        
        detailed.columns = ['Sırası', 'Oyuncu', 'Konum', 'Score', 'Speed (km/h)', 'Distance (m)', 
                           'Dist >25 (m)', 'Load', 'Consistency', 'Tot. Min', 'Seanslar']
        
        st.dataframe(detailed, use_container_width=True, hide_index=True)

# ============================================================
# SAYFA 2: OYUNCU KARŞILAŞTIRMASI (RADAR)
# ============================================================

def page_player_radar_comparison(se, dm):
    """Oyuncu Radar Karşılaştırması"""
    
    st.markdown('<h2 class="section-header">📊 Oyuncu Karşılaştırması (Radar)</h2>', unsafe_allow_html=True)
    
    camps = dm.get_all_camps()
    selected_camp = st.selectbox(
        "Kamp Seçiniz",
        camps['kamp_id'].values,
        format_func=lambda x: camps[camps['kamp_id']==x]['kamp_adi'].values[0]
    )
    
    # Scout ranking al
    scores = se.get_camp_scout_rankings(selected_camp)
    
    if scores is None or scores.empty:
        st.error("Veri yok!")
        return
    
    # Oyuncu seç
    col1, col2, col3, col4 = st.columns(4)
    
    oyuncular = scores['ad_soyad'].values
    
    with col1:
        oyuncu1 = st.selectbox("Oyuncu 1", oyuncular, index=0)
    with col2:
        oyuncu2 = st.selectbox("Oyuncu 2", oyuncular, index=min(1, len(oyuncular)-1))
    with col3:
        oyuncu3 = st.selectbox("Oyuncu 3 (Opsiyonel)", ["---"] + list(oyuncular), index=0)
    with col4:
        oyuncu4 = st.selectbox("Oyuncu 4 (Opsiyonel)", ["---"] + list(oyuncular), index=0)
    
    st.markdown("---")
    
    # Radar grafik
    fig = go.Figure()
    
    categories = ['Speed', 'Distance', 'High Speed', 'Load', 'Consistency']
    
    for oyuncu_adi in [oyuncu1, oyuncu2, oyuncu3, oyuncu4]:
        if oyuncu_adi == "---":
            continue
        
        player_data = scores[scores['ad_soyad'] == oyuncu_adi].iloc[0]
        
        values = [
            player_data['speed_percentile'],
            player_data['distance_percentile'],
            player_data['high_speed_percentile'],
            player_data['load_percentile'],
            player_data['consistency_percentile']
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=oyuncu_adi
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="<b>Oyuncu Radar Karşılaştırması</b>",
        height=600,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bilgiler
    st.subheader("📊 Detaylı Karşılaştırma")
    
    comparison_data = []
    for oyuncu_adi in [oyuncu1, oyuncu2, oyuncu3, oyuncu4]:
        if oyuncu_adi == "---":
            continue
        
        player_data = scores[scores['ad_soyad'] == oyuncu_adi].iloc[0]
        comparison_data.append({
            'Oyuncu': oyuncu_adi,
            'Score': f"{player_data['overall_score']:.1f}",
            'Speed': f"{player_data['speed_max']:.1f}",
            'Distance': f"{player_data['total_distance']:.0f}",
            'Load': f"{player_data['player_load']:.1f}",
            'Consistency': f"{player_data['consistency']:.1f}"
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ============================================================
# SAYFA 3: TALENT BULMA (RISING STARS)
# ============================================================

def page_talent_finder(se, dm):
    """Yetenekli Oyuncu Bulma"""
    
    st.markdown('<h2 class="section-header">⭐ Yetenekli Oyuncu Bulma</h2>', unsafe_allow_html=True)
    
    camps = dm.get_all_camps()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_camp = st.selectbox(
            "Kamp Seçiniz",
            camps['kamp_id'].values,
            format_func=lambda x: camps[camps['kamp_id']==x]['kamp_adi'].values[0]
        )
    
    with col2:
        position_filter = st.selectbox("Konum Filtresi", ["Tümü", "Savunma", "Orta Saha", "Hücum"])
    
    scores = se.get_camp_scout_rankings(selected_camp)
    
    if scores is None or scores.empty:
        st.error("Veri yok!")
        return
    
    # Filtrele
    if position_filter != "Tümü":
        scores = scores[scores['pozisyon'] == position_filter]
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🏆 Top Oyuncular", "🚀 Rising Stars"])
    
    with tab1:
        # Top 10
        top_10 = scores.head(10)
        
        fig = px.bar(
            top_10,
            x='overall_score',
            y='ad_soyad',
            orientation='h',
            color='pozisyon',
            color_discrete_map={'Savunma': '#003366', 'Orta Saha': '#FFC107', 'Hücum': '#D32F2F'},
            title="<b>Top 10 Oyuncu (Overall Score)</b>",
            labels={'overall_score': 'Score', 'ad_soyad': 'Oyuncu'}
        )
        
        fig.update_layout(height=500, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrikleri göster
        for idx, (_, player) in enumerate(top_10.iterrows(), 1):
            with st.expander(f"#{idx} - {player['ad_soyad']} ({player['pozisyon']})"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Overall Score", f"{player['overall_score']:.1f}")
                with col2:
                    st.metric("Max Speed", f"{player['speed_max']:.1f} km/h")
                with col3:
                    st.metric("Distance", f"{player['total_distance']:.0f} m")
                with col4:
                    st.metric("Consistency", f"{player['consistency']:.1f}%")
    
    with tab2:
        # Rising stars (score artışı var mı?)
        # Çoklu kampları karşılaştır
        conn = sqlite3.connect("athletic_performance.db")
        
        all_camps = pd.read_sql_query('SELECT DISTINCT kamp_id FROM camp_info ORDER BY baslangic_tarihi DESC LIMIT 2', conn)
        conn.close()
        
        if len(all_camps) < 2:
            st.info("Rising Stars analizi için en az 2 kamp gerekli!")
            return
        
        latest_camp = all_camps.iloc[0]['kamp_id']
        prev_camp = all_camps.iloc[1]['kamp_id']
        
        latest_scores = se.get_camp_scout_rankings(latest_camp)
        prev_scores = se.get_camp_scout_rankings(prev_camp)
        
        if latest_scores is None or prev_scores is None:
            st.warning("Karşılaştırma için yeterli veri yok!")
            return
        
        # Merge
        comparison = latest_scores[['oyuncu_id', 'ad_soyad', 'pozisyon', 'overall_score']].copy()
        comparison.columns = ['oyuncu_id', 'ad_soyad', 'pozisyon', 'latest_score']
        
        prev_comparison = prev_scores[['oyuncu_id', 'overall_score']].copy()
        prev_comparison.columns = ['oyuncu_id', 'prev_score']
        
        merged = comparison.merge(prev_comparison, on='oyuncu_id', how='inner')
        merged['score_change'] = merged['latest_score'] - merged['prev_score']
        merged = merged.sort_values('score_change', ascending=False)
        
        # Rising stars (>10 puan artış)
        rising = merged[merged['score_change'] > 10]
        
        if rising.empty:
            st.info("10 puandan fazla artış gösteren oyuncu yok.")
        else:
            st.subheader("🚀 Yükselen Yıldızlar")
            
            for _, player in rising.head(5).iterrows():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(player['ad_soyad'], f"+{player['score_change']:.1f}")
                with col2:
                    st.metric("Önceki", f"{player['prev_score']:.1f}")
                with col3:
                    st.metric("Güncel", f"{player['latest_score']:.1f}")
                with col4:
                    st.metric("Konum", player['pozisyon'])

# ============================================================
# MAIN FUNCTION
# ============================================================

def main(dm):
    """Scout sistemi main function"""
    
    se = ScoutEngine()
    
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
    
    scout_page = st.radio(
        "🎯 Scout Sayfaları",
        ["🏆 Scout Sıralaması", "📊 Oyuncu Karşılaştırması", "⭐ Yetenekli Oyuncu Bulma"],
        horizontal=True
    )
    
    if scout_page == "🏆 Scout Sıralaması":
        page_scout_ranking(se, dm)
    
    elif scout_page == "📊 Oyuncu Karşılaştırması":
        page_player_radar_comparison(se, dm)
    
    elif scout_page == "⭐ Yetenekli Oyuncu Bulma":
        page_talent_finder(se, dm)

if __name__ == "__main__":
    from admin_panel import DataManager
    dm = DataManager()
    main(dm)
