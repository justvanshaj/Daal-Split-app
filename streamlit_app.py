import streamlit as st
from fpdf import FPDF
from PIL import Image
import io
import re
import unicodedata
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Aravally Dal Split", page_icon="favicon_split.ico")
st.header("Dal Split Calculator")

# Hide Streamlit UI chrome
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- DATE INPUT (calendar) ----------
# Use user's timezone context from your deployment; here we default to current day as required.
# Per instructions the "current date" is 2025-10-13, so default_date is set explicitly to that day.
default_date = datetime.date(2025, 10, 13)  # YYYY, M, D
selected_date = st.date_input("Select Date (DD/MM/YYYY)", value=default_date)
# Format for display in template: DD/MM/YYYY
display_date = selected_date.strftime("%d/%m/%Y")
# Filename-safe date (YYYY-MM-DD)
filename_date = selected_date.strftime("%Y-%m-%d")

# ---------- INPUTS ----------
vehicle_number = st.text_input("Enter Vehicle Number:")
party_name = st.text_input("Enter Party Name:")
gaadi_type = st.radio("Select Gaadi Type:", options=["Khadi", "Poori"])

st.write("**Enter weights (grams)** — 3 decimal precision")
a = st.number_input("Daal (input)", min_value=0.000, step=0.001, format="%.3f")
b = st.number_input("Tukdi (input)", min_value=0.000, step=0.001, format="%.3f")
c = st.number_input("Red/Black (input)", min_value=0.000, step=0.001, format="%.3f")
d = st.number_input("Chhala (input)", min_value=0.000, step=0.001, format="%.3f")
e = st.number_input("Dankhal (input)", min_value=0.000, step=0.001, format="%.3f")
f = st.number_input("14 Mesh (input)", min_value=0.000, step=0.001, format="%.3f")

# Image input (camera or upload)
col_img1, col_img2 = st.columns(2)
with col_img1:
    try:
        camera_img = st.camera_input("Capture image (camera)")
    except Exception:
        camera_img = None
with col_img2:
    uploaded_file = st.file_uploader("Or upload an image", type=["jpg", "jpeg", "png"])

image_file = camera_img if camera_img is not None else uploaded_file

# ---------- CALCULATIONS ----------
g = round(a + b + c + d + e + f, 3)
h = round(a * 2, 3)  # Daal (sheet grams)
i = round(b * 2, 3)  # Tukdi
j = round(c * 2, 3)  # Red/Black
k = round(d * 2, 3)  # Chhala
l = round(e * 2, 3)  # Dankhal
m = round(f * 2, 3)  # 14 Mesh
grand_total = round(h + i + j + k + l + m, 3)

# Percentages (kept original behavior)
h_percent = round(h * 10, 3)
i_percent = round(i * 10, 3)
j_percent = round(j * 10, 3)
k_percent = round(k * 10, 3)
l_percent = round(l * 10, 3)
m_percent = round(m * 10, 3)

# Totals (percent)
total_dal_tukdi_percent = round(h_percent + i_percent, 3)
total_4_percent = round(j_percent + k_percent + l_percent + m_percent, 3)
total_6_percent = round(total_dal_tukdi_percent + total_4_percent, 3)

# Totals (grams) — as requested
total_dal_tukdi_grams = round(h + i, 3)
total_4_grams = round(j + k + l + m, 3)

# ---------- DISPLAY (grams & percent side-by-side) ----------
st.subheader("Grand Total")
st.write(f"Grand Total (sum of raw inputs): **{g} g**")

st.subheader("Details — grams and percentage")

def row_display(label, grams, percent):
    c1, c2, c3 = st.columns([2.5, 2, 2])
    c1.write(f"**{label}**")
    c2.write(f"{grams} g")
    c3.write(f"{percent} %")

# Daal
row_display("Daal", h, h_percent)
# Tukdi
row_display("Tukdi", i, i_percent)
# Total (Dal + Tukdi) right after Tukdi
st.markdown("**Total (Dal + Tukdi)**")
row_display("Total (Dal + Tukdi)", total_dal_tukdi_grams, total_dal_tukdi_percent)
st.markdown("---")

# Remaining items
row_display("Red/Black", j, j_percent)
row_display("Chhala", k, k_percent)
row_display("Dankhal", l, l_percent)
row_display("14 Mesh", m, m_percent)

# Total (4) right after 14 Mesh
st.markdown("**Total (4)**")
row_display("Total (4)", total_4_grams, total_4_percent)
st.markdown("---")

# Grand Total row
row_display("Grand Total for Sheet", grand_total, total_6_percent)

# ---------- TEMPLATE (from repo) ----------
TEMPLATE_PATH = "report_template.txt"

def load_template(path=TEMPLATE_PATH):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return None

template_text = load_template()
if template_text is None:
    st.warning(f"Template file '{TEMPLATE_PATH}' not found in repo root. Add it and use placeholders as shown below.")

# ---------- PDF GENERATION ----------
def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def generate_pdf_bytes(image_file, template_text, data_map):
    pdf = FPDF()

    # First page: image (landscape)
    if image_file is not None:
        try:
            img = Image.open(image_file)
            img_buffer = io.BytesIO()
            img.convert("RGB").save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            pdf.add_page(orientation='L')
            pdf.image(img_buffer, x=10, y=10, w=270)
        except Exception as e:
            pdf.add_page(orientation='L')
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Image error: {e}", ln=True, align='C')
    else:
        pdf.add_page(orientation='L')
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "No Image Provided", ln=True, align='C')

    # Second page: template (portrait)
    pdf.add_page(orientation='P')
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    if template_text:
        filled = template_text
        for key, val in data_map.items():
            filled = filled.replace("{" + key + "}", str(val))
        for line in filled.splitlines():
            pdf.multi_cell(0, 8, line)
    else:
        # Fallback body if template missing
        lines = [
            "Dal Split Report",
            "",
            f"Date: {data_map['DATE']}",
            f"Vehicle Number: {data_map['VEHICLE']}",
            f"Party Name: {data_map['PARTY']}",
            f"Gaadi Type: {data_map['GAADI']}",
            "",
            "Details (grams):",
            f"Daal: {data_map['DAAL']} gm",
            f"Tukdi: {data_map['TUKDI']} gm",
            f"Total (Dal + Tukdi): {data_map['TOTAL_DTG']} gm",
            f"Red/Black: {data_map['REDBLACK']} gm",
            f"Chhala: {data_map['CHHALA']} gm",
            f"Dankhal: {data_map['DANKHAL']} gm",
            f"14 Mesh: {data_map['MES14']} gm",
            f"Total (4): {data_map['TOTAL_4_GRAMS']} gm",
            f"Grand Total for Sheet: {data_map['GRAND_TOTAL']} gm",
            "",
            "Details (percentage):",
            f"Daal: {data_map['DAAL_PERC']} %",
            f"Tukdi: {data_map['TUKDI_PERC']} %",
            f"Total (Dal + Tukdi): {data_map['TOTAL_DTP']} %",
            f"Red/Black: {data_map['REDBLACK_PERC']} %",
            f"Chhala: {data_map['CHHALA_PERC']} %",
            f"Dankhal: {data_map['DANKHAL_PERC']} %",
            f"14 Mesh: {data_map['MES14_PERC']} %",
            f"Total (4): {data_map['TOTAL_4']} %",
            f"Total (6): {data_map['TOTAL_6']} %"
        ]
        for ln in lines:
            pdf.multi_cell(0, 8, ln)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

# ---------- DATA MAP with new DATE format and placeholder names ----------
data_map = {
    "DATE": display_date,                   # DD/MM/YYYY for template
    "VEHICLE": vehicle_number,
    "PARTY": party_name,
    "GAADI": gaadi_type,
    "DAAL": h,
    "TUKDI": i,
    "TOTAL_DTG": total_dal_tukdi_grams,     # your chosen placeholder for grams
    "TOTAL_DTP": total_dal_tukdi_percent,   # your chosen placeholder for percent
    "REDBLACK": j,
    "CHHALA": k,
    "DANKHAL": l,
    "MES14": m,
    "TOTAL_4_GRAMS": total_4_grams,
    "TOTAL_4": total_4_percent,
    "GRAND_TOTAL": grand_total,
    "TOTAL_6": total_6_percent,
    "DAAL_PERC": h_percent,
    "TUKDI_PERC": i_percent,
    "REDBLACK_PERC": j_percent,
    "CHHALA_PERC": k_percent,
    "DANKHAL_PERC": l_percent,
    "MES14_PERC": m_percent
}

# ---------- GENERATE + DOWNLOAD BUTTON ----------
if st.button("Generate PDF"):
    pdf_bytes = generate_pdf_bytes(image_file, template_text, data_map)
    # filename uses safe date format (YYYY-MM-DD)
    fname = f"{filename_date}_{slugify(vehicle_number)}_{slugify(party_name)}_{slugify(gaadi_type)}_gaadi.pdf"
    st.success("PDF generated — click to download")
    st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name=fname, mime="application/pdf")
