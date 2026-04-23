

# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from Exec import run_model_for_column          # CCS
from Desalination import run_desalination_model # Desalination

st.set_page_config(layout="wide")
st.title("Multi-System Sustainability Model")

# =========================
# Upload File
# =========================
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    excel_file = pd.ExcelFile(uploaded_file)

    st.subheader("Detected Sheets")
    st.write(excel_file.sheet_names)

    # =========================
    # Run Model Button
    # =========================
    if st.button("Run Model for All Sheets"):

        results_list = []

        # Loop through sheets
        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            st.write(f"Processing sheet: {sheet_name}")

            # -------------------------
            # SELECT MODEL BASED ON NAME
            # -------------------------
            if sheet_name.lower() == "ccs":
                model_function = run_model_for_column
                model_label = "CCS"

            elif sheet_name.lower() == "desalination":
                model_function = run_desalination_model
                model_label = "Desalination"

            else:
                st.warning(f"Skipping unknown sheet: {sheet_name}")
                continue

            # -------------------------
            # LOOP THROUGH SCENARIOS
            # -------------------------
            for col in df.columns[1:]:

                op = df[col]

                try:
                    result = model_function(op)

                    result["Scenario"] = f"{model_label} - {col}"
                    result["System"] = model_label

                    results_list.append(result)

                except Exception as e:
                    st.warning(f"Error in {sheet_name} / {col}: {e}")

        results_df = pd.DataFrame(results_list)

        # Save results
        st.session_state["results_df"] = results_df

    # =========================
    # DISPLAY RESULTS
    # =========================
    if "results_df" in st.session_state:

        results_df = st.session_state["results_df"]

        if results_df.empty:
            st.warning("No results to display.")
        else:
            st.subheader("Results Table")
            st.dataframe(results_df)

            # =========================
            # CHART TYPE TOGGLE
            # =========================
            chart_type = st.radio(
                "Select Visualization Type",
                ["Grouped Bar Chart", "Stacked Sustainability Chart"],
                help = "Weighting"
                
            )

            # =========================
            # GROUPED BAR CHART
            # =========================
            if chart_type == "Grouped Bar Chart":

                metrics = st.multiselect(
                    "Select metrics",
                    [col for col in results_df.columns if col not in ["Scenario", "System"]],
                    default=["Carbon Score", "Economic Score", "Water Score", "Social Score"]
                )

                if metrics:
                    fig, ax = plt.subplots()

                    scenarios = results_df["Scenario"]
                    x = np.arange(len(scenarios))
                    width = 0.8 / len(metrics)

                    for i, metric in enumerate(metrics):
                        ax.bar(
                            x + i * width,
                            results_df[metric],
                            width=width,
                            label=metric
                        )

                    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
                    ax.set_xticklabels(scenarios, rotation=45)

                    ax.set_ylabel("Value")
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

                if not all(col in results_df.columns for col in required_cols):
                    st.error("Missing required columns for stacked chart.")
                else:
                    fig, ax = plt.subplots()

                    scenarios = results_df["Scenario"]
                    carbon = results_df["Carbon Score"]
                    econ = results_df["Economic Score"]
                    water = results_df["Water Score"]
                    social = results_df["Social Score"]
                    ploterror = results_df["Error"]
                    cweight = results_df["Carbon Weight"]
                    eweight = results_df["Economic Weight"]
                    wweight = results_df["Water Weight"]
                    sweight = results_df["Social Weight"]
                    modelerror = results_df["Error"]

                    
                    carbonw =carbon*cweight
                    econw = econ*eweight
                    waterw = water*wweight
                    socialw = social*sweight
                    

                    # Stacked bars
                    ax.bar(scenarios, carbonw, label="Carbon")
                    ax.bar(scenarios, econw, bottom=carbonw, label="Economic")
                    ax.bar(scenarios, waterw, bottom=carbonw + econw, label="Water")
                    ax.bar(scenarios, socialw, bottom=carbonw + econw + waterw, label="Social", yerr = modelerror)

                    # Total for error bar
                    totals = carbon + econ + water + social


                    

                    ax.set_ylabel("Total Score")
                    ax.legend()
                    plt.xticks(rotation=45)

                    st.pyplot(fig)

    else:
        st.info("Click 'Run Model for All Sheets' to generate results.")
