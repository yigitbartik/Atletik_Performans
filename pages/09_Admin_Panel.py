# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - ADMIN PANEL
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
from config import AGE_GROUPS, ADMIN_PASSWORD, COLORS
from database import db_manager
from styles import inject_styles, page_header, section_title, info_box

st.set_page_config(page_title="Admin Panel | TFF", layout="wide")
inject_styles()

# ─── ADMIN OTURUM KONTROLÜ ───────────────────────────────────────────────────
if 'admin_logged_in' not in st.session_state:
    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 48px; margin-bottom: 20px;">🔐</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 28px;
                   letter-spacing: 2px; color: {COLORS['GRAY_900']};
                   margin-bottom: 30px;">
            ADMIN OTURUM
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    password = st.text_input("Şifre Girin", type="password", placeholder="••••••••")
    
    if st.button("✅ OTURUM AÇ", use_container_width=True, type="primary"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("✅ Başarıyla giriş yapıldı!")
            st.rerun()
        else:
            st.error("❌ Şifre yanlış!")
    st.stop()

# ─── ADMIN HEADER ────────────────────────────────────────────────────────────
page_header("⚙️", "ADMIN PANEL", "Sistem yönetimi, veri silme, oyuncu bilgileri güncellemesi")

if st.button("🚪 ÇIKIŞ YAP", key="logout"):
    del st.session_state.admin_logged_in
    st.rerun()

st.divider()

# ─── TAB YAPISI ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 OYUNCU YÖNETİMİ",
    "📊 KAMP YÖNETİMİ", 
    "🗑️ VERİ SİLME",
    "📸 GÖRSEL YÖNETIMI",
    "📋 AUDIT LOG"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: OYUNCU YÖNETİMİ
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    section_title("OYUNCU KAYITLARI VE YÖNETİMİ", "👤")
    
    try:
        all_data = db_manager.get_all_data()
        
        if not all_data.empty:
            # İstatistikler
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px;">
                <div class="metric-card">
                    <div class="sc-label">TOPLAM OYUNCU</div>
                    <div class="sc-val">{all_data['player_name'].nunique()}</div>
                </div>
                <div class="metric-card">
                    <div class="sc-label">TOPLAM KAMP</div>
                    <div class="sc-val">{all_data['camp_id'].nunique()}</div>
                </div>
                <div class="metric-card">
                    <div class="sc-label">TOPLAM KAYIT</div>
                    <div class="sc-val">{len(all_data)}</div>
                </div>
                <div class="metric-card">
                    <div class="sc-label">MAÇ GÜNÜ</div>
                    <div class="sc-val">{all_data[all_data['tip'].str.upper()=='MATCH']['tarih'].nunique()}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Oyuncu listesi
            st.subheader("Oyuncu Listesi")
            players_info = []
            
            for player_name in sorted(all_data['player_name'].unique()):
                p_data = all_data[all_data['player_name'] == player_name]
                players_info.append({
                    'OYUNCU': player_name,
                    'YAŞ GRUBU': p_data['age_group'].iloc[0],
                    'SEANS': len(p_data),
                    'KAMP': p_data['camp_id'].nunique(),
                    'SON GÜN': p_data['tarih'].max().strftime('%d.%m.%Y')
                })
            
            players_df = pd.DataFrame(players_info)
            st.dataframe(players_df, use_container_width=True, hide_index=True, height=500)
        else:
            st.info("📭 Henüz oyuncu kaydı bulunmuyor")
    
    except Exception as e:
        st.error(f"❌ Hata: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: KAMP YÖNETİMİ
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    section_title("KAMP KAYITLARI", "⚽")
    
    try:
        all_data = db_manager.get_all_data()
        
        if not all_data.empty:
            camps_list = []
            
            for camp_id in sorted(all_data['camp_id'].unique()):
                c_data = all_data[all_data['camp_id'] == camp_id]
                age_group = c_data['age_group'].iloc[0] if not c_data.empty else "?"
                
                camps_list.append({
                    'KAMP ID': camp_id,
                    'YAŞ GRUBU': age_group,
                    'OYUNCU': c_data['player_name'].nunique(),
                    'SEANS': len(c_data),
                    'BAŞ. TARİHİ': c_data['tarih'].min().strftime('%d.%m.%Y'),
                    'BİTİŞ TARİHİ': c_data['tarih'].max().strftime('%d.%m.%Y')
                })
            
            camps_df = pd.DataFrame(camps_list)
            st.dataframe(camps_df, use_container_width=True, hide_index=True, height=500)
            
            st.info("💡 Kampları silmek için 'VERİ SİLME' sekmesini kullanınız")
        else:
            st.info("📭 Henüz kamp kaydı bulunmuyor")
    
    except Exception as e:
        st.error(f"❌ Hata: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: VERİ SİLME
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    section_title("VERİ SİLME İŞLEMLERİ", "🗑️")
    
    st.warning("⚠️ SİLME İŞLEMLERİ GERİ ALINA MAZ. LÜTFEN DİKKAT EDİN!")
    
    delete_mode = st.radio(
        "SİLİNECEK VERİ TÜRÜ",
        ["Oyuncu Silme", "Kamp Silme", "Tüm Yaş Grubu Silme"],
        horizontal=True
    )
    
    # ─── OYUNCU SİLME ────────────────────────────────────────────────────────
    if delete_mode == "Oyuncu Silme":
        all_data = db_manager.get_all_data()
        
        if not all_data.empty:
            players = sorted(all_data['player_name'].unique())
            
            st.markdown("### 👤 Silinecek Oyuncu Seçin")
            selected_player = st.selectbox("", players, key="del_player")
            
            player_data = all_data[all_data['player_name'] == selected_player]
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                    <div>
                        <div class="sc-label">Yaş Grubu</div>
                        <div style="font-size: 18px; color: {COLORS['RED']};">{player_data['age_group'].iloc[0]}</div>
                    </div>
                    <div>
                        <div class="sc-label">Seans Sayısı</div>
                        <div style="font-size: 18px; color: {COLORS['RED']};">{len(player_data)}</div>
                    </div>
                    <div>
                        <div class="sc-label">Kamplar</div>
                        <div style="font-size: 18px; color: {COLORS['RED']};">{player_data['camp_id'].nunique()}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ OYUNCUYU SİL", use_container_width=True, type="secondary"):
                    with st.spinner("Siliniyor..."):
                        result = db_manager.delete_player(selected_player)
                        if result['status'] == 'success':
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
    
    # ─── KAMP SİLME ───────────────────────────────────────────────────────────
    elif delete_mode == "Kamp Silme":
        all_data = db_manager.get_all_data()
        
        if not all_data.empty:
            age_group = st.selectbox("Yaş Grubu Seçin", AGE_GROUPS, key="del_camp_age")
            
            ag_data = all_data[all_data['age_group'] == age_group]
            camps = sorted(ag_data['camp_id'].unique())
            
            if camps:
                selected_camp = st.selectbox("Silinecek Kampı Seçin", camps, key="del_camp_id")
                
                camp_data = ag_data[ag_data['camp_id'] == selected_camp]
                
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                        <div>
                            <div class="sc-label">Oyuncu Sayısı</div>
                            <div style="font-size: 18px; color: {COLORS['RED']};">{camp_data['player_name'].nunique()}</div>
                        </div>
                        <div>
                            <div class="sc-label">Seans Sayısı</div>
                            <div style="font-size: 18px; color: {COLORS['RED']};">{len(camp_data)}</div>
                        </div>
                        <div>
                            <div class="sc-label">Tarih Aralığı</div>
                            <div style="font-size: 14px; color: {COLORS['RED']};">
                                {camp_data['tarih'].min().strftime('%d.%m')} - {camp_data['tarih'].max().strftime('%d.%m')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ KAMPI SİL", use_container_width=True, type="secondary"):
                    with st.spinner("Siliniyor..."):
                        result = db_manager.delete_excel_import(age_group, selected_camp)
                        if result['status'] == 'success':
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
    
    # ─── YAŞ GRUBU SİLME ──────────────────────────────────────────────────────
    else:
        st.markdown("### ⚠️ Tüm Yaş Grubu Silme")
        selected_age = st.selectbox("Silinecek Yaş Grubunu Seçin", AGE_GROUPS, key="del_age")
        
        all_data = db_manager.get_all_data()
        age_data = all_data[all_data['age_group'] == selected_age]
        
        st.markdown(f"""
        <div class="metric-card" style="border: 2px solid {COLORS['DANGER']}; background: #FEE2E2;">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div>
                    <div class="sc-label">Oyuncu Sayısı</div>
                    <div style="font-size: 18px; color: {COLORS['DANGER']};">{age_data['player_name'].nunique()}</div>
                </div>
                <div>
                    <div class="sc-label">Toplam Seans</div>
                    <div style="font-size: 18px; color: {COLORS['DANGER']};">{len(age_data)}</div>
                </div>
                <div>
                    <div class="sc-label">Kamplar</div>
                    <div style="font-size: 18px; color: {COLORS['DANGER']};">{age_data['camp_id'].nunique()}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Tüm verileri kalıcı olarak silmek üzeresiniz. Bu işlem geri alınamaz!**")
        
        confirm = st.checkbox(f"✓ {selected_age} grubunun TÜM verilerini silmek istiyorum", value=False)
        
        if confirm and st.button("🗑️ YAŞ GRUBUNU TAMAMEN SİL", use_container_width=True, type="secondary"):
            with st.spinner("Siliniyor..."):
                result = db_manager.delete_excel_import(selected_age)
                if result['status'] == 'success':
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: GÖRSEL YÖNETİMİ
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    section_title("OYUNCU FOTO ĞRAF VE KULÜP LOGOSU YÖNETİMİ", "📸")
    
    info_box("🔗 <b>URL Nasıl Alınır?</b> Resme sağ tıklayıp 'Resim Adresini Kopyala' demeniz yeterlidir. Transfermarkt veya TFF web sitesinden alabilirsiniz.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        admin_age = st.selectbox("Yaş Grubu", AGE_GROUPS, key="admin_age")
    
    with col2:
        players = db_manager.get_players(admin_age)
        if players:
            admin_player = st.selectbox("Oyuncu Seçin", players, key="admin_player")
        else:
            st.warning("Bu yaş grubunda oyuncu yok")
            admin_player = None
    
    if admin_player:
        player_info = db_manager.get_player_info(admin_player)
        curr_photo = player_info.get('photo_url') or ""
        curr_logo = player_info.get('club_logo_url') or ""
        
        st.markdown("### 📸 Görsel URL'leri")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Oyuncu Fotoğrafı**")
            new_photo = st.text_area("Fotoğraf URL'si", value=curr_photo, height=60, placeholder="https://...")
            if new_photo:
                st.image(new_photo, width=150, caption="Önizleme")
        
        with col2:
            st.markdown("**Kulüp Logosu**")
            new_logo = st.text_area("Logo URL'si", value=curr_logo, height=60, placeholder="https://...")
            if new_logo:
                st.image(new_logo, width=100, caption="Önizleme")
        
        if st.button("✅ GÖRSELLERI KAYDET", use_container_width=True, type="primary"):
            db_manager.update_player_images(admin_player, new_photo, new_logo)
            st.success(f"✅ {admin_player} için görseller kaydedildi!")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: AUDIT LOG
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    section_title("SİSTEM İŞLEM LOG'U", "📋")
    
    try:
        log = db_manager.get_audit_log(100)
        if log is not None and not log.empty:
            log['timestamp'] = pd.to_datetime(log['timestamp']).dt.strftime('%d.%m.%Y %H:%M:%S')
            log.columns = ['LOG ID', 'İŞLEM TİPİ', 'DETAYLAR', 'KULLANANICI', 'ZAMaN']
            
            st.dataframe(log, use_container_width=True, hide_index=True, height=600)
        else:
            st.info("📭 Henüz log kaydı bulunmuyor")
    except Exception as e:
        st.warning(f"⚠️ Log yüklenemedi: {e}")

st.divider()

st.markdown(f"""
<div class="tff-footer">
    <p>Türkiye Futbol Federasyonu • Admin Panel</p>
</div>
""", unsafe_allow_html=True)
