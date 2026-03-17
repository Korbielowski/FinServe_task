# FinServe - AI and Automation Opportunities

## 1. Identified Business Problems and Proposed AI/Automation Solutions

### Problem 1 - Manual preparation of credit memos and proposals

**Description**  
Analysts and sales/operations teams manually extract data from CRM and internal
systems, copy-paste into Word/PDF templates, format documents, and send them to
clients or credit committees. This process is time-consuming, repetetive,
error-prone, and delays client responses and credit decisions.

**Proposed Solution**  
AI-powered credit memo generator:

- Automatically pull client data from CRM
- Use LLM to create structured, professional credit memo in
  Markdown
- Convert Markdown to HTML and then to PDF
- Allow human review and edit one-click download or email delivery

### Problem 2 - Manual re-keying of loan applications into core banking system

**Description**  
Applications arrive via email or portal, staff re-enter or copy data into the
core system. This leads to wasted time, data entry errors, inconsistencies
between channels, and delayed risk assessment.

**Proposed Solution**  
Intelligent document ingestion pipeline:

- OCR, LLM-based document understanding to extract key fields from PDFs,
  emails, scans
- Structured output, auto-populate core banking forms
- Validation rules, flagging of missing/inconsistent data
- Audit trail of extracted vs entered values

### Problem 3 - Inconsistent and slow client support and complaint handling

**Description**  
Every enquiry, complaint or status request is handled manually without shared
templates, knowledge base or quick access to client history resulting in
inconsistent
quality, long response times, regulatory risk.

**Proposed Solution**  
AI-enhanced support agent:

- RAG over internal KB, regulations, client
  history
- Auto-generate personalized, compliant draft replies
- Auto-log actions in ticketing system
- Escalate only complex cases to humans

## 2. Chosen Solution and Rationale

**Selected for implementation:** Problem 1 - AI Credit Memo Generator

**Why this one?**

- Highest operational pain point and clearest ROI
- Directly improves client experience (faster proposals) and internal efficiency
- Easiest to demonstrate tangible business value in a short PoC
- Combines AI (content generation), automation (PDF and email) and simple UI -
  perfect showcase of end-to-end value
- Other problems require deeper system integrations or larger datasets, harder
  to prototype quickly

## 3. Implementation Walkthrough

**Technology stack**

- Python
- Streamlit
- OpenAI GPT-4o-mini for memo generation
- pandas - CRM data simulation (CSV)
- markdown - Markdown to HTML
- WeasyPrint - HTML to PDF
- smtplib - email delivery with attachment

**How it works**

1. Load sample CRM data
2. Dropdown to select client
3. Display key client facts, basic business rules (collateral warning, risk
   hint)
4. One-click “Generate Credit Memo” - structured prompt sent to LLM
5. Generated Markdown appears in editable text area
6. Convert to PDF with company branding, date, confidentiality footer
7. Download PDF or send directly via email (customizable recipient/subject/body)

**GitHub-ready prototype**  
Clean code structure, .env support, sample data included, easy to run locally or
deploy.

## 4. Potential Extensions and Improvements (given more time)

- Real CRM integration e.g. Salesforce
- Multi-template support e.g. credit memo, loan offer
- RAG layer pulling internal credit policies / regulatory updates into prompts
- Basic risk scoring calculated and embedded in memo
- Document versioning + approval workflow
- Quality monitoring
- Security and compliance: data masking, prompt/response logging, audit trail
