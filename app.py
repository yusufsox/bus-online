import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Bus Booking System", layout="centered")

# --- KONFIGURASI LINK ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1eQ3sS8Gy-8QrE0RHfuFCQghA_Ph0tUdEtrr-JtCrqC4/edit?usp=sharing"

# Paksa hapus memori lama setiap kali halaman dibuka agar sinkron
st.cache_data.clear()

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Baca data dari Google Sheets
        data = conn.read(spreadsheet=URL_SHEET)
        # Hapus baris yang benar-benar kosong atau tidak ada namanya
        data = data.dropna(subset=['Nomor Kursi', 'Nama Penumpang'])
        return data
    except:
        return pd.DataFrame(columns=['Nomor Kursi', 'Nama Penumpang'])

df_existing = load_data()

# Membuat daftar kursi yang benar-benar sudah ada namanya
booked_seats = {}
for _, row in df_existing.iterrows():
    try:
        no_kursi = int(row['Nomor Kursi'])
        nama_pax = str(row['Nama Penumpang']).strip()
        if nama_pax != "" and nama_pax != "nan":
            booked_seats[no_kursi] = nama_pax
    except:
        continue

st.title("🚌 Sistem Reservasi Bus (2-3)")
st.write(f"Sisa Kursi Tersedia: {60 - len(booked_seats)}")

# --- VISUALISASI DENAH ---
for r in range(12):
    c1, c2, spacer, c3, c4, c5 = st.columns([1, 1, 0.5, 1, 1, 1])
    row_cols = [c1, c2, c3, c4, c5]
    
    for i, col in enumerate(row_cols):
        seat_num = r * 5 + (i + 1)
        
        if seat_num in booked_seats:
            # Kursi Merah (Terisi)
            col.button(f"{seat_num}", key=f"s{seat_num}", disabled=True, help=f"Dipesan oleh: {booked_seats[seat_num]}")
        else:
            # Kursi Biru (Tersedia)
            if col.button(f"{seat_num}", key=f"s{seat_num}", type="primary"):
                st.session_state.pilihan = seat_num

# --- FORM PEMESANAN ---
if 'pilihan' in st.session_state:
    st.markdown(f"### 📋 Form Pemesanan Kursi: {st.session_state.pilihan}")
    with st.form("my_form", clear_on_submit=True):
        nama_input = st.text_input("Nama Lengkap Penumpang:")
        submit = st.form_submit_button("Konfirmasi Pesanan")
        
        if submit:
            if nama_input:
                # Tambah data baru
                new_data = pd.DataFrame([{"Nomor Kursi": int(st.session_state.pilihan), "Nama Penumpang": nama_input}])
                df_final = pd.concat([df_existing, new_data], ignore_index=True)
                
                # Kirim ke Google Sheets
                conn.update(spreadsheet=URL_SHEET, data=df_final)
                
                st.success(f"Kursi {st.session_state.pilihan} Berhasil Dipesan!")
                if 'pilihan' in st.session_state:
                    del st.session_state.pilihan
                st.rerun()
            else:
                st.error("Nama tidak boleh kosong!")
