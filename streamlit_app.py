import streamlit as st
from PIL import Image
# Set the page configuration (title and favicon)
st.set_page_config(
    page_title="Aravally Split Calculator",  # Page title
    page_icon="favicon.ico"  # Path to your favicon file
)
st.header("Aravally Split Calculator")
hide_st_style="""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(hide_st_style, unsafe_allow_html=True)
# Load the image (replace 'image.jpg' with your file path)
img = Image.open('Banner.jpg')

# Display the image
st.image(img, caption='', use_column_width=True)

st.header("Details Calculation in terms of 5gm")

# Inputs
a = st.number_input("Enter Daal:", min_value=0.000, step=0.001,format="%.3f")
b = st.number_input("Enter Tukdi:", min_value=0.000, step=0.001,format="%.3f")
c = st.number_input("Enter Red/Black:", min_value=0.000, step=0.001,format="%.3f")
d = st.number_input("Enter Chhala:", min_value=0.000, step=0.001,format="%.3f")
e = st.number_input("Enter Dankhal:", min_value=0.000, step=0.001,format="%.3f")
f = st.number_input("Enter 14 Mesh:", min_value=0.000, step=0.001,format="%.3f")

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
