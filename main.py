import streamlit as st
from brd_master.app import run as run_brd
from code_switch.app import main as run_codeswitch
from ImageRAG.app import main as run_imagerag
from etl_job_rationalization.app import etl_rationalization_main
from resume_mapping.main import resume_mapping
import subprocess
import os
import time

# Streamlit Page Configuration
st.set_page_config(
    page_title="Combined App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Home Page Function
def home_page():
    st.title("Welcome to the Gen AI-Powered Platform")
    
    # Create two columns for image and main description
    main_col1, main_col2 = st.columns([1, 2])
    
    with main_col1:
        st.image(
            "./Images/unnamed.jpg",
            use_column_width=True
        )
    
    with main_col2:
        st.markdown("""
        <h3 style="margin-top: 20px;">Supercharge Your Development with Gen AI</h3>

        Welcome to the future of development! Our Gen AI Powered Development Kit is designed to help you streamline workflows,
        boost efficiency, and achieve more with less effort. Using the latest in Large Language Model (LLM) technology, we've crafted several 
        powerful tools to transform how you handle business requirements, code, and image-based document analysis.

        Meet Your New Tools:
                        
        📝 BRD Test Case Generator  
        - Effortlessly generate precise test cases from your Business Requirement Documents (BRDs).  
                        
        💻 Code Conversion Engine  
        - Instantly convert code between different programming languages.  

        📄 PDF Analysis with RAG and Claude  
        - Analyze PDFs and answer queries with image and text context using cutting-edge Retrieval-Augmented Generation technology.  

        📋 Resume Mapping  
        - Match job descriptions with resumes using AWS Bedrock and advanced embeddings.
        """, unsafe_allow_html=True)
    
    # Add separator
    st.markdown("---")

# Main Function
def main():
    st.sidebar.title("Task Panel")
    app_choice = st.sidebar.radio(
        "Choose Application",
        ["Home", "BRD Test Master", "Code Switch", "Image RAG", "ETL Job Rationalisation", "Resume Mapping"]
    )

    if app_choice == "Home":
        home_page()
    elif app_choice == "BRD Test Master":
        run_brd()
    elif app_choice == "Code Switch":
        run_codeswitch()
    elif app_choice == "Image RAG":
        run_imagerag()
    elif app_choice == "ETL Job Rationalisation":
        etl_rationalization_main()
    elif app_choice == "Resume Mapping":
        resume_mapping()

if __name__ == "__main__":
    main()
