



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from Exec import run_model_for_column          # CCS
from Desalination import run_desalination_model # Desalination
from DistrictHeating import run_districtheating_model

st.set_page_config(layout="wide")
st.title("Heat Waste Recovery Tool")


# Uploading Excel File

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    excel_file = pd.ExcelFile(uploaded_file)

    ##st.subheader("Detected Sheets")
    ##st.write(excel_file.sheet_names)

   
   
    if st.button("Run Model"):

        results_list = []

        # Loop through sheets
        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            st.write(f"Processing sheet: {sheet_name}")

            
            if sheet_name.lower() == "ccs":
                model_function = run_model_for_column
                model_label = ""

            elif sheet_name.lower() == "desalination":
                model_function = run_desalination_model
                model_label = ""
                
            elif sheet_name.lower() == "district heating":
                model_function = run_districtheating_model
                model_label = ""

            else:
                st.warning(f"Skipping unknown sheet: {sheet_name}")
                continue

            # Scenario Loop
            for idx, col in enumerate(df.columns[1:]):

                op = df[col]

                try:
                    result = model_function(op, idx)

                    result["Scenario"] = f"{model_label}  {col}"
                    result["System"] = model_label

                    results_list.append(result)

                except Exception as e:
                    st.warning(f"Error in {sheet_name} / {col}: {e}")

        results_df = pd.DataFrame(results_list)

        # Saving results
        st.session_state["results_df"] = results_df

    # Graphs and Results
    if "results_df" in st.session_state:

        results_df = st.session_state["results_df"]

        if results_df.empty:
            st.warning("No results to display.")
        else:
            

            st.subheader("Scenario Results")

            selected_scenario = st.selectbox(
                "Select Scenario",
                results_df["Scenario"]
            )
            
            # Get selected row
            row = results_df[
                results_df["Scenario"] == selected_scenario
            ].iloc[0]

            st.markdown("## Savings & Profit")

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Profit",
                    f"${row['Total Profit']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "Total Carbon Saved",
                    f"{row['Total Carbon Saved']:,.2f} tCO₂"
                )
            
            with col3:
                st.metric(
                    "Total Water Saved",
                    f"{row['Total Water Saved']:.2f} m³ "
                )

            st.markdown("## Energy Reuse Metrics")

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "ERE Improvement",
                    f"{row['ERE improvement']:.3f}%"
                )
            
            with col2:
                st.metric(
                    "ERF",
                    f"{row['ERF']:.3f}"
                )
            with col3:
                st.metric(
                    "",
                    f"{"N/A"}"
                )

            st.markdown("## Scope 2 Savings")

            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Scope 2 CO₂ Saved",
                    f"{row['Tons Carbon']:,.2f} tCO₂"
                )
            
            with col2:
                st.metric(
                    "Scope 2 Water Saved",
                    f"{row['Cubic Meters Water']:.2f} m³"
                )

            with st.expander("Show Full Results Table"):

                st.dataframe(results_df)



            #endofedit
            chart_type = st.radio(
                "Select Visualization Type",
                ["Grouped Bar Chart", "Stacked Sustainability Chart"],
                help = "Weighting"
                
            )

            # Bar Charts
            if chart_type == "Grouped Bar Chart":

                

                fig, ax = plt.subplots()
                
                scenarios = results_df["Scenario"]
                x = np.arange(len(scenarios))
                
                width = 0.2
                
                
                carbon = results_df["Carbon Score"]
                econ   = results_df["Economic Score"]
                water  = results_df["Water Score"]
                social = results_df["Social Score"]
                
                
                carbon_err = results_df["CarbonError"]
                econ_err   = results_df["EconomicError"]
                water_err  = results_df["WaterError"]
                social_err = results_df["SocialError"]
                
                
                ax.bar(x - 1.5*width, carbon, width, yerr=carbon_err, capsize=4, label="Carbon")
                ax.bar(x - 0.5*width, econ,   width, yerr=econ_err,   capsize=4, label="Economic")
                ax.bar(x + 0.5*width, water,  width, yerr=water_err,  capsize=4, label="Water")
                ax.bar(x + 1.5*width, social, width, yerr=social_err, capsize=4, label="Social")
                
                
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45)
                
                ax.set_ylabel("Score")
                ax.set_xlabel("Scenario")
                ax.legend()
                
                st.pyplot(fig)

                
            # Stacked Bar Chart
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
                    

                    #wweight = st.sidebar.slider("Water Weight", 0.0, 1.0, .25, 0.01)
                    #sweight = st.sidebar.slider("Social Weight", 0.0, 1.0, .25, 0.01)
                    #eweight = st.sidebar.slider("Economic Weight", 0.0, 1.0, .25, 0.01)
                    #cweight = st.sidebar.slider("Carbon Weight", 0.0, 1.0, .25, 0.01)

                    wweight = st.sidebar.number_input(
                        "Water Weighting",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.25,
                        step=0.01
                    )
                    
                    sweight = st.sidebar.number_input(
                        "Social Weighting",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.25,
                        step=0.01
                    )
                    
                    eweight = st.sidebar.number_input(
                        "Economic Weighting",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.25,
                        step=0.01
                    )
                    
                    cweight = st.sidebar.number_input(
                        "Carbon Weighting",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.25,
                        step=0.01
                    )

                    carbonw =carbon*cweight
                    econw = econ*eweight
                    waterw = water*wweight
                    socialw = social*sweight
                    

                    
                    ax.bar(scenarios, carbonw, label="Carbon")
                    ax.bar(scenarios, econw, bottom=carbonw, label="Economic")
                    ax.bar(scenarios, waterw, bottom=carbonw + econw, label="Water")
                    ax.bar(scenarios, socialw, bottom=carbonw + econw + waterw, label="Social", yerr = modelerror)

                   
                    totals = carbon + econ + water + social


                    

                    ax.set_ylabel("Total Score")
                    ax.legend()
                    plt.xticks(rotation=45)

                    st.pyplot(fig)

            #Display Economic Impact

            
            
                
           




            selected_scenario = st.selectbox(
                "Select Offtaker for Cost Breakdown",
                results_df["Scenario"]
            )
            
            row = results_df[results_df["Scenario"] == selected_scenario].iloc[0]
            
            cost_labels = [
                "Pipe Cost(Seperate of Data Center)",
                "Insulation Cost",
                "Pump Cost",
                "Heat Exchanger Cost",
                "Yearly Maintenance Cost",
                "Yearly Electicity Cost"
            ]
            
            cost_values = [
                row["Pipe Cost"],
                row["Insulation Cost"],
                row["Pump Cost"],
                row["Heat Exchanger Cost"],
                row["Maintenance per annum"],
                row["Electricity per annum"]
            ]

            
            
            fig, ax = plt.subplots()
            
            colors = [
                "#1f77b4",   # Pipe
                "#1f77b4",   # Insulation
                "#1f77b4",   # Pump
                "#ff7f0e",   # Heat Exchanger
                "#ff7f0e",  # Maintenance
                "#1f77b4"   # Electricity
            ]
            
            bars = ax.barh(cost_labels, cost_values, color = colors)
            
            for bar in bars:
                width = bar.get_width()
            
                ax.text(
                    width,
                    bar.get_y() + bar.get_height()/2,
                    f"${width:,.0f}",
                    va='center'
                )
            
            ax.set_xlabel("Cost ($)")
            ax.set_title(f"Economic Cost Breakdown: {selected_scenario}")
            from matplotlib.patches import Patch

            legend_elements = [
                Patch(facecolor="#1f77b4", label="Non Data Center Costs"),
                Patch(facecolor="#ff7f0e", label="Data Center Costs")
            ]

            ax.legend(handles=legend_elements)
            
            st.pyplot(fig,)

    else:
        st.info("Click 'Run Model for All Sheets' to generate results.")
