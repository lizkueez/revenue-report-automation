import streamlit as st
import pandas as pd

st.title("Partner Revenue Report Generator")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if uploaded_file:

    try:
        # Read Excel starting from row 6
        df = pd.read_excel(uploaded_file, header=5)

        st.subheader("Detected Columns")
        st.write(df.columns.tolist())

        st.subheader("Preview of Data")
        st.write(df.head())

    except Exception as e:
        st.error(f"Error: {e}")
