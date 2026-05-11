import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
from io import BytesIO
import zipfile
import subprocess
import tempfile
import os

st.title("Partner Revenue Report Generator")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

month = st.text_input("Month")
year = st.text_input("Year")


def format_currency(value):

    if pd.isna(value):
        return "$0"

    if float(value).is_integer():
        return f"${value:,.0f}"

    return f"${value:,.2f}"


if uploaded_file and month and year:

    try:

        # Read raw Excel
        raw_df = pd.read_excel(
            uploaded_file,
            header=None
        )

        header_row = None

        # Detect correct report table
        for idx, row in raw_df.iterrows():

            row_values = row.astype(str).tolist()

            if (
                "Partner" in row_values
                and "Total Spend" in row_values
            ):
                header_row = idx
                break

        if header_row is None:
            st.error("Could not find report table.")
            st.stop()

        # Read actual table
        df = pd.read_excel(
            uploaded_file,
            header=header_row
        )

        # Clean column names
        df.columns = (
            df.columns
            .astype(str)
            .str.replace("\n", " ", regex=False)
            .str.strip()
        )

        # Keep required columns
        df = df[
            [
                "Partner",
                "Total Spend",
                "Total Revenue (reports, after deduction)",
                "Net Revenue (-7% Kueez share)",
                "Net ROI (Net Rev - Spend)",
                "Total Payout"
            ]
        ]

        # Remove empty rows
        df = df.dropna(subset=["Partner"])

        st.success(
            f"Loaded {len(df)} partner rows."
        )

        if st.button("Generate PDF Reports"):

            zip_buffer = BytesIO()

            with zipfile.ZipFile(
                zip_buffer,
                "a"
            ) as zip_file:

                for _, row in df.iterrows():

                    partner_name = str(
                        row["Partner"]
                    )

                    # Safe filename version
                    safe_partner_name = (
                        partner_name
                        .replace("/", "-")
                        .replace("\\", "-")
                        .replace(":", "-")
                        .replace("*", "")
                        .replace("?", "")
                        .replace('"', "")
                        .replace("<", "")
                        .replace(">", "")
                        .replace("|", "")
                    )

                    context = {
                        "partner_name": partner_name,
                        "month": month,
                        "year": year,

                        "total_spend": format_currency(
                            row["Total Spend"]
                        ),

                        "total_revenue": format_currency(
                            row["Total Revenue (reports, after deduction)"]
                        ),

                        "net_revenue": format_currency(
                            row["Net Revenue (-7% Kueez share)"]
                        ),

                        "net_roi": format_currency(
                            row["Net ROI (Net Rev - Spend)"]
                        ),

                        "total_payout": format_currency(
                            row["Total Payout"]
                        )
                    }

                    with tempfile.TemporaryDirectory() as tmpdir:

                        docx_path = os.path.join(
                            tmpdir,
                            f"{safe_partner_name}.docx"
                        )

                        pdf_path = os.path.join(
                            tmpdir,
                            f"{safe_partner_name}.pdf"
                        )

                        doc = DocxTemplate(
                            "template.docx"
                        )

                        doc.render(context)

                        doc.save(docx_path)

                        subprocess.run(
                            [
                                "libreoffice",
                                "--headless",
                                "--convert-to",
                                "pdf",
                                docx_path,
                                "--outdir",
                                tmpdir
                            ],
                            check=True
                        )

                        with open(pdf_path, "rb") as pdf_file:

                            zip_file.writestr(
                                f"{safe_partner_name}_{month}_{year}.pdf",
                                pdf_file.read()
                            )

            st.download_button(
                label="Download PDF Reports ZIP",
                data=zip_buffer.getvalue(),
                file_name=(
                    f"partner_reports_{month}_{year}.zip"
                ),
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"Error: {e}")
