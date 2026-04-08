import streamlit as st
import pandas as pd
from Exec import run_model

st.set_page_config(
    page_title="Waste Heat Recovery Model",
    layout="wide"
)

st.title("Waste Heat Recovery Model")
st.write("Upload an Excel file to run the WHR model.")

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=["xlsx"]
)

if uploaded_file is not None:
    st.success("File uploaded successfully")

    # Run model
    inputdata = run_model(uploaded_file)

    st.subheader("Input Data Preview")
    st.dataframe(inputdata)

else:
    st.info("Please upload an Excel file to continue.")
