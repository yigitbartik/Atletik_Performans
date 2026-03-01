# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from datetime import datetime
from config import COLORS, METRICS, PRIMARY_METRICS
from export_tools import export_manager

# ═══════════════════════════════════════════════════════════════════════════════
# GRAFIK FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def plot_player_performance_with_band(player_data, team_data, metric):
    """Oyuncu performansı ve takım bandı grafiği"""
    data = player_data.sort_values('tarih').copy()
    team_band = team_data.groupby('tarih')[metric].agg(['mean', 'std']).reset_index()
    
    fig = go.Figure()
    
    # Takım band'i (min-max)
    fig.add_trace(go.Scatter(
        x=team_band['tarih'],
        y=team_band['mean'] + team_band['std'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=team_band['tarih'],
        y=team_band['mean'] - team_band['std'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        fillcolor='rgba(227,10,23,0.1)',
        name='Takım Aralığı (±Std)',
        hoverinfo='skip'
    ))
    
    # Takım ortalaması
    fig.add_trace(go.Scatter(
        x=team_band['tarih'],
        y=team_band['mean'],
        mode='lines',
        name='Takım Ortalaması',
        line=dict(color='#E30A17', width=2, dash='dash')
    ))
    
    # Oyuncu verisi
    fig.add_trace(go.Scatter(
        x=data['tarih'],
        y=data[metric],
        mode='lines+markers',
        name='Oyuncu',
        line=dict(color='#0D0D0D', width=3),
        marker=dict(size=8, color='white', line=dict(color='#0D0D0D', width=2))
    ))
    
    metric_label = METRICS.get(metric, {}).get('display', metric)
    metric_unit = METRICS.get(metric, {}).get('unit', '')
    
    fig.update_layout(
        title=f"{metric_label} ({metric_unit})",
        template='plotly_white',
        hovermode='x unified',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            title='Tarih',
            gridcolor='#F3F4F6',
            tickformat='%d.%m'
        ),
        yaxis=dict(
            title=f'{metric_label} ({metric_unit})',
            gridcolor='#F3F4F6'
        )
    )
    
    return fig

def plot_player_radar(player_data, team_data):
    """Oyuncu radar grafiği (percentile)"""
    percentiles = {}
    
    for metric in PRIMARY_METRICS:
        if metric in player_data.columns and metric in team_data.columns:
            player_val = player_data[metric].mean()
            team_vals = team_data[metric].dropna()
            
            if len(team_vals) > 0 and not pd.isna(player_val):
                percentile = (team_vals < player_val).sum() / len(team_vals) * 100
                percentiles[metric] = percentile
    
    if not percentiles:
        st.warning("Radar grafiği için yeterli veri yok")
        return None
    
    fig = go.Figure(data=go.Scatterpolar(
        r=list(percentiles.values()),
        theta=[METRICS.get(m, {}).get('display', m) for m in percentiles.keys()],
        fill='toself',
        marker=dict(size=8, color='#E30A17'),
        line=dict(color='#E30A17', width=2),
        fillcolor='rgba(227,10,23,0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=11, weight='bold')
            )
        ),
        title='Atletik Performans Profili (Percentile %)',
        template='plotly_white',
        height=500
    )
    
    return fig

def plot_scatter(data, x_metric, y_metric, color_by='player_name', 
                 highlight_player=None, show_avg_lines=True):
    """Scatter plot grafiği"""
    colors_map = {'TRAINING': '#10B981', 'MATCH': '#EF4444'}
    
    fig = go.Figure()
    
    if color_by == 'tip':
        for session_type in data['tip'].unique():
            subset = data[data['tip'] == session_type]
            fig.add_trace(go.Scatter(
                x=subset[x_metric],
                y=subset[y_metric],
                mode='markers',
                name=session_type,
                marker=dict(
                    size=8,
                    color=colors_map.get(session_type, '#9CA3AF'),
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=subset['player_name'],
                hovertemplate='<b>%{text}</b><br>X: %{x:.1f}<br>Y: %{y:.1f}'
            ))
    else:
        players = data['player_name'].unique()
        for player in players:
            subset = data[data['player_name'] == player]
            color = '#E30A17' if player == highlight_player else '#9CA3AF'
            size = 12 if player == highlight_player else 8
            
            fig.add_trace(go.Scatter(
                x=subset[x_metric],
                y=subset[y_metric],
                mode='markers',
                name=player,
                marker=dict(
                    size=size,
                    color=color,
                    opacity=0.8 if player == highlight_player else 0.5,
                    line=dict(width=2 if player == highlight_player else 0, color='white')
                ),
                hovertemplate=f'<b>{player}</b><br>X: %{{x:.1f}}<br>Y: %{{y:.1f}}'
            ))
    
    if show_avg_lines:
        x_mean = data[x_metric].mean()
        y_mean = data[y_metric].mean()
        
        fig.add_hline(y=y_mean, line_dash='dash', line_color='#E30A17', opacity=0.5,
                     annotation_text='Y Ort.')
        fig.add_vline(x=x_mean, line_dash='dash', line_color='#E30A17', opacity=0.5,
                     annotation_text='X Ort.')
    
    x_label = METRICS.get(x_metric, {}).get('display', x_metric)
    y_label = METRICS.get(y_metric, {}).get('display', y_metric)
    
    fig.update_layout(
        title=f"{x_label} vs {y_label}",
        xaxis=dict(title=x_label, gridcolor='#F3F4F6'),
        yaxis=dict(title=y_label, gridcolor='#F3F4F6'),
        template='plotly_white',
        hovermode='closest',
        height=500
    )
    
    return fig

def plot_percentile_gauge(percentile, label):
    """Percentile göstergesi (gauge)"""
    color = '#059669' if percentile >= 80 else '#10B981' if percentile >= 65 else '#F59E0B' if percentile >= 50 else '#EF4444'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentile,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': label.upper(), 'font': {'size': 13, 'color': '#6B7280', 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickfont': {'size': 11}},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': '#FEE2E2'},
                {'range': [50, 65], 'color': '#FEF08A'},
                {'range': [65, 80], 'color': '#DBEAFE'},
                {'range': [80, 100], 'color': '#DCFCE7'}
            ],
            'threshold': {
                'line': {'color': '#E30A17', 'width': 2},
                'thickness': 0.75,
                'value': percentile
            }
        },
        number={'suffix': '%', 'font': {'size': 24, 'color': color}}
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=300,
        font=dict(family='DM Sans', size=11)
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# ANALİZ FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_player_stats(player_data):
    """Oyuncu istatistiklerini hesaplar"""
    return {
        'camp_count': player_data['camp_id'].nunique(),
        'session_count': len(player_data),
        'max_speed': player_data['smax_kmh'].max() if 'smax_kmh' in player_data.columns else 0,
        'avg_distance': player_data['total_distance'].mean() if 'total_distance' in player_data.columns else 0,
        'total_load': player_data['player_load'].sum() if 'player_load' in player_data.columns else 0
    }

def calculate_composite_score(player_data, team_data, session_filter="ALL"):
    """Atletik Performans Skoru hesapla (Composite Score)"""
    scores = {}
    
    if player_data.empty:
        return {metric: 50 for metric in PRIMARY_METRICS}
    
    for metric in PRIMARY_METRICS:
        if metric not in player_data.columns:
            continue
        
        team_compare = team_data
        
        if session_filter != "ALL":
            player_data = player_data[player_data['tip'].str.upper() == session_filter]
            team_compare = team_data[team_data['tip'].str.upper() == session_filter]
        
        if player_data.empty or team_compare.empty:
            scores[metric] = 50
            continue
        
        player_val = player_data[metric].mean()
        team_vals = team_compare[metric].dropna()
        
        if len(team_vals) > 0 and not pd.isna(player_val):
            percentile = (team_vals < player_val).sum() / len(team_vals) * 100
            scores[metric] = percentile
        else:
            scores[metric] = 50
    
    # Ortalama composite skor
    composite = np.mean(list(scores.values()))
    scores['composite'] = composite
    
    return scores

def percentile_color(percentile):
    """Percentile değerine göre renk döner"""
    if percentile >= 80:
        return '#059669'  # Koyu yeşil
    elif percentile >= 65:
        return '#10B981'  # Yeşil
    elif percentile >= 50:
        return '#F59E0B'  # Sarı
    else:
        return '#EF4444'  # Kırmızı

# ═══════════════════════════════════════════════════════════════════════════════
# KÜMELEME ANALİZİ (CLUSTERING)
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_player_clustering(age_group_data, selected_player):
    """Oyuncuyu kümeye göre benzer oyuncuları bulur"""
    
    if age_group_data.empty:
        return None, None
    
    # Oyuncu bazlı ortalamalar
    player_means = age_group_data.groupby('player_name')[PRIMARY_METRICS].mean()
    
    if selected_player not in player_means.index:
        return None, None
    
    # NaN değerleri doldur
    player_means = player_means.fillna(player_means.mean())
    
    # Ölçekle
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(player_means)
    
    # K-Means clustering (4 küme)
    kmeans = KMeans(n_clusters=min(4, len(player_means)), random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    player_means['cluster'] = clusters
    
    # Seçilen oyuncunun kümesi
    selected_cluster = player_means.loc[selected_player, 'cluster']
    
    # Aynı kümede başka oyuncular
    similar_players = player_means[
        (player_means['cluster'] == selected_cluster) & 
        (player_means.index != selected_player)
    ]
    
    return similar_players, player_means

def get_similarity_score(player1_stats, player2_stats):
    """İki oyuncu arasında benzerlik skoru (0-100)"""
    differences = []
    
    for metric in PRIMARY_METRICS:
        if metric in player1_stats.index and metric in player2_stats.index:
            v1 = player1_stats[metric]
            v2 = player2_stats[metric]
            
            if max(v1, v2) > 0:
                diff = abs(v1 - v2) / max(abs(v1), abs(v2), 1)
                differences.append(diff)
    
    if differences:
        avg_diff = np.mean(differences)
        similarity = max(0, 100 * (1 - avg_diff))
    else:
        similarity = 0
    
    return similarity

# ═══════════════════════════════════════════════════════════════════════════════
# IMPACT SCORE (ETKİ SKORu) HESAPLAMA
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_impact_score_engine(camp_data):
    """Impact Score motor - Günlük objektif performans hesabı"""
    
    if camp_data.empty:
        return camp_data
    
    data = camp_data.copy()
    
    # Dakikaya göre normalleştir
    for metric in ['dist_25_plus', 'player_load', 'hsr', 'acc_over_3', 'dec_under_minus_3', 'amp', 'metrage']:
        if metric in data.columns:
            data[f'{metric}_pm'] = data[metric] / (data['minutes'] + 1)
    
    # Günlük ve oyuncu gruplaması
    daily_means = data.groupby('tarih')[[m for m in data.columns if '_pm' in m or m == 'smax_kmh']].mean()
    
    # Z-Score hesapla
    for col in daily_means.columns:
        mean = daily_means[col].mean()
        std = daily_means[col].std()
        
        if std > 0:
            data[f'{col}_z'] = (data[col] - mean) / std
        else:
            data[f'{col}_z'] = 0
    
    # Ağırlıklı Impact Score
    weights = {
        'dist_25_plus_pm_z': 0.25,
        'player_load_pm_z': 0.20,
        'acc_over_3_z': 0.10,
        'dec_under_minus_3_z': 0.10,
        'smax_kmh_z': 0.10,
        'metrage_pm_z': 0.10,
        'amp_z': 0.10
    }
    
    data['impact_score'] = 0
    
    for col, weight in weights.items():
        if col in data.columns:
            data['impact_score'] += (data[col] * weight)
    
    # 0-100 aralığına ölçekle
    data['impact_score'] = (data['impact_score'] + 3) / 6 * 100
    data['impact_score'] = data['impact_score'].clip(0, 100)
    
    # Durum etiketi
    def get_status(score):
        if score >= 80:
            return "🟢 Mükemmel"
        elif score >= 65:
            return "🔵 İyi"
        elif score >= 50:
            return "🟡 Orta"
        else:
            return "🔴 Düşük"
    
    data['status_tag'] = data['impact_score'].apply(get_status)
    
    return data

def calculate_development_stats(current_data, historical_data):
    """Geçmiş kamplara göre gelişim istatistikleri"""
    
    current_avg = current_data.groupby('player_name')[
        ['impact_score', 'dist_25_plus_pm', 'player_load_pm', 'total_distance_pm']
    ].mean()
    
    historical_avg = historical_data.groupby('player_name')[
        ['impact_score', 'dist_25_plus_pm', 'player_load_pm', 'total_distance_pm']
    ].mean()
    
    development = pd.DataFrame()
    
    for player in current_avg.index:
        if player in historical_avg.index:
            for col in current_avg.columns:
                curr = current_avg.loc[player, col]
                hist = historical_avg.loc[player, col]
                
                if hist > 0:
                    change = ((curr - hist) / hist) * 100
                else:
                    change = 0
                
                development.loc[player, col] = change
    
    return development

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT ve TABLO FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def build_stats_table(player_data, team_data):
    """Min/Ort/Max tablo oluştur"""
    result = []
    
    for metric in PRIMARY_METRICS:
        if metric not in player_data.columns:
            continue
        
        p_min = player_data[metric].min()
        p_mean = player_data[metric].mean()
        p_max = player_data[metric].max()
        
        t_mean = team_data[metric].mean()
        
        metric_label = METRICS.get(metric, {}).get('display', metric)
        
        result.append({
            'METRİK': metric_label,
            'MIN': f"{p_min:.1f}",
            'ORT': f"{p_mean:.1f}",
            'MAX': f"{p_max:.1f}",
            'TAKIM ORT': f"{t_mean:.1f}"
        })
    
    return pd.DataFrame(result)

def render_export_buttons(fig=None, df=None, html_report=None, key_prefix="exp", filename="data"):
    """Export butonlarını render et"""
    cols = st.columns([1, 1, 1] if all([fig, df]) else [1, 1])
    
    with cols[0]:
        if fig:
            export_manager.export_figure_html(fig, filename)
    
    with cols[1]:
        if df is not None:
            export_manager.export_dataframe_excel(df, filename)
    
    if len(cols) > 2 and html_report:
        with cols[2]:
            st.download_button(
                label="📄 RAPOR İNDİR",
                data=html_report,
                file_name=f"{filename}_Rapor.html",
                mime="text/html"
            )

def generate_player_report_html(player_name, age_group, stats, score_dict, 
                               player_data, team_data, camp_name, photo_url, club_logo_url):
    """Oyuncu rapor kartı HTML oluştur"""
    
    composite = score_dict.get('composite', 50)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{player_name} - Rapor Kartı</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'DM Sans', -apple-system, sans-serif;
                background: #F9FAFB;
                padding: 20px;
            }}
            .report {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #E30A17 0%, #c40810 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            .logo-section {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .logo-section img {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                border: 4px solid white;
            }}
            .header h1 {{
                font-size: 36px;
                letter-spacing: 2px;
                margin-bottom: 10px;
            }}
            .header p {{
                font-size: 14px;
                opacity: 0.9;
                letter-spacing: 1px;
            }}
            .content {{
                padding: 40px;
            }}
            .section {{
                margin-bottom: 40px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 1.5px;
                color: #111827;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #E30A17;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }}
            .stat-label {{
                font-size: 11px;
                color: #6B7280;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 6px;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: 700;
                color: #E30A17;
                font-family: 'Bebas Neue', sans-serif;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                border-top: 1px solid #E5E7EB;
                color: #6B7280;
                font-size: 12px;
            }}
            .timestamp {{
                text-align: center;
                padding: 20px;
                color: #9CA3AF;
                font-size: 11px;
            }}
        </style>
    </head>
    <body>
        <div class="report">
            <div class="header">
                <div class="logo-section">
                    <img src="https://upload.wikimedia.org/wikipedia/tr/b/b9/Türkiye_Futbol_Federasyonu_logo.png" alt="TFF">
                </div>
                <h1>{player_name.upper()}</h1>
                <p>🇹🇷 {age_group} MİLLİ TAKIMI • {camp_name}</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <div class="section-title">📊 GENEL İSTATİSTİKLER</div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Toplam Kamp</div>
                            <div class="stat-value">{int(stats.get('camp_count', 0))}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Seans Sayısı</div>
                            <div class="stat-value">{int(stats.get('session_count', 0))}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Maksimum Hız</div>
                            <div class="stat-value">{stats.get('max_speed', 0):.1f} km/h</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Atletik Performans Skoru</div>
                            <div class="stat-value">{composite:.0f}%</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">🎯 METRIK PERFORMANSLARI (PERCENTILE)</div>
                    <div class="stats-grid">
    """
    
    for metric in PRIMARY_METRICS[:8]:
        score = score_dict.get(metric, 50)
        label = METRICS.get(metric, {}).get('display', metric)
        html += f"""
                        <div class="stat-card">
                            <div class="stat-label">{label}</div>
                            <div class="stat-value">{score:.0f}%</div>
                        </div>
        """
    
    html += f"""
                    </div>
                </div>
            </div>
            
            <div class="timestamp">
                <p>📅 Rapor Oluşturma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <p>Türkiye Futbol Federasyonu • Atletik Performans Sistemi</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

print("✅ Yardımcı fonksiyonlar yüklendi | Clustering, Export, Analysis")
