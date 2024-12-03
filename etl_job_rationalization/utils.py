import os
import pandas as pd

def combine_files(file):
    if not os.path.exists('data/csv'):
        os.makedirs('data/csv')
    for file in file:
        file_path = os.path.join("data/csv/", file.filename)
        file.save(file_path)
        df = pd.read_csv(file_path)
    return df

def save_uploaded_file(df):
    try:
        df.to_csv("data/combined_df.csv")
        return df

    except Exception as e:
        raise Exception(f"An error occurred while saving or reading the file: {str(e)}")

def save_clustered_file(df):
    try:
        clustered_file_path = os.path.join("data/", "clustered_workflows.csv")
        df.to_csv(clustered_file_path, index=False)
        return clustered_file_path

    except Exception as e:
        raise Exception(f"An error occurred while saving the clustered file: {str(e)}")