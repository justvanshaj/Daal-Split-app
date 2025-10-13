# app.py
import streamlit as st
from fpdf import FPDF
from PIL import Image
import io
import datetime
import unicodedata
import re
import tempfile
import os

# ---------- Config ----------
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
@media (max-width: 480px) {
  .result-table td, .result-table th { font-size: 14px; padding: 6px; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Inputs ----------
selected_date = st.date_input("Select Date (DD/MM/YYYY)", value=datetime.date.today())
display_date = selected_date.strftime("%d/%m/%Y")
filename_date = selected_date.strftime("%Y-%m-%d")

vehicle_number = st.text_input("Vehicle Number:")
party_name = st.text_input("Party Name:")
gaadi_type = st.radio("Gaadi Type:", ["Khadi", "Poori"])

st.write("Enter weights (input values; app computes sheet grams = input * 2). Precision: 3 decimals")
a = st.number_input("Daal (input)", min_value=0.000, step=0.001, format="%.3f")
b = st.number_input("Tukdi (input)", min_value=0.000, step=0.001, format="%.3f")
c = st.number_input("Red/Black (input)", min_value=0.000, step=0.001, format="%.3f")
d = st.number_input("Chhala (input)", min_value=0.000, step=0.001, format="%.3f")
e = st.number_input("Dankhal (input)", min_value=0.000, step=0.001, format="%.3f")
f = st.number_input("14 Mesh (input)", min_value=0.000, step=0.001, format="%.3f")

# File uploader (no camera)
uploaded_file = st.file_uploader("Upload an image (jpg, jpeg, png) — this will be page 1 of the PDF", type=["jpg", "jpeg", "png"])

# ---------- Calculations ----------
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
st.subheader("Results preview")
st.write(f"Grand total (sum of inputs): **{g_sum_inputs} g**")
def render_results_table():
    html = f"""
    <table class="result-table">
      <thead>
        <tr><th>Item</th><th>Grams</th><th>Percentage</th></tr>
      </thead>
      <tbody>
        <tr><td>Daal</td><td>{h} g</td><td>{h_perc} %</td></tr>
        <tr><td>Tukdi</td><td>{i} g</td><td>{i_perc} %</td></tr>
        <tr style="font-weight:700;"><td>Total (Dal + Tukdi)</td><td>{total_dal_tukdi_grams} g</td><td>{total_dal_tukdi_perc} %</td></tr>
        <tr><td>Red/Black</td><td>{j} g</td><td>{j_perc} %</td></tr>
        <tr><td>Chhala</td><td>{k} g</td><td>{k_perc} %</td></tr>
        <tr><td>Dankhal</td><td>{l} g</td><td>{l_perc} %</td></tr>
        <tr><td>14 Mesh</td><td>{m} g</td><td>{m_perc} %</td></tr>
        <tr style="font-weight:700;"><td>Total (4)</td><td>{total_4_grams} g</td><td>{total_4_perc} %</td></tr>
        <tr style="font-weight:700;"><td>Grand Total for Sheet</td><td>{grand_total_sheet} g</td><td>{total_6_perc} %</td></tr>
      </tbody>
    </table>
    """
    st.markdown(html, unsafe_allow_html=True)
render_results_table()

# ---------- Image compression ----------
MAX_WIDTH, MAX_HEIGHT, JPEG_QUALITY = 1200, 1600, 70
def resize_and_compress_image(pil_img, max_w=MAX_WIDTH, max_h=MAX_HEIGHT, quality=JPEG_QUALITY):
    img = pil_img.copy()
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    buf.seek(0)
    return buf

# ---------- PDF generation ----------
def slugify(value):
    value = str(value or "")
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def generate_pdf_bytes(uploaded_img_file, data):
    pdf = FPDF(format='A4')

    # --- Page 1: image (landscape) ---
    if uploaded_img_file is not None:
        temp_path = None
        try:
            pil_img = Image.open(uploaded_img_file)
            img_buf = resize_and_compress_image(pil_img)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
                tmpfile.write(img_buf.read())
                tmpfile.flush()
                temp_path = tmpfile.name
            pdf.add_page(orientation='L')
            pdf.image(temp_path, x=10, y=10, w=pdf.w - 20)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        pdf.add_page(orientation='L')
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "No Image Provided", ln=True, align='C')

    # --- Page 2: report (✅ landscape now) ---
    pdf.add_page(orientation='L')
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header box
    pdf.set_font("Arial", "B", 14)
    box_x, box_y, box_w, box_h = 20, 10, pdf.w - 40, 14
    pdf.rect(box_x, box_y, box_w, box_h)
    pdf.set_xy(box_x, box_y + 1)
    pdf.cell(box_w, 6, txt="ARAVALLY PROCESSED AGROTECH PVT. LTD.", ln=1, align='C')
    pdf.set_xy(box_x, box_y + 7)
    pdf.set_font("Arial", size=12)
    pdf.cell(box_w, 6, txt="DAL SPLIT REPORT", ln=1, align='C')
    pdf.ln(6)

    # Party / Date / Vehicle / Gaadi
    pdf.set_font("Arial", size=10)
    col_w = (pdf.w - 20) / 2
    row_h = 8
    start_x = 10
    y_before = pdf.get_y()
    pdf.rect(start_x, y_before, col_w, row_h)
    pdf.rect(start_x + col_w, y_before, col_w, row_h)
    pdf.set_xy(start_x + 2, y_before + 2)
    pdf.cell(col_w - 4, 4, txt=f"PARTY NAME : {data['PARTY']}")
    pdf.set_xy(start_x + col_w + 2, y_before + 2)
    pdf.cell(col_w - 4, 4, txt=f"DATE : {data['DATE']}")
    pdf.ln(row_h + 2)

    y2 = pdf.get_y()
    pdf.rect(start_x, y2, col_w, row_h)
    pdf.rect(start_x + col_w, y2, col_w, row_h)
    pdf.set_xy(start_x + 2, y2 + 2)
    pdf.cell(col_w - 4, 4, txt=f"VEHICLE NUMBER : {data['VEHICLE']}")
    pdf.set_xy(start_x + col_w + 2, y2 + 2)
    pdf.cell(col_w - 4, 4, txt=f"GAADI TYPE : {data['GAADI']}")
    pdf.ln(row_h + 6)

    # Table
    pdf.set_font("Arial", "B", 10)
    page_inner_w = pdf.w - 20
    left_col_w, right_col_w = page_inner_w / 2, page_inner_w / 2
    table_x, table_y, current_y = 10, pdf.get_y(), pdf.get_y()
    row_h = 8
    pdf.rect(table_x, current_y, left_col_w + right_col_w, row_h)
    pdf.set_xy(table_x + 2, current_y + 2)
    pdf.cell(left_col_w - 4, 4, "INDIVIDUAL PARTICLE DATA (in gram)")
    pdf.set_xy(table_x + left_col_w + 2, current_y + 2)
    pdf.cell(right_col_w - 4, 4, "INDIVIDUAL PARTICLE DATA (in percentage)")
    current_y += row_h

    def row_two_columns(left, right, bold=False):
        nonlocal current_y
        h = 8
        pdf.rect(table_x, current_y, left_col_w, h)
        pdf.rect(table_x + left_col_w, current_y, right_col_w, h)
        pdf.set_font("Arial", "B" if bold else "", 10)
        pdf.set_xy(table_x + 2, current_y + 2)
        pdf.multi_cell(left_col_w - 4, 4, left)
        pdf.set_xy(table_x + left_col_w + 2, current_y + 2)
        pdf.multi_cell(right_col_w - 4, 4, right)
        current_y += h

    row_two_columns(f"DAAL : {data['DAAL']} gm", f"DAAL : {data['DAAL_PERC']} %")
    row_two_columns(f"TUKDI : {data['TUKDI']} gm", f"TUKDI : {data['TUKDI_PERC']} %")
    row_two_columns(f"TOTAL ( DAAL + TUKDI ) : {data['TOTAL_DTG']} gm", f"TOTAL ( DAAL + TUKDI ) : {data['TOTAL_DTP']} %", True)
    row_two_columns(f"RED / BLACK : {data['REDBLACK']} gm", f"RED / BLACK : {data['REDBLACK_PERC']} %")
    row_two_columns(f"CHHALA : {data['CHHALA']} gm", f"CHHALA : {data['CHHALA_PERC']} %")
    row_two_columns(f"DANKHAL : {data['DANKHAL']} gm", f"DANKHAL : {data['DANKHAL_PERC']} %")
    row_two_columns(f"14 MESH : {data['MES14']} gm", f"14 MESH : {data['MES14_PERC']} %")
    row_two_columns(f"TOTAL ( R/B + C + D + 14# ) : {data['TOTAL_4_GRAMS']} gm", f"TOTAL ( R/B + C + D + 14# ) : {data['TOTAL_4']} %", True)
    row_two_columns(f"GRAND TOTAL : {data['GRAND_TOTAL']} gm", f"GRAND TOTAL : {data['TOTAL_6']} %", True)
    pdf.rect(table_x, table_y, left_col_w + right_col_w, current_y - table_y)

    return pdf.output(dest='S').encode('latin-1')

# ---------- Data ----------
data = {
    "DATE": display_date,
    "VEHICLE": vehicle_number or "",
    "PARTY": party_name or "",
    "GAADI": gaadi_type,
    "DAAL": h, "TUKDI": i, "TOTAL_DTG": total_dal_tukdi_grams, "TOTAL_DTP": total_dal_tukdi_perc,
    "REDBLACK": j, "CHHALA": k, "DANKHAL": l, "MES14": m,
    "TOTAL_4_GRAMS": total_4_grams, "TOTAL_4": total_4_perc,
    "GRAND_TOTAL": grand_total_sheet, "TOTAL_6": total_6_perc,
    "DAAL_PERC": h_perc, "TUKDI_PERC": i_perc, "REDBLACK_PERC": j_perc,
    "CHHALA_PERC": k_perc, "DANKHAL_PERC": l_perc, "MES14_PERC": m_perc
}

# ---------- Generate & Download ----------
if st.button("Generate PDF"):
    try:
        pdf_bytes = generate_pdf_bytes(uploaded_file, data)
        safe_name = f"{filename_date}_{slugify(vehicle_number)}_{slugify(party_name)}_{slugify(gaadi_type)}_gaadi.pdf"
        st.success("PDF generated — click to download")
        st.download_button("📥 Download PDF", data=pdf_bytes, file_name=safe_name, mime="application/pdf")
    except Exception as ex:
        st.error(f"Failed to generate PDF: {ex}")
