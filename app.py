import streamlit as st
import pandas as pd
from jinja2 import Template
from xhtml2pdf import pisa
import io

st.set_page_config(page_title="Partner Revenue Tool", layout="centered")

st.title("📊 Revenue PDF Generator")

# User Inputs
report_date = st.text_input("Enter Month/Year (e.g. October 2024)")
uploaded_file = st.file_uploader("Upload your Revenue CSV", type=['csv'])

def create_pdf(row, date_str):
    with open("template.html", "r") as f:
        template = Template(f.read())
    
    # Map the columns you specified
    html_out = template.render(
        report_date=date_str,
        partner_name=row['Partner'],
        total_spend=row['Total'],
        total_revenue=row['Rev after DD'],
        net_revenue=row['Net Rev (-Kueez share)'],
        net_roi=row['Total Profit Net ROI (Net Rev - Spend)'],
        facebook_spend=row['Total'],
        total_payout=row['KMS']
    )
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html_out.encode("utf-8")), dest=pdf_buffer)
    return pdf_buffer.getvalue()

if uploaded_file and report_date:
    df = pd.read_csv(uploaded_file)
    # Remove rows with empty revenue
    df = df.dropna(subset=['Rev after DD'])
    
    # Group by Partner (Column C) [cite: 1]
    summary = df.groupby('Partner').agg({
        'Total': 'sum',
        'Rev after DD': 'sum',
        'Net Rev (-Kueez share)': 'sum', 
        'Total Profit Net ROI (Net Rev - Spend)': 'sum',
        'KMS': 'sum'
    }).reset_index()

    st.success(f"Generated data for {len(summary)} partners.")
    
    for _, row in summary.iterrows():
        pdf_data = create_pdf(row, report_date)
        st.download_button(
            label=f"📥 Download PDF for {row['Partner']}",
            data=pdf_data,
            file_name=f"{row['Partner']}_Summary.pdf",
            mime="application/pdf"
        )
