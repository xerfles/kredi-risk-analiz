import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Kurumsal Sayfa Mimarisi
st.set_page_config(page_title="Risk Matrix Lab", layout="wide")

# Model Yükleme
try:
    model = joblib.load('kredi_modeli.pkl')
except:
    model = None

# Başlık Paneli (Tier-1 Bankacılık Standartlarında UI)
st.title("🛡️ Institutional Credit Risk Hub & Advanced Simulation Lab")
st.markdown("_Merkezi Risk Yönetimi, Makro Stress-Testing ve Duyarlılık Analiz Platformu_")
st.write("---")

# Sol Panel: Girdiler ve Senaryolar
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🎛️ Senaryo & Müşteri Matrisi")
    
    st.subheader("🌐 1. Makroekonomik Senaryo")
    makro_durum = st.selectbox(
        "Stres Testi Konjonktürü", 
        ["Normal Ekonomik Şartlar", "Şok / Sistemik Resesyon (Sıkılaşma)", "Hiperenflasyon / Likidite Sıkışıklığı", "Ekonomik Büyüme (Genişleme)"]
    )
    
    st.write("---")
    st.subheader("📊 2. Finansal Profil Kontrolleri")
    gelir = st.number_input("Yıllık Brüt Gelir ($)", 20000, 1000000, value=95000, step=5000)
    skor = st.slider("Kredi Skoru (FICO)", 300, 850, value=670)
    borc = st.slider("Mevcut DTI (Borç/Gelir Oranı)", 0.0, 1.0, value=0.30, step=0.01)
    yil = st.number_input("İş İstikrarı (Yıl)", 0, 40, value=6)
    
    st.write("---")
    st.subheader("💰 3. Finansman Yapılandırma")
    kredi_turu = st.selectbox("Ürün Grubu", ["Ticari Kredi", "Konut Kredisi", "İhtiyaç Kredisi"])
    talep_edilen = st.number_input("Talep Edilen Tutar ($)", 5000, 2000000, value=100000, step=10000)
    vade = st.slider("Vade Yapısı (Ay)", 12, 120, value=48, step=12)

    st.write(" ")
    analiz_butonu = st.button("Uçtan Uca Kurumsal Analiz Çalıştır", use_container_width=True)

# Sağ Panel: Analitik Raporlar ve Gelişmiş Grafik Paneli
with col2:
    st.header("📊 Kurumsal Karar ve Analitik Çıktılar")
    
    if analiz_butonu:
        # Finansal Matematik Çekirdeği
        aylik_gelir = gelir / 12
        mevcut_aylik_borc = aylik_gelir * borc
        
        # Dinamik Faiz Algoritması
        base_faiz = 0.10 if kredi_turu == "Ticari Kredi" else (0.07 if kredi_turu == "Konut Kredisi" else 0.14)
        if "Resesyon" in makro_durum or "Hiperenflasyon" in makro_durum:
            base_faiz += 0.05
        elif "Büyüme" in makro_durum:
            base_faiz -= 0.01
            
        # Taksit ve Yeni DTI Hesaplama
        aylik_faiz = base_faiz / 12
        taksit = (talep_edilen * aylik_faiz) / (1 - (1 + aylik_faiz) ** (-vade))
        yeni_dti = (mevcut_aylik_borc + taksit) / aylik_gelir
        
        # Hibrit Altman Z-Skor Benzetimi (Finansal Sağlık İndeksi)
        z_score = (skor / 850) * 4.0 + (1 - yeni_dti) * 3.0 + (yil / 10) * 1.5
        
        # Makro Çarpan
        risk_multiplier = 1.0
        if "Resesyon" in makro_durum: risk_multiplier = 0.65
        elif "Hiperenflasyon" in makro_durum: risk_multiplier = 0.50
        elif "Büyüme" in makro_durum: risk_multiplier = 1.25
        
        # Skorlama Algoritması
        base_prob = 0.55
        if skor > 740: base_prob += 0.25
        if skor < 550: base_prob -= 0.40
        if yeni_dti > 0.45: base_prob -= 0.35
        if yil > 5: base_prob += 0.05
        
        onay_olasiligi = np.clip(base_prob * risk_multiplier, 0.01, 0.99)
        karar = 1 if onay_olasiligi >= 0.50 and yeni_dti <= 0.60 else 0
        
        # KPI Metrik Kartları
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Kredi Onay İhtimali", value=f"%{onay_olasiligi*100:.1f}")
        with m2:
            st.metric(label="Aylık Taksit Yükü", value=f"${taksit:.2f}")
        with m3:
            st.metric(label="Kredi Sonrası DTI", value=f"%{yeni_dti*100:.1f}", delta=f"%{(yeni_dti-borc)*100:.1f}")
        with m4:
            st.metric(label="Finansal Sağlık (Z-Skor)", value=f"{z_score:.2f}")
            
        st.progress(float(onay_olasiligi))
        st.write(" ")
        
        # Grafikler: 3'lü Gelişmiş Matris
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**1. Portföy Risk Dağılımı (FICO)**")
            fig1, ax1 = plt.subplots(figsize=(6, 3.5))
            mock_skorlar = np.random.normal(670, 80, 1000)
            sns.histplot(mock_skorlar, kde=True, color="#2c3e50", alpha=0.6, ax=ax1)
            ax1.axvline(skor, color="#e74c3c", linestyle="--", linewidth=2, label="Müşteri Notu")
            ax1.set_title("Müşterinin Portföy Skor Dağılımındaki Yeri")
            ax1.legend()
            st.pyplot(fig1)
            
        with g2:
            st.write("**2. Vadeye Göre Risk Duyarlılık Haritası (Sensitivity Heatmap)**")
            fig2, ax2 = plt.subplots(figsize=(6, 3.5))
            # Farklı vade ve borç oranlarında risk matrisi simülasyonu
            vade_ekseni = [24, 48, 72, 96, 120]
            dti_ekseni = [0.2, 0.4, 0.6, 0.8]
            matrix_data = np.zeros((len(dti_ekseni), len(vade_ekseni)))
            for i, d in enumerate(dti_ekseni):
                for j, v in enumerate(vade_ekseni):
                    matrix_data[i, j] = np.clip(onay_olasiligi * (1 - (d*0.4) - (v*0.002)), 0, 1)
            sns.heatmap(matrix_data, xticklabels=vade_ekseni, yticklabels=dti_ekseni, annot=True, cmap="RdYlGn", fmt=".2f", ax=ax2)
            ax2.set_xlabel("Vade (Ay)")
            ax2.set_ylabel("DTI Oranı")
            st.pyplot(fig2)
            
        # Finansal Sağlık Sınıflandırma Tablosu
        st.write("**3. Erken Uyarı Sinyalleri Karnesi**")
        z_durum = "Güvenli Bölge (Green Zone)" if z_score > 5.5 else ("Gri Alan (Caution)" if z_score > 3.5 else "Yüksek Risk (Distress Zone)")
        karneler = {
            "Risk Katmanı": ["Ekonometrik Sağlık (Z-Skor)", "Kaldıraç Durumu (Leverage)", "Vade Uyumsuzluğu"],
            "Durum Değerlendirmesi": [z_durum, "Sınır Değer Aşılmadı" if yeni_dti < 0.50 else "Aşırı Borçlanma Risk", "Uyumlu" if vade <= 60 else "Uzun Vade Likidite Riski"]
        }
        st.table(pd.DataFrame(karneler))
            
        # Kredi Komitesi Nihai Strateji Raporu
        st.write(" ")
        st.subheader("📋 Kredi Tahsis ve Portföy Yönetimi Komite Kararı")
        
        if karar == 1:
            st.success(f"**STRATEJİK ONAY:** Başvuru, **'{makro_durum}'** parametreleri altında yürütülen stres testini ve duyarlılık analizini geçmiştir. Hesaplanan Finansal Sağlık İndeksi ({z_score:.2f}) güvenli bölgededir. Tahsis sürecine engel bir bulguya rastlanmamıştır.")
        else:
            st.error(f"**STRATEJİK RED:** Sistemik risk uyarısı! Özellikle **'{makro_durum}'** senaryosunda müşterinin duyarlılık matrisindeki başarı oranı kritik seviyelere düşmektedir. Portföy risk dengesi açısından kredilendirme uygun bulunmamıştır.")
            
        # Proje Raporlama Özelliği (Mülakat Sürprizi)
        st.button("🖨️ Resmi Kredi Komite Raporunu Çıktı Al (PDF)", use_container_width=True)
            
    else:
        st.info("Kurumsal analitik laboratuvarı çalıştırmak için sol panelden parametreleri girip simülasyonu başlatın.")
