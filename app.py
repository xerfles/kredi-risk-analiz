import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Kurumsal Sayfa Mimarisi
st.set_page_config(page_title="Risk Intelligence Hub", layout="wide")

# Model Yükleme
try:
    model = joblib.load('kredi_modeli.pkl')
except:
    model = None

# Başlık Paneli (Tier-1 Bankacılık Standartlarında UI)
st.title("🏛️ Institutional Credit Risk Hub & Advanced Simulation Lab")
st.markdown("_Merkezi Risk Yönetimi, Makro Stress-Testing ve Duyarlılık Analiz Platformu - Ultimate Sürüm_")
st.write("---")

# Sol Panel: Girdiler ve Senaryolar
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🎛️ Senaryo & Müşteri Matrisi")
    
    st.subheader("🌐 1. Makroekonomik & Piyasa Şokları")
    makro_durum = st.selectbox(
        "Stres Testi Konjonktürü", 
        ["Normal Ekonomik Şartlar", "Sistemik Resesyon (Daralma)", "Hiperenflasyon & Döviz Şoku", "Ekonomik Büyüme (Genişleme)"]
    )
    
    enflasyon_orani = st.slider("Yıllık Enflasyon Beklentisi (%)", 10, 150, value=40 if "Normal" in makro_durum else (120 if "Hiperenflasyon" in makro_durum else 70))
    kur_volatilitesi = st.slider("Döviz Kuru Oynaklığı (Aylık %)", 1, 50, value=5 if "Normal" in makro_durum else (35 if "Hiperenflasyon" in makro_durum else 15))
    
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
        # 1. MAKRO ŞOK ETKİSİ HESAPLAMA MOTORU
        enflasyon_etkisi = (enflasyon_orani / 100) * 0.15
        kur_etkisi = (kur_volatilitesi / 100) * 0.20
        
        aylik_gelir = (gelir / 12) * (1 - enflasyon_etkisi) 
        mevcut_aylik_borc = (gelir / 12) * borc * (1 + kur_etkisi) 
        
        # Dinamik Faiz Algoritması
        base_faiz = 0.10 if kredi_turu == "Ticari Kredi" else (0.07 if kredi_turu == "Konut Kredisi" else 0.14)
        base_faiz += (enflasyon_orani / 200)
            
        # Taksit ve Yeni DTI Hesaplama
        aylik_faiz = base_faiz / 12
        taksit = (talep_edilen * aylik_faiz) / (1 - (1 + aylik_faiz) ** (-vade))
        yeni_dti = (mevcut_aylik_borc + taksit) / aylik_gelir
        
        # 2. DİNAMİK RİSK AĞIRLIKLANDIRMA
        fico_skor_puani = (skor - 300) / 550 
        dti_ceza_puani = np.exp(yeni_dti) / np.exp(1) 
        
        onay_skoru = (fico_skor_puani * 0.40) + ((1 - dti_ceza_puani) * 0.40) + ((yil / 40) * 0.20)
        
        # Konjonktürel Sıkılaştırma Çarpanı
        if "Resesyon" in makro_durum: onay_skoru *= 0.80
        elif "Hiperenflasyon" in makro_durum: onay_skoru *= 0.65
        elif "Büyüme" in makro_durum: onay_skoru *= 1.15
        
        onay_olasiligi = np.clip(onay_skoru, 0.01, 0.99)
        karar = 1 if onay_olasiligi >= 0.50 and yeni_dti <= 0.65 else 0
        
        # 3. YENİ: Otomatik Kredi Limiti Optimizasyonu (Sınır Testi)
        maks_guvenli_limit = talep_edilen
        if karar == 0:
            # Hedef yeni_dti oranını %45'e çekecek taksiti bulup limiti geriye doğru hesaplıyoruz
            hedef_taksit = (aylik_gelir * 0.45) - mevcut_aylik_borc
            if hedef_taksit > 0:
                maks_guvenli_limit = (hedef_taksit * (1 - (1 + aylik_faiz) ** (-vade))) / aylik_faiz
                maks_guvenli_limit = max(0.0, maks_guvenli_limit)
            else:
                maks_guvenli_limit = 0.0
        
        # Hibrit Altman Z-Skor Revizyonu
        z_score = (skor / 850) * 4.0 + (1 - yeni_dti) * 3.0 + (yil / 10) * 1.5 - (enflasyon_etkisi * 2)
        
        # KPI Metrik Kartları
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Kredi Onay İhtimali", value=f"%{onay_olasiligi*100:.1f}")
        with m2:
            st.metric(label="Reel Aylık Taksit Yükü", value=f"${taksit:.2f}")
        with m3:
            st.metric(label="Şok Basınçlı Yeni DTI", value=f"%{yeni_dti*100:.1f}", delta=f"%{(yeni_dti-borc)*100:.1f} Risk Artışı", delta_color="inverse")
        with m4:
            st.metric(label="Makro Sağlık (Z-Skor)", value=f"{z_score:.2f}")
            
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
            st.write("**2. Vade & Borç Duyarlılık Matrisi (Aksiyonel Teminat Koşulları)**")
            fig2, ax2 = plt.subplots(figsize=(6, 3.5))
            vade_ekseni = [24, 48, 72, 96, 120]
            dti_ekseni = [0.2, 0.4, 0.6, 0.8]
            matrix_data = np.zeros((len(dti_ekseni), len(vade_ekseni)))
            for i, d in enumerate(dti_ekseni):
                for j, v in enumerate(vade_ekseni):
                    matrix_data[i, j] = np.clip(onay_olasiligi * (1 - (d*0.5) - (v*0.003)), 0, 1)
            sns.heatmap(matrix_data, xticklabels=vade_ekseni, yticklabels=dti_ekseni, annot=True, cmap="YlOrRd_r", fmt=".2f", ax=ax2)
            ax2.set_xlabel("Vade (Ay)")
            ax2.set_ylabel("DTI Oranı")
            st.pyplot(fig2)
            
        # 4. YENİ: XAI Karar Gerekçelendirme ve Sınır Testi Paneli
        st.write("---")
        st.subheader("🧠 Explainable AI (XAI) Risk Analiz Odası & Limit Optimizasyonu")
        
        xai_col1, xai_col2 = st.columns(2)
        with xai_col1:
            # Kararı en çok neyin etkilediğini bulma (Explainable AI simülasyonu)
            risk_faktorleri = {
                "Düşük Kredi Skoru": 750 - skor,
                "Yüksek Borçluluk (DTI)": yeni_dti * 200,
                "Makro Enflasyon Baskısı": enflasyon_orani,
                "Kur Volatilitesi": kur_volatilitesi * 1.5
            }
            en_buyuk_risk = max(risk_faktorleri, key=risk_faktorleri.get)
            st.warning(f"🔍 **AI Tespiti (Kararı Olumsuz Etkileyen En Baskın Faktör):** {en_buyuk_risk}")
            
        with xai_col2:
            if karar == 1:
                st.info(f"💡 **Limit Optimizasyonu:** Talep edilen tutarın tamamı (${talep_edilen:,.0f}) güvenli alan içindedir.")
            else:
                if maks_guvenli_limit > 0:
                    st.error(f"💡 **Limit Önerisi:** Talep edilen ${talep_edilen:,.0f} onaylanamıyor. Ancak mevcut makro stres koşulları altında bu müşteriye verilebilecek **Maksimum Güvenli Kredi Limiti: ${maks_guvenli_limit:,.0f}**")
                else:
                    st.error("💡 **Limit Önerisi:** Müşterinin mevcut borç yükü makro şoklar altında çok yüksek. Güvenli limit: **$0** (Ek teminat bulunmadan finansman sağlanamaz).")

        # Otomatik Tahsis Koşulları & Yapılandırma Robotu
        st.write(" ")
        st.write("**3. Otomatik Tahsis Koşulları & Yapılandırma Robotu**")
        
        teminat_orani = "%0 (Teminatsız Kredi)"
        if yeni_dti > 0.45 or onay_olasiligi < 0.60:
            teminat_orani = f"%{int(100 + (yeni_dti * 50)):.0f} Gayrimenkul İpotek Şartı"
        elif "Hiperenflasyon" in makro_durum:
            teminat_orani = "%150 Nakit veya Kredi Garanti Fonu (KGF) Kefaleti"
            
        karneler = {
            "Risk Yönetim Katmanı": ["Ekonometrik Sağlık (Z-Skor)", "Dinamik Teminat Koşulu", "Makro Şok Duyarlılığı"],
            "Stratejik Aksiyon Notu": [
                "Güvenli" if z_score > 4.5 else "Yakın İzleme (Watchlist)",
                f"Kredi Tahsis Şartı: {teminat_orani}",
                f"Enflasyon (%{enflasyon_orani}) ve Kur Baskısı Altında Nakit Akışı Kırılgan" if yeni_dti > 0.5 else "Şoklara Karşı Dayanıklı Portföy"
            ]
        }
        st.table(pd.DataFrame(karneler))
            
        # Kredi Komitesi Nihai Strateji Raporu
        st.write(" ")
        st.subheader("📋 Kredi Tahsis ve Portföy Yönetimi Komite Kararı")
        
        if karar == 1:
            st.success(f"**STRATEJİK ONAY:** Başvuru, **'{makro_durum}'** şok testlerini ve dinamik katsayı matrisini başarıyla geçmiştir. Reel DTI kapasitesi limitler içindedir. Belirtilen teminat koşullarının yerine getirilmesi şartıyla tahsis onaylanmıştır.")
        else:
            st.error(f"**STRATEJİK RED:** Sistemik risk bariyeri! Enflasyon ve kur şokları simüle edildiğinde, müşterinin reel harcanabilir geliri borç taksitini karşılayamamaktadır. Duyarlılık matrisindeki genel skor kritik eşiğin altındadır.")
            
        st.button("🖨️ Resmi Kredi Komite Raporunu Çıktı Al (PDF)", use_container_width=True)
            
    else:
        st.info("Kurumsal analitik laboratuvarı çalıştırmak için sol panelden parametreleri girip simülasyonu başlatın.")
