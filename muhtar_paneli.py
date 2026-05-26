import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import urllib.parse
import sqlite3

# Sayfa Ayarları
st.set_page_config(page_title="Karacaardıç Köyü Dijital Muhtarlık", layout="wide")

# ==========================================
# 💾 KALICI VERİTABANI AYARLARI (SQLITE)
# ==========================================
def veritabanı_kur():
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sikayetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            gonderen TEXT,
            telefon TEXT,
            konu TEXT,
            detay TEXT,
            durum TEXT
        )
    ''')
    conn.commit()
    conn.close()

def verileri_yukle():
    veritabanı_kur()
    conn = sqlite3.connect("muhtar_veritabanı.db")
    df = pd.read_sql_query("SELECT * FROM sikayetler", conn)
    conn.close()
    return df.to_dict(orient="records")

def veriyi_kaydet(tarih, gonderen, telefon, konu, detay, durum):
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sikayetler (tarih, gonderen, telefon, konu, detay, durum)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tarih, gonderen, telefon, konu, detay, durum))
    conn.commit()
    conn.close()

def veriyi_sil(kayit_id):
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sikayetler WHERE id = ?", (kayit_id,))
    conn.commit()
    conn.close()

# Üst Başlık
st.title("🌾 KONYA BOZKIR - KARACAARDIÇ KÖYÜ DİJİTAL MUHTARLIĞI")
st.write("---")

# Sol Panel - Giriş Türü Seçimi
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
st.sidebar.header("Sistem Girişi")
kullanici_turu = st.sidebar.radio("Lütfen Rolünüzü Seçiniz:", ["👤 Hane Sakini (Köylü)", "🔑 Muhtar Girişi"])

st.sidebar.write("---")
st.sidebar.info("📍 İlçe: BOZKIR\n\n🏡 Köy: KARACAARDIÇ")

# Canlı verileri çek
mevcut_sikayetler = verileri_yukle()

# ==========================================
# 1. KULLANICI: HANE SAKİNİ (KÖYLÜ) EKRANI
# ==========================================
if kullanici_turu == "👤 Hane Sakini (Köylü)":
    st.header("📝 Vatandaş Talep, Öneri ve Şikayet Masası")
    st.write("Sayın köylümüz, köyümüz için her türlü talebinizi doğrudan muhtarımıza güvenli şekilde iletebilirsiniz.")
    st.warning("🔒 Yazdıklarınızı muhtardan başka hiçbir köylü göremez. İsterseniz isminizi tamamen gizleyebilirsiniz.")
    
    with st.form("sikayet_formu", clear_on_submit=True):
        st.subheader("Dilekçe Kayıt Formu")
        
        anonim_mi = st.checkbox("❌ İsmimi Gizle (Muhtar beni 'Anonim' olarak görsün)", value=False)
        ad_soyad = st.text_input("Adınız Soyadınız:", placeholder="Örn: Veli Yılmaz", disabled=anonim_mi)
        tel_no = st.text_input("Telefon Numaranız (Başında 0 olmadan):", placeholder="532XXXXXXX", max_chars=10, disabled=anonim_mi)
        
        konu = st.selectbox("Konu:", ["Yol Yapım / Mıcır / Asfalt", "Tarımsal Sulama / Çeşmeler", "Elektrik / Sokak Lambası arızası", "Diğer"])
        detay = st.text_area("Talebinizin Detayı:")
        
        submitted = st.form_submit_button("Muhtarın Ekranına Gönder 🚀")
        
        if submitted:
            if not detay:
                st.error("Lütfen detay kısmını boş bırakmayınız.")
            elif not anonim_mi and not tel_no:
                st.error("Lütfen telefon numaranızı giriniz (Veya anonim seçeneğini kullanınız).")
            else:
                gonderen_isim = "Anonim Sakin 👤" if anonim_mi or not ad_soyad else ad_soyad
                telefon_kayit = "-" if anonim_mi or not tel_no else tel_no
                tarih_bugun = datetime.date.today().strftime('%d.%m.%Y')
                
                # Veritabanına Kalıcı Kayıt
                veriyi_kaydet(tarih_bugun, gonderen_isim, telefon_kayit, konu, detay, "Yeni Bildirim 🟢")
                st.success("🎉 Talebiniz başarıyla doğrudan muhtarın kalıcı paneline iletildi!")
                
                # KÖYLÜ İÇİN OTOMATİK WHATSAPP ONAY BUTONU
                if not anonim_mi and tel_no:
                    # Tam istediğin o saygılı hitap şekli
                    ham_mesaj = f"Sayın {gonderen_isim}, saygıdeğer köy sakinimiz; vermiş olduğunuz talep muhtarlığımıza ulaşmıştır. Sizleri bu konu hakkında en kısa sürede bilgilendireceğiz."
                    kodlanmis_mesaj = urllib.parse.quote(ham_mesaj)
                    whatsapp_link = f"https://wa.me/90{tel_no}?text={kodlanmis_mesaj}"
                    
                    st.write("---")
                    st.info("📱 Muhtarlıktan telefonunuza resmi onay mesajı gelmesi için aşağıdaki butona basarak WhatsApp hattını tetikleyebilirsiniz:")
                    st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;font-size:16px;cursor:pointer;font-weight:bold;">💬 Muhtarlık WhatsApp Onayını Al</button></a>', unsafe_allow_html=True)

# ==========================================
# 2. KULLANICI: MUHTAR EKRANI (ŞİFRELİ)
# ==========================================
elif kullanici_turu == "🔑 Muhtar Girişi":
    st.header("👨‍💼 Karacaardıç Köyü Muhtarlık Özel Yönetim Paneli")
    sifre = st.text_input("Muhtarlık Giriş Şifresini Giriniz:", type="password")
    
    if sifre == "4242":
        st.success("Giriş Başarılı. Sayın Muhtarım Hoş Geldiniz!")
        
        tab1, tab2 = st.tabs(["📩 Köylünün Şikayetleri (Kalıcı Veritabanı)", "🗺️ Canlı Uydu Haritası"])
        
        with tab1:
            st.subheader("📬 Gelen İstek ve Şikayet Listesi")
            
            # Üst bilgi alanında yeni şikayet sayısını göstererek muhtara bildirim yapıyoruz
            yeni_sayisi = sum(1 for s in mevcut_sikayetler if s['durum'] == "Yeni Bildirim 🟢")
            if yeni_sayisi > 0:
                st.sidebar.warning(f"🔔 Muhtarım, panonuzda incelenmeyi bekleyen {yeni_sayisi} yeni şikayet var!")
            
            if len(mevcut_sikayetler) > 0:
                for sikayet in mevcut_sikayetler:
                    with st.expander(f"📋 {sikayet['tarih']} - {sikayet['gonderen']} ({sikayet['konu']})"):
                        st.write(f"**Telefon:** {sikayet['telefon']}")
                        st.write(f"**Detay:** {sikayet['detay']}")
                        st.write(f"**Durum:** {sikayet['durum']}")
                        
                        col_sil, col_wa = st.columns([1, 4])
                        with col_sil:
                            if st.button(f"Dilekçeyi Sil 🗑️", key=f"sil_{sikayet['id']}"):
                                veriyi_sil(sikayet['id'])
                                st.rerun()
                        
                        # MUHTARIN KÖYLÜYE WHATSAPP'TAN ÖZEL CEVAP DÖNME BUTONU
                        if sikayet['telefon'] != "-":
                            with col_wa:
                                # Muhtar için de isme özel hitap taslağı hazırlandı
                                muhtar_ham_mesaj = f"Sayın {sikayet['gonderen']}, saygıdeğer köy sakinimiz; iletmiş olduğunuz '{sikayet['konu']}' konulu talebiniz muhtarlığımızca incelenmiş ve işleme alınmıştır."
                                muhtar_kodlanmis_mesaj = urllib.parse.quote(muhtar_ham_mesaj)
                                muhtar_wa_link = f"https://wa.me/90{sikayet['telefon']}?text={muhtar_kodlanmis_mesaj}"
                                st.markdown(f'<a href="{muhtar_wa_link}" target="_blank"><button style="background-color:#128C7E;color:white;border:none;padding:5px 10px;border-radius:3px;font-size:12px;cursor:pointer;">💬 Vatandaşa WhatsApp\'tan Resmi Cevap Yaz</button></a>', unsafe_allow_html=True)
            else:
                st.info("Okunmamış veya gelen herhangi bir dilekçe bulunmamaktadır.")
                
        with tab2:
            st.subheader("🗺️ Karacaardıç Köyü Canlı Uydu Görüntüsü")
            karacaardic_koordinat = [37.1517, 32.2222] 
            m = folium.Map(location=karacaardic_koordinat, zoom_start=16, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri World Imagery')
            folium.Marker([37.1517, 32.2222], popup="<b>Karacaardıç Köy Merkezi</b>", icon=folium.Icon(color="red", icon="home")).add_to(m)
            st_folium(m, width=900, height=450)
            
    elif sifre != "" and sifre != "4242":
        st.error("❌ Hatalı Şifre!")
