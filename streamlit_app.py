# app.py
import streamlit as st
from fpdf import FPDF
from PIL import Image
import io
import datetime
import unicodedata
import re

st.set_page_config(page_title="Aravally Dal Split", page_icon="favicon_split.ico")
st.title("Aravally Dal Split")

# Hide Streamlit chrome
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Inputs ----------
selected_date = st.date_input("Select Date (DD/MM/YYYY)", value=datetime.date.today())
display_date = selected_date.strftime("%d/%m/%Y")
filename_date = selected_date.strftime("%Y-%m-%d")

vehicle_number = st.text_input("Vehicle Number:")
party_name = st.text_input("Party Name:")
gaadi_type = st.radio("Gaadi Type:", ["Khadi", "Poori"])

st.write("Enter weights (grams) — 3 decimal precision")
a = st.number_input("Daal (input)", min_value=0.000, step=0.001, format="%.3f")
b = st.number_input("Tukdi (input)", min_value=0.000, step=0.001, format="%.3f")
c = st.number_input("Red/Black (input)", min_value=0.000, step=0.001, format="%.3f")
d = st.number_input("Chhala (input)", min_value=0.000, step=0.001, format="%.3f")
e = st.number_input("Dankhal (input)", min_value=0.000, step=0.001, format="%.3f")
f = st.number_input("14 Mesh (input)", min_value=0.000, step=0.001, format="%.3f")

uploaded_file = st.file_uploader("Upload an image (jpg/png) — will be page 1 of PDF", type=["jpg","jpeg","png"])
image_file = uploaded_file

# ---------- Calculations (same logic as you used) ----------
g_sum_inputs = round(a + b + c + d + e + f, 3)
h = round(a * 2, 3)  # daal grams for sheet
i = round(b * 2, 3)  # tukdi
j = round(c * 2, 3)
k = round(d * 2, 3)
l = round(e * 2, 3)
m = round(f * 2, 3)

grand_total_sheet = round(h + i + j + k + l + m, 3)

# percents following original logic
h_perc = round(h * 10, 3)
i_perc = round(i * 10, 3)
j_perc = round(j * 10, 3)
k_perc = round(k * 10, 3)
l_perc = round(l * 10, 3)
m_perc = round(m * 10, 3)

total_dal_tukdi_perc = round(h_perc + i_perc, 3)
total_4_perc = round(j_perc + k_perc + l_perc + m_perc, 3)
total_6_perc = round(total_dal_tukdi_perc + total_4_perc, 3)

# grams totals requested
total_dal_tukdi_grams = round(h + i, 3)
total_4_grams = round(j + k + l + m, 3)

# Small preview on page
st.subheader("Preview (rows aligned for mobile)")
st.markdown(f"**Grand total (inputs):** {g_sum_inputs} g")
st.table({
    "Item": ["Daal","Tukdi","Total (Dal+Tukdi)","Red/Black","Chhala","Dankhal","14 Mesh","Total (4)","Grand Total for Sheet"],
    "Grams": [h, i, total_dal_tukdi_grams, j, k, l, m, total_4_grams, grand_total_sheet],
    "Percent": [h_perc, i_perc, total_dal_tukdi_perc, j_perc, k_perc, l_perc, m_perc, total_4_perc, total_6_perc]
})

# ---------- PDF generation helper ----------
def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii','ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def generate_pdf_bytes(image_file, data):
    """
    Create a PDF with:
     - page 1: uploaded image (landscape)
     - page 2: report (portrait) with a two-column table (grams | percentage),
       styled and boxed to match the screenshot.
    data: dict of values used below.
    """
    pdf = FPDF(format='A4')  # default portrait; we'll set orientation per page
    # --- Page 1: image (landscape) ---
    if image_file is not None:
        try:
            img = Image.open(image_file)
            # Save into buffer as JPEG
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG")
            buf.seek(0)
            pdf.add_page(orientation='L')  # landscape
            # Fit image with margins
            pdf.image(buf, x=10, y=10, w=pdf.w - 20)
        except Exception as e:
            pdf.add_page(orientation='L')
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Image error: {e}", ln=True, align='C')
    else:
        pdf.add_page(orientation='L')
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, "No Image Provided", ln=True, align='C')

    # --- Page 2: report table (portrait) ---
    pdf.add_page(orientation='P')
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header (company name centered with border box)
    pdf.set_font("Arial", "B", 14)
    # calculate positions
    left_margin = 10
    right_margin = pdf.w - 10
    # Draw a top centered box around the heading region
    # We'll draw rectangles and then place text centered within
    # top header box
    box_x = 20
    box_w = pdf.w - 40
    box_y = 10
    box_h = 14
    pdf.rect(box_x, box_y, box_w, box_h)  # top border box
    pdf.set_xy(0, box_y)
    pdf.cell(0, box_h, txt="", ln=True)

    # Company title centered inside box
    pdf.set_xy(box_x, box_y + 1)
    pdf.cell(box_w, 6, txt="ARAVALLY PROCESSED AGROTECH PVT. LTD.", border=0, ln=1, align='C')

    # Subtitle below
    pdf.set_xy(box_x, box_y + 7)
    pdf.set_font("Arial", size=12)
    pdf.cell(box_w, 6, txt="DAL SPLIT REPORT", border=0, ln=1, align='C')

    pdf.ln(6)

    # Party / Date / Vehicle / Gaadi in two-column small table
    pdf.set_font("Arial", size=10)
    col_w = (pdf.w - 20) / 2
    # Draw small table border cells manually
    start_x = 10
    y_before = pdf.get_y()
    # Row height
    row_h = 8
    # Row 1 (Party / Date)
    pdf.rect(start_x, y_before, col_w, row_h)
    pdf.rect(start_x + col_w, y_before, col_w, row_h)
    pdf.set_xy(start_x + 2, y_before + 2)
    pdf.cell(col_w - 4, 4, txt=f"PARTY NAME : {data['PARTY']}", ln=0)
    pdf.set_xy(start_x + col_w + 2, y_before + 2)
    pdf.cell(col_w - 4, 4, txt=f"DATE : {data['DATE']}", ln=0)
    pdf.ln(row_h + 2)

    # Row 2 (Vehicle / Gaadi)
    y2 = pdf.get_y()
    pdf.rect(start_x, y2, col_w, row_h)
    pdf.rect(start_x + col_w, y2, col_w, row_h)
    pdf.set_xy(start_x + 2, y2 + 2)
    pdf.cell(col_w - 4, 4, txt=f"VEHICLE NUMBER : {data['VEHICLE']}", ln=0)
    pdf.set_xy(start_x + col_w + 2, y2 + 2)
    pdf.cell(col_w - 4, 4, txt=f"GAADI TYPE : {data['GAADI']}", ln=0)
    pdf.ln(row_h + 6)

    # --- Main two-column table header ---
    pdf.set_font("Arial", "B", 10)
    # Define widths for left and right big columns
    page_inner_w = pdf.w - 20
    left_col_w = page_inner_w * 0.5
    right_col_w = page_inner_w * 0.5
    x0 = 10
    y0 = pdf.get_y()

    # draw top border for main table area
    # We'll draw the entire table as a rectangle; then draw inner horizontal lines and vertical midline.
    table_x = x0
    table_y = y0
    # approximate height: we'll compute lines and increase y as we add rows
    # We'll draw rows individually and track current y.
    current_y = table_y

    # Title row spanning two columns
    row_h = 8
    pdf.set_xy(table_x, current_y)
    pdf.set_font("Arial", "B", 10)
    # Outer rect for the whole title row (two columns)
    pdf.rect(table_x, current_y, left_col_w + right_col_w, row_h)
    # Left cell title
    pdf.set_xy(table_x + 2, current_y + 2)
    pdf.cell(left_col_w - 4, 4, txt="INDIVIDUAL PARTICLE DATA (in gram)", ln=0)
    # Right cell title
    pdf.set_xy(table_x + left_col_w + 2, current_y + 2)
    pdf.cell(right_col_w - 4, 4, txt="INDIVIDUAL PARTICLE DATA (in percentage)", ln=0)
    current_y += row_h

    # Helper to draw a 2-column row with left text and right text, both inside their cells with borders
    def row_two_columns(left_text, right_text, bold=False):
        nonlocal current_y
        h = 8
        # draw left cell
        pdf.rect(table_x, current_y, left_col_w, h)
        # draw right cell
        pdf.rect(table_x + left_col_w, current_y, right_col_w, h)
        # write texts
        if bold:
            pdf.set_font("Arial", "B", 10)
        else:
            pdf.set_font("Arial", size=10)
        pdf.set_xy(table_x + 2, current_y + 2)
        pdf.multi_cell(left_col_w - 4, 4, left_text)
        # right cell
        # align right text left-aligned inside cell
        pdf.set_xy(table_x + left_col_w + 2, current_y + 2)
        pdf.multi_cell(right_col_w - 4, 4, right_text)
        current_y += h

    # Now add the rows in the requested order:
    row_two_columns(f"DAAL : {data['DAAL']} gm", f"DAAL : {data['DAAL_PERC']} %")
    row_two_columns(f"TUKDI : {data['TUKDI']} gm", f"TUKDI : {data['TUKDI_PERC']} %")
    # TOTAL (DAL + TUKDI) right after Tukdi
    row_two_columns(f"TOTAL ( DAAL + TUKDI ) : {data['TOTAL_DTG']} gm", f"TOTAL ( DAAL + TUKDI ) : {data['TOTAL_DTP']} %", bold=True)
    # spacer line (visual separation) - we can just continue rows
    row_two_columns(f"RED / BLACK : {data['REDBLACK']} gm", f"RED / BLACK : {data['REDBLACK_PERC']} %")
    row_two_columns(f"CHHALA : {data['CHHALA']} gm", f"CHHALA : {data['CHHALA_PERC']} %")
    row_two_columns(f"DANKHAL : {data['DANKHAL']} gm", f"DANKHAL : {data['DANKHAL_PERC']} %")
    row_two_columns(f"14 MESH : {data['MES14']} gm", f"14 MESH : {data['MES14_PERC']} %")
    # TOTAL (4) right after 14 Mesh
    row_two_columns(f"TOTAL ( R/B + C + D + 14# ) : {data['TOTAL_4_GRAMS']} gm", f"TOTAL ( R/B + C + D + 14# ) : {data['TOTAL_4']} %", bold=True)
    # Grand total row
    row_two_columns(f"GRAND TOTAL : {data['GRAND_TOTAL']} gm", f"GRAND TOTAL : {data['TOTAL_6']} %", bold=True)

    # Optionally draw an outer border around the whole table area (from initial table_y to current_y)
    pdf.rect(table_x, table_y, left_col_w + right_col_w, current_y - table_y)

    # Return bytes
    return pdf.output(dest='S').encode('latin-1')

# Data dictionary
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

# ---------- Generate and download ----------
if st.button("Generate PDF"):
    pdf_bytes = generate_pdf_bytes(image_file, data)
    name = f"{filename_date}_{slugify(vehicle_number)}_{slugify(party_name)}_{slugify(gaadi_type)}_gaadi.pdf"
    st.success("PDF generated — click to download")
    st.download_button("📥 Download PDF", data=pdf_bytes, file_name=name, mime="application/pdf")
