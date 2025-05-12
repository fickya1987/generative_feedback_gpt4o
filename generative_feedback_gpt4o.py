# Create Streamlit app for batch Generative Feedback using GPT-4o and based on PDF-based performance principles

batch_gpt4_feedback_code = """
import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load .env API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Batch Generative Feedback GPT-4o", layout="wide")
st.title("🧠 Batch Generative Feedback Assistant - GPT-4o")
st.markdown("Upload file KPI dan dapatkan umpan balik otomatis berdasarkan kaidah PDF Pelindo dengan GPT-4o")

# Upload KPI file
uploaded_file = st.file_uploader("📤 Upload KPI File (CSV/XLSX)", type=["csv", "xlsx"])
if not uploaded_file:
    st.stop()

# Load Data
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# Minimal columns validation
required_cols = ['NIPP PEKERJA', 'POSISI PEKERJA', 'PERUSAHAAN', 'BOBOT', 'REALISASI TW TERKAIT', 'TARGET TW TERKAIT', 'POLARITAS']
if not all(col in df.columns for col in required_cols):
    st.error("❌ File tidak memiliki kolom yang sesuai format kpi_cleaned.csv")
    st.stop()

# Preprocessing
df['REALISASI TW TERKAIT'] = pd.to_numeric(df['REALISASI TW TERKAIT'], errors='coerce')
df['TARGET TW TERKAIT'] = pd.to_numeric(df['TARGET TW TERKAIT'], errors='coerce')
df['BOBOT'] = pd.to_numeric(df['BOBOT'], errors='coerce')
df['POLARITAS'] = df['POLARITAS'].str.strip().str.lower()

def calculate_capaian(row):
    realisasi = row['REALISASI TW TERKAIT']
    target = row['TARGET TW TERKAIT']
    polaritas = row['POLARITAS']
    if pd.isna(realisasi) or pd.isna(target) or target == 0 or realisasi == 0:
        return None
    if polaritas == 'positif':
        return (realisasi / target) * 100
    elif polaritas == 'negatif':
        return (target / realisasi) * 100
    else:
        return None

df['CAPAIAN (%)'] = df.apply(calculate_capaian, axis=1)
df['SKOR KPI'] = df['CAPAIAN (%)'] * df['BOBOT'] / 100

# Aggregate per pekerja
summary = df.groupby(['NIPP PEKERJA', 'POSISI PEKERJA', 'PERUSAHAAN'], as_index=False).agg(
    TOTAL_SKOR=('SKOR KPI', 'sum'),
    TOTAL_BOBOT=('BOBOT', 'sum')
)
summary = summary[summary['TOTAL_BOBOT'] != 0]
summary['SKOR AKHIR'] = (summary['TOTAL_SKOR'] / summary['TOTAL_BOBOT']) * 100

# Kategorisasi
def classify(score):
    if score > 110:
        return "Istimewa"
    elif score > 105:
        return "Sangat Baik"
    elif score >= 90:
        return "Baik"
    elif score >= 80:
        return "Cukup"
    else:
        return "Kurang"
summary['KATEGORI TALENT'] = summary['SKOR AKHIR'].apply(classify)

# Pilihan perilaku AKHLAK
summary['SKOR PERILAKU AKHLAK'] = st.slider("Skor rata-rata perilaku AKHLAK (1–6) untuk semua pekerja", 1, 6, 4)

# Prompt template
def build_prompt(row):
    return f\"\"\"
Nama: {row['NIPP PEKERJA']}, Jabatan: {row['POSISI PEKERJA']}, Perusahaan: {row['PERUSAHAAN']}.
Skor akhir KPI-nya adalah {round(row['SKOR AKHIR'], 2)} dan termasuk dalam kategori '{row['KATEGORI TALENT']}'.
Skor penilaian perilaku AKHLAK adalah {row['SKOR PERILAKU AKHLAK']}/6.
Berdasarkan pedoman manajemen kinerja Pelindo (PDF), berikan umpan balik profesional dalam bahasa Indonesia,
maksimal 3 kalimat, yang mendorong pengembangan karier dan mencerminkan gaya coaching SDM.
\"\"\"

# Generate feedback
if st.button("🧠 Generate Feedback dengan GPT-4o"):
    feedback_list = []
    with st.spinner("Menghubungi GPT-4o dan menghasilkan umpan balik..."):
        for _, row in summary.iterrows():
            try:
                prompt = build_prompt(row)
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Anda adalah asisten HR profesional di lingkungan BUMN Indonesia."},
                        {"role": "user", "content": prompt}
                    ]
                )
                feedback = response.choices[0].message["content"]
            except Exception as e:
                feedback = f"Error: {e}"
            feedback_list.append(feedback)
    summary['UMPAN BALIK GPT-4o'] = feedback_list
    st.dataframe(summary[['NIPP PEKERJA', 'POSISI PEKERJA', 'SKOR AKHIR', 'KATEGORI TALENT', 'UMPAN BALIK GPT-4o']])
    st.download_button("📥 Download Hasil Feedback", data=summary.to_csv(index=False), file_name="feedback_gpt4o.csv", mime="text/csv")
"""
