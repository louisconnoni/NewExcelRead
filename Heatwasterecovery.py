
import numpy as np
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

    #st.subheader("Input Data Preview")
    #st.dataframe(df.head())

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

        # STORE RESULTS
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
                ["Standard Bar Chart", "Stacked Sustainability Chart"],
                help = "Switch between standard or stacked bar charts"
            )

            # =========================
            # STANDARD BAR CHART
            # =========================
            if chart_type == "Standard Bar Chart":

                
                metrics = st.multiselect(
                    "Select metrics to display",
                    [col for col in results_df.columns if col != "Scenario"],
                    default=["Carbon Score", "Economic Score", "Water Score", "Social Score"]
                )
                
                if metrics:
                    fig, ax = plt.subplots()
                
                    scenarios = results_df["Scenario"]
                    x = np.arange(len(scenarios))  # positions for scenarios
                
                    width = 0.8 / len(metrics)  # auto-fit bars nicely
                
                    for i, metric in enumerate(metrics):
                        ax.bar(
                            x + i * width,
                            results_df[metric],
                            width=width,
                            label=metric
                        )
                
                    # Center x-axis labels
                    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
                    ax.set_xticklabels(scenarios, rotation=45)
                
                    ax.set_ylabel("Value")
                    ax.set_xlabel("Scenario")
                    ax.legend()
                
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
                    carbonw =carbon*results_df["Carbon Weight"]
                    econw = econ*results_df["Economic Weight"]
                    waterw = water*results_df["Water Weight"]
                    socialw = social*results_df["Social Weight"]
                    

                    # Stacked bars
                    ax.bar(scenarios, carbonw, label="Carbon")
                    ax.bar(scenarios, econw, bottom=carbonw, label="Economic")
                    ax.bar(scenarios, waterw, bottom=carbonw + econw, label="Water")
                    ax.bar(scenarios, socialw, bottom=carbonw + econw + waterw, label="Social", yerr = .1)

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
