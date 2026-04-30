

# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from Exec import run_model_for_column          # CCS
from Desalination import run_desalination_model # Desalination
from DistrictHeating import run_districtheating_model

st.set_page_config(layout="wide")
st.title("Heat Waste Recovery Tool")

# =========================
# Upload File
# =========================
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    excel_file = pd.ExcelFile(uploaded_file)

    ##st.subheader("Detected Sheets")
    ##st.write(excel_file.sheet_names)

    # =========================
    # Run Model Button
    # =========================
    if st.button("Run Model"):

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
                
            elif sheet_name.lower() == "district heating":
                model_function = run_districtheating_model
                model_label = "District Heating"

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

                

                fig, ax = plt.subplots()
                
                scenarios = results_df["Scenario"]
                x = np.arange(len(scenarios))
                
                width = 0.2
                
                # Data
                carbon = results_df["Carbon Score"]
                econ   = results_df["Economic Score"]
                water  = results_df["Water Score"]
                social = results_df["Social Score"]
                
                # Uncertainties
                carbon_err = results_df["CarbonError"]
                econ_err   = results_df["EconomicError"]
                water_err  = results_df["WaterError"]
                social_err = results_df["SocialError"]
                
                # Bars + error bars
                ax.bar(x - 1.5*width, carbon, width, yerr=carbon_err, capsize=4, label="Carbon")
                ax.bar(x - 0.5*width, econ,   width, yerr=econ_err,   capsize=4, label="Economic")
                ax.bar(x + 0.5*width, water,  width, yerr=water_err,  capsize=4, label="Water")
                ax.bar(x + 1.5*width, social, width, yerr=social_err, capsize=4, label="Social")
                
                # Axis formatting
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45)
                
                ax.set_ylabel("Score")
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

                    cweight2 = cweight
                    eweight2 = eweight
                    wweight2 = wweight
                    sweight2 = sweight

                    
                    

                    st.sidebar.subheader("Adjust Sustainability Weights")
                    

                    wweight = st.sidebar.slider("Water Weight", 0.0, 1.0, .25, 0.01)
                    sweight = st.sidebar.slider("Social Weight", 0.0, 1.0, .25, 0.01)
                    eweight = st.sidebar.slider("Economic Weight", 0.0, 1.0, .25, 0.01)
                    cweight = st.sidebar.slider("Carbon Weight", 0.0, 1.0, .25, 0.01)

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

            #Pie Chart

            selected_scenario = st.selectbox(
                "Select Scenario for Cost Breakdown",
                results_df["Scenario"]
            )
            
            row = results_df[results_df["Scenario"] == selected_scenario].iloc[0]
            
            cost_labels = ["Labor", "Electricity", "Operations", "Capital"]
            cost_values = [
                row["Labor Cost"],
                row["Electricity Cost"],
                row["Operations Cost"],
                row["Capital Cost"]
            ]
            
            fig, ax = plt.subplots()
            
            ax.pie(
                cost_values,
                labels=cost_labels,
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops=dict(width=0.4)
            )
            
            total_cost = sum(cost_values)
            
            ax.text(0, 0, f"${total_cost:,.0f}", ha='center', va='center')
            
            ax.set_title(f"Cost Breakdown: {selected_scenario}")
            
            st.pyplot(fig)

    else:
        st.info("Click 'Run Model for All Sheets' to generate results.")
