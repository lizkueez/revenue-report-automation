import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
from io import BytesIO
import zipfile

st.title("Partner Revenue Report Generator")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

month = st.text_input("Month")
year = st.text_input("Year")

if uploaded_file and month and year:

    df = pd.read_excel(uploaded_file)

    if st.button("Generate Reports"):

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "a") as zip_file:

            for _, row in df.iterrows():

                partner_name = str(row["Partner"])

                doc = DocxTemplate("template.docx")

                context = {
                    "partner_name": partner_name,
                    "month": month,
                    "year": year,
                    "total_spend": row["Total Spend"],
                    "total_revenue": row["Total Revenue"],
                    "net_revenue": row["Net Revenue (-7% Kueez share)"],
                    "net_roi": row["Net ROI (Net Rev - Spend)"],
                    "total_payout": row["Total Payout"]
                }

                doc.render(context)

                output = BytesIO()
                doc.save(output)

                filename = f"{partner_name}_{month}_{year}.docx"

                zip_file.writestr(
                    filename,
                    output.getvalue()
                )

        st.download_button(
            label="Download Reports ZIP",
            data=zip_buffer.getvalue(),
            file_name=f"partner_reports_{month}_{year}.zip",
            mime="application/zip"
        )
