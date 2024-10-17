import streamlit as st
from fpdf import FPDF
import base64
from PIL import Image

# Set the page configuration (title and favicon)
st.set_page_config(
    page_title="Aravally Dal Split",  # Page title
    page_icon="favicon.ico"  # Path to your favicon file
)

st.header("Aravally Dal Split Calculator")

# Hide unnecessary Streamlit UI components
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Load the image (replace 'image.jpg' with your file path)
img = Image.open('Banner.png')
st.image(img, caption='', width=100)

# Collecting additional details
date = st.text_input("Enter Date:")
vehicle_number = st.text_input("Enter Vehicle Number:")
party_name = st.text_input("Enter Party Name:")

# Radio button for Gaadi Type
gaadi_type = st.radio("Select Gaadi Type:", options=["Khadi", "Poori"])

# Inputs for weights (with three decimal precision)
a = st.number_input("Enter Daal:", min_value=0.000, step=0.001, format="%.3f")
b = st.number_input("Enter Tukdi:", min_value=0.000, step=0.001, format="%.3f")
c = st.number_input("Enter Red/Black:", min_value=0.000, step=0.001, format="%.3f")
d = st.number_input("Enter Chhala:", min_value=0.000, step=0.001, format="%.3f")
e = st.number_input("Enter Dankhal:", min_value=0.000, step=0.001, format="%.3f")
f = st.number_input("Enter 14 Mesh:", min_value=0.000, step=0.001, format="%.3f")

# Calculations (rounded to 3 decimal points)
g = round(a + b + c + d + e + f, 3)
h = round(a * 2, 3)
i = round(b * 2, 3)
j = round(c * 2, 3)
k = round(d * 2, 3)
l = round(e * 2, 3)
m = round(f * 2, 3)
grand_total = round(h + i + j + k + l + m, 3)

# Percentage calculations (rounded to 3 decimal points)
h_percent = round(h * 10, 3)
i_percent = round(i * 10, 3)
total_dal_tukdi_percent = round(h_percent + i_percent, 3)
j_percent = round(j * 10, 3)
k_percent = round(k * 10, 3)
l_percent = round(l * 10, 3)
m_percent = round(m * 10, 3)
total_4_percent = round(j_percent + k_percent + l_percent + m_percent, 3)
total_6_percent = round(total_dal_tukdi_percent + total_4_percent, 3)

# Display results
st.subheader("Grand Total")
st.write(f"Grand Total: {g}")

st.subheader("Details for Sheet")
st.write(f"Daal: {h}")
st.write(f"Tukdi: {i}")
st.write(f"Red/Black: {j}")
st.write(f"Chhala: {k}")
st.write(f"Dankhal: {l}")
st.write(f"14 Mesh: {m}")
st.write(f"Grand Total for Sheet: {grand_total}")

st.subheader("Details in Percentage")
st.write(f"Daal: {h_percent}%")
st.write(f"Tukdi: {i_percent}%")
st.write(f"Total (Dal + Tukdi): {total_dal_tukdi_percent}%")
st.write(f"Red/Black: {j_percent}%")
st.write(f"Chhala: {k_percent}%")
st.write(f"Dankhal: {l_percent}%")
st.write(f"14 Mesh: {m_percent}%")
st.write(f"Total (4): {total_4_percent}%")
st.write(f"Total (6): {total_6_percent}%")

# Generate PDF content with rounded values
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()

    # Add the image to the PDF (adjust size and position)
    pdf.image('Banner.png', x=160, y=10, w=40)  # Adjust x, y, and width as needed
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Dal Split Report", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Date: {date}", ln=True)
    pdf.cell(200, 10, txt=f"Vehicle Number: {vehicle_number}", ln=True)
    pdf.cell(200, 10, txt=f"Party Name: {party_name}", ln=True)
    pdf.cell(200, 10, txt=f"Gaadi Type: {gaadi_type}", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, txt="Details (in grams):", ln=True)
    pdf.cell(200, 10, txt=f"Daal: {h}gm", ln=True)
    pdf.cell(200, 10, txt=f"Tukdi: {i}gm", ln=True)
    pdf.cell(200, 10, txt=f"Red/Black: {j}gm", ln=True)
    pdf.cell(200, 10, txt=f"Chhala: {k}gm", ln=True)
    pdf.cell(200, 10, txt=f"Dankhal: {l}gm", ln=True)
    pdf.cell(200, 10, txt=f"14 Mesh: {m}gm", ln=True)
    pdf.cell(200, 10, txt=f"Grand Total for Sheet: {grand_total}gm", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, txt="Details (in percentage):", ln=True)
    pdf.cell(200, 10, txt=f"Daal: {h_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Tukdi: {i_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Total (Dal + Tukdi): {total_dal_tukdi_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Red/Black: {j_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Chhala: {k_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Dankhal: {l_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"14 Mesh: {m_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Total (4): {total_4_percent}%", ln=True)
    pdf.cell(200, 10, txt=f"Total (6): {total_6_percent}%", ln=True)

    pdf_file = "dal_split_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Function to create a download link
def pdf_download_link(pdf_file):
    with open(pdf_file, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="dal_split_report.pdf">📥 Download PDF</a>'
    return href

# Display the PDF download button
if st.button("Generate PDF"):
    pdf_file = generate_pdf()
    st.markdown(pdf_download_link(pdf_file), unsafe_allow_html=True)
