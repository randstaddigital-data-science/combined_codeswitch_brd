import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os
from yellowbrick.cluster import KElbowVisualizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
# from pycaret.clustering import *
matplotlib.use('Agg')

def hopkins_statistic(X, n_neighbors=10):
    m, d = X.shape

    rand_points = np.random.rand(m, d)
    nn_data = NearestNeighbors(n_neighbors=n_neighbors)
    nn_rand = NearestNeighbors(n_neighbors=n_neighbors)

    nn_data.fit(X)
    nn_rand.fit(rand_points)

    data_distances, _ = nn_data.kneighbors(X, n_neighbors=n_neighbors)
    rand_distances, _ = nn_rand.kneighbors(rand_points, n_neighbors=n_neighbors)

    numerator = np.sum(data_distances, axis=1)
    denominator = np.sum(data_distances + rand_distances, axis=1)

    hopkins_stat = np.mean(numerator / denominator)
    return hopkins_stat

def visualize_clusters_tsne(df, jaccard_matrix, num_clusters=6):
    tsne = TSNE(n_components=2, random_state=42)
    tsne_result = tsne.fit_transform(jaccard_matrix)
    tsne_plot_path = "static/images/tsne_plot.png"

    plt.figure(figsize=(10, 6))

    for cluster in range(num_clusters):
        cluster_points = tsne_result[df['Cluster ID'] == cluster, :]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {cluster + 1}', alpha=0.5)

    plt.title('Cluster Visualization')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.legend()
    plt.savefig(tsne_plot_path)

    return tsne_plot_path

# def cluster_plot(df, features_pca):
#     plt.figure(figsize=(10, 6))
#     sns.scatterplot(x=features_pca[:, 0], y=features_pca[:, 1], hue=df['Cluster ID'], palette='muted')
#     plt.title('2D Cluster Plot')
#     plot_path = "static/images/cluster_plot.png"
#     plt.savefig(plot_path)
#     return plot_path

def cluster_plot(df, features_pca):
    df['Cluster ID'] = df['Cluster ID'].astype('category')
    hover_template = ["%%{customdata[%d]}" % i for i in range(len(df.columns))]
    fig = px.scatter(df, x=features_pca[:, 0], y=features_pca[:, 1], color='Cluster ID', custom_data=df.columns)

    fig.update_layout(
        width=1600,  
        height=700,
        plot_bgcolor='white',
        xaxis=dict(title_text=''),
        yaxis=dict(title_text='')
    )
    
    fig.update_traces(hovertemplate="<br>".join(hover_template))

    plot_path = "static/images/cluster_plot.html"
    fig.write_html(plot_path)
    return plot_path


def plot_elbow_curve(X, components_range=(1, 30)):
    model = KMeans(n_init=30)
    visualizer = KElbowVisualizer(model, k=(1, 30))
    visualizer.fit(X)
    visualizer.show(outpath="static/images/elbow_curve_plot.png")
    no_clusters = visualizer.elbow_value_
    wcss_approx_score = visualizer.elbow_score_
    return no_clusters, wcss_approx_score

def similarity_matrix(df):
    data = df[['Tables', 'Columns']].values.tolist()

    transformed_data = [set(row[0]).union(set((feature['Name'], feature['Type']) for feature in row[1])) for row in data]

    num_rows = len(transformed_data)
    jaccard_matrix = np.zeros((num_rows, num_rows))

    for i in range(num_rows):
        for j in range(i + 1, num_rows):
            intersection_size = len(transformed_data[i].intersection(transformed_data[j]))
            union_size = len(transformed_data[i].union(transformed_data[j]))
            jaccard_matrix[i, j] = jaccard_matrix[j, i] = intersection_size / union_size
    return jaccard_matrix

def perform_pca(df):
    features = df.copy(deep=True)
    features_encoded = pd.get_dummies(df)
    features_standardized = StandardScaler().fit_transform(features_encoded)
    pca = PCA(n_components=2)
    features_pca = pca.fit_transform(features_standardized)
    return features_pca

def kmeans_clustering(df,jaccard_matrix,no_clusters):
    num_clusters = no_clusters
    kmeans = KMeans(n_clusters=num_clusters, random_state=39)
    df['Cluster ID'] = kmeans.fit_predict(jaccard_matrix)
    silhouette_avg = silhouette_score(jaccard_matrix, df['Cluster ID'])
    return df,silhouette_avg

def perform_clustering(df):
    jaccard_matrix = similarity_matrix(df)
    hopkins_val = hopkins_statistic(jaccard_matrix)
    no_clusters, wcss_approx_score = plot_elbow_curve(jaccard_matrix)
    results_df,sil_score = kmeans_clustering(df,jaccard_matrix)
    tsne_plot_path = visualize_clusters_tsne(results_df,jaccard_matrix)
    return results_df, sil_score, no_clusters, wcss_approx_score

def pca_clustering(df):
    features_pca = perform_pca(df)
    # cluster = setup(features_pca, session_id=34)
    no_clusters, wcss_approx_score = plot_elbow_curve(features_pca)
    # model_kmeans = create_model('kmeans', num_clusters=no_clusters)
    # metrics = pull()
    # results = assign_model(model_kmeans)
    # sil_score = metrics['Silhouette'][0]
    results_df,sil_score = kmeans_clustering(df,features_pca,no_clusters)
    # df_with_cluster = pd.merge(df, results[['Cluster']], left_index=True, right_index=True, how='left')
    results_df.insert(0, results_df.columns[-1], results_df.pop(results_df.columns[-1]))
    cluster_plot_path = cluster_plot(results_df, features_pca)
    return results_df, sil_score, no_clusters, wcss_approx_score

def actual_clusters():
    file_path = "data/Actual_Results_for_Cluster.xlsx"
    actual_df = pd.read_excel(file_path)
    return actual_df

def merge_results(results_df, actual_df):
    merged_df = pd.merge(results_df[['Report_Name', 'Cluster ID']], actual_df, left_on='Report_Name', right_on='Report', how='outer')
    merged_df.drop(columns=['Report'], axis=1, inplace=True)
    compare_df_path = os.path.join("data/", "Compare_Clusters.csv")
    merged_df.to_csv(compare_df_path, index=False)
    return compare_df_path