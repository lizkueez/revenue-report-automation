import streamlit as st
import pandas as pd

st.title("Partner Revenue Report Generator")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if uploaded_file:

    header_row = st.number_input(
        "Header Row Number",
        min_value=1,
        max_value=50,
        value=1
    )

    try:
        # Read Excel using selected header row
        df = pd.read_excel(
            uploaded_file,
            header=header_row - 1
        )

        st.subheader("Detected Columns")
        st.write(df.columns.tolist())

        st.subheader("Preview of Data")
        st.write(df.head())

    except Exception as e:
        st.error(f"Error: {e}")
