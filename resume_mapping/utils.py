import streamlit as st
from PyPDF2 import PdfReader
import faiss
import numpy as np

def parse_pdf_to_text(pdf_file):
    """Extract text from a PDF with error handling."""
    try:
        reader = PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text.strip()
    except Exception as e:
        st.warning(f"PDF parsing error for {pdf_file.name}: {str(e)}")
        return ""

def create_faiss_index(embeddings):
    """Create FAISS index for embeddings with error handling."""
    try:
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        return index
    except Exception as e:
        st.error(f"FAISS index creation error: {str(e)}")
        st.stop()