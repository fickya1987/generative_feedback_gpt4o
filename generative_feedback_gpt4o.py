
import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Generative Feedback Assistant (GPT-4o)", layout="centered")

st.title("🧠 Generative Feedback Assistant with GPT-4o")
st.markdown("Masukkan informasi kinerja untuk menghasilkan umpan balik otomatis menggunakan GPT-4o.")

# Input form
with st.form("feedback_form"):
    nama = st.text_input("Nama Pekerja")
    jabatan = st.text_input("Jabatan Pekerja")
    skor_kpi = st.number_input("Skor Akhir KPI", min_value=0.0, max_value=150.0, value=100.0)
    kategori_talent = st.selectbox("Kategori Talent", ["Istimewa", "Sangat Baik", "Baik", "Cukup", "Kurang"])
    nilai_perilaku = st.slider("Skor Perilaku AKHLAK (1–6)", min_value=1, max_value=6, value=4)
    submitted = st.form_submit_button("🔍 Hasilkan Umpan Balik")

if submitted:
    with st.spinner("Menghasilkan umpan balik dengan GPT-4o..."):
        prompt = f'''
        Anda adalah asisten pengembangan SDM. Buatlah umpan balik profesional dalam 2-3 kalimat
        untuk seorang pekerja bernama {nama}, dengan jabatan {jabatan}.
        Skor KPI akhir adalah {skor_kpi}, tergolong dalam kategori talent "{kategori_talent}".
        Skor perilaku AKHLAK adalah {nilai_perilaku} dari 6.

        Berikan umpan balik yang positif, berbobot, dan mengarahkan pada pengembangan karier.
        Tampilkan dalam bahasa Indonesia yang profesional.
        '''

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah asisten SDM profesional."},
                    {"role": "user", "content": prompt}
                ]
            )
            feedback = response.choices[0].message["content"]
            st.subheader("✍️ Umpan Balik dari GPT-4o:")
            st.success(feedback)

        except Exception as e:
            st.error(f"Gagal menghasilkan umpan balik: {e}")
