import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import urllib.parse # WhatsApp mesaj linkindeki Türkçe karakterleri düzeltmek için

# Sayfa Ayarları
st.set_page_config(page_title="Karacaardıç Köyü Dijital Muhtarlık", layout="wide")

# Veritabanı Simülasyonu
if "sikayetler" not in st.session_state:
    st.session_state.sikayetler = [
        {"Tarih": "24.05.2026", "Gonderen": "Hüseyin Şahin (Hane 42)", "Telefon": "05320000042", "Konu": "Yol Yapım / Mıcır", "Detay": "Köy içi ara yolların stabilize mıcırlanması talebi.", "Durum": "Bozkır Bld. İletildi 🔵"},
        {"Tarih": "25.05.2026", "Gonderen": "Anonim Sakin 👤", "Telefon": "-", "Konu": "Su / Kanalizasyon", "Detay": "Yüksek tarlalara giden su vanasında sızıntı var, ilgilenilmesini rica ederim.", "Durum": "Muhtar İncelemesinde 🟡"}
    ]

# Üst Başlık
st.title("🌾 KONYA BOZKIR - KARACAARDIÇ KÖYÜ DİJİTAL MUHTARLIĞI")
st.write("---")

# Sol Panel - Giriş Türü Seçimi
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
st.sidebar.header("Sistem Girişi")
kullanici_turu = st.sidebar.radio("Lütfen Rolünüzü Seçiniz:", ["👤 Hane Sakini (Köylü)", "🔑 Muhtar Girişi"])

st.sidebar.write("---")
st.sidebar.info("📍 İlçe: BOZKIR\n\n🏡 Köy: KARACAARDIÇ")

# ==========================================
# 1. KULLANICI: HANE SAKİNİ (KÖYLÜ) EKRANI
# ==========================================
if kullanici_turu == "👤 Hane Sakini (Köylü)":
    st.header("📝 Vatandaş Talep, Öneri ve Şikayet Masası")
    st.write("Sayın köylümüz, köyümüz için her türlü talebinizi doğrudan muhtarımıza güvenli şekilde iletebilirsiniz.")
    
    st.warning("🔒 Yazdıklarınızı muhtardan başka hiçbir köylü göremez. İsterseniz isminizi tamamen gizleyebilirsiniz.")
    
    with st.form("sikayet_formu", clear_on_submit=False): # WhatsApp butonu görünebilsin diye formu hemen sıfırlamıyoruz
        st.subheader("Dilekçe Kayıt Formu")
        
        anonim_mi = st.checkbox("❌ İsmimi Gizle (Muhtar beni 'Anonim' olarak görsün)", value=False)
        ad_soyad = st.text_input("Adınız Soyadınız:", placeholder="Örn: Veli Yılmaz", disabled=anonim_mi)
        
        # Telefon Numarası Girişi (WhatsApp mesajı için kritik alan)
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
                
                yeni_kayit = {
                    "Tarih": tarih_bugun,
                    "Gonderen": gonderen_isim,
                    "Telefon": telefon_kayit,
                    "Konu": konu,
                    "Detay": detay,
                    "Durum": "Yeni Bildirim 🟢"
                }
                st.session_state.sikayetler.append(yeni_kayit)
                st.success("🎉 Talebiniz başarıyla doğrudan muhtarın paneline iletildi!")
                
                # Eğer anonim değilse köylüye WhatsApp butonu gösteriyoruz
                if not anonim_mi and tel_no:
                    # İstediğin mesaj formatı
                    ham_mesaj = "Değerli köy sakinimiz, vermiş olduğunuz talep muhtarlığımıza ulaşmıştır. Sizleri bu konu hakkında bilgilendireceğiz."
                    # Mesajı internet linkine uygun formata çeviriyoruz (Boşlukları ve Türkçe harfleri korur)
                    kodlanmis_mesaj = urllib.parse.quote(ham_mesaj)
                    
                    # WhatsApp Web / Uygulama tetikleme linki
                    whatsapp_link = f"https://wa.me/90{tel_no}?text={kodlanmis_mesaj}"
                    
                    st.write("---")
                    st.info("📱 Muhtarlıktan onay/bilgilendirme mesajı almak için aşağıdaki yeşil butona basarak WhatsApp hattımızı tetikleyebilirsiniz:")
                    st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;font-size:16px;cursor:pointer;font-weight:bold;">💬 Muhtarlık WhatsApp Bildirimini Başlat</button></a>', unsafe_allow_html=True)

# ==========================================
# 2. KULLANICI: MUHTAR EKRANI (ŞİFRELİ)
# ==========================================
elif kullanici_turu == "🔑 Muhtar Girişi":
    st.header("👨‍💼 Karacaardıç Köyü Muhtarlık Özel Yönetim Paneli")
    
    sifre = st.text_input("Muhtarlık Giriş Şifresini Giriniz:", type="password", help="Giriş şifresi: 4242")
    
    if sifre == "4242":
        st.success("Giriş Başarılı. Sayın Muhtarım Hoş Geldiniz!")
        
        # Göz Boyama Butonları
        st.write("### ⚡ Muhtar Hızlı Erişim Araçları")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📢 Köy Hoparlörüne Bağlan (Anons Yap)"):
                st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") 
                st.success("Köy hoparlör sistemi aktif. Mikrofon açık!")
        with c2:
            if st.button("🚜 İlçe Tarım ÇKS Sistemini Sorgula"):
                st.info("Karacaardıç Köyü Çiftçi Kayıt Sistemi senkronize ediliyor...")
        with c3:
            if st.button("🖨️ Bozkır Kaymakamlığına Rapor Çıkar"):
                st.success("Dilekçeler resmi PDF formatına dönüştürüldü, yazıcıya gönderilmeye hazır!")

        st.write("---")
        
        # Sekmeler
        tab1, tab2, tab3 = st.tabs(["📩 Köylünün Şikayetleri (Gizli)", "🗺️ Canlı Uydu Haritası", "👥 Nüfus & Hane Listesi"])
        
        with tab1:
            st.subheader("📬 Gelen İstek ve Şikayet Listesi")
            st.write("Köylülerin gönderdiği mesajları buradan inceleyebilir, telefon numaralarını görebilir ve silebilirsiniz:")
            
            if len(st.session_state.sikayetler) > 0:
                for idx, sikayet in enumerate(st.session_state.sikayetler):
                    with st.expander(f"📋 {sikayet['Tarih']} - {sikayet['Gonderen']} ({sikayet['Konu']})"):
                        st.write(f"**Telefon:** {sikayet['Telefon']}")
                        st.write(f"**Detay:** {sikayet['Detay']}")
                        st.write(f"**Durum:** {sikayet['Durum']}")
                        
                        col_sil, col_wa = st.columns([1, 4])
                        with col_sil:
                            if st.button(f"Dilekçeyi Sil 🗑️", key=f"sil_{idx}"):
                                st.session_state.sikayetler.pop(idx)
                                st.rerun()
                        
                        # Muhtar da köylüye kendi panelinden tek tıkla WhatsApp mesajı atabilsin diye ekstra kısım
                        if sikayet['Telefon'] != "-":
                            with col_wa:
                                muhtar_mesaj = urllib.parse.quote(f"Merhaba ben Karacaardıç Köyü Muhtarı. {sikayet['Tarih']} tarihli '{sikayet['Konu']}' hakkındaki talebiniz incelenmiştir.")
                                muhtar_wa_link = f"https://wa.me/90{sikayet['Telefon']}?text={muhtar_mesaj}"
                                st.markdown(f'<a href="{muhtar_wa_link}" target="_blank"><button style="background-color:#128C7E;color:white;border:none;padding:5px 10px;border-radius:3px;font-size:12px;cursor:pointer;">💬 Vatandaşa WhatsApp\'tan Dönüş Yap</button></a>', unsafe_allow_html=True)
            else:
                st.info("Okunmamış veya gelen herhangi bir dilekçe bulunmamaktadır.")
                
        with tab2:
            st.subheader("🗺️ Karacaardıç Köyü Canlı Uydu Görüntüsü")
            karacaardic_koordinat = [37.1517, 32.2222] 
            m = folium.Map(
                location=karacaardic_koordinat, 
                zoom_start=16, 
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri World Imagery'
            )
            folium.Marker([37.1517, 32.2222], popup="<b>Karacaardıç Köy Merkezi</b>", icon=folium.Icon(color="red", icon="home")).add_to(m)
            st_folium(m, width=900, height=450)
            
        with tab3:
            st.subheader("👥 Karacaardıç Nüfus Defteri")
            data = {
                "Hane No": [101, 102, 103, 104, 105],
                "Hane Reisi": ["Mustafa Karaca", "Mehmet Öztürk", "Ayşe Yılmaz", "İbrahim Dağ", "Ali Akpınar"],
                "Kişi Sayısı": [4, 3, 5, 2, 6],
                "Büyükbaş Hayvan": [12, 0, 8, 22, 4],
                "Traktör": ["Var", "Yok", "Var", "Var", "Yok"]
            }
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            
    elif sifre != "" and sifre != "4242":
        st.error("❌ Hatalı Şifre!")