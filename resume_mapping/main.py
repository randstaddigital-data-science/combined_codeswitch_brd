import os
import streamlit as st
import numpy as np
import traceback
from dotenv import load_dotenv

# Import custom modules
from resume_mapping.embeddings import get_bedrock_client, get_titan_embedding
from resume_mapping.resume_analysis import sync_process_resumes, display_detailed_analysis
from resume_mapping.utils import parse_pdf_to_text, create_faiss_index

# Load environment variables
load_dotenv()

# Main Function for Resume Mapping
def resume_mapping():
    # Set a title for this specific feature
    st.header("🔍 Enhanced Resume Matcher with AWS Bedrock")

    # Input: Job Description
    st.subheader("Job Description")
    job_description = st.text_area("Paste the Job Description Below", height=200)

    # Input: Upload Resumes
    st.subheader("Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF Files", accept_multiple_files=True, type=['pdf']
    )

    if st.button("Analyze Resumes"):
        # Validation
        if not job_description or not uploaded_files:
            st.error("Please provide both a job description and upload resumes.")
            return

        try:
            # Initialize Bedrock Client
            st.info("Initializing AWS Bedrock Client...")
            bedrock_client = get_bedrock_client()

            # Generate Job Description Embedding
            st.info("Generating embeddings for the job description...")
            job_embedding = get_titan_embedding(job_description, bedrock_client)
            if job_embedding is None:
                st.error("Failed to generate embedding for the job description.")
                return

            # Process Resumes
            resumes = []
            resume_embeddings = []

            st.info("Processing resumes and generating embeddings...")
            for uploaded_file in uploaded_files:
                resume_text = parse_pdf_to_text(uploaded_file)

                if not resume_text:
                    st.warning(f"No text found in {uploaded_file.name}. Skipping...")
                    continue

                embedding = get_titan_embedding(resume_text, bedrock_client)
                if embedding is None:
                    st.warning(f"Skipping {uploaded_file.name} due to embedding failure.")
                    continue

                resumes.append({"filename": uploaded_file.name, "resume_text": resume_text})
                resume_embeddings.append(embedding)

            if not resumes:
                st.error("No valid resumes processed. Please check your inputs.")
                return

            # Build FAISS Index and Search
            st.info("Building FAISS index and performing similarity search...")
            index = create_faiss_index(np.array(resume_embeddings, dtype='float32'))
            distances, indices = index.search(np.array([job_embedding], dtype='float32'), len(resumes))

            # Analyze Results
            st.info("Analyzing resumes...")
            results = sync_process_resumes(job_description, resumes, distances, indices)
            display_detailed_analysis(results)

        except Exception as e:
            st.error("An unexpected error occurred while processing resumes.")
            st.error(str(e))
            st.error(traceback.format_exc())
