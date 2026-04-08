import streamlit as st
import pandas as pd

from CCSv8 import run_model


# --------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Waste Heat Recovery Model",
    layout="wide"
)

st.title("Waste Heat Recovery Model")
st.write(
    "Upload an Excel file to evaluate multiple waste heat recovery scenarios."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload input Excel file",
    type=["xlsx"]
)


# --------------------------------------------------
# MAIN APP LOGIC
# --------------------------------------------------
if uploaded_file is not None:

    # ----------------------------------------------
    # READ INPUT EXCEL FILE
    # ----------------------------------------------
    input_df = pd.read_excel(uploaded_file)

    st.subheader("Input Data Preview")
    st.dataframe(input_df)


    # ----------------------------------------------
    # RUN MODEL FOR EACH COLUMN (SCENARIO)
    # ----------------------------------------------
    all_results = {}

    for column_name in input_df.columns:
        # Extract ONE column as a DataFrame
        scenario_df = input_df[[column_name]]

        # Run CCS model (calculations happen inside CCSv8.py)
        results = run_model(scenario_df)

        # Store results
        all_results[column_name] = results


    # ----------------------------------------------
    # KPI DISPLAY (SIDE-BY-SIDE)
    # ----------------------------------------------
    st.subheader("Model Results")

    result_columns = st.columns(len(all_results))

    for col, (scenario_name, results) in zip(
        result_columns, all_results.items()
    ):
        with col:
            st.markdown(f"### {scenario_name}")

            st.metric(
                "Total Profit",
                f"${results['Total Profit']:,.0f}"
            )

            st.metric(
                "Total Water Saved",
                f"{results['Total Water Saved']:,.2f}"
            )

            st.metric(
                "Total Carbon Saved",
                f"{results['Total Carbon Saved']:,.2f}"
            )

            st.metric(
                "Total Score",
                f"{results['Total Score']:.2f}"
            )

            st.metric(
                "Water Score",
                f"{results['Water Score']:.2f}"
            )

            st.metric(
                "Economic Score",
                f"{results['Economic Score']:.2f}"
            )

            st.metric(
                "Social Score",
                f"{results['Social Score']:.2f}"
            )

            st.metric(
                "Carbon Score",
                f"{results['Carbon Score']:.2f}"
            )

            st.metric(
                "ERE Improvement",
                f"{results['ERE Improvement']:.2f}%"
            )

            st.metric(
                "ERF",
                f"{results['ERF']:.2f}"
            )


    # ----------------------------------------------
    # COMPARISON TABLE (OPTIONAL BUT VERY USEFUL)
    # ----------------------------------------------
    st.subheader("Comparison Table")

    comparison_df = pd.DataFrame(all_results)
    st.dataframe(comparison_df)


else:
    st.info("Please upload an Excel file to begin.")
