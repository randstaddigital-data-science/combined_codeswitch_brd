import boto3
import os
import json
import streamlit as st
import asyncio
import pandas as pd
import numpy as np

async def analyze_resume_with_claude(job_description, resume_text, similarity_percentage):
    """Asynchronous resume analysis with improved error handling and parsing."""
    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    prompt = f"""
    You are analyzing resumes for a job description. Given the job description and resume content below, perform the following:
    - Return matched percentage: {similarity_percentage:.2f}%.
    - Provide a reason for the match or mismatch.
    - Suggest skills to improve based on missing skills in the resume.
    - Identify any irrelevant experience or skills in the resume.
    - Provide a list of keywords that are matched between the resume and the job description.

    IMPORTANT: Your response MUST be a valid JSON object. 
    If you cannot generate a proper analysis, return this exact JSON:
    {{
      "Matched Percentage": "0.00%",
      "Reason": "Unable to perform detailed analysis.",
      "Skills To Improve": "N/A",
      "Irrelevant": "N/A",
      "Keywords": "N/A"
    }}

    Job Description:
    {job_description}

    Resume:
    {resume_text}
    """

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    })

    try:
        response = await asyncio.to_thread(
            bedrock_client.invoke_model,
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=body,
            contentType="application/json"
        )

        response_body = json.loads(response['body'].read().decode('utf-8'))
        content_text = response_body.get("content", [{}])[0].get("text", "{}")
        
        # Try to parse the JSON, with fallback
        try:
            return json.loads(content_text)
        except json.JSONDecodeError:
            st.warning(f"Invalid JSON response: {content_text}")
            return {
                "Matched Percentage": "0.00%",
                "Reason": "Unable to parse analysis response.",
                "Skills To Improve": "N/A",
                "Irrelevant": "N/A",
                "Keywords": "N/A"
            }
    except Exception as e:
        st.error(f"Claude analysis error: {str(e)}")
        return {
            "Matched Percentage": "0.00%",
            "Reason": f"Analysis failed: {str(e)}",
            "Skills To Improve": "N/A",
            "Irrelevant": "N/A",
            "Keywords": "N/A"
        }

def sync_process_resumes(job_description, resumes, distances, indices):
    """Synchronous wrapper for async resume processing with sorted results."""
    results = asyncio.run(_async_process_resumes(job_description, resumes, distances, indices))
    
    # Convert percentage to float for sorting
    sorted_results = sorted(
        results, 
        key=lambda x: float(x['Matched Percentage'].rstrip('%')), 
        reverse=True
    )
    
    # Add resume number starting from 1
    for i, result in enumerate(sorted_results, 1):
        result['Resume Number'] = i
    
    return sorted_results

async def _async_process_resumes(job_description, resumes, distances, indices):
    """Process all resumes concurrently with robust error handling."""
    results = []
    try:
        tasks = [
            analyze_resume_with_claude(
                job_description,
                resumes[idx]["resume_text"],
                round(max(0, 1 - np.sqrt(distances[0][rank])) * 100, 2)
            )
            for rank, idx in enumerate(indices[0])
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append({
                    "Resume Name": resumes[indices[0][idx]]["filename"],
                    "Matched Percentage": "0.00%",
                    "Reason": f"Processing error: {str(response)}",
                    "Skills To Improve": "N/A",
                    "Irrelevant": "N/A",
                    "Matched Keywords": "N/A"
                })
            else:
                # Ensure Matched Keywords is always a string
                keywords = response.get("Keywords", "No matched keywords.")
                if isinstance(keywords, list):
                    keywords = ", ".join(keywords)
                
                results.append({
                    "Resume Name": resumes[indices[0][idx]]["filename"],
                    "Matched Percentage": str(response.get("Matched Percentage", "0.00%")),
                    "Reason": str(response.get("Reason", "No reason provided.")),
                    "Skills To Improve": str(response.get("Skills To Improve", "No suggestions.")),
                    "Irrelevant": str(response.get("Irrelevant", "No irrelevant content.")),
                    "Matched Keywords": keywords
                })
        return results
    except Exception as e:
        st.error(f"Resume processing error: {str(e)}")
        return []

def display_detailed_analysis(results):
    """Display detailed analysis of resume matching with improved formatting and error handling."""
    st.subheader("🔍 Detailed Resume Analysis")
    
    if not results:
        st.warning("No resume analysis results available.")
        return
    
    # Create a DataFrame with consistent string types
    try:
        results_df = pd.DataFrame(results)
        
        # Optionally, select and reorder columns for better display
        display_columns = [
            "Resume Number",
            "Resume Name", 
            "Matched Percentage", 
            "Reason", 
            "Skills To Improve", 
            "Irrelevant", 
            "Matched Keywords"
        ]
        
        st.dataframe(results_df[display_columns], use_container_width=True)
    except Exception as e:
        st.error(f"Error creating results DataFrame: {e}")
    
    # Detailed view for each resume
    for result in results:
        st.markdown(f"""
        ### 📄 Resume {result['Resume Number']}: {result['Resume Name']}
        | **Category**            | **Details**                                                                 |
        |-------------------------|-----------------------------------------------------------------------------|
        | **Matched Percentage**  | :green[{result['Matched Percentage']}]                                     |
        | **Reason**              | {result['Reason']}                                                         |
        | **Skills To Improve**   | {result['Skills To Improve']}                                              |
        | **Irrelevant**          | {result['Irrelevant']}                                                     |
        | **Keywords**            | {result['Matched Keywords']}                                               |
        """, unsafe_allow_html=True)
        st.markdown("---")