import streamlit as st
from brd_master.app import run as run_brd
from code_switch.app import main as run_codeswitch

st.set_page_config(
    page_title="Combined_codeswitch_brd",
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
            # caption="Platform Overview",
            use_column_width=True
        )
    
    with main_col2:
        st.markdown("""
        <h3 style="margin-top: 20px;">Supercharge Your Development with Gen AI</h3>
                        
                    


        Welcome to the future of development! Our Gen AI Powered Development Kit is designed to help you streamline workflows,<br>
        boost efficiency, and achieve more with less effort. Using the latest in Large Language Model (LLM) technology, we've crafted two <br>powerful tools to transform how you handle business requirements and code.
        
        Meet Your New Tools:
                        
        📝 BRD Test Case Generator
        - Effortlessly generate precise test cases from your Business Requirement Documents (BRDs).
        - Say goodbye to manual work and hello to more time for innovation!
                        
        💻 Code Conversion Engine
        - Instantly convert code between different programming languages. 
        - Whether you're working across platforms or modernizing legacy systems, this tool will save you hours of tedious re-coding.
        """, unsafe_allow_html=True)
    
    # Add separator
    st.markdown("---")
    
    # Center the "Our Tools" heading
    # st.markdown("<h3 style='text-align: center;'>Our Tools</h3>", unsafe_allow_html=True)
    
    # tool_col1, tool_col2 = st.columns(2)
    
    # with tool_col1:
    #     st.markdown("""
    #     #### 🔍 BRD Test Master
    #     Comprehensive solution for Business Requirement Document testing:
    #     - Document processing
    #     - Content analysis
    #     - Quick PDF review
    #     - Automated text extraction
    #     """)
    
    # with tool_col2:
    #     st.markdown("""
    #     #### 🔄 Code Switch
    #     Advanced code conversion and analysis platform:
    #     - Multi-language support
    #     - Syntax validation
    #     - Code explanation
    #     - Performance optimization
    #     """)

def main():
    # Sidebar configuration
    st.sidebar.title("Task Panel")
    
    # Navigation options without image
    app_choice = st.sidebar.radio(
        "Choose Application",
        ["Home", "BRD Test Master", "Code Switch"]
    )
    
    # Sidebar info
    # st.sidebar.markdown("---")
    # st.sidebar.info("Version 1.0.0")
    
    # Main content area
    if app_choice == "Home":
        home_page()
    elif app_choice == "BRD Test Master":
        run_brd()
    elif app_choice == "Code Switch":
        run_codeswitch()
    
    # Footer
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("© 2024 Multi-Tool Platform")

if __name__ == "__main__":
    main()
