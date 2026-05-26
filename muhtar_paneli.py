import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import urllib.parse
import sqlite3
import random
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Karacaardıç Köyü Dijital Muhtarlık", layout="wide")

# Gerçek Karacaardıç Koordinatları
KUP_ENLEM = 37.2025
KUP_BOYLAM = 32.2285

# ==========================================
# 💾 KALICI VERİTABANI AYARLARI (SQLITE)
# ==========================================
def veritabanı_kur():
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sikayetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            takip_kodu TEXT,
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
    try:
        df = pd.read_sql_query("SELECT * FROM sikayetler", conn)
        conn.close()
        return df.to_dict(orient="records")
    except:
        conn.close()
        return []

def veriyi_kaydet(takip_kodu, tarih, gonderen, telefon, konu, detay, durum):
    veritabanı_kur()
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sikayetler (takip_kodu, tarih, gonderen, telefon, konu, detay, durum)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (takip_kodu, tarih, gonderen, telefon, konu, detay, durum))
    conn.commit()
    conn.close()

def durum_guncelle(kayit_id, yeni_durum):
    veritabanı_kur()
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE sikayetler SET durum = ? WHERE id = ?", (yeni_durum, kayit_id))
    conn.commit()
    conn.close()

def veriyi_sil(kayit_id):
    veritabanı_kur()
    conn = sqlite3.connect("muhtar_veritabanı.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sikayetler WHERE id = ?", (kayit_id,))
    conn.commit()
    conn.close()

# Üst Başlık
st.title("🌾 KONYA BOZKIR - KARACAARDIÇ KÖYÜ DİJİTAL MUHTARLIĞI")
st.write("---")

# ==========================================
# ⚡ SOL PANEL & MODEREN MÜHENDİSLİK REKLAMI
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
st.sidebar.header("Sistem Girişi")
kullanici_turu = st.sidebar.radio("Lütfen Rolünüzü Seçiniz:", ["👤 Hane Sakini (Köylü)", "🔑 Muhtar Girişi"])

st.sidebar.write("---")
st.sidebar.info("📍 İlçe: BOZKIR\n\n🏡 Köy: KARACAARDIÇ")

st.sidebar.write("---")
# Kurumsal Reklam Alanı
st.sidebar.markdown(
    """
    <div style="background-color:#141414; padding:15px; border-radius:10px; border: 2px solid #FF4B4B; text-align:center; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);">
        <h4 style="color:#FF4B4B; margin-top:0; font-weight:bold; letter-spacing:1px;">⚡ MODEREN MÜHENDİSLİK ⚡</h4>
        <p style="color:#FFFFFF; font-size:13px; margin-bottom:5px;">Endüstriyel Lazer Kesim & Mekanik Tasarım Çözümleri</p>
        <hr style="border-color:#333; margin:8px 0;">
        <p style="color:#A3A3A3; font-size:11px; margin:0;"><i>"Bu dijital portal MODEREN Mühendislik katkılarıyla hazırlanmıştır."</i></p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Canlı verileri çek
mevcut_sikayetler = verileri_yukle()

# ==========================================
# 1. KULLANICI: HANE SAKİNİ (KÖYLÜ) EKRANI
# ==========================================
if kullanici_turu == "👤 Hane Sakini (Köylü)":
    
    # HAVA DURUMU VE SAAT MODÜLÜ (Üst Alan)
    col_hava, col_saat = st.columns([3, 1])
    with col_hava:
        try:
            hava_url = f"https://api.open-meteo.com/v1/forecast?latitude={KUP_ENLEM}&longitude={KUP_BOYLAM}&current_weather=true"
            res = requests.get(hava_url).json()
            temp = res["current_weather"]["temperature"]
            wind = res["current_weather"]["windspeed"]
            st.info(f"🌍 **Karacaardıç Köyü Canlı Hava Durumu:** {temp} °C | **Rüzgar Hızı:** {wind} km/h")
        except:
            st.info("🌍 **Karacaardıç Köyü Canlı Hava Durumu:** 22 °C (Bağlantı güncelleniyor...)")
            
    with col_saat:
        simdi = datetime.datetime.now()
        st.metric(label="📅 Dijital Saat", value=simdi.strftime("%H:%M"), delta=simdi.strftime("%d.%m.%Y"))
        
    st.write("---")

    tab_gonder, tab_sorgula, tab_harita = st.tabs(["✍️ Yeni Dilekçe Gönder", "🔍 Dilekçe Durumu Sorgula", "📍 Köyümüzün Haritası"])
    
    with tab_gonder:
        st.header("📝 Vatandaş Talep, Öneri ve Şikayet Masası")
        st.write("Taleplerinizi doğrudan muhtarımıza güvenli şekilde iletebilirsiniz.")
        
        with st.form("sikayet_formu", clear_on_submit=True):
            anonim_mi = st.checkbox("❌ İsmimi Gizle (Şikayet tamamen anonim gitsin)", value=False)
            ad_soyad = st.text_input("Adınız Soyadınız:", placeholder="Örn: Veli Yılmaz", disabled=anonim_mi)
            tel_no = st.text_input("Telefon Numaranız (Başında 0 olmadan):", placeholder="532XXXXXXX", max_chars=10, disabled=anonim_mi)
            konu = st.selectbox("Konu:", ["Yol Yapım / Mıcır / Asfalt", "Tarımsal Sulama / Çeşmeler", "Elektrik / Sokak Lambası arızası", "Diğer"])
            detay = st.text_area("Talebinizin Detayı:")
            
            submitted = st.form_submit_button("Muhtarın Ekranına Gönder 🚀")
            
            if submitted:
                if not detay:
                    st.error("Lütfen detay kısmını boş bırakmayınız.")
                else:
                    gonderen_isim = "Anonim Sakin 👤" if anonim_mi or not ad_soyad else ad_soyad
                    telefon_kayit = "-" if anonim_mi or not tel_no else tel_no
                    tarih_bugun = datetime.date.today().strftime('%d.%m.%Y')
                    
                    rastgele_kod = f"KA-{random.randint(1000, 9999)}"
                    
                    veriyi_kaydet(rastgele_kod, tarih_bugun, gonderen_isim, telefon_kayit, konu, detay, "Muhtar İncelemesinde (Okunmadı) 🟡")
                    
                    st.success(f"🎉 Talebiniz başarıyla veritabanına iletildi!")
                    st.subheader(f"🔑 SİZİN GİZLİ TAKİP KODUNUZ: {rastgele_kod}")
                    st.info("🚨 Lütfen bu kodu not edin! Şikayetinizin durumunu 'Dilekçe Durumu Sorgula' kısmından bu kodla takip edeceksiniz.")
                    
                    # Muhtara WhatsApp'tan Bildirim Tetikleme Alanı
                    muhtar_telefon = "5XXXXXXXXX" # BURAYA KENDİ TELEFON NUMARANIZI YAZIN MUHTARIM
                    bildirim_metni = f"🔔 *YENİ TALEP GELDİ (Dijital Muhtarlık)*\n\n👤 *Gönderen:* {gonderen_isim}\n📞 *Tel:* {telefon_kayit}\n📁 *Konu:* {konu}\n📝 *Detay:* {detay}\n🔑 *Takip Kod:* {rastgele_kod}"
                    kodlanmis_bildirim = urllib.parse.quote(bildirim_metni)
                    muhtar_whatsapp_link = f"https://wa.me/90{muhtar_telefon}?text={kodlanmis_bildirim}"
                    
                    st.markdown("---")
                    st.write("📢 **Muhtara anlık bildirim göndermek için aşağıdaki butona basın:**")
                    st.markdown(f'<a href="{muhtar_whatsapp_link}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:12px 25px;border-radius:5px;font-size:16px;cursor:pointer;font-weight:bold;box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">💬 Muhtara WhatsApp Bildirimi Gönder</button></a>', unsafe_allow_html=True)

    with tab_sorgula:
        st.header("🔍 Anonim / Kişisel Dilekçe Takip Sistemi")
        sorgu_kodu = st.text_input("Lütfen size verilen Takip Kodunu giriniz (Örn: KA-1234):").strip()
        
        if sorgu_kodu:
            bulunanlar = [s for s in mevcut_sikayetler if s.get('takip_kodu', '').lower() == sorgu_kodu.lower()]
            if bulunanlar:
                dilekce = bulunanlar[0]
                st.write("---")
                st.subheader("📊 Dilekçenizin Canlı Durumu:")
                
                if "Okunmadı" in dilekce['durum']:
                    st.warning(f"📌 GÜNCEL DURUM: {dilekce['durum']}")
                elif "Okudu" in dilekce['durum']:
                    st.info(f"📌 GÜNCEL DURUM: {dilekce['durum']}")
                else:
                    st.success(f"📌 GÜNCEL DURUM: {dilekce['durum']}")
                    
                st.write(f"📅 **Gönderim Tarihi:** {dilekce['tarih']}")
                st.write(f"📁 **Konu Başlığı:** {dilekce['konu']}")
                st.write(f"💬 **Yazdığınız Detay:** {dilekce['detay']}")
            else:
                st.error("❌ Hatalı veya geçersiz bir takip kodu girdiniz. Lütfen kontrol edin.")
                
    with tab_harita:
        st.subheader("📍 Karacaardıç Köyü Haritadaki Doğru Konumu")
        m_koy = folium.Map(location=[KUP_ENLEM, KUP_BOYLAM], zoom_start=15)
        folium.Marker([KUP_ENLEM, KUP_BOYLAM], popup="<b>Karacaardıç Köyü</b>", icon=folium.Icon(color="green", icon="tree-conifer")).add_to(m_koy)
        st_folium(m_koy, width=900, height=450)

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
            
            if len(mevcut_sikayetler) > 0:
                for sikayet in mevcut_sikayetler:
                    with st.expander(f"📋 {sikayet['tarih']} - {sikayet['gonderen']} [{sikayet['takip_kodu']}]"):
                        st.write(f"**Güncel Durum:** {sikayet['durum']}")
                        st.write(f"**Telefon:** {sikayet['telefon']}")
                        st.write(f"**Detay:** {sikayet['detay']}")
                        
                        st.write("**⚙️ Bu Dilekçenin Durumunu Değiştir (Köylü Canlı Görecek):**")
                        c_okundu, c_cozuldu, c_sil = st.columns(3)
                        with c_okundu:
                            if st.button("👁️ Okundu Yap", key=f"okundu_{sikayet['id']}"):
                                durum_guncelle(sikayet['id'], "Muhtar Okudu ve İşleme Aldı 🔵")
                                st.rerun()
                        with c_cozuldu:
                            if st.button("✅ Çözüldü Yap", key=f"cozuldu_{sikayet['id']}"):
                                durum_guncelle(sikayet['id'], "Sorun Muhtar Tarafından Çözüldü 🟢")
                                st.rerun()
                        with c_sil:
                            if st.button("🗑️ Sil", key=f"sil_{sikayet['id']}"):
                                veriyi_sil(sikayet['id'])
                                st.rerun()
                                
                        if sikayet['telefon'] != "-":
                            st.write("---")
                            muhtar_ham_mesaj = f"Sayın {sikayet['gonderen']}, saygıdeğer köy sakinimiz; iletmiş olduğunuz {sikayet['takip_kodu']} kodlu talebiniz muhtarlığımızca incelenmiştir."
                            muhtar_kodlanmis_mesaj = urllib.parse.quote(muhtar_ham_mesaj)
                            muhtar_wa_link = f"https://wa.me/90{sikayet['telefon']}?text={muhtar_kodlanmis_mesaj}"
                            st.markdown(f'<a href="{muhtar_wa_link}" target="_blank"><button style="background-color:#128C7E;color:white;border:none;padding:5px 10px;border-radius:3px;font-size:12px;cursor:pointer;">💬 Vatandaşa WhatsApp\'tan Resmi Cevap Yaz</button></a>', unsafe_allow_html=True)
            else:
                st.info("Okunmamış veya gelen herhangi bir dilekçe bulunmamaktadır.")
                
        with tab2:
            st.subheader("🗺️ Karacaardıç Köyü Canlı Uydu Görüntüsü (Gerçek Konum)")
            m = folium.Map(location=[KUP_ENLEM, KUP_BOYLAM], zoom_start=16, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri World Imagery')
            folium.Marker([KUP_ENLEM, KUP_BOYLAM], popup="<b>Karacaardıç Köy Merkezi</b>", icon=folium.Icon(color="red", icon="home")).add_to(m)
            st_folium(m, width=900, height=450)
            
    elif sifre != "" and sifre != "4242":
        st.error("❌ Hatalı Şifre!")
