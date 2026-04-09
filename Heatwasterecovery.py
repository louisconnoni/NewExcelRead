

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



        chart_type = st.radio(
            "Select Visualization Type",
            ["Standard Bar Chart", "Stacked Sustainability Chart"]
            )
        # =========================
        # Display Results
        # =========================
        st.subheader("Results Table")
        st.dataframe(results_df)

        # =========================
        # Plot Results
        # =========================
        if not results_df.empty:

            st.subheader("Comparison Plot")

            numeric_cols = results_df.select_dtypes(include="number").columns

            selected_metrics = st.multiselect(
                "Select metrics to plot",
                numeric_cols,
                default=list(numeric_cols[:2])
            )

            if selected_metrics:
                fig, ax = plt.subplots()

                for metric in selected_metrics:
                    ax.plot(
                        results_df["Scenario"],
                        results_df[metric],
                        marker='o',
                        label=metric
                    )

                ax.set_ylabel("Value")
                ax.set_xlabel("Scenario")
                ax.legend()
                plt.xticks(rotation=45)

                st.pyplot(fig)

        
