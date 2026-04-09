from CCSv8 import run_ccs_model
import streamlit as st
import pandas as pd

st.title("CCS WHR Model")

uploaded_file = st.file_uploader("Upload Excel input file", type=["xlsx", "xls"])

if uploaded_file:
    inputdata = pd.read_excel(uploaded_file)
    st.dataframe(inputdata)

    if st.button("Run Model"):
        results = run_ccs_model(inputdata)
        st.success("Model completed")
