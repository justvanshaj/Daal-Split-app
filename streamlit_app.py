# app.py (final, robust)
import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageFile
import io, os, tempfile, unicodedata, re, datetime

# allow PIL to load truncated images sometimes
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
g_sum_inputs = round(a + b + c + d + e + f, 3)

h = round(a * 2, 3)
i = round(b * 2, 3)
j = round(c * 2, 3)
k = round(d * 2, 3)
l = round(e * 2, 3)
m = round(f * 2, 3)

grand_total_sheet = round(h + i + j + k + l + m, 3)

h_perc = round(h * 10, 3)
i_perc = round(i * 10, 3)
j_perc = round(j * 10, 3)
k_perc = round(k * 10, 3)
l_perc = round(l * 10, 3)
m_perc = round(m * 10, 3)

total_dal_tukdi_perc = round(h_perc + i_perc, 3)
total_4_perc = round(j_perc + k_perc + l_perc + m_perc, 3)
total_6_perc = round(total_dal_tukdi_perc + total_4_perc, 3)

total_dal_tukdi_grams = round(h + i, 3)
total_4_grams = round(j + k + l + m, 3)

# ---------- Preview table ----------
st.subheader("Results")
st.write(f"Live Input Checker: **{g_sum_inputs} gm**")

def render_results_table():
    html = f"""
    <table class="result-table">
      <thead>
        <tr><th>Item</th><th>Grams</th><th>Percentage</th></tr>
      </thead><tbody>
        <tr><td>Daal</td><td>{h} g</td><td>{h_perc} %</td></tr>
        <tr><td>Tukdi</td><td>{i} g</td><td>{i_perc} %</td></tr>
        <tr style="font-weight:700;"><td>Total (Dal + Tukdi)</td><td>{total_dal_tukdi_grams} g</td><td>{total_dal_tukdi_perc} %</td></tr>
        <tr><td>Red/Black</td><td>{j} g</td><td>{j_perc} %</td></tr>
        <tr><td>Chhala</td><td>{k} g</td><td>{k_perc} %</td></tr>
        <tr><td>Dankhal</td><td>{l} g</td><td>{l_perc} %</td></tr>
        <tr><td>14 Mesh</td><td>{m} g</td><td>{m_perc} %</td></tr>
        <tr style="font-weight:700;"><td>Total (4)</td><td>{total_4_grams} g</td><td>{total_4_perc} %</td></tr>
        <tr style="font-weight:700;"><td>Grand Total for Sheet</td><td>{grand_total_sheet} g</td><td>{total_6_perc} %</td></tr>
      </tbody></table>
    """
    st.markdown(html, unsafe_allow_html=True)

render_results_table()

# ---------- Image processing helpers ----------
def adaptive_resize_and_save(uploaded_file_obj):
    if uploaded_file_obj is None:
        return None

    uploaded_file_obj.seek(0)
    pil_img = Image.open(uploaded_file_obj)

    if pil_img.mode not in ("RGB", "L"):
        pil_img = pil_img.convert("RGB")

    pil_img.thumbnail((1400, 1400), Image.LANCZOS)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    pil_img.save(tmp, format="JPEG", quality=75, optimize=True)
    tmp.close()

    return tmp.name

# ---------- PDF generation ----------
def generate_pdf_bytes_safe(uploaded_img_file, data):
    pdf = FPDF(format='A4')

    if uploaded_img_file is not None:
        temp_img_path = adaptive_resize_and_save(uploaded_img_file)
        pdf.add_page(orientation='L')
        pdf.image(temp_img_path, x=10, y=10, w=pdf.w - 20)
        os.remove(temp_img_path)
    else:
        pdf.add_page(orientation='L')
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "No Image Provided", ln=True, align='C')

    pdf.add_page(orientation='L')
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "DAL SPLIT REPORT", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    for k, v in data.items():
        pdf.cell(0, 8, f"{k} : {v}", ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ---------- Data mapping ----------
data = {
    "DATE": display_date,
    "VEHICLE": vehicle_number or "",
    "PARTY": party_name or "",
    "GAADI": gaadi_type,
    "DAAL": h,
    "TUKDI": i,
    "GRAND_TOTAL": grand_total_sheet
}

# ---------- Generate & download ----------
if st.button("Generate Karo"):
    try:
        pdf_bytes = generate_pdf_bytes_safe(uploaded_file, data)

        # ✅ NEW PRETTY RENAMING SYSTEM (ONLY CHANGE)
        pretty_date = selected_date.strftime("%d-%m-%Y")
        pretty_vehicle = (vehicle_number or "").upper().replace("_", "-").strip()
        pretty_party = (party_name or "").title().strip()
        pretty_gaadi = f"{gaadi_type.title()}-Gaadi"

        safe_name = f"{pretty_date} {pretty_vehicle} {pretty_party} {pretty_gaadi}.pdf"
        safe_name = re.sub(r'[<>:"/\\|?*]', '', safe_name)

        st.success("PDF generate hogayi")
        st.download_button("📥 Download Karo", data=pdf_bytes, file_name=safe_name, mime="application/pdf")

    except Exception as ex:
        st.error("Failed to generate PDF")
        st.write(repr(ex))
