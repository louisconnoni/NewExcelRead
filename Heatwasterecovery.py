

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
    # Run Model Button
    # =========================
    if st.button("Run Model for All Scenarios"):

        results_list = []

        for col in df.columns[1:]:  # skip first column (labels)
            op = df[col]

            try:
                result = run_model_for_column(op)
                result["Scenario"] = col
                results_list.append(result)

            except Exception as e:
                st.warning(f"Error in column {col}: {e}")

        results_df = pd.DataFrame(results_list)

        # 🔥 STORE RESULTS
        st.session_state["results_df"] = results_df

    # =========================
    # DISPLAY RESULTS (PERSISTENT)
    # =========================
    if "results_df" in st.session_state:

        results_df = st.session_state["results_df"]

        if results_df.empty:
            st.warning("No results to display.")
        else:
            st.subheader("Results Table")
            st.dataframe(results_df)

            # =========================
            # CHART TOGGLE
            # =========================
            chart_type = st.radio(
                "Select Visualization Type",
                ["Standard Bar Chart", "Stacked Sustainability Chart"]
            )

            # =========================
            # STANDARD BAR CHART
            # =========================
            if chart_type == "Standard Bar Chart":

                metrics = st.multiselect(
                    "Select metrics to display",
                    [col for col in results_df.columns if col != "Scenario"],
                    default=["Total Score"] if "Total Score" in results_df.columns else None
                )

                if metrics:
                    fig, ax = plt.subplots()

                    for metric in metrics:
                        ax.bar(results_df["Scenario"], results_df[metric], label=metric)

                    ax.set_ylabel("Value")
                    ax.set_xlabel("Scenario")
                    ax.legend()
                    plt.xticks(rotation=45)

                    st.pyplot(fig)

            # =========================
            # STACKED BAR CHART
            # =========================
            elif chart_type == "Stacked Sustainability Chart":

                required_cols = [
                    "Carbon Score",
                    "Economic Score",
                    "Water Score",
                    "Social Score"
                ]

                # Check required columns exist
                if not all(col in results_df.columns for col in required_cols):
                    st.error("Missing required score columns for stacked plot.")
                else:
                    fig, ax = plt.subplots()

                    scenarios = results_df["Scenario"]

                    carbon = results_df["Carbon Score"]
                    econ = results_df["Economic Score"]
                    water = results_df["Water Score"]
                    social = results_df["Social Score"]
                    ploterror = results_df["Error"]
                    

                    # Stacked bars
                    ax.bar(scenarios, carbon, label="Carbon")
                    ax.bar(scenarios, econ, bottom=carbon, label="Economic")
                    ax.bar(scenarios, water, bottom=carbon + econ, label="Water")
                    ax.bar(scenarios, social, bottom=carbon + econ + water, label="Social", yerr = .1)

                    # Total for error bar
                    totals = carbon + econ + water + social

                    # Error bars (if available)
                    

                    ax.set_ylabel("Total Score")
                    ax.set_xlabel("Scenario")
                    ax.legend()
                    plt.xticks(rotation=45)

                    st.pyplot(fig)

    else:
        st.info("Click 'Run Model for All Scenarios' to generate results.")
