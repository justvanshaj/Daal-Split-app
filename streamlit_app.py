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

# Only uploader (no camera)
uploaded_file = st.file_uploader("Upload an image (jpg, jpeg, png) — this will be page 1 of the PDF", type=["jpg", "jpeg", "png"])

# ---------- Calculations ----------
g_sum_inputs = round(a + b + c + d + e + f, 3)

# Sheet grams (your original logic)
h = round(a * 2, 3)  # Daal (sheet grams)
i = round(b * 2, 3)  # Tukdi
j = round(c * 2, 3)
k = round(d * 2, 3)
l = round(e * 2, 3)
m = round(f * 2, 3)

grand_total_sheet = round(h + i + j + k + l + m, 3)

# Percent values (original behaviour: *10)
h_perc = round(h * 10, 3)
i_perc = round(i * 10, 3)
j_perc = round(j * 10, 3)
k_perc = round(k * 10, 3)
l_perc = round(l * 10, 3)
m_perc = round(m * 10, 3)

total_dal_tukdi_perc = round(h_perc + i_perc, 3)
total_4_perc = round(j_perc + k_perc + l_perc + m_perc, 3)
total_6_perc = round(total_dal_tukdi_perc + total_4_perc, 3)

# Gram totals
total_dal_tukdi_grams = round(h + i, 3)
total_4_grams = round(j + k + l + m, 3)

# ---------- Preview table (mobile-friendly HTML) ----------
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

# ---------- Image resize/compress settings ----------
MAX_WIDTH = 1200          # maximum width in pixels after resize (helps avoid OOM)
MAX_HEIGHT = 1600         # max height (preserve aspect ratio)
JPEG_QUALITY = 70         # 0-100 (lower -> smaller file)

def resize_and_compress_image(pil_img, max_w=MAX_WIDTH, max_h=MAX_HEIGHT, quality=JPEG_QUALITY):
    img = pil_img.copy()
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    buf.seek(0)
    return buf

# ---------- PDF generation (uses temp file for image) ----------
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

            # Save to a temporary file so FPDF can read it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
                tmpfile.write(img_buf.read())
                tmpfile.flush()
                temp_path = tmpfile.name

            pdf.add_page(orientation='L')
            page_w = pdf.w - 20
            pdf.image(temp_path, x=10, y=10, w=page_w)

        except Exception as e:
            pdf.add_page(orientation='L')
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Image error: {e}", ln=True, align='C')
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
    else:
        pdf.add_page(orientation='L')
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "No Image Provided", ln=True, align='C')

    # --- Page 2: report (portrait) ---
    pdf.add_page(orientation='P')
    pdf.set_auto_page_break(auto=True, margin=15)

    # Company header box
    pdf.set_font("Arial", "B", 14)
    box_x = 20
    box_w = pdf.w - 40
    box_y = 10
    box_h = 14
    pdf.rect(box_x, box_y, box_w, box_h)
    pdf.set_xy(box_x, box_y + 1)
    pdf.cell(box_w, 6, txt="ARAVALLY PROCESSED AGROTECH PVT. LTD.", border=0, ln=1, align='C')
    pdf.set_xy(box_x, box_y + 7)
    pdf.set_font("Arial", size=12)
    pdf.cell(box_w, 6, txt="DAL SPLIT REPORT", border=0, ln=1, align='C')
    pdf.ln(6)

    # Party / Date / Vehicle / Gaadi table (two columns)
    pdf.set_font("Arial", size=10)
    col_w = (pdf.w - 20) / 2
    row_h = 8
    start_x = 10
    y_before = pdf.get_y()
    pdf.rect(start_x, y_before, col_w, row_h)
    pdf.rect(start_x + col_w, y_before, col_w, row_h)
    pdf.set_xy(start_x + 2, y_before + 2)
    pdf.cell(col_w - 4, 4, txt=f"PARTY NAME : {data['PARTY']}", ln=0)
    pdf.set_xy(start_x + col_w + 2, y_before + 2)
    pdf.cell(col_w - 4, 4, txt=f"DATE : {data['DATE']}", ln=0)
    pdf.ln(row_h + 2)

    y2 = pdf.get_y()
    pdf.rect(start_x, y2, col_w, row_h)
    pdf.rect(start_x + col_w, y2, col_w, row_h)
    pdf.set_xy(start_x + 2, y2 + 2)
    pdf.cell(col_w - 4, 4, txt=f"VEHICLE NUMBER : {data['VEHICLE']}", ln=0)
    pdf.set_xy(start_x + col_w + 2, y2 + 2)
    pdf.cell(col_w - 4, 4, txt=f"GAADI TYPE : {data['GAADI']}", ln=0)
    pdf.ln(row_h + 6)

    # Main two-column table body
    pdf.set_font("Arial", "B", 10)
    page_inner_w = pdf.w - 20
    left_col_w = page_inner_w * 0.5
    right_col_w = page_inner_w * 0.5
    table_x = 10
    table_y = pdf.get_y()
    current_y = table_y

    # Title row
    row_h = 8
    pdf.rect(table_x, current_y, left_col_w + right_col_w, row_h)
    pdf.set_xy(table_x + 2, current_y + 2)
    pdf.cell(left_col_w - 4, 4, txt="INDIVIDUAL PARTICLE DATA (in gram)", ln=0)
    pdf.set_xy(table_x + left_col_w + 2, current_y + 2)
    pdf.cell(right_col_w - 4, 4, txt="INDIVIDUAL PARTICLE DATA (in percentage)", ln=0)
    current_y += row_h

    def row_two_columns(left_text, right_text, bold=False):
        nonlocal current_y
        h = 8
        pdf.rect(table_x, current_y, left_col_w, h)
        pdf.rect(table_x + left_col_w, current_y, right_col_w, h)
        if bold:
            pdf.set_font("Arial", "B", 10)
        else:
            pdf.set_font("Arial", size=10)
        pdf.set_xy(table_x + 2, current_y + 2)
        pdf.multi_cell(left_col_w - 4, 4, left_text)
        pdf.set_xy(table_x + left_col_w + 2, current_y + 2)
        pdf.multi_cell(right_col_w - 4, 4, right_text)
        current_y += h

    # Rows in specified order
    row_two_columns(f"DAAL : {data['DAAL']} gm", f"DAAL : {data['DAAL_PERC']} %")
    row_two_columns(f"TUKDI : {data['TUKDI']} gm", f"TUKDI : {data['TUKDI_PERC']} %")
    row_two_columns(f"TOTAL ( DAAL + TUKDI ) : {data['TOTAL_DTG']} gm", f"TOTAL ( DAAL + TUKDI ) : {data['TOTAL_DTP']} %", bold=True)
    row_two_columns(f"RED / BLACK : {data['REDBLACK']} gm", f"RED / BLACK : {data['REDBLACK_PERC']} %")
    row_two_columns(f"CHHALA : {data['CHHALA']} gm", f"CHHALA : {data['CHHALA_PERC']} %")
    row_two_columns(f"DANKHAL : {data['DANKHAL']} gm", f"DANKHAL : {data['DANKHAL_PERC']} %")
    row_two_columns(f"14 MESH : {data['MES14']} gm", f"14 MESH : {data['MES14_PERC']} %")
    row_two_columns(f"TOTAL ( R/B + C + D + 14# ) : {data['TOTAL_4_GRAMS']} gm", f"TOTAL ( R/B + C + D + 14# ) : {data['TOTAL_4']} %", bold=True)
    row_two_columns(f"GRAND TOTAL : {data['GRAND_TOTAL']} gm", f"GRAND TOTAL : {data['TOTAL_6']} %", bold=True)

    # Outer border around the whole table
    pdf.rect(table_x, table_y, left_col_w + right_col_w, current_y - table_y)

    return pdf.output(dest='S').encode('latin-1')

# ---------- Data dictionary for PDF generation ----------
data = {
    "DATE": display_date,
    "VEHICLE": vehicle_number or "",
    "PARTY": party_name or "",
    "GAADI": gaadi_type,
    "DAAL": h,
    "TUKDI": i,
    "TOTAL_DTG": total_dal_tukdi_grams,
    "TOTAL_DTP": total_dal_tukdi_perc,
    "REDBLACK": j,
    "CHHALA": k,
    "DANKHAL": l,
    "MES14": m,
    "TOTAL_4_GRAMS": total_4_grams,
    "TOTAL_4": total_4_perc,
    "GRAND_TOTAL": grand_total_sheet,
    "TOTAL_6": total_6_perc,
    "DAAL_PERC": h_perc,
    "TUKDI_PERC": i_perc,
    "REDBLACK_PERC": j_perc,
    "CHHALA_PERC": k_perc,
    "DANKHAL_PERC": l_perc,
    "MES14_PERC": m_perc
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
        st.write("If you are on mobile and still see memory errors, reduce image size before upload or deploy the app to a server so generation happens server-side.")
