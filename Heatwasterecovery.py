import streamlit as st
import pandas as pd
from Exec import run_model

st.set_page_config(page_title="WHR Model", layout="wide")
st.title("Waste Heat Recovery Model")

uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Input Data")
    st.dataframe(df)

    # Dictionary to store results for each column
    all_results = {}

    for column_name in df.columns:
        # Extract ONE column as DataFrame
        column_df = df[[column_name]]

        # Run model
        results = run_model(column_df)

        all_results[column_name] = results

        st.subheader("Model Results")
        
        cols = st.columns(len(all_results))
        
        for col, (case_name, results) in zip(cols, all_results.items()):
            with col:
                st.markdown(f"### {case_name}")
        
                st.metric("Total Profit", f"${results['Total Profit']:,.0f}")
                st.metric("Total Water Saved", f"{results['Total Water Saved']:,.2f}")
                st.metric("Total Carbon Saved", f"{results['Total Carbon Saved']:,.2f}")
        
                st.metric("Total Score", f"{results['Total Score']:.2f}")
                st.metric("Water Score", f"{results['Water Score']:.2f}")
                st.metric("Economic Score", f"{results['Economic Score']:.2f}")
                st.metric("Social Score", f"{results['Social Score']:.2f}")
                st.metric("Carbon Score", f"{results['Carbon Score']:.2f}")
        
                st.metric("ERE Improvement", f"{results['ERE Improvement']:.2f}%")
                st.metric("ERF", f"{results['ERF']:.2f}")
