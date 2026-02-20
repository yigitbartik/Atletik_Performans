"""
ATLETİK PERFORMANS SİSTEMİ
Kimlik Doğrulama ve Güvenlik Modülü
"""

import streamlit as st
import hashlib
import sqlite3
from datetime import datetime
import json
import os

USERS_DB = "users.db"

class SecurityManager:
    """Kullanıcı kimlik doğrulama ve yönetimi"""
    
    def __init__(self):
        self.init_users_db()
    
    def init_users_db(self):
        """Kullanıcı veritabanını başlat"""
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            rol TEXT DEFAULT 'viewer',
            yas_grubu TEXT,
            ekleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            aktif INTEGER DEFAULT 1
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            status TEXT
        )
        ''')
        
        # Default admin kullanıcı oluştur (password: admin123)
        try:
            cursor.execute('''
            INSERT INTO users (username, password_hash, email, rol, yas_grubu, aktif)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin',
                self.hash_password('admin123'),
                'admin@tff.org.tr',
                'admin',
                'Tüm Yaş Grupları',
                1
            ))
        except:
            pass  # Admin zaten var
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password):
        """Şifreyi hashle"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, username, password):
        """Kullanıcı giriş doğrula"""
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? AND aktif = 1', (username,))
        user = cursor.fetchone()
        
        if user:
            stored_hash = user[2]  # password_hash
            if stored_hash == self.hash_password(password):
                conn.close()
                return True, user  # (username, password_hash, email, rol, yas_grubu)
        
        conn.close()
        return False, None
    
    def add_user(self, username, password, email, rol='viewer', yas_grubu='Tüm'):
        """Yeni kullanıcı ekle"""
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO users (username, password_hash, email, rol, yas_grubu)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                username,
                self.hash_password(password),
                email,
                rol,
                yas_grubu
            ))
            conn.commit()
            conn.close()
            return True, "Kullanıcı başarıyla oluşturuldu"
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def get_all_users(self):
        """Tüm kullanıcıları getir"""
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, email, rol, yas_grubu, ekleme_tarihi, aktif FROM users')
        users = cursor.fetchall()
        conn.close()
        return users
    
    def delete_user(self, username):
        """Kullanıcıyı deaktif et"""
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET aktif = 0 WHERE username = ?', (username,))
        conn.commit()
        conn.close()
    
    def change_password(self, username, old_password, new_password):
        """Şifre değiştir"""
        success, user = self.verify_login(username, old_password)
        if not success:
            return False, "Mevcut şifre yanlış"
        
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password_hash = ? WHERE username = ?',
            (self.hash_password(new_password), username)
        )
        conn.commit()
        conn.close()
        return True, "Şifre başarıyla değiştirildi"
    
    def log_login(self, username, status="SUCCESS"):
        """Giriş kaydı ekle"""
        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO login_logs (username, status) VALUES (?, ?)',
            (username, status)
        )
        conn.commit()
        conn.close()

def login_page():
    """Giriş sayfası"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #003366;'>🏆 TFF Genç Milli Takımlar</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #D32F2F;'>Atletik Performans Sistemi</h3>", 
                   unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center;'>🔐 Kullanıcı Girişi</h4>", 
                       unsafe_allow_html=True)
            
            username = st.text_input("👤 Kullanıcı Adı", placeholder="admin")
            password = st.text_input("🔑 Şifre", type="password", placeholder="Şifrenizi giriniz")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                login_btn = st.form_submit_button("📍 Giriş Yap", use_container_width=True)
            with col_btn2:
                signup_btn = st.form_submit_button("➕ Kayıt Ol", use_container_width=True)
            
            if login_btn:
                sm = SecurityManager()
                success, user = sm.verify_login(username, password)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_rol = user[3]  # rol
                    st.session_state.user_yas_grubu = user[4]  # yas_grubu
                    sm.log_login(username, "SUCCESS")
                    st.success("✅ Giriş başarılı! Yönlendiriliyorsunuz...")
                    st.rerun()
                else:
                    sm.log_login(username, "FAILED")
                    st.error("❌ Kullanıcı adı veya şifre yanlış!")
            
            if signup_btn:
                st.info("💡 Yeni hesap oluşturmak için lütfen sistem yöneticisine başvurunuz.")
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 30px;'>
        <p>📧 <strong>Sorunlar için:</strong> admin@tff.org.tr</p>
        <p>🔐 <strong>Güvenlik Notu:</strong> Bu sistem gizli ve sadece yetkili kullanıcılar içindir.</p>
        </div>
        """, unsafe_allow_html=True)

def logout():
    """Çıkış yap"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_rol = None
    st.session_state.user_yas_grubu = None
    st.rerun()

def require_login(func):
    """Giriş kontrolü decorator'u"""
    def wrapper():
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        
        if not st.session_state.logged_in:
            login_page()
            st.stop()
        
        return func()
    
    return wrapper

def require_admin(func):
    """Admin kontrolü decorator'u"""
    def wrapper():
        if 'logged_in' not in st.session_state or not st.session_state.logged_in:
            st.error("❌ Giriş yapmanız gerekiyor!")
            st.stop()
        
        if st.session_state.user_rol != 'admin':
            st.error("❌ Bu sayfaya erişim izniniz yok! (Admin gerekli)")
            st.stop()
        
        return func()
    
    return wrapper

def create_user_management_page():
    """Kullanıcı yönetim sayfası (Admin için)"""
    
    st.markdown("<h3 style='color: #D32F2F;'>👥 Kullanıcı Yönetimi</h3>", unsafe_allow_html=True)
    
    sm = SecurityManager()
    
    tab1, tab2, tab3 = st.tabs(["Kullanıcı Listesi", "Yeni Kullanıcı", "Şifre Değiştir"])
    
    with tab1:
        st.subheader("Mevcut Kullanıcılar")
        users = sm.get_all_users()
        
        if users:
            users_df = pd.DataFrame(users, columns=['ID', 'Kullanıcı Adı', 'Email', 'Rol', 'Yaş Grubu', 'Ekleme Tarihi', 'Aktif'])
            st.dataframe(users_df, use_container_width=True, hide_index=True)
        else:
            st.info("Kullanıcı yok")
    
    with tab2:
        st.subheader("Yeni Kullanıcı Ekle")
        
        with st.form("yeni_kullanici_form"):
            username = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            email = st.text_input("Email")
            
            col_rol = st.columns(2)
            with col_rol[0]:
                rol = st.selectbox("Rol", ["viewer", "editor", "admin"])
            with col_rol[1]:
                yas_grubu = st.selectbox("Yaş Grubu", ["Tüm", "U15", "U16", "U17", "U19", "U20", "U21"])
            
            if st.form_submit_button("Kullanıcı Ekle"):
                if username and password and email:
                    success, msg = sm.add_user(username, password, email, rol, yas_grubu)
                    if success:
                        st.success(msg)
                    else:
                        st.error(f"Hata: {msg}")
                else:
                    st.warning("Tüm alanları doldurunuz!")
    
    with tab3:
        st.subheader("Şifre Değiştir")
        
        with st.form("sifre_degistir_form"):
            old_password = st.text_input("Mevcut Şifre", type="password")
            new_password = st.text_input("Yeni Şifre", type="password")
            new_password_confirm = st.text_input("Yeni Şifre (Tekrar)", type="password")
            
            if st.form_submit_button("Şifre Değiştir"):
                if old_password and new_password:
                    if new_password != new_password_confirm:
                        st.error("Yeni şifreler eşleşmiyor!")
                    else:
                        success, msg = sm.change_password(
                            st.session_state.username,
                            old_password,
                            new_password
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                else:
                    st.warning("Tüm alanları doldurunuz!")

# Test için
if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        st.write(f"Hoş geldiniz, {st.session_state.username}!")
        if st.button("Çıkış Yap"):
            logout()
