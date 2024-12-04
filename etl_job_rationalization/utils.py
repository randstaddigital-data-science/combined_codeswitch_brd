# import os
# import pandas as pd

# def combine_files(file):
#     if not os.path.exists('data/csv'):
#         os.makedirs('data/csv')
#     for file in file:
#         file_path = os.path.join("data/csv/", file.filename)
#         file.save(file_path)
#         df = pd.read_csv(file_path)
#     return df

# def save_uploaded_file(df):
#     try:
#         df.to_csv("data/combined_df.csv")
#         return df

#     except Exception as e:
#         raise Exception(f"An error occurred while saving or reading the file: {str(e)}")

# def save_clustered_file(df):
#     try:
#         clustered_file_path = os.path.join("data/", "clustered_workflows.csv")
#         df.to_csv(clustered_file_path, index=False)
#         return clustered_file_path

#     except Exception as e:
#         raise Exception(f"An error occurred while saving the clustered file: {str(e)}")


import os
import pandas as pd

def combine_files(uploaded_files):
    """
    Combine uploaded files into a single DataFrame.
    """
    data_frames = []
    for file in uploaded_files:
        df = pd.read_csv(file)
        data_frames.append(df)
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df

def save_uploaded_file(df, output_path="data/combined_df.csv"):
    """
    Save uploaded DataFrame to a CSV file.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path
    except Exception as e:
        raise Exception(f"An error occurred while saving the file: {str(e)}")

def save_clustered_file(df, output_path="data/clustered_workflows.csv"):
    """
    Save clustered DataFrame to a CSV file.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path
    except Exception as e:
        raise Exception(f"An error occurred while saving the clustered file: {str(e)}")
