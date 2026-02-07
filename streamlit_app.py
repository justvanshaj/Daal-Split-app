# app.py (final, robust)
import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageFile
import io, os, tempfile, unicodedata, re, datetime

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---------- CONFIG ----------
st.set_page_config(page_title="Aravally Dal Split", page_icon="favicon_split.ico")
st.title("Aravally Dal Split")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.result-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
.result-table th, .result-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
.result-table th { background-color: #f2f2f2; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ---------- INPUTS ----------
selected_date = st.date_input("Enter Date", value=datetime.date.today())
display_date = selected_date.strftime("%d/%m/%Y")

vehicle_number = st.text_input("Vehicle Number:")
party_name = st.text_input("Party Name:")
gaadi_type = st.radio("Gaadi Type:", ["KHADI", "POORI"])

a = st.number_input("Daal", min_value=0.000, step=0.001, format="%.3f")
b = st.number_input("Tukdi", min_value=0.000, step=0.001, format="%.3f")
c = st.number_input("Red/Black", min_value=0.000, step=0.001, format="%.3f")
d = st.number_input("Chhala", min_value=0.000, step=0.001, format="%.3f")
e = st.number_input("Dankhal", min_value=0.000, step=0.001, format="%.3f")
f = st.number_input("14 Mesh", min_value=0.000, step=0.001, format="%.3f")

uploaded_file = st.file_uploader("Capture/Upload an image", type=["jpg", "jpeg", "png"])

# ---------- CALCULATIONS ----------
h, i, j, k, l, m = [round(x*2,3) for x in [a,b,c,d,e,f]]

h_perc, i_perc, j_perc, k_perc, l_perc, m_perc = [round(x*10,3) for x in [h,i,j,k,l,m]]

total_dal_tukdi_grams = round(h+i,3)
total_4_grams = round(j+k+l+m,3)
grand_total_sheet = round(h+i+j+k+l+m,3)

total_dal_tukdi_perc = round(h_perc+i_perc,3)
total_4_perc = round(j_perc+k_perc+l_perc+m_perc,3)
total_6_perc = round(total_dal_tukdi_perc+total_4_perc,3)

# ---------- Image helper ----------
def adaptive_resize_and_save(uploaded_file_obj):
    if uploaded_file_obj is None:
        return None
    uploaded_file_obj.seek(0)
    img = Image.open(uploaded_file_obj).convert("RGB")
    img.thumbnail((1400,1400), Image.LANCZOS)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    img.save(tmp, format="JPEG", quality=75, optimize=True)
    tmp.close()
    return tmp.name

# ---------- PDF generation ----------
def generate_pdf_bytes_safe(uploaded_img_file):
    pdf = FPDF(format='A4')

    # page 1 image
    if uploaded_img_file:
        path = adaptive_resize_and_save(uploaded_img_file)
        pdf.add_page(orientation='L')
        pdf.image(path, x=10, y=10, w=pdf.w-20)
        os.remove(path)

    # page 2 table
    pdf.add_page(orientation='L')
    pdf.set_font("Arial","B",16)
    pdf.cell(0,12,"DAL SPLIT REPORT",ln=True,align="C")
    pdf.ln(5)

    col1, col2, col3 = 90, 60, 60
    row_h = 8

    def row(a,b,c,bold=False):
        pdf.set_font("Arial","B" if bold else "",10)
        pdf.cell(col1,row_h,a,1)
        pdf.cell(col2,row_h,b,1)
        pdf.cell(col3,row_h,c,1,ln=True)

    row("Item","Grams","Percentage",True)
    row("Daal",f"{h}",f"{h_perc}")
    row("Tukdi",f"{i}",f"{i_perc}")
    row("Total (Dal+Tukdi)",f"{total_dal_tukdi_grams}",f"{total_dal_tukdi_perc}",True)
    row("Red/Black",f"{j}",f"{j_perc}")
    row("Chhala",f"{k}",f"{k_perc}")
    row("Dankhal",f"{l}",f"{l_perc}")
    row("14 Mesh",f"{m}",f"{m_perc}")
    row("Total (4)",f"{total_4_grams}",f"{total_4_perc}",True)
    row("Grand Total",f"{grand_total_sheet}",f"{total_6_perc}",True)

    return pdf.output(dest='S').encode('latin-1')

# ---------- Generate & download ----------
if st.button("Generate Karo"):
    pdf_bytes = generate_pdf_bytes_safe(uploaded_file)

    # ✅ ONLY RENAMING SYSTEM
    pretty_date = selected_date.strftime("%d-%m-%Y")
    pretty_vehicle = (vehicle_number or "").upper().replace("_","-").strip()
    pretty_party = (party_name or "").title().strip()
    pretty_gaadi = f"{gaadi_type.title()}-Gaadi"

    safe_name = f"{pretty_date} {pretty_vehicle} {pretty_party} {pretty_gaadi}.pdf"
    safe_name = re.sub(r'[<>:"/\\|?*]', '', safe_name)

    st.success("PDF generate hogayi")
    st.download_button("📥 Download Karo", data=pdf_bytes, file_name=safe_name, mime="application/pdf")
