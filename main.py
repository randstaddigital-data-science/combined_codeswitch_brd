import streamlit as st
from brd_master.app import run as run_brd
from code_switch.app import main as run_codeswitch
from ImageRAG.app import main as run_imagerag  # Import the main function from ImageRAG
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
        boost efficiency, and achieve more with less effort. Using the latest in Large Language Model (LLM) technology, we've crafted three 
        powerful tools to transform how you handle business requirements, code, and image-based document analysis.

        Meet Your New Tools:
                        
        📝 BRD Test Case Generator
        - Effortlessly generate precise test cases from your Business Requirement Documents (BRDs).
        - Say goodbye to manual work and hello to more time for innovation!
                        
        💻 Code Conversion Engine
        - Instantly convert code between different programming languages. 
        - Whether you're working across platforms or modernizing legacy systems, this tool will save you hours of tedious re-coding.

        📄 PDF Analysis with RAG and Claude
        - Analyze PDFs and answer queries with image and text context using cutting-edge Retrieval-Augmented Generation technology.
        """, unsafe_allow_html=True)
    
    # Add separator
    st.markdown("---")

def run_flask():
    """Run the Flask application."""
    flask_app_dir = os.path.abspath("etl_job_rationalization")
    
    # Ensure the directory exists
    if not os.path.exists(flask_app_dir):
        st.error(f"Directory does not exist: {flask_app_dir}")
        return

    try:
        # Start Flask as a background process
        flask_process = subprocess.Popen(
            ["flask", "run", "--host=0.0.0.0", "--port=9090"],
            cwd=flask_app_dir,
            shell=True,
            env={"FLASK_APP": "app.py", **os.environ},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Provide immediate feedback while Flask starts
        st.info("Starting Flask application... Please wait.")
        time.sleep(5)  # Allow time for Flask to start

        # Check if Flask is running
        if flask_process.poll() is None:
            st.success("Flask application is running.")
            st.markdown("""
                ### Flask Application
                The Flask application is running. Access it here:
                [http://localhost:9090](http://localhost:9090)
            """)
        else:
            stderr = flask_process.stderr.read().decode()
            st.error(f"Flask application failed to start. Error: {stderr}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def etl_job_page():
    """Display the ETL Job Rationalisation page."""
    st.title("ETL Job Rationalisation")
    st.markdown("""
        This page will start the ETL Job Rationalisation Flask application and provide access once it's running.
    """)

    # Trigger Flask start
    run_flask()

# Main Function
def main():
    # Sidebar configuration
    st.sidebar.title("Task Panel")
    
    # Navigation options
    app_choice = st.sidebar.radio(
        "Choose Application",
        ["Home", "BRD Test Master", "Code Switch", "Image RAG", "ETL Job Rationalisation"]
    )
    
    # Main content area
    if app_choice == "Home":
        home_page()
    elif app_choice == "BRD Test Master":
        run_brd()
    elif app_choice == "Code Switch":
        run_codeswitch()
    elif app_choice == "Image RAG":
        run_imagerag()  # Run the ImageRAG application
    elif app_choice == "ETL Job Rationalisation":
        etl_job_page()  # Display the ETL Job Rationalisation page

# Run the App
if __name__ == "__main__":
    main()
