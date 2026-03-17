from pathlib import Path
import streamlit as st
import pandas as pd
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from tempfile import NamedTemporaryFile
from openai import OpenAI
from dotenv import dotenv_values
import smtplib
from email.message import EmailMessage
import datetime
import markdown

if "init" not in st.session_state:
    config = dotenv_values("../.env")
    if "OPENAI_API_KEY" not in config:
        raise Exception("OPENAI_API_KEY is not specified in the .env config file")
    st.session_state["api_client"] = OpenAI(api_key=config["OPENAI_API_KEY"])

    if "SENDER_EMAIL" not in config:
        raise Exception("SENDER_EMAIL is not specified in the .env config file")
    st.session_state["sender_email"] = config["SENDER_EMAIL"]

    if "SENDER_PASSWORD" not in config:
        raise Exception("SENDER_PASSWORD is not specified in the .env config file")
    st.session_state["sender_password"] = config["SENDER_PASSWORD"]

    df = pd.read_csv("data/example.csv")
    df["label"] = df["company_name"] + " (" + df["legal_form"] + ")"
    st.session_state["crm_df"] = df

    st.session_state["init"] = True

st.set_page_config(page_title="Credit Memo Generator", layout="wide")

st.markdown("""
<style>
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI Credit Memo Generator")
st.caption("Simulated CRM-based workflow for FinServe")

df = st.session_state["crm_df"]
selected = st.selectbox(
    "Select client",
    df["label"],
    on_change=lambda: st.session_state.pop("generated_text", None)
)
client_data = df[df["label"] == selected].iloc[0]

st.subheader("Client Overview")
col1, col2 = st.columns(2)

with col1:
    st.write("**Company:**", client_data["company_name"])
    st.write("**Legal form:**", client_data["legal_form"])
    st.write("**NIP:**", client_data["tax_id"])
    st.write("**Lead source:**", client_data["lead_source"])

with col2:
    st.write("**Requested amount:**", f"{client_data['requested_amount']:,} PLN")
    st.write("**Risk rating:**", client_data["risk_rating"])
    st.write("**Collateral:**", client_data["collateral_type"])
    st.write("**Collateral value:**", f"{client_data['collateral_value']:,} PLN")

if client_data["collateral_value"] < client_data["requested_amount"]:
    st.warning("⚠️ Collateral lower than requested amount")

if client_data["risk_rating"] == "High":
    decision_hint = "High risk client – proceed with caution."
elif client_data["risk_rating"] == "Medium":
    decision_hint = "Moderate risk – standard review required."
else:
    decision_hint = "Low risk client."

if st.button("Generate Credit Memo"):
    with st.spinner("Generating..."):
        prompt = f"""
        You are a credit analyst at a financial institution.

        Client:
        - Company: {client_data['company_name']}
        - Legal form: {client_data['legal_form']}
        - Requested amount: {client_data['requested_amount']} PLN
        - Risk rating: {client_data['risk_rating']}
        - Collateral: {client_data['collateral_type']}
        - Collateral value: {client_data['collateral_value']} PLN

        Internal note: {decision_hint}

        Write a structured credit memo with sections:
        1. Company overview
        2. Credit request
        3. Risk assessment
        4. Collateral evaluation
        5. Recommendation

        Keep it concise and professional.
        Use **bold** and *italic* Markdown syntax.
        """

        response = st.session_state["api_client"].chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        st.session_state["generated_text"] = response.choices[0].message.content

if "generated_text" in st.session_state:
    edited_text = st.text_area(
        "Edit before export / sending",
        st.session_state["generated_text"],
        height=400
    )

    def create_pdf_from_markdown(md_text: str, company_name: str) -> Path | None:
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: "Helvetica", "Arial", sans-serif; font-size: 11pt; line-height: 1.45; color: #111; margin: 2.5cm 2cm 2cm 2cm; }}
                h1, h2, h3 {{ color: #1a1a1a; margin-top: 1.2em; margin-bottom: 0.6em; }}
                h1 {{ font-size: 18pt; }}
                h2 {{ font-size: 14pt; }}
                strong {{ font-weight: bold; }}
                em {{ font-style: italic; }}
                p {{ margin: 0.8em 0; }}
                .footer {{ margin-top: 3cm; font-size: 9pt; color: #555; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>Credit Memo</h1>
            <p><strong>Company:</strong> {company}</p>
            <p><strong>Date:</strong> {date}</p>
            <hr>
            {content}
            <div class="footer">Confidential – For internal use only</div>
        </body>
        </html>
        """

        today = datetime.date.today().strftime("%Y-%m-%d")
        html_content = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
        full_html = html_template.format(company=company_name, date=today, content=html_content)

        font_config = FontConfiguration()

        try:
            tmp_file = NamedTemporaryFile(suffix=".pdf", delete=False)
            tmp_file.close()

            HTML(string=full_html).write_pdf(
                tmp_file.name,
                font_config=font_config
            )
            return Path(tmp_file.name)
        except Exception as e:
            st.error(f"Błąd podczas generowania PDF: {str(e)}")
            return None

    if st.button("Download PDF"):
        if "pdf_path" not in st.session_state or not st.session_state["pdf_path"].exists():
            pdf_path = create_pdf_from_markdown(edited_text, client_data["company_name"])
            if pdf_path:
                st.session_state["pdf_path"] = pdf_path
            else:
                st.stop()

        pdf_path = st.session_state["pdf_path"]

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download credit_memo.pdf",
                data=f,
                file_name="credit_memo.pdf",
                mime="application/pdf",
                key="download_btn"
            )

    st.subheader("Send PDF via Email")
    recipient = st.text_input("Recipient email", client_data.get("contact_email", ""))
    subject = st.text_input("Email subject", "Credit Memo")
    body = st.text_area("Email body", "Dear Client,\n\nPlease find attached the credit memo.\n\nBest regards,")

    def send_pdf_email(sender_email, sender_password, recipient_email, subject, body, pdf_path):
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.set_content(body)

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='credit_memo.pdf')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

    if st.button("Send PDF"):
        if not recipient:
            st.error("Please enter recipient email")
        else:
            if "pdf_path" not in st.session_state or not st.session_state["pdf_path"].exists():
                pdf_path = create_pdf_from_markdown(edited_text, client_data["company_name"])
                if pdf_path:
                    st.session_state["pdf_path"] = pdf_path
                else:
                    st.stop()
            else:
                pdf_path = st.session_state["pdf_path"]

            try:
                send_pdf_email(
                    sender_email=st.session_state["sender_email"],
                    sender_password=st.session_state["sender_password"],
                    recipient_email=recipient,
                    subject=subject,
                    body=body,
                    pdf_path=pdf_path
                )
                st.success("Email sent successfully!")
            except Exception as e:
                st.error(f"Error sending email: {str(e)}")