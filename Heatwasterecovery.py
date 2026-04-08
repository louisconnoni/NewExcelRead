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

    results = run_model(uploaded_file)

    st.subheader("Waste Heat Recovery Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Profit", f"${results['Total Profit']:,.0f}")
        st.metric("Total Water Saved", f"{results['Total Water Saved']:,.2f}")
        st.metric("Total Carbon Saved", f"{results['Total Carbon Saved']:,.2f}")
    
    with col2:
        st.metric("Total Score", f"{results['Total Score']:.2f}")
        st.metric("Water Score", f"{results['Water Score']:.2f}")
        st.metric("Economic Score", f"{results['Economic Score']:.2f}")
    
    with col3:
        st.metric("Social Score", f"{results['Social Score']:.2f}")
        st.metric("Carbon Score", f"{results['Carbon Score']:.2f}")
        st.metric("ERE Improvement", f"{results['ERE Improvement']:.2f}%")
        st.metric("ERF", f"{results['ERF']:.2f}")

else:
    st.info("Please upload an Excel file to continue.")
