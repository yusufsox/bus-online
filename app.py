import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Judul di Browser
st.set_page_config(page_title="Booking Bus 60 Kursi", layout="centered")

# --- MASUKKAN LINK GOOGLE SHEET ANDA DI BAWAH INI ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1eQ3sS8Gy-8QrE0RHfuFCQghA_Ph0tUdEtrr-JtCrqC4/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existing = conn.read(spreadsheet=URL_SHEET, usecols=[0, 1]).dropna()
    booked_seats = dict(zip(df_existing['Nomor Kursi'].astype(int), df_existing['Nama Penumpang']))
except:
    booked_seats = {}

st.title("🚌 Reservasi Kursi Bus")
st.info("Pilih kursi yang tersedia (Putih). Kursi Merah sudah terisi.")

# Layout 12 baris, konfigurasi 2-3
for r in range(12):
    c1, c2, spacer, c3, c4, c5 = st.columns([1, 1, 0.5, 1, 1, 1])
    row_cols = [c1, c2, c3, c4, c5]
    
    for i, col in enumerate(row_cols):
        seat_num = r * 5 + (i + 1)
        if seat_num in booked_seats:
            col.button(f"{seat_num}", key=f"s{seat_num}", disabled=True, type="secondary", help=f"Nama: {booked_seats[seat_num]}")
        else:
            if col.button(f"{seat_num}", key=f"s{seat_num}", type="primary"):
                st.session_state.pilihan = seat_num

# Form input jika kursi dipilih
if 'pilihan' in st.session_state:
    with st.form("form_pesan"):
        st.write(f"### Konfirmasi Kursi: {st.session_state.pilihan}")
        nama = st.text_input("Masukkan Nama Penumpang")
        if st.form_submit_button("Simpan Pesanan"):
            if nama:
                # Proses simpan ke Google Sheet
                new_row = pd.DataFrame([{"Nomor Kursi": st.session_state.pilihan, "Nama Penumpang": nama}])
                if not booked_seats:
                    df_final = new_row
                else:
                    df_final = pd.concat([df_existing, new_row], ignore_index=True)
                
                conn.update(spreadsheet=URL_SHEET, data=df_final)
                st.success("Berhasil! Silakan refresh halaman.")
                del st.session_state.pilihan
                st.rerun()
            else:
                st.error("Nama harus diisi!")
