import streamlit as st
from config import AGE_GROUPS
from database import db_manager
from styles import inject_styles, page_header, section_title

st.set_page_config(page_title="Admin Panel | TFF", layout="wide")
inject_styles()

# Basit password check
if 'admin_logged_in' not in st.session_state:
    password = st.text_input("Admin Şifresi", type="password")
    if password == "tff2024":
        st.session_state.admin_logged_in = True
    else:
        st.stop()

page_header("⚙️", "Admin Panel", "Sistem yönetimi ve ayarları")

tabs = st.tabs(["👤 Oyuncular", "⚽ Kamplar", "🎨 Ayarlar", "📋 Log"])

with tabs[0]:
    section_title("Oyuncu Fotoğraf ve Kulüp Logosu Yönetimi", "📸")
    st.info("İnternetten (Örn: TFF veya Transfermarkt) kopyaladığınız resim adreslerini (URL) buraya yapıştırın. Resme sağ tıklayıp 'Resim Adresini Kopyala' demeniz yeterlidir.")
    
    c1, c2 = st.columns([1,2])
    with c1:
        admin_age = st.selectbox("Yaş Grubu Seçin", AGE_GROUPS, key="adm_age")
    with c2:
        players = db_manager.get_players(admin_age)
        if players:
            admin_player = st.selectbox("Oyuncu Seçin", players, key="adm_player")
        else:
            admin_player = None
            st.warning("Bu yaş grubunda oyuncu bulunamadı.")
            
    if admin_player:
        # Oyuncunun mevcut bilgilerini DB'den çek
        player_info = db_manager.get_player_info(admin_player)
        curr_photo = player_info.get('photo_url') or ""
        curr_logo = player_info.get('club_logo_url') or ""
        
        st.markdown("### Görsel URL'leri")
        p1, p2 = st.columns(2)
        with p1:
            new_photo = st.text_input("Oyuncu Fotoğrafı (URL)", value=curr_photo, placeholder="https://...")
            if new_photo: 
                st.image(new_photo, width=120, caption="Fotoğraf Önizleme")
        with p2:
            new_logo = st.text_input("Kulüp Logosu (URL)", value=curr_logo, placeholder="https://...")
            if new_logo: 
                st.image(new_logo, width=60, caption="Logo Önizleme")
            
        if st.button("Görselleri Kaydet", type="primary"):
            db_manager.update_player_images(admin_player, new_photo, new_logo)
            db_manager._log_action("image_update", f"{admin_player} görselleri güncellendi")
            st.success(f"✅ {admin_player} için fotoğraflar başarıyla veritabanına kaydedildi! Oyuncu Galerisi'nde görebilirsiniz.")

with tabs[1]:
    st.subheader("Kamp Yönetimi")
    st.info("Yakında: Kamp silme, isim değiştirme veya excel verilerini tamamen temizleme işlemleri eklenecektir.")

with tabs[2]:
    st.subheader("Sistem Ayarları")
    st.info("Yakında: PDF çıktı formatları, genel metrik ayarları buradan yönetilecek.")

with tabs[3]:
    st.subheader("Audit Log")
    try:
        log = db_manager.get_audit_log(50)
        if log is not None and not log.empty:
            st.dataframe(log, width='stretch')
        else:
            st.info("Henüz kayıt bulunmuyor. Veri yükleme veya sistem işlemleri sonrası burada görünecek.")
    except Exception as e:
        st.warning(f"Audit log yüklenemedi: {e}")

st.markdown('<div class="tff-footer"><p>TFF Performans Sistemi · Admin</p></div>', unsafe_allow_html=True)