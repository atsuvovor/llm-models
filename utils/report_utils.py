# utils/report_utils.py
import smtplib
from fpdf import FPDF
from email.message import EmailMessage
import tempfile
import streamlit as st

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Cyber Attack Summary", ln=True, align="C")

    for i, row in df.head(30).iterrows():  # Limiting to 30 rows
        pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

def send_email_with_pdf(receiver_email, pdf_path):
    EMAIL = "your_email@example.com"
    PASSWORD = "your_password"
    
    msg = EmailMessage()
    msg["Subject"] = "Cyber Attack Simulation Report"
    msg["From"] = EMAIL
    msg["To"] = receiver_email
    msg.set_content("Attached is your cyber attack simulation report.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="report.pdf")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

def render_pdf_and_email_ui(df):
    st.markdown("### 📤 Download / Email PDF Report")
    if st.button("📄 Generate PDF Report"):
        pdf_path = generate_pdf_report(df)
        with open(pdf_path, "rb") as f:
            st.download_button("💾 Download PDF", f, file_name="cyber_report.pdf")

    email = st.text_input("📧 Email this report to:")
    if st.button("Send Email") and email:
        try:
            pdf_path = generate_pdf_report(df)
            send_email_with_pdf(email, pdf_path)
            st.success(f"Email sent to {email}!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")
