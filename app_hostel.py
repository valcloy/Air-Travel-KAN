import streamlit as st
import io
import pandas as pd
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_hostel_pdf(data):
    template_path = "Hostel Form.pdf"
    if not os.path.exists(template_path):
        st.error("File template 'Hostel Form.pdf' tidak ditemukan!")
        return None
    try:
        reader = PdfReader(template_path)
        writer = PdfWriter()
        page = reader.pages[0]
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Menggunakan font 10.5 agar pas di atas garis titik-titik
        can.setFont("Helvetica", 10.5)

        # 1. TANGGAL PENGAJUAN (ATAS)
        can.drawString(355, 694, data['today_date'])

        # 2. DATA DIRI
        can.drawString(90, 660, data['name'])           
        can.drawString(125, 635, data['id_no'])          
        des_nat = f"{data['designation']} / {data['nationality']}"
        can.drawString(140, 609, des_nat)                
        can.drawString(145, 580, data['tel_no'])         
        can.drawString(145, 555, data['dept'])           
        can.drawString(145, 528, data['address'])        

        # 3. KONTAK DARURAT
        y_emg = 473 
        for i in range(1, 4):
            if data[f'en{i}']:
                can.drawString(38, y_emg, data[f'en{i}'])   
                can.drawString(215, y_emg, data[f'er{i}'])  
                can.drawString(360, y_emg, data[f'et{i}'])  
            y_emg -= 15 

        # 4. JADWAL MENGINAP
        can.drawString(210, 390, data['check_in']) 
        if data['check_out']:
            can.drawString(210, 375, data['check_out'])

        # --- TAMBAHAN: TANGGAL DI KIRI BAWAH SAJA ---
        # Menempatkan tanggal di atas garis "Date/Tanggal" sisi kiri (GA Use Only)
        can.drawString(80, 151, data['today_date']) 

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()
    except Exception as e:
        st.error(f"Gagal memproses PDF: {e}")
        return None

# --- UI WEBSITE ---
st.title("Hostel Accommodation Form PT KAN")

if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = None

with st.form("hostel_form"):
    tgl = st.date_input("Tanggal").strftime("%d-%m-%Y")
    c1, c2 = st.columns(2)
    with c1:
        nama = st.text_input("Nama Lengkap")
        ic = st.text_input("IC/Passport No")
        jab = st.text_input("Jabatan")
    with c2:
        neg = st.text_input("Kewarganegaraan")
        dep = st.text_input("Departemen")
        tel = st.text_input("No HP")
    adr = st.text_area("Alamat Lengkap")

    st.subheader("Kontak Darurat")
    emg = {}
    for i in range(1, 4):
        col1, col2, col3 = st.columns(3)
        emg[f'en{i}'] = col1.text_input(f"Nama {i}", key=f"en{i}")
        emg[f'er{i}'] = col2.text_input(f"Hubungan {i}", key=f"er{i}")
        emg[f'et{i}'] = col3.text_input(f"Telp {i}", key=f"et{i}")

    cin = st.date_input("Check-In").strftime("%d-%m-%Y")
    cout_opt = st.checkbox("Tentukan tanggal Check-Out?")
    cout = st.date_input("Check-Out").strftime("%d-%m-%Y") if cout_opt else ""

    if st.form_submit_button("Proses & Simpan"):
        payload = {
            'today_date': tgl, 'name': nama, 'id_no': ic,
            'designation': jab, 'nationality': neg, 'tel_no': tel,
            'dept': dep, 'address': adr, 'check_in': cin, 'check_out': cout, **emg
        }
        st.session_state.pdf_ready = generate_hostel_pdf(payload)
        st.session_state.download_name = nama
        st.success("Data berhasil diproses!")

if st.session_state.pdf_ready:
    st.download_button("⬇️ Download PDF Hasil", st.session_state.pdf_ready, f"Hostel_{st.session_state.download_name}.pdf")