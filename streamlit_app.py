import streamlit as st
from fpdf import FPDF
from PIL import Image
import io
import re
import unicodedata
import datetime
import logging

# ---------- Config ----------
st.set_page_config(page_title="Aravally Dal Split", page_icon="favicon_split.ico")
st.header("Dal Split Calculator")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Table styling for results */
.result-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
.result-table th, .result-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
.result-table th { background-color: #f2f2f2; font-weight:600; }
@media (max-width: 480px) {
  .result-table td, .result-table th { font-size: 14px; padding: 6px; }
}
</style>
""", unsafe_allow_html=True)

logger = logging.getLogger(__name__)

# ---------- DATE INPUT ----------
selected_date = st.date_input("Select Date (DD/MM/YYYY)", value=datetime.date.today())
display_date = selected_date.strftime("%d/%m/%Y")
filename_date = selected_date.strftime("%Y-%m-%d")

# ---------- INPUT FIELDS ----------
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

# ---------- IMAGE UPLOADER (camera removed) ----------
uploaded_file = st.file_uploader("Upload an image (jpg, jpeg, png) — this will be page 1 of the PDF", type=["jpg", "jpeg", "png"])
image_file = uploaded_file  # only uploader used

# ---------- CALCULATIONS ----------
g = round(a + b + c + d + e + f, 3)
h = round(a * 2, 3)  # Daal grams for sheet
i = round(b * 2, 3)  # Tukdi grams for sheet
j = round(c * 2, 3)
k = round(d * 2, 3)
l = round(e * 2, 3)
m = round(f * 2, 3)
grand_total = round(h + i + j + k + l + m, 3)

# Percents (original behavior preserved)
h_percent = round(h * 10, 3)
i_percent = round(i * 10, 3)
j_percent = round(j * 10, 3)
k_percent = round(k * 10, 3)
l_percent = round(l * 10, 3)
m_percent = round(m * 10, 3)

total_dal_tukdi_percent = round(h_percent + i_percent, 3)
total_4_percent = round(j_percent + k_percent + l_percent + m_percent, 3)
total_6_percent = round(total_dal_tukdi_percent + total_4_percent, 3)

# NEW grams totals requested
total_dal_tukdi_grams = round(h + i, 3)
total_4_grams = round(j + k + l + m, 3)

# ---------- RESPONSIVE HTML TABLE DISPLAY (keeps rows intact on mobile) ----------
def render_results_table():
    html = f"""
    <table class="result-table">
      <thead>
        <tr><th>Item</th><th>Grams</th><th>Percentage</th></tr>
      </thead>
      <tbody>
        <tr><td>Daal</td><td>{h} g</td><td>{h_percent} %</td></tr>
        <tr><td>Tukdi</td><td>{i} g</td><td>{i_percent} %</td></tr>
        <tr style="font-weight:700;"><td>Total (Dal + Tukdi)</td><td>{total_dal_tukdi_grams} g</td><td>{total_dal_tukdi_percent} %</td></tr>
        <tr><td>Red/Black</td><td>{j} g</td><td>{j_percent} %</td></tr>
        <tr><td>Chhala</td><td>{k} g</td><td>{k_percent} %</td></tr>
        <tr><td>Dankhal</td><td>{l} g</td><td>{l_percent} %</td></tr>
        <tr><td>14 Mesh</td><td>{m} g</td><td>{m_percent} %</td></tr>
        <tr style="font-weight:700;"><td>Total (4)</td><td>{total_4_grams} g</td><td>{total_4_percent} %</td></tr>
        <tr style="font-weight:700;"><td>Grand Total for Sheet</td><td>{grand_total} g</td><td>{total_6_percent} %</td></tr>
      </tbody>
    </table>
    """
    st.markdown(html, unsafe_allow_html=True)

st.subheader("Grand Total")
st.write(f"Grand Total (sum of raw inputs): **{g} g**")
st.subheader("Details — grams and percentage (rows keep aligned on mobile)")
render_results_table()

# ---------- Robust template loader to avoid UnicodeDecodeError ----------
def load_template(path="report_template.txt"):
    candidates = ["utf-8-sig", "utf-8", "utf-16", "latin-1", "cp1252"]
    for enc in candidates:
        try:
            with open(path, "r", encoding=enc) as fh:
                text = fh.read()
            return text, enc
        except FileNotFoundError:
            return None, None
        except Exception as e:
            logger.debug(f"Failed to read {path} with {enc}: {e}")
            continue
    # Fallback binary decode with replacement
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", errors="replace")
        return text, "fallback-utf8-replace"
    except FileNotFoundError:
        return None, None
    except Exception as e:
        logger.error(f"Failed binary fallback reading template: {e}")
        return None, None

template_text, template_encoding = load_template()
if template_text is None:
    st.warning("Template file 'report_template.txt' not found in the repo root. Add it and use placeholders exactly as shown in the example.")
else:
    st.info(f"Loaded template (encoding: {template_encoding})")

# ---------- PDF generation ----------
def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def generate_pdf_bytes(image_file, template_text, data_map):
    pdf = FPDF()
    # First page: uploaded image (landscape)
    if image_file is not None:
        try:
            img = Image.open(image_file)
            img_buffer = io.BytesIO()
            img.convert("RGB").save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            pdf.add_page(orientation='L')
            pdf.image(img_buffer, x=10, y=10, w=270)
        except Exception as ex:
            pdf.add_page(orientation='L')
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Image processing error: {ex}", ln=True, align='C')
    else:
        pdf.add_page(orientation='L')
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "No Image Provided", ln=True, align='C')

    # Second page: filled template (portrait)
    pdf.add_page(orientation='P')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    if template_text:
        filled = template_text
        for key, val in data_map.items():
            filled = filled.replace("{" + key + "}", str(val))
        for paragraph in filled.splitlines():
            pdf.multi_cell(0, 8, paragraph)
    else:
        # fallback report content if template missing
        lines = [
            "Dal Split Report",
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

# ---------- Data map (placeholders) ----------
data_map = {
    "DATE": display_date,                   # DD/MM/YYYY for template
    "VEHICLE": vehicle_number,
    "PARTY": party_name,
    "GAADI": gaadi_type,
    "DAAL": h,
    "TUKDI": i,
    "TOTAL_DTG": total_dal_tukdi_grams,     # your renamed placeholder for grams
    "TOTAL_DTP": total_dal_tukdi_percent,   # your renamed placeholder for percent
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

# ---------- Generate + Download ----------
if st.button("Generate PDF"):
    pdf_bytes = generate_pdf_bytes(image_file, template_text, data_map)
    fname = f"{filename_date}_{slugify(vehicle_number)}_{slugify(party_name)}_{slugify(gaadi_type)}_gaadi.pdf"
    st.success("PDF generated — click to download")
    st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name=fname, mime="application/pdf")
