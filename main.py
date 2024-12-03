import streamlit as st
from brd_master.app import run as run_brd
from Code_switch.app import main as run_codeswitch
from ImageRAG.app import main as run_imagerag  # Import the main function from ImageRAG
import subprocess
import os
import time

st.set_page_config(
    page_title="Combined App",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    flask_app_dir = os.path.join(os.getcwd(), "etl_job_rationalization")
    
    # Ensure the directory exists
    if not os.path.exists(flask_app_dir):
        raise NotADirectoryError(f"Directory does not exist: {flask_app_dir}")
    
    # Start the Flask app as a subprocess with the same command used previously
    flask_process = subprocess.Popen(
        ["flask", "run", "--host=0.0.0.0", "--port=3001"],
        cwd=flask_app_dir,
        shell=True,
        env={"FLASK_APP": "app.py", **os.environ}  # Set FLASK_APP and preserve other environment variables
    )
    
    # Allow time for the Flask server to start
    time.sleep(5)
    
    # Provide a link to the Flask app in Streamlit
    st.markdown("""
        ### Flask Application
        The Flask application is running. You can access it at:
        [http://localhost:3001](http://localhost:3001)
    """)
    
    # Optionally return the process for later management
    return flask_process


def main():
    # Sidebar configuration
    st.sidebar.title("Task Panel")
    
    # Navigation options
    app_choice = st.sidebar.radio(
        "Choose Application",
        ["Home", "BRD Test Master", "Code Switch", "Image RAG", "Flask App"]
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
        flask_process = run_flask()
        # Optionally handle process cleanup when app exits
    
    # Footer
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("© 2024 Multi-Tool Platform")

if __name__ == "__main__":
    main()
