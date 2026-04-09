

import streamlit as st
import pandas as pd
from Exec import run_model_for_column
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("CCS Waste Heat Recovery Model")

# =========================
# Upload File
# =========================
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Input Data Preview")
    st.dataframe(df.head())

    # =========================
    # Run Model
    # =========================
    if st.button("Run Model"):

        results_list = []

        # Loop through columns (skip first column if it's labels)
        for col in df.columns[1:]:
            op = df[col]

            try:
                result = run_model_for_column(op)
                result["Scenario"] = col
                results_list.append(result)

            except Exception as e:
                st.warning(f"Error in column {col}: {e}")

        # Convert to DataFrame
        results_df = pd.DataFrame(results_list)



        
        # =========================
        # Display Results
        # =========================
        st.subheader("Results Table")
        st.dataframe(results_df)

        chart_type = st.radio(
            "Select Visualization Type",
            ["Standard Bar Chart", "Stacked Sustainability Chart"]
            )

        # =========================
        # Plot Results
        # =========================
        if chart_type == "Standard Bar Chart":
            fig, ax = plt.subplots()
        
            metrics = st.multiselect(
                "Select metrics",
                ["Total Score", "Carbon Score", "Economic Score", "Water Score", "Social Score"],
                default=["Total Score"]
            )
        
            for metric in metrics:
                ax.bar(results_df["Scenario"], results_df[metric], label=metric)
        
            ax.set_ylabel("Value")
            ax.set_xlabel("Scenario")
            ax.legend()
            plt.xticks(rotation=45)
        
            st.pyplot(fig)
        if chart_type == "Stacked Sustainability Chart":

            fig, ax = plt.subplots()
        
            scenarios = results_df["Scenario"]
        
            carbon = results_df["Carbon Score"]
            econ = results_df["Economic Score"]
            water = results_df["Water Score"]
            social = results_df["Social Score"]
        
            # Stack bars
            ax.bar(scenarios, carbon, label="Carbon")
            ax.bar(scenarios, econ, bottom=carbon, label="Economic")
            ax.bar(scenarios, water, bottom=carbon+econ, label="Water")
            ax.bar(scenarios, social, bottom=carbon+econ+water, label="Social")
        
            # Total height for error bar placement
            totals = carbon + econ + water + social
        
            # Error bars
            if "errors" in results_df.columns:
                ax.errorbar(
                    scenarios,
                    totals,
                    yerr=results_df["errors"],
                    fmt='none',
                    ecolor='black',
                    capsize=5
                )
        
            ax.set_ylabel("Total Score")
            ax.set_xlabel("Scenario")
            ax.legend()
            plt.xticks(rotation=45)
        
            st.pyplot(fig)
        
