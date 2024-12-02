### pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
### run above in myenv so this works

import streamlit as st
import os
from ImageRAG.rag_claude import RAGClaudeProcessor

# Initialize the RAGClaudeProcessor
def main():
    @st.cache_resource
    def get_processor():
        return RAGClaudeProcessor()
    processor = get_processor()
    st.title("PDF Analysis with RAG and Claude")
    # Ensure the 'uploads' directory exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        # Save the uploaded file
        pdf_path = os.path.join("uploads", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {uploaded_file.name} successfully uploaded!")
        # Index the PDF
        with st.spinner("Indexing PDF..."):
            processor.index_pdf(pdf_path)
        st.success("PDF indexed successfully!")
        # Text input for the query
        query = st.text_input("Enter your query about the PDF:")
        if st.button("Process Query"):
            if query:
                with st.spinner("Processing query..."):
                    result = processor.process_query(query)
                st.subheader("Result:")
                st.write(result)
            else:
                st.warning("Please enter a query.")
    # Clean up: remove uploaded files when the app is closed
    import atexit
    def cleanup():
        if os.path.exists("uploads"):
            for file in os.listdir("uploads"):
                os.remove(os.path.join("uploads", file))
    atexit.register(cleanup)

# Ensure this script can be imported as a module and run standalone
if __name__ == "__main__":
    main()
