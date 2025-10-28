import agreement_comparision
import data_extraction
import json
import streamlit as st 
import schedule
import threading
import time
import scraping
import notification

# ******** Modern CSS Styling ******** #
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 20px 0;
        border: none;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid #667eea;
        background-color: #f0f4f8;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Success message styling */
    .stAlert [data-testid="stMarkdownContainer"] {
        color: #059669;
    }
    
    /* Error message styling */
    .stAlert [data-testid="stMarkdownContainer"] p {
        color: #dc2626;
    }
    
    /* Subheader styling */
    h2 {
        color: #1e293b !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-top: 2rem !important;
    }
    
    /* Text styling */
    .stMarkdown {
        color: #374151;
        line-height: 1.6;
    }
    
    /* Card-like containers for results */
    .result-container {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Progress and status indicators */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom metric styling */
    .stMetric {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Sidebar styling (if you add one later) */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ******** Phase 2    ******** #

def run_scheduler():
    # call call_scrape_funtion function every night at 12 am 
    schedule.every().day.at("00:00").do(scraping.call_scrape_funtion)
    
    # these are for testing purpose 
    # for testing part we will call scheduler in every 10 seconds 
    # schedule.every(10).seconds.do(scraping.call_scrape_funtion)
    
    # schedule.every(1).minutes.do(scraping.call_scrape_funtion)
    
    while True:
        schedule.run_pending()
        time.sleep(1)     #check every 5 seconds 

# start scheduler in background thread so streamlit does not block 
threading.Thread(target=run_scheduler, daemon=True).start() 

if __name__ == "__main__":
    
    AGREEMENT_JSON_MAP={
        "Data Processing Agreement":"json_files/dpa.json",
        "Joint Controller Agreement": "json_files/jca.json",
        "Controller-to-Controller Agreement":"json_files/c2c.json",
        "Processor-to-Subprocessor Agreement":"json_files/subprocessor.json",
        "Standard Contractual Clauses": "json_files/scc.json"
    }
    
    # Define the recipient email (as used in notification.py)
    RECIPIENT_EMAIL = "kavyavijjana@gmail.com"
    
    # Modern header with gradient
    st.markdown('<h1 class="main-header">Contract Compliance Checker</h1>', unsafe_allow_html=True)
    
    # Add a brief description
    st.markdown("""
    <div style='text-align: center; color: #64748b; margin-bottom: 2rem;'>
        Upload your agreement document to check GDPR compliance and receive automated analysis reports.
    </div>
    """, unsafe_allow_html=True)
    
    # file upload 
    uploaded_file = st.file_uploader("Upload an agreement (PDF Only)", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Processing your document..."):
            with open("temp_uploded.pdf", "wb") as f:
                f.write(uploaded_file.read())
                
                st.info("Processing your file...")
                
                # step 1: identify the type of agreement
                agreement_type = agreement_comparision.document_type("temp_uploded.pdf")
                
                # Display document type in a styled container
                st.markdown(f"""
                <div class="result-container">
                    <h3>Detected Document Type</h3>
                    <p style="font-size: 1.2rem; font-weight: 600; color: #667eea;">{agreement_type}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if agreement_type in AGREEMENT_JSON_MAP:
                    
                    # step 2 : extract clause from unseen file 
                    unseen_data = data_extraction.Clause_extraction("temp_uploded.pdf")
                    
                    st.success("Clause extraction completed successfully!")
                    
                    # step 3: Load respective template json 
                    template_file = AGREEMENT_JSON_MAP[agreement_type]
                    
                    print("template_file------------", template_file)
                    
                    with open(template_file, "r", encoding="utf-8") as f:
                        template_data = json.load(f)
                        
                    # step 4: Compare agreements
                    result = agreement_comparision.compare_agreements(unseen_data, template_data)
                    
                    # show result in a styled container
                    st.markdown("""
                    <div class="result-container">
                        <h2>Compliance Analysis Results</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write(result)
                    
                    # Email notification section
                    try:
                        st.info(f"Sending compliance report to {RECIPIENT_EMAIL}...")
                        
                        # Set up the email content
                        email_subject = f"Compliance Check Report: {uploaded_file.name} ({agreement_type})"
                        email_body = (
                            f"Analysis complete for file: {uploaded_file.name}\n"
                            f"Detected Type: {agreement_type}\n"
                            f"Template Used: {template_file}\n\n"
                            "--- ANALYSIS RESULT ---\n\n"
                            f"{result}"
                        )
                        
                        # Call the notification function
                        notification.send_email_notification(
                            subject=email_subject,
                            body=email_body,
                            receiver_email=RECIPIENT_EMAIL
                        )
                        
                        st.success(f"Compliance report successfully sent to {RECIPIENT_EMAIL}!")
                    
                    except Exception as e:
                        st.error(f"Failed to send email notification. Error: {e}")
                    
                else:
                    st.error(f"This document is not under GDPR Compliance")
                    
                    
    # Add a footer
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; margin-top: 4rem; padding: 1rem;'>
        <hr style='border: 0.5px solid #e2e8f0; margin-bottom: 1rem;'>
        Contract Compliance Checker • GDPR Compliance Tool
    </div>
    """, unsafe_allow_html=True)