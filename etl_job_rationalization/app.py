from flask import Flask, render_template, send_file, request
import pandas as pd
import ast
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

def transform_slash_features(value):
    if '/' in value:
        split_parts = value.split('/')
        transformed_value = split_parts[-2]
    else:
        transformed_value = value
    return transformed_value

def remove_quotations(value):
    return value.strip('"')

def extract_value(value):
    try:
        if isinstance(value, str):
            value = ast.literal_eval(value)

        if isinstance(value, list):
            return [{f"{i}_{k}": v for k, v in item.items()} for i, item in enumerate(value) if isinstance(item, dict)]
        elif isinstance(value, dict):
            return [{k: v} for k, v in value.items()]
    except Exception as e:
        print(f"Warning: Error processing value: {value},Exception {e}")
        pass

def transform_features(raw_data, features_to_transform):
    transformed_data = raw_data.copy()

    for feature in features_to_transform:
        new_values = raw_data[feature].apply(extract_value)

        for i, item in enumerate(new_values.iloc[0]):
            for key, value in item.items():
                transformed_data[f"{feature}_{key}"] = new_values.apply(lambda x: x[i][key] if isinstance(x, list) and len(x) > i and key in x[i] else None)
    transformed_data = transformed_data.drop(features_to_transform, axis=1)
    return transformed_data

def columns_similar_check(data, columns_to_check):
    res = all(data[column].equals(data[columns_to_check[0]]) for column in columns_to_check)
    if res:
        print(f"Same Values: {columns_to_check}")
    else:
        print("Not Same Values")

def columns_same_value(data, columns_to_check):
    non_similar_value_columns = [column for column in columns_to_check if data[column].nunique() != 1]
    if not non_similar_value_columns:
        print(f"One Value: {columns_to_check}")
    else:
        print(f"Not One Value: {non_similar_value_columns}")

def combine_similar_rows_columns(transformed_data, similar_rows_columns, drop_columns):
    combined_columns = '__'.join(similar_rows_columns)
    transformed_data[combined_columns] = transformed_data[similar_rows_columns[0]]
    transformed_data.drop(similar_rows_columns, axis=1, inplace=True)

def drop_columns(transformed_data, columns_to_drop):
    transformed_data.drop(columns=columns_to_drop, axis=1, inplace=True)

def perform_eda(raw_data):
    raw_data['FlatFileSource_ConnectionName'] = raw_data['FlatFileSource_ConnectionName'].apply(transform_slash_features)
    raw_data['FlatFileDestination_ConnectionName'] = raw_data['FlatFileDestination_ConnectionName'].apply(transform_slash_features)

    features_to_transform = ['FlatFileSource_Property', 'OleDbSource_Property', 'MergeJoinTransform_JoinInput',
                             'MergeJoinTransform_JoinCondition', 'LookupTransform_LookupOutputColumn',
                             'LookupTransform_LookupSource', 'LookupTransform_LookupCondition',
                             'OleDbDestination_Property', 'FlatFileDestination_Property']
    transformed_data = transform_features(raw_data, features_to_transform)

    transformed_data['FlatFileSource_Property_1_#text'] = transformed_data['FlatFileSource_Property_1_#text'].apply(remove_quotations)
    transformed_data['FlatFileDestination_Property_1_#text'] = transformed_data['FlatFileDestination_Property_1_#text'].apply(remove_quotations)

    # Combine and drop similar rows and columns
    similar_rows_columns_1 = ['FlatFileSource_Name', 'FlatFileSource_ConnectionName', 'OleDbSource_Name',
                              'OleDbDestination_Name', 'FlatFileDestination_Name', 'FlatFileDestination_ConnectionName',
                              'LookupTransform_LookupSource_@Name']
    combine_similar_rows_columns(transformed_data, similar_rows_columns_1, similar_rows_columns_1)

    similar_rows_columns_2 = ['MergeJoinTransform_JoinInput_0_@SourceName', 'OleDbDestination_Property_0_@Name']
    combine_similar_rows_columns(transformed_data, similar_rows_columns_2, similar_rows_columns_2)

    similar_rows_columns_3 = ['MergeJoinTransform_JoinInput_1_@SourceName', 'OleDbDestination_Property_1_@Name']
    combine_similar_rows_columns(transformed_data, similar_rows_columns_3, similar_rows_columns_3)

    similar_rows_columns_4 = ['OleDbDestination_Property_0_#text', 'OleDbDestination_Property_1_#text']
    combine_similar_rows_columns(transformed_data, similar_rows_columns_4, similar_rows_columns_4)

    # Drop specific columns
    one_value_columns = ['FlatFileSource_DataType', 'OleDbSource_ConnectionName', 'OleDbSource_ReadSolids',
                         'LookupTransform_InputName', 'LookupTransform_DestinationName', 'OleDbDestination_ConnectionName',
                         'FlatFileDestination_DataType', 'FlatFileDestination_Format',
                         'FlatFileSource_Property_0_@Name', 'OleDbSource_Property_@Name',
                         'MergeJoinTransform_JoinInput_0_@OutputName', 'MergeJoinTransform_JoinInput_1_@OutputName',
                         'LookupTransform_LookupOutputColumn_@ColumnName', 'LookupTransform_LookupOutputColumn_@DataType',
                         'LookupTransform_LookupSource_@ConnectionName', 'FlatFileDestination_Property_0_@Name',
                         'FlatFileDestination_Property_1_@Name', 'FlatFileDestination_Property_1_#text']
    drop_columns(transformed_data, one_value_columns)
    # Drop irrelevant columns
    irrelevant_columns = ['FlatFileSource_Format', 'FlatFileSource_Property_1_#text', 'MergeJoinTransform_Name',
                          'OleDbSource_Property_#text', 'FlatFileSource_ColumnDelimiter',
                          'LookupTransform_Name', 'ExpressionTransform_Name', 'FlatFileSource_Property_0_#text',
                          'FlatFileSource_Property_1_@Name', 'FlatFileDestination_Property_0_#text']
    drop_columns(transformed_data, irrelevant_columns)

    return transformed_data


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


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', show_elbow_curve=False, show_clusters=False)

@app.route('/get_clusters', methods=['POST'])
def get_clusters():
    try:

        files = request.files.getlist('csv_files')
        raw_df = combine_files(files)
        df = perform_eda(raw_df)
        columns_to_display = ['Cluster ID', 'MergeJoinTransform_JoinType', 'ExpressionTransform_InputName', 'xml_filename']

        df_clustered, sil_score, no_clusters, wcss_approx_score = pca_clustering(df)
        #clustering_quality = lambda x: "Good" if x > 0.4 else "Overlap" if 0 <= x <= 0.4 else "Poor"
        clustering_quality = lambda x: f"{x * 100:.2f}%"


        clustered_file_path = save_clustered_file(df_clustered)


        return render_template(
            'index.html',
            show_elbow_curve=False,
            show_clusters=True,
            clustered_file_path=clustered_file_path,
            num_reports=df_clustered.shape[0],
            num_clusters=no_clusters,
            cluster_quality=clustering_quality(sil_score),
            distortion_score=wcss_approx_score,
            clustered_rows=df_clustered.to_dict(orient='records'),  # Convert DataFrame to dict
            cluster_ids=df_clustered['Cluster ID'].astype(str).unique(),
            columns=columns_to_display
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/download/<path:clustered_file_path>')
def download_clustered_file(clustered_file_path):
    return send_file(clustered_file_path, download_name="clustered_workflows.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)