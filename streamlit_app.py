import streamlit as st
from fpdf import FPDF
import base64

# Set the page configuration
st.set_page_config(page_title="Details Calculation", page_icon="📄")

st.header("Details Calculation in terms of 5gm")

# Collecting additional details
date = st.text_input("Enter Date:")
vehicle_number = st.text_input("Enter Vehicle Number:")
party_name = st.text_input("Enter Party Name:")

# Radio button for Gaadi Type
gaadi_type = st.radio("Select Gaadi Type:", options=["Khadi", "Poori"])

# Inputs for weights
a = st.number_input("Enter Daal:", min_value=0.0, step=0.1)
b = st.number_input("Enter Tukdi:", min_value=0.0, step=0.1)
c = st.number_input("Enter Red/Black:", min_value=0.0, step=0.1)
d = st.number_input("Enter Chhala:", min_value=0.0, step=0.1)
e = st.number_input("Enter Dankhal:", min_value=0.0, step=0.1)
f = st.number_input("Enter 14 Mesh:", min_value=0.0, step=0.1)

# Calculations
g = a + b + c + d + e + f
h = a * 2
i = b * 2
j = c * 2
k = d * 2
l = e * 2
m = f * 2
grand_total = h + i + j + k + l + m

# Percentage calculations
h_percent = h * 10
i_percent = i * 10
total_dal_tukdi_percent = h_percent + i_percent
j_percent = j * 10
k_percent = k * 10
l_percent = l * 10
m_percent = m * 10
total_4_percent = j_percent + k_percent + l_percent + m_percent
total_6_percent = total_dal_tukdi_percent + total_4_percent

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

# Generate PDF content
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Dal Split Report", ln=True, align='C')
    pdf.ln(10)  # Add a line space

    pdf.cell(200, 10, txt=f"Date: {date}", ln=True)
    pdf.cell(200, 10, txt=f"Vehicle Number: {vehicle_number}", ln=True)
    pdf.cell(200, 10, txt=f"Party Name: {party_name}", ln=True)
    pdf.cell(200, 10, txt=f"Gaadi Type: {gaadi_type}", ln=True)
    pdf.ln(10)  # Add a line space

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

    # Save the PDF to a temporary file
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
