# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - STİL SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
from config import COLORS

# ─── GLOBAL CSS İNJEKSİYONU ─────────────────────────────────────────────────────
def inject_styles():
    """Tüm sayfaya uygulanacak CSS'i enjekte eder"""
    st.markdown(f"""
    <style>
    /* ─── GENEL AYARLAR ─── */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS['GRAY_50']};
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* ─── SIDEBAR STİLİ ─── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(135deg, {COLORS['DARK']} 0%, #1a1a1a 100%);
        border-right: 3px solid {COLORS['RED']};
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: {COLORS['WHITE']};
    }}
    
    [data-testid="stSidebar"] label {{
        color: {COLORS['WHITE']} !important;
    }}
    
    [data-testid="stSidebar"] .stSelectbox, 
    [data-testid="stSidebar"] .stNumberInput {{
        color: {COLORS['WHITE']};
    }}
    
    /* ─── SEÇİM KAISIYETLERİ STİLİ ─── */
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stNumberInput > div {{
        background-color: rgba(255,255,255,0.1);
        border: 1px solid {COLORS['RED']};
        border-radius: 8px;
        color: {COLORS['WHITE']};
    }}
    
    [data-testid="stSidebar"] .stSelectbox div[role="listbox"] {{
        background-color: {COLORS['DARK']};
        color: {COLORS['WHITE']};
    }}
    
    /* ─── BUTTON STİLLERİ ─── */
    [data-testid="stSidebar"] .stButton > button {{
        background: linear-gradient(135deg, {COLORS['RED']} 0%, #c40810 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        padding: 12px 20px;
    }}
    
    [data-testid="stSidebar"] .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(227,10,23,0.3);
    }}
    
    /* ─── SIDEBAR ETIKETLER ─── */
    .sidebar-label {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        color: {COLORS['WHITE']};
        text-transform: uppercase;
        padding: 16px 0 8px 0;
        border-bottom: 2px solid {COLORS['RED']};
        margin-bottom: 12px;
    }}
    
    /* ─── METRIK KARTLARI ─── */
    .metric-card {{
        background: {COLORS['WHITE']};
        border: 1px solid {COLORS['GRAY_200']};
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(227,10,23,0.12);
        border-color: {COLORS['RED']};
    }}
    
    .sc-label {{
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        color: {COLORS['GRAY_500']};
        letter-spacing: 1px;
    }}
    
    .sc-val {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 28px;
        color: {COLORS['RED']};
        font-weight: 700;
        margin-top: 4px;
        letter-spacing: 1px;
    }}
    
    /* ─── YAŞGRUBU KARTLARI ─── */
    .ag-card {{
        background: white;
        border: 1px solid {COLORS['GRAY_200']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .ag-card.has-data {{
        cursor: pointer;
    }}
    
    .ag-card.has-data:hover {{
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(227,10,23,0.15);
        border-color: {COLORS['RED']};
    }}
    
    .ag-card.no-data {{
        opacity: 0.5;
        background: {COLORS['GRAY_50']};
        border-style: dashed;
    }}
    
    .ag-label {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 32px;
        letter-spacing: 2px;
        color: {COLORS['GRAY_900']};
        margin-bottom: 8px;
    }}
    
    .ag-stat {{
        font-size: 12px;
        color: {COLORS['GRAY_600']};
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    
    /* ─── FOOTER ─── */
    .tff-footer {{
        text-align: center;
        padding: 30px;
        margin-top: 50px;
        border-top: 2px solid {COLORS['GRAY_200']};
        background: {COLORS['GRAY_50']};
        border-radius: 12px;
    }}
    
    .tff-footer p {{
        margin: 4px 0;
        font-size: 12px;
        color: {COLORS['GRAY_600']};
        font-weight: 600;
    }}
    
    /* ─── BAŞLIKLAR ─── */
    h1, h2, h3 {{
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 1.5px;
    }}
    
    /* ─── TABLO STİLLERİ ─── */
    .stDataFrame {{
        border-collapse: collapse;
    }}
    
    /* ─── İNFO KUTUSU ─── */
    .info-box {{
        background: linear-gradient(135deg, {COLORS['INFO']}20 0%, {COLORS['INFO']}10 100%);
        border-left: 4px solid {COLORS['INFO']};
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 13px;
        color: {COLORS['GRAY_700']};
        margin: 12px 0;
    }}
    
    /* ─── OYUNCU KARTI ─── */
    .player-card {{
        background: {COLORS['WHITE']};
        border: 1px solid {COLORS['GRAY_200']};
        border-radius: 16px;
        padding: 20px 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }}
    
    .player-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(227,10,23,0.15);
        border-color: {COLORS['RED']};
    }}
    
    /* ─── MOBILE OPTİMİZASYONU ─── */
    @media (max-width: 768px) {{
        .metric-card {{
            padding: 12px;
        }}
        
        h1 {{
            font-size: 28px !important;
        }}
        
        h2 {{
            font-size: 20px !important;
        }}
        
        [data-testid="stSidebar"] {{
            width: 100% !important;
        }}
        
        .stTabs {{
            flex-direction: column;
        }}
    }}
    
    @media (max-width: 480px) {{
        [data-testid="stSidebar"] {{
            display: none;
        }}
        
        .metric-card {{
            padding: 8px;
            margin-bottom: 8px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ─── SAYFA BAŞLIĞI ──────────────────────────────────────────────────────────────
def page_header(icon, title, subtitle=""):
    """Sayfa başlığını gösterir"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['WHITE']} 0%, {COLORS['GRAY_50']} 100%);
                border-bottom: 3px solid {COLORS['RED']};
                padding: 30px 0;
                margin-bottom: 25px;
                border-radius: 0 0 16px 16px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 44px;">{icon}</div>
            <div>
                <div style="font-family: 'Bebas Neue', sans-serif; font-size: 36px;
                           letter-spacing: 2px; color: {COLORS['GRAY_900']};
                           font-weight: 700;">
                    {title.upper()}
                </div>
                {f'<div style="font-size: 13px; color: {COLORS["GRAY_600"]}; margin-top: 4px; font-weight: 600;">{subtitle}</div>' if subtitle else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── KİSİM BAŞLIĞI ──────────────────────────────────────────────────────────────
def section_title(title, icon="", tooltip=""):
    """Kısım başlığını gösterir"""
    tooltip_html = f'title="{tooltip}"' if tooltip else ''
    st.markdown(f"""
    <div style="margin-top: 25px; margin-bottom: 15px;" {tooltip_html}>
        <div style="display: flex; align-items: center; gap: 10px; border-left: 4px solid {COLORS['RED']};
                   padding-left: 12px;">
            <div style="font-size: 20px;">{icon}</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 20px;
                       letter-spacing: 1.5px; color: {COLORS['GRAY_900']};
                       font-weight: 700;">
                {title.upper()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── BİLGİ KUTUSU ───────────────────────────────────────────────────────────────
def info_box(content):
    """Bilgi kutusunu gösterir"""
    st.markdown(f"""
    <div class="info-box" style="background: linear-gradient(135deg, {COLORS['INFO']}15 0%, {COLORS['INFO']}5 100%);
                                  border-left: 4px solid {COLORS['INFO']};
                                  padding: 14px 16px;
                                  border-radius: 8px;
                                  margin: 15px 0;">
        {content}
    </div>
    """, unsafe_allow_html=True)

# ─── SIDEBAR MARKALAMA ───────────────────────────────────────────────────────────
def sidebar_brand():
    """Sidebar üst logosunu gösterir"""
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid {COLORS['RED']};
               margin-bottom: 20px;">
        <div style="font-size: 48px; margin-bottom: 10px;">🇹🇷</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 18px;
                   letter-spacing: 2px; color: {COLORS['WHITE']};
                   font-weight: 700;">
            TFF PERFORMANs
        </div>
        <div style="font-size: 11px; color: {COLORS['GRAY_400']}; margin-top: 6px;
                   letter-spacing: 1px; font-weight: 600;">
            ATLETİK VERİ PLATFORMU
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── KARŞILAŞTIRMA KARTI ────────────────────────────────────────────────────────
def comparison_card(metric_name, value1, value2, unit="", player1_name="Oyuncu 1", player2_name="Oyuncu 2"):
    """Renk-kodlu karşılaştırma kartını gösterir"""
    diff = value1 - value2
    percent_diff = (diff / value2 * 100) if value2 != 0 else 0
    
    if diff > 0:
        color = COLORS['SUCCESS']
        arrow = "▲"
    elif diff < 0:
        color = COLORS['DANGER']
        arrow = "▼"
    else:
        color = COLORS['GRAY_400']
        arrow = "▬"
    
    return f"""
    <div style="background: white; border: 1px solid {COLORS['GRAY_200']};
                border-radius: 12px; padding: 16px; margin: 10px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        <div style="font-size: 11px; color: {COLORS['GRAY_600']};
                   font-weight: 800; text-transform: uppercase; margin-bottom: 12px;">
            {metric_name}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div style="background: {COLORS['GRAY_50']}; padding: 12px; border-radius: 8px;
                       border-left: 3px solid {COLORS['RED']};">
                <div style="font-size: 10px; color: {COLORS['GRAY_600']};
                           font-weight: 700; margin-bottom: 4px;">
                    {player1_name.upper()}
                </div>
                <div style="font-family: 'Bebas Neue'; font-size: 24px;
                           color: {COLORS['RED']}; font-weight: 700;">
                    {value1:.1f}
                </div>
                <div style="font-size: 10px; color: {COLORS['GRAY_500']};">{unit}</div>
            </div>
            <div style="background: {COLORS['GRAY_50']}; padding: 12px; border-radius: 8px;
                       border-left: 3px solid {COLORS['GRAY_400']};">
                <div style="font-size: 10px; color: {COLORS['GRAY_600']};
                           font-weight: 700; margin-bottom: 4px;">
                    {player2_name.upper()}
                </div>
                <div style="font-family: 'Bebas Neue'; font-size: 24px;
                           color: {COLORS['GRAY_700']}; font-weight: 700;">
                    {value2:.1f}
                </div>
                <div style="font-size: 10px; color: {COLORS['GRAY_500']};">{unit}</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 12px; padding-top: 12px;
                   border-top: 1px solid {COLORS['GRAY_200']};">
            <span style="font-family: 'Bebas Neue'; font-size: 18px;
                        color: {color}; font-weight: 700; margin-right: 4px;">
                {arrow}
            </span>
            <span style="color: {color}; font-weight: 700;">
                {abs(diff):.1f} ({percent_diff:+.1f}%)
            </span>
        </div>
    </div>
    """

print("✅ Stil sistemi yüklendi | Tema: Profesyonel TFF")
