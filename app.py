import streamlit as st
import joblib
import pandas as pd

# Kayıtlı modeli yükle
model = joblib.load('kredi_modeli.pkl')

st.set_page_config(page_title="Finansal Risk Analiz", layout="centered")
st.title("🏦 Kredi Risk Değerlendirme Paneli")

# Sidebar'da girişler
st.sidebar.header("Müşteri Bilgileri")
gelir = st.sidebar.number_input("Yıllık Gelir", 20000, 200000)
skor = st.sidebar.slider("Kredi Skoru", 300, 850, 600)
borc = st.sidebar.slider("Borç/Gelir Oranı", 0.0, 1.0, 0.3)
yil = st.sidebar.number_input("İş Süresi (Yıl)", 0, 40)

if st.button("Tahmin Et"):
    input_df = pd.DataFrame([[gelir, skor, borc, yil]], 
                            columns=['Gelir', 'Kredi_Skoru', 'Borc_Orani', 'Is_Suresi'])
    tahmin = model.predict(input_df)
    
    if tahmin[0] == 1:
        st.success("✅ Onaylandı: Müşteri kredi almaya uygun.")
    else:
        st.error("❌ Reddedildi: Risk oranı yüksek.")