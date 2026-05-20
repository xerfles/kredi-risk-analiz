import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Sayfa Genişlik ve Tema Ayarları
st.set_page_config(page_title="Advanced Risk Intelligence", layout="wide")

# Model Yükleme
try:
    model = joblib.load('kredi_modeli.pkl')
except:
    model = None

# Başlık Paneli
st.title("🛡️ Advanced Credit Risk Intelligence & Macro Stress Testing")
st.markdown("_Risk Yönetimi ve Stratejik Karar Destek Sistemi - Versiyon 2026.2_")
st.write("---")

# Layout Bölünmesi
col1, col2 = st.columns([1, 2])

with col1:
    st.header("👤 Müşteri & Makro Parametreler")
    
    # Yeni Eklenen: Makroekonomik Konjonktür (Stres Testi Filtresi)
    st.subheader("🌐 Makroekonomik Senaryo")
    makro_durum = st.selectbox("Mevcut Ekonomik Konjonktür", 
                               ["Normal Ekonomik Şartlar", "Resesyon / Sıkılaşma Dönemi", "Ekonomik Büyüme / Genişleme"])
    
    st.write("---")
    st.subheader("📊 Müşteri Mikro Verileri")
    gelir = st.number_input("Yıllık Gelir ($)", 20000, 250000, value=75000, step=5000)
    skor = st.slider("Kredi Skoru (FICO)", 300, 850, value=640)
    borc = st.slider("Borç / Gelir Oranı (DTI)", 0.0, 1.0, value=0.38, step=0.01)
    yil = st.number_input("Mevcut İş Süresi (Yıl)", 0, 40, value=4)
    
    st.write("---")
    st.subheader("🏦 Kredi Talep Detayları")
    kredi_turu = st.selectbox("Kredi Türü", ["İhtiyaç Kredisi", "Konut Kredisi", "Ticari Kredi"])
    talep_edilen = st.number_input("Talep Edilen Kredi Tutarı ($)", 5000, 500000, value=30000, step=5000)

    st.write(" ")
    analiz_butonu = st.button("Uçtan Uca Finansal Analiz Yap", use_container_width=True)

with col2:
    st.header("📉 Risk Metrikleri ve Karar Matrisi")
    
    if analiz_butonu:
        # Finansal Hesaplamalar
        aylik_gelir = gelir / 12
        mevcut_aylik_borc = aylik_gelir * borc
        
        # Makro senaryoya göre risk çarpanı belirleme (İktisat vizyonu!)
        risk_multiplier = 1.0
        if makro_durum == "Resesyon / Sıkılaşma Dönemi":
            risk_multiplier = 0.75 # Banka risk iştahını düşürür, onay zorlaşır
        elif makro_durum == "Ekonomik Büyüme / Genişleme":
            risk_multiplier = 1.15 # Banka daha rahat kredi verir
            
        # Olasılık Tabanı
        base_prob = 0.5
        if skor > 700: base_prob += 0.25
        if skor < 520: base_prob -= 0.35
        if borc < 0.30: base_prob += 0.15
        if borc > 0.55: base_prob -= 0.3
        if yil > 5: base_prob += 0.1
        
        # Makro etkiyi yansıt
        onay_olasiligi = np.clip(base_prob * risk_multiplier, 0.01, 0.99)
        karar = 1 if onay_olasiligi >= 0.52 else 0
        
        # Üst Metrik Kartları
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Kredi Onay İhtimali", value=f"%{onay_olasiligi*100:.1f}")
        with m2:
            durum = "DÜŞÜK" if onay_olasiligi > 0.75 else ("ORTA" if onay_olasiligi > 0.48 else "YÜKSEK")
            st.metric(label="Portföy Risk Skalası", value=durum)
        with m3:
            st.metric(label="Mevcut Aylık Borç Yükü", value=f"${mevcut_aylik_borc:.0f}")
        with m4:
            # Talep edilen kredinin gelire oranı
            kredi_gelir_orani = (talep_edilen / gelir) * 100
            st.metric(label="Kredi / Yıllık Gelir Oranı", value=f"%{kredi_gelir_orani:.1f}")
            
        # Güven Barı
        st.progress(float(onay_olasiligi))
        st.write(" ")
        
        # Grafikler Yan Yana (Double Column Layout)
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**1. Müşteri Gelirinin Sektör Dağılımındaki Yeri**")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            mock_gelirler = np.random.normal(60000, 18000, 1000)
            sns.kdeplot(mock_gelirler, fill=True, color="#2b5c8f", alpha=0.4, label="Banka Müşteri Havuzu", ax=ax1)
            ax1.axvline(gelir, color="red", linestyle="--", linewidth=2, label="Mevcut Başvuru")
            ax1.set_xlabel("Yıllık Gelir ($)")
            ax1.legend()
            st.pyplot(fig1)
            
        with g2:
            st.write("**2. Finansal Kaldıraç & DTI Kıyaslaması**")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            kategoriler = ['Müşteri DTI Oranı', 'Kritik Eşik (DTI)', 'Sektör Ortalaması']
            degerler = [borc, 0.50, 0.35]
            colors = ['#d9534f' if borc > 0.5 else '#5cb85c', '#292b2c', '#0275d8']
            ax2.bar(kategoriler, degerler, color=colors)
            ax2.set_ylabel("Oran (%)")
            ax2.set_ylim(0, 1.0)
            st.pyplot(fig2)
            
        # Analist Raporu ve Makro Şerhi
        st.write(" ")
        st.subheader("📋 Kredi Komitesi & Analist Strateji Notu")
        
        if karar == 1:
            st.success(f"**ONAY TAVSİYESİ:** Müşteri, seçilen **'{makro_durum}'** senaryosundaki stres testinden başarıyla geçmiştir. Kredi Skoru ({skor}) ve finansal kaldıraçı borç servis kapasitesini desteklemektedir.")
        else:
            st.error(f"**RED TAVSİYESİ:** Risk tespit edilmiştir. Özellikle **'{makro_durum}'** şokları altında müşterinin borç ödeme esnekliğinin kırılacağı öngörülmektedir. Tahsis politikası gereği başvuru askıya alınmıştır.")
            
    else:
        st.info("Sol taraftaki panelden müşteri bilgilerini girip, ülkenin makroekonomik durumunu seçerek 'Uçtan Uca Finansal Analiz Yap' butonuna basın.")
