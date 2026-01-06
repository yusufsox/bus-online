import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Booking Bus 60 Kursi", layout="centered")

# --- MASUKKAN LINK GOOGLE SHEET ANDA ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1eQ3sS8Gy-8QrE0RHfuFCQghA_Ph0tUdEtrr-JtCrqC4/edit?usp=sharing"

# Inisialisasi Koneksi
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Membaca data dan menghapus baris yang benar-benar kosong
        data = conn.read(spreadsheet=URL_SHEET).dropna(how="all")
        return data
    except:
        return pd.DataFrame(columns=['Nomor Kursi', 'Nama Penumpang'])
st.cache_data.clear() # Baris tambahan untuk hapus memori
df_existing = load_data()

# Pastikan kolom ada, jika tidak buat baru
if 'Nomor Kursi' not in df_existing.columns:
    df_existing = pd.DataFrame(columns=['Nomor Kursi', 'Nama Penumpang'])

# Logika Kursi Terisi: Hanya anggap merah jika ada Nomor Kursi DAN Nama Penumpang
booked_seats = {}
if not df_existing.empty:
    for index, row in df_existing.iterrows():
        try:
            if pd.notnull(row['Nomor Kursi']) and pd.notnull(row['Nama Penumpang']):
                booked_seats[int(row['Nomor Kursi'])] = row['Nama Penumpang']
        except:
            continue

st.title("🚌 Reservasi Kursi Bus")
st.write("Klik nomor kursi putih untuk memesan.")

# Membuat Grid 2-3 (12 Baris)
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

if 'pilihan' in st.session_state:
    with st.form("form_pesan"):
        st.write(f"### Konfirmasi Kursi: {st.session_state.pilihan}")
        nama = st.text_input("Nama Penumpang")
        if st.form_submit_button("Submit"):
            if nama:
                new_row = pd.DataFrame([{"Nomor Kursi": int(st.session_state.pilihan), "Nama Penumpang": nama}])
                df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                
                # Simpan ke Google Sheet
                conn.update(spreadsheet=URL_SHEET, data=df_updated)
                st.success(f"Berhasil! Kursi {st.session_state.pilihan} sudah dipesan.")
                if 'pilihan' in st.session_state:
                    del st.session_state.pilihan
                st.rerun()
            else:
                st.error("Nama tidak boleh kosong!")
