import streamlit as st
import asyncio
import tempfile
import os
from prometheus_client import start_http_server
from brd_master.analyze_pdf import analyze_pdf
from brd_master.remove_pages import remove_preceding_pages

def run():
    # Center the title and make it bigger using HTML and CSS
    st.markdown(
        "<h1>BRD Test Master</h1>",
        unsafe_allow_html=True
    )
    
    # Add columns for image and description
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(
            "./Images/Test_Case_Generator_LLM_Design.jpeg",  # Replace with your actual image path
            # caption="Demo Image",
            use_column_width=True
        )
    
    with col2:
        st.markdown("""
### About BRD Test Master

**BRD Test Master** is an advanced tool designed to automate the analysis of Business Requirement Documents (BRDs) and other complex PDFs. By converting BRDs into images and using cutting-edge Generative AI, it ensures accurate and comprehensive test case generation that captures both textual and visual requirements.

The tool addresses challenges in document processing, such as handling diverse BRD formats and extracting detailed content. Its AI-driven approach ensures precision in identifying key requirements, user-friendly interface allows for quick and efficient test case generation.
##### Key Features:
- **Standardized Document Handling**: Converts different BRD formats into images for consistent, accurate analysis.
- **Advanced Content Analysis**: Leverages AI to extract both text and images, ensuring complete coverage.
- **Automated Test Case Generation**: Quickly generates test cases to minimize manual effort and ensure accuracy.
- **User-Friendly Interface**: Easily upload BRDs and generate test cases without requiring technical expertise.

**BRD Test Master** simplifies document analysis, enhancing both accuracy and efficiency.

Simply upload your file below to get started!



""", unsafe_allow_html=True)

    
    # Add a separator
    st.markdown("---")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        start_page = st.number_input(
            "Start analyzing from page:", min_value=1, value=1, step=1
        )
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        
        if st.button("Analyze PDF"):
            status_placeholder = st.empty()
            status_placeholder.write("Analyzing the PDF...")
            
            temp_output_path = temp_file_path + "_modified.pdf"
            
            result_text = ""
            
            try:
                # Remove preceding pages
                remove_preceding_pages(temp_file_path, start_page, temp_output_path)
                
                with open(temp_output_path, "rb") as f:
                    pdf_bytes = f.read()
                
                results = asyncio.run(analyze_pdf(pdf_bytes))
                
                # Prepare results for download
                for page_num, result in results.items():
                    result_text += f"Page {page_num}:\n"
                    if result:
                        result_text += f"{result}\n\n"
                    else:
                        result_text += "Failed to analyze this page.\n\n"
                
                # Display download button before showing results
                st.download_button(
                    label="Download Results as .txt",
                    data=result_text,
                    file_name="analysis_results.txt",
                    mime="text/plain",
                )
                
                # Clear the "Analyzing the PDF..." message
                status_placeholder.empty()
                
                # Display the results as they come, after showing download option
                for page_num, result in results.items():
                    st.write(f"\nAnalysis result for Page {page_num}:")
                    if result:
                        st.write(result)
                    else:
                        st.write("Failed to analyze this page.")
            
            except Exception as e:
                status_placeholder.write(f"An error occurred: {e}")
            finally:
                temp_file.close()
                os.remove(temp_file_path)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)

if __name__ == "__main__":
    # Start Prometheus metrics server
    # start_http_server(8000)  # Exposes metrics on http://localhost:8000/metrics
    run()
