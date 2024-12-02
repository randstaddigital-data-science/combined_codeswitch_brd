import streamlit as st
from brd_master.app import run as run_brd
from code_switch.app import main as run_codeswitch
from ImageRAG.app import main as run_imagerag  # Import the main function from ImageRAG

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

def main():
    # Sidebar configuration
    st.sidebar.title("Task Panel")
    
    # Navigation options
    app_choice = st.sidebar.radio(
        "Choose Application",
        ["Home", "BRD Test Master", "Code Switch", "Image RAG"]
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
    
    # Footer
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("© 2024 Multi-Tool Platform")

if __name__ == "__main__":
    main()
