import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from yellowbrick.cluster import KElbowVisualizer
import plotly.express as px
import os

def etl_rationalization_main():
    # Set page configuration (optional if set globally)
    # st.set_page_config(page_title="ETL Workflows Rationalization", layout="wide")
    st.title("ETL Workflows Rationalization")
    st.subheader("Upload your CSV files for clustering analysis.")

    # Helper functions
    def perform_pca(df):
        features_encoded = pd.get_dummies(df)
        features_standardized = StandardScaler().fit_transform(features_encoded)
        pca = PCA(n_components=2)
        features_pca = pca.fit_transform(features_standardized)
        return features_pca

    def plot_elbow_curve(X):

    # Define the directory and file path
        static_dir = "static/images"
        plot_path = os.path.join(static_dir, "elbow_curve_plot.png")
        
        # Ensure the directory exists
        os.makedirs(static_dir, exist_ok=True)

        # Create the elbow plot
        model = KMeans(random_state=39)
        visualizer = KElbowVisualizer(model, k=(2, 15), timings=False)
        visualizer.fit(X)
        visualizer.show(outpath=plot_path)  # Save the plot to the specified path

        return plot_path, visualizer.elbow_value_

    def kmeans_clustering(df, features_pca, no_clusters):
        kmeans = KMeans(n_clusters=no_clusters, random_state=39)
        df['Cluster ID'] = kmeans.fit_predict(features_pca)
        silhouette_avg = silhouette_score(features_pca, df['Cluster ID'])
        return df, silhouette_avg

    def cluster_plot(df, features_pca):
        fig = px.scatter(
            x=features_pca[:, 0],
            y=features_pca[:, 1],
            color=df['Cluster ID'].astype(str),
            title="Cluster Visualization",
            labels={'x': 'PC1', 'y': 'PC2'},
        )
        st.plotly_chart(fig)

    # Initialize session state
    if "clustered_df" not in st.session_state:
        st.session_state["clustered_df"] = None
    if "features_pca" not in st.session_state:
        st.session_state["features_pca"] = None
    if "optimal_clusters" not in st.session_state:
        st.session_state["optimal_clusters"] = None
    if "silhouette_avg" not in st.session_state:
        st.session_state["silhouette_avg"] = None

    uploaded_files = st.file_uploader(
        "Choose CSV Files", type=["csv"], accept_multiple_files=True
    )

    if uploaded_files:
        dfs = [pd.read_csv(file) for file in uploaded_files]
        combined_df = pd.concat(dfs, ignore_index=True)
        st.write("Uploaded Data", combined_df.head())

        st.subheader("Clustering Analysis")
        if st.button("Perform Clustering"):
            try:
                features_pca = perform_pca(combined_df)
                elbow_plot_path, optimal_clusters = plot_elbow_curve(features_pca)
                st.session_state["optimal_clusters"] = optimal_clusters
                st.session_state["features_pca"] = features_pca
                clustered_df, silhouette_avg = kmeans_clustering(combined_df, features_pca, optimal_clusters)
                st.session_state["clustered_df"] = clustered_df
                st.session_state["silhouette_avg"] = silhouette_avg
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.session_state["clustered_df"] is not None:
        st.subheader("Clustering Analysis Results")
        st.image("static/images/elbow_curve_plot.png", caption="Elbow Curve")
        st.write(f"**Optimal Number of Clusters:** {st.session_state['optimal_clusters']}")
        st.write(f"**Silhouette Score:** {st.session_state['silhouette_avg']:.2f}")
        st.write("Clustered Data")
        st.dataframe(st.session_state["clustered_df"])
        st.subheader("Cluster Visualization")
        cluster_plot(st.session_state["clustered_df"], st.session_state["features_pca"])

        st.subheader("Filter Clustered Data")
        cluster_ids = sorted(st.session_state["clustered_df"]['Cluster ID'].unique())
        selected_cluster = st.selectbox("Filter by Cluster ID", options=["All"] + list(cluster_ids))

        if selected_cluster != "All":
            filtered_df = st.session_state["clustered_df"][
                st.session_state["clustered_df"]['Cluster ID'] == selected_cluster
            ]
        else:
            filtered_df = st.session_state["clustered_df"]

        st.write(f"Filtered Data (Cluster ID: {selected_cluster})")
        st.dataframe(filtered_df)

        output_path = "clustered_workflows.csv"
        st.session_state["clustered_df"].to_csv(output_path, index=False)
        st.download_button(
            "Download Clustered Data",
            data=open(output_path, "rb").read(),
            file_name="clustered_workflows.csv",
            mime="text/csv",
        )
