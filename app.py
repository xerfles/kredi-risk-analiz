import streamlit as st
import joblib
import pandas as pd

# Kayıtlı modeli yükle
try:
    model = joblib.load('kredi_modeli.pkl')
except:
    model = None

st.set_page_config(page_title="Finansal Risk Analiz", layout="centered")
st.title("🏦 Kredi Risk Değerlendirme Paneli")
st.write("Müşteri finansal verilerine göre anlık risk simülasyonu.")

# Sidebar'da girişler
st.sidebar.header("Müşteri Bilgileri")
gelir = st.sidebar.number_input("Yıllık Gelir ($)", 20000, 200000, value=50000, step=5000)
skor = st.sidebar.slider("Kredi Skoru", 300, 850, value=600)
borc = st.sidebar.slider("Borç / Gelir Oranı", 0.0, 1.0, value=0.3, step=0.05)
yil = st.sidebar.number_input("Mevcut İş Süresi (Yıl)", 0, 40, value=5)

if st.button("Risk Analizini Başlat"):
    # Girdi verisini DataFrame haline getiriyoruz
    input_df = pd.DataFrame([[gelir, skor, borc, yil]], 
                            columns=['Gelir', 'Kredi_Skoru', 'Borc_Orani', 'Is_Suresi'])
    
    # 1. Aşama: Temel Bankacılık Kural Seti (Hard Rules)
    # Gerçek bankalar modelden önce kesin filtrelere bakar
    if skor < 450 or borc > 0.70:
        tahmin_sonucu = 0 # Kesin Red
    elif skor > 750 and borc < 0.35:
        tahmin_sonucu = 1 # Kesin Onay
    else:
        # 2. Aşama: Gri alandaki müşteriler için Makine Öğrenmesi Modeli devreye girer
        if model is not None:
            tahmin_sonucu = model.predict(input_df)[0]
        else:
            # Model yüklenemezse geçici mantık
            tahmin_sonucu = 1 if (gelir * (1 - borc) > 20000) else 0

    # Sonuç Ekranı
    st.write("---")
    if tahmin_sonucu == 1:
        st.success(f"✅ **KREDİ ONAYLANDI** \n\nMüşteri risk profili limitler dahilindedir. (Skor: {skor}, Borç Oranı: %{borc*100:.0f})")
        st.balloons() # Onay durumunda kutlama efekti
    else:
        st.error(f"❌ **KREDİ REDDEDİLDİ** \n\nYüksek risk tespiti. Başvuru kriterleri karşılanamıyor. (Skor: {skor}, Borç Oranı: %{borc*100:.0f})")
