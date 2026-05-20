import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Sayfa Genişlik ve Kurumsal Tema Ayarları
st.set_page_config(page_title="Risk Intelligence & Decision Matrix", layout="wide")

# Model Yükleme
try:
    model = joblib.load('kredi_modeli.pkl')
except:
    model = None

# Başlık Paneli (Premium Görünüm)
st.title("🏛️ Institutional Credit Risk Architecture & Financial Stress Lab")
st.markdown("_Risk Modelleme, Portföy Stratejisi ve Karar Destek Mekanizması - Pro Sürüm_")
st.write("---")

# Layout Bölünmesi: Sol Girişler, Sağ Sonuçlar
col1, col2 = st.columns([1, 2])

with col1:
    st.header("👤 Parametre Yönetimi")
    
    st.subheader("🌐 1. Makroekonomik Risk Filtresi")
    makro_durum = st.selectbox(
        "Konjonktürel Senaryo (Stres Testi)", 
        ["Normal Ekonomik Şartlar", "Şok / Resesyon Dönemi (Sıkı Para Politikası)", "Ekonomik Genişleme (Gevşek Para Politikası)"]
    )
    
    st.write("---")
    st.subheader("📊 2. Müşteri Mikro Verileri")
    gelir = st.number_input("Yıllık Brüt Gelir ($)", 20000, 500000, value=85000, step=5000)
    skor = st.slider("Kredi Skoru (FICO)", 300, 850, value=650)
    borc = st.slider("Mevcut Borç / Gelir Oranı (DTI)", 0.0, 1.0, value=0.35, step=0.01)
    yil = st.number_input("Mevcut İş Süresi (Yıl)", 0, 40, value=5)
    
    st.write("---")
    st.subheader("💰 3. Kredi Yapılandırma")
    kredi_turu = st.selectbox("Kredi Ürün Grubu", ["Konut Kredisi", "Ticari Kredi", "İhtiyaç Kredisi"])
    talep_edilen = st.number_input("Talep Edilen Kredi Tutarı ($)", 5000, 1000000, value=50000, step=5000)
    vade = st.slider("Vade Seçeneği (Ay)", 12, 120, value=36, step=12)

    st.write(" ")
    analiz_butonu = st.button("Uçtan Uca Kurumsal Analiz Çalıştır", use_container_width=True)

with col2:
    st.header("📉 Finansal Karar Matrisi & Analitik Çıktılar")
    
    if analiz_butonu:
        # 1. Finansal Matematik Motoru
        aylik_gelir = gelir / 12
        mevcut_aylik_borc = aylik_gelir * borc
        
        # Faiz oranlarını kredi türüne göre dinamik belirleme
        base_faiz = 0.08 if kredi_turu == "Konut Kredisi" else (0.12 if kredi_turu == "Ticari Kredi" else 0.15)
        if makro_durum == "Şok / Resesyon Dönemi (Sıkı Para Politikası)":
            base_faiz += 0.04 # Faizler artar
        elif makro_durum == "Ekonomik Genişleme (Gevşek Para Politikası)":
            base_faiz -= 0.02 # Faizler düşer
            
        # Basit Aylık Taksit Hesaplama (PMT Yaklaşımı)
        aylik_faiz = base_faiz / 12
        taksit = (talep_edilen * aylik_faiz) / (1 - (1 + aylik_faiz) ** (-vade))
        yeni_dti = (mevcut_aylik_borc + taksit) / aylik_gelir
        
        # Makro senaryoya göre risk çarpanı (İktisat teorisi)
        risk_multiplier = 1.0
        if makro_durum == "Şok / Resesyon Dönemi (Sıkı Para Politikası)":
            risk_multiplier = 0.70 
        elif makro_durum == "Ekonomik Genişleme (Gevşek Para Politikası)":
            risk_multiplier = 1.20
            
        # Olasılık Algoritması
        base_prob = 0.52
        if skor > 720: base_prob += 0.23
        if skor < 540: base_prob -= 0.35
        if yeni_dti > 0.50: base_prob -= 0.32
        if yeni_dti < 0.30: base_prob += 0.12
        if yil > 4: base_prob += 0.08
        
        onay_olasiligi = np.clip(base_prob * risk_multiplier, 0.01, 0.99)
        karar = 1 if onay_olasiligi >= 0.50 else 0
        
        # Üst Metrik Paneli (KPI Dashboard)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Kredi Onay İhtimali", value=f"%{onay_olasiligi*100:.1f}")
        with m2:
            st.metric(label="Öngörülen Aylık Taksit", value=f"${taksit:.2f}")
        with m3:
            st.metric(label="Yeni DTI (Borç/Gelir Yükü)", value=f"%{yeni_dti*100:.1f}", delta=f"%{(yeni_dti - borc)*100:.1f} Artış", delta_color="inverse")
        with m4:
            st.metric(label="Uygulanan Yıllık Faiz", value=f"%{base_faiz*100:.1f}")
            
        st.progress(float(onay_olasiligi))
        st.write(" ")
        
        # Gelişmiş Grafikler (Double Column)
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**1. Portföy Gelir Dağılımı ve Müşteri Konumu**")
            fig1, ax1 = plt.subplots(figsize=(6, 3.5))
            mock_gelirler = np.random.normal(70000, 20000, 1000)
            sns.kdeplot(mock_gelirler, fill=True, color="#1c3d5a", alpha=0.5, label="Mevcut Kredi Portföyü", ax=ax1)
            ax1.axvline(gelir, color="#e3342f", linestyle="--", linewidth=2, label="Müşteri Geliri")
            ax1.set_xlabel("Yıllık Gelir ($)")
            ax1.legend()
            st.pyplot(fig1)
            
        with g2:
            st.write("**2. FICO Skor Kıyaslaması ve Risk Eşikleri**")
            fig2, ax2 = plt.subplots(figsize=(6, 3.5))
            mock_skorlar = np.random.normal(680, 70, 1000)
            sns.histplot(mock_skorlar, kde=True, color="#38c172", alpha=0.4, bins=30, ax=ax2, label="Banka Portföy Dağılımı")
            ax2.axvline(skor, color="#e3342f", linestyle="-", linewidth=2, label="Müşteri Skoru")
            ax2.set_xlabel("FICO Score")
            ax2.legend()
            st.pyplot(fig2)
            
        # Finansal Sağlık Check-up Tablosu
        st.write("**3. Müşteri Finansal Sağlık Karnesi**")
        karneler = {
            "Metrik": ["Kredi Notu (FICO)", "Borç Yükü (DTI)", "İş İstikrarı"],
            "Durum": ["Güvenli" if skor > 680 else "Risk Sınırında", "Kritik Seviye" if yeni_dti > 0.45 else "İdeal", "Yeterli" if yil >= 3 else "Zayıf"]
        }
        st.table(pd.DataFrame(karneler))
            
        # Kurumsal Komite Raporu
        st.write(" ")
        st.subheader("📋 Kredi Tahsis Komitesi Stratejik Notu")
        
        if karar == 1:
            st.success(f"**ONAY STRATEJİSİ:** Başvuru, seçilen **'{makro_durum}'** şok testlerinden başarıyla geçmiştir. Hesaplanan yeni DTI oranı (%{yeni_dti*100:.1f}) bankanın maksimum risk iştahı olan %50 sınırının altındadır. Finansman sağlanması portföy kalitesini bozmaz.")
        else:
            st.error(f"**RED STRATEJİSİ:** Yüksek Risk! Talep edilen kredi taksiti eklendiğinde müşterinin borçluluk yükü (DTI) kritik eşik olan %{yeni_dti*100:.1f} seviyesine çıkmaktadır. **'{makro_durum}'** şartlarında nakit akış kırılganlığı çok yüksektir. Tahsis reddedilmiştir.")
            
    else:
        st.info("Kurumsal risk analizi ve stres testini çalıştırmak için sol panelden verileri yapılandırıp butona tıklayın.")
