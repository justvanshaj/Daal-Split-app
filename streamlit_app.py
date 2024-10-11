import streamlit as st
from PIL import Image

st.header("Aravally Sieve Shaker Calculator")
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

# Input for sample
x = st.number_input("Enter Sample:", min_value=1, step=1)

# Inputs for each weight
y1 = st.number_input("Enter 60#:", min_value=0.000, step=0.001,format="%.3f")
y2 = st.number_input("Enter 100#:", min_value=0.000, step=0.001,format="%.3f")
y3 = st.number_input("Enter 150#:", min_value=0.000, step=0.001,format="%.3f")
y4 = st.number_input("Enter 200#:", min_value=0.000, step=0.001,format="%.3f")
y5 = st.number_input("Enter 240#:", min_value=0.000, step=0.001,format="%.3f")
y6 = st.number_input("Enter 300#:", min_value=0.000, step=0.001,format="%.3f")
y7 = st.number_input("Enter 350#:", min_value=0.000, step=0.001,format="%.3f")
y8 = st.number_input("Enter Base:", min_value=0.000, step=0.001,format="%.3f")

# Perform the calculations
if x > 0:
    z1 = (y1 * 100) / x
    z2 = (y2 * 100) / x + z1
    z3 = (y3 * 100) / x + z2
    z4 = (y4 * 100) / x + z3
    z5 = (y5 * 100) / x + z4
    z6 = (y6 * 100) / x + z5
    z7 = (y7 * 100) / x + z6
    z8 = (y8 * 100) / x + z7

    # Display the results
    st.write(f"60#  : {z1:.4f}%")
    st.write(f"100# : {z2:.4f}%")
    st.write(f"150# : {z3:.4f}%")
    st.write(f"200# : {z4:.4f}%")
    st.write(f"240# : {z5:.4f}%")
    st.write(f"300# : {z6:.4f}%")
    st.write(f"350# : {z7:.4f}%")
    st.write(f"Base : {z8:.4f}%")
else:
    st.write("Please enter a sample greater than 0.")
