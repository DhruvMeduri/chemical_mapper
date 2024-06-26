from flask import render_template,request, url_for, jsonify, redirect, Response, send_from_directory
from app import app
from app import APP_STATIC
from app import APP_ROOT
from types import SimpleNamespace
import linecache
import json
import itertools
import csv
import numpy as np
import pandas as pd
import os
import re
from .kmapper import KeplerMapper
from .cover import Cover
#from .kmapper_parallel import KeplerMapper, Cover
from sklearn import cluster
import networkx as nx
import sklearn
# from sklearn.linear_model import LinearRegression
try:
    import statsmodels.api as sm
except:
    print('No statsmodel found')
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KernelDensity
from scipy.spatial import distance
from sklearn.cluster import KMeans
import importlib
# from .enhanced_mapper.cover import Cover, UniformCover
from .enhanced_mapper.cover import Cover as enhanced_Cover
from .enhanced_mapper.mapper import generate_mapper_graph
from .enhanced_mapper.AdaptiveCover import BIC_Cover_Centroid, construct_cover_from_xmeans, mapper_xmeans_centroid
from app import draw_structure


@app.route('/')
@app.route('/MapperInteractive_new')
def index():
    return render_template('index.html')

@app.route('/data_process', methods=['POST','GET'])
def process_text_data():
    '''
    Check for:
    1. Missing value
    2. Non-numerical elements in numerical cols
    3. If cols are non-numerical, check if cols are categorical
    '''
    text_data = request.get_data().decode('utf-8').splitlines()
    cols = text_data[0].split(',')
    cols = [col for col in cols if col!=""] # not include the col is there is no colname
    mat = [n.split(',') for n in text_data] # csv: if an element is empty, it will be "".
    newdf1 = np.array(mat)[1:]
    rows2delete = np.array([])
    cols2delete = []
    
    # ### Delete missing values ###
    for i in range(len(cols)):
        col = newdf1[:,i]
        if np.sum(col == "") >= 0.2*len(newdf1): # if more than 20% elements in this column are empty, delete the whole column
            cols2delete.append(i)
        else:
            rows2delete = np.concatenate((rows2delete, np.where(col=="")[0]))
    rows2delete = np.unique(rows2delete).astype("int")
    newdf2 = np.delete(np.delete(newdf1, cols2delete, axis=1), rows2delete, axis=0)
    cols = [cols[i] for i in range(len(cols)) if i not in cols2delete]

    ### check if numerical cols ###
    cols_numerical_idx = []
    cols_categorical_idx = []
    cols_others_idx = []
    rows2delete = np.array([])
    r1 = re.compile(r'^-?\d+(?:\.\d+)?$')
    r2 = re.compile(r'[+\-]?[^A-Za-z]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)') # scientific notation
    vmatch = np.vectorize(lambda x:bool(r1.match(x) or r2.match(x)))
    for i in range(len(cols)):
        col = newdf2[:,i]
        col_match = vmatch(col)
        if np.sum(col_match) >= 0.8*len(newdf1): # if more than 90% elements can be converted to float, keep the col, and delete rows that cannot be convert to float:
            cols_numerical_idx.append(i)
            rows2delete = np.concatenate((rows2delete, np.where(col_match==False)[0]))
        else: 
            ### check if categorical cols### 
            if len(np.unique(col)) <= 200: # if less than 10 different values: categorical
                cols_categorical_idx.append(i)
            else:
                cols_others_idx.append(i)
    newdf3 = newdf2[:, cols_numerical_idx+cols_categorical_idx+cols_others_idx]
    rows2delete = rows2delete.astype(int)
    newdf3 = np.delete(newdf3, rows2delete, axis=0)
    newdf3_cols = [cols[idx] for idx in cols_numerical_idx+cols_categorical_idx+cols_others_idx]
    newdf3 = pd.DataFrame(newdf3)
    newdf3.columns = newdf3_cols
    # write the data frame
    newdf3.to_csv(APP_STATIC+"/uploads/processed_data.csv", index=False) 
    newdf3.to_csv("./CLI_examples/processed_data.csv", index=False) 
    # write the cols info
    cols_numerical = [cols[idx] for idx in cols_numerical_idx]
    cols_categorical = [cols[idx] for idx in cols_categorical_idx]
    cols_others = [cols[idx] for idx in cols_others_idx]
    cols_dict = {'cols_numerical':cols_numerical, 'cols_categorical':cols_categorical, 'cols_others':cols_others}
    with open(APP_STATIC+"/uploads/cols_info.json", 'w') as f:
        f.write(json.dumps(cols_dict, indent=4))
    return jsonify(columns=cols_numerical, categorical_columns=cols_categorical, other_columns=cols_others)

# @app.route('/data_process', methods=['POST','GET'])
# def load_data():
#     filename = request.get_data().decode('utf-8').splitlines()[0]
#     print(filename)
#     df = pd.read_csv(APP_STATIC+"/uploads/"+filename)
#     cols = list(df.columns)
#     df_0 = df.iloc[0,:]
#     cols_numerical_idx = []
#     cols_categorical_idx = []
#     cols_others_idx = []
#     rows2delete = np.array([])
#     for i in range(len(cols)):
#         c = df_0.iloc[i]
#         try:
#             float(c)
#             cols_numerical_idx.append(i)
#         except ValueError:
#             cols_categorical_idx.append(i)
#         # if isinstance(c,int) or isinstance(c,float):
#             # cols_numerical_idx.append(i)
#         # else:
#             # cols_categorical_idx.append(i)
#     df.to_csv(APP_STATIC+"/uploads/processed_data.csv", index=False) 
#     cols_numerical = [cols[idx] for idx in cols_numerical_idx]
#     cols_categorical = [cols[idx] for idx in cols_categorical_idx]
#     cols_others = [cols[idx] for idx in cols_others_idx]
#     cols_dict = {'cols_numerical':cols_numerical, 'cols_categorical':cols_categorical, 'cols_others':cols_others}
#     print(cols_dict)
#     with open(APP_STATIC+"/uploads/cols_info.json", 'w') as f:
#         f.write(json.dumps(cols_dict, indent=4))
#     return jsonify(columns=cols_numerical, categorical_columns=cols_categorical, other_columns=cols_others)

@app.route('/mapper_data_process', methods=['POST','GET'])
def load_mapper_data():
    filename = request.get_data().decode('utf-8').splitlines()[0]
    with open(filename) as f:
        mapper_graph = json.load(f)
    #mapper_graph["links"] = mapper_graph["edges"]
    #del mapper_graph["edges"]

    #obj.nodes = mapper_graph["nodes"]
    #obj.links = mapper_graph["edges"]
    #mapper_graph_new = _parse_result(mapper_graph, lens_dict={}, data_array=[], if_cli=True)
    #print("DEBUG: ",mapper_graph_new)

    #mapper_graph_new = _parse_enhanced_graph(obj, data_array=[], if_cli=True)
    #connected_components = compute_cc(mapper_graph_new)

    #return jsonify(mapper=mapper_graph_new, connected_components=connected_components,categorical_cols = ['label','scaffold'])
    return jsonify(mapper_graph)
    # return jsonify(mapper=mapper_graph_new, connected_components=connected_components)

@app.route('/mapper_loader', methods=['POST','GET'])
def get_graph():
    mapper_data = request.form.get('data')
    mapper_data = json.loads(mapper_data)
    selected_cols = mapper_data['cols']
    all_cols = mapper_data['all_cols'] # all numerical cols
    categorical_cols = mapper_data['categorical_cols']
    data = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    data_categorical = data[categorical_cols]
    data = data[all_cols]

    # data = data[selected_cols].astype("float")
    config = mapper_data["config"]
    norm_type = config["norm_type"]
    clustering_alg = config["clustering_alg"]
    clustering_alg_params = config["clustering_alg_params"]
    # eps = config["eps"]
    # min_samples = config["min_samples"]

    #### TODO: update filter_parameters ####
    filter_parameters = config

    # filter functions
    filter_function = config["filter"]
    if len(filter_function) == 1:
        interval = int(config["interval1"])
        overlap = float(config["overlap1"]) / 100
    elif len(filter_function) == 2:
        interval = [int(config["interval1"]), int(config["interval2"])]
        overlap = [float(config["overlap1"])/100, float(config["overlap2"])/100]
    print(interval, overlap)
    # TODO: fix normalization (only point cloud column needs to be modified?)
    # normalization
    if norm_type == "none":
        pass
    elif norm_type == "0-1": # axis=0, min-max norm for each column
        scaler = MinMaxScaler()
        data = scaler.fit_transform(data)
    else:
        data = sklearn.preprocessing.normalize(data, norm=norm_type, axis=0, copy=False, return_norm=False)
    data = pd.DataFrame(data, columns = all_cols)
    mapper_result = run_mapper(data, selected_cols, interval, overlap, clustering_alg, clustering_alg_params, filter_function, filter_parameters)
    if len(categorical_cols) > 0:
        for node in mapper_result['nodes']:
            vertices = node['vertices']
            data_categorical_i = data_categorical.iloc[vertices]
            node['categorical_cols_summary'] = {}
            for col in categorical_cols:
                node['categorical_cols_summary'][col] = data_categorical_i[col].value_counts().to_dict()
    connected_components = compute_cc(mapper_result)
    print(mapper_result)
    return jsonify(mapper=mapper_result, connected_components=connected_components)

@app.route('/enhanced_mapper_loader', methods=['POST','GET'])
def get_enhanced_graph():
    mapper_data = request.form.get('data')
    mapper_data = json.loads(mapper_data)
    selected_cols = mapper_data['cols']
    all_cols = mapper_data['all_cols'] # all numerical cols
    categorical_cols = mapper_data['categorical_cols']
    data = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    data_categorical = data[categorical_cols]
    data = data[all_cols]

    config = mapper_data["config"]
    norm_type = config["norm_type"]
    clustering_alg = config["clustering_alg"]
    clustering_alg_params = config["clustering_alg_params"]
    filter_parameters = config
    enhanced_parameters = mapper_data["enhanced_config"]

    filter_function = config["filter"]
    if len(filter_function) == 1:
        interval = int(config["interval1"])
        overlap = float(config["overlap1"]) / 100
    elif len(filter_function) == 2:
        interval = [int(config["interval1"]), int(config["interval2"])]
        overlap = [float(config["overlap1"])/100, float(config["overlap2"])/100]

    if norm_type == "none":
        pass
    elif norm_type == "0-1": # axis=0, min-max norm for each column
        scaler = MinMaxScaler()
        data = scaler.fit_transform(data)
    else:
        data = sklearn.preprocessing.normalize(data, norm=norm_type, axis=0, copy=False, return_norm=False)
    data = pd.DataFrame(data, columns = all_cols)

    mapper = KeplerMapper()
    if len(selected_cols) == 1:
        data_new = np.array(data[selected_cols[0]]).reshape(-1,1)
    else:
        data_new = np.array(data[selected_cols])

    if len(filter_function) == 1:
        f = filter_function[0]
        if f in data.columns:
            lens = data[f]
        else:
            lens = compute_lens(f, data_new, mapper, filter_parameters)
        
    elif len(filter_function) == 2:
        lens = []
        for f in filter_function:
            if f in data.columns:
                lens_f = np.array(data[f]).reshape(-1,1)
            else:
                lens_f = compute_lens(f, data_new, mapper, filter_parameters)
            lens.append(lens_f)
        lens = np.concatenate((lens[0], lens[1]), axis=1)

    if clustering_alg == "DBSCAN":
        clusterer = cluster.DBSCAN(eps=float(clustering_alg_params["eps"]), min_samples=int(clustering_alg_params["min_samples"]))
    elif clustering_alg == "Agglomerative Clustering":
        clusterer = cluster.AgglomerativeClustering(n_clusters=None, linkage=clustering_alg_params["linkage"], distance_threshold=float(clustering_alg_params["dist"]))
    elif clustering_alg == "Mean Shift":
        clusterer = cluster.MeanShift(bandwidth=float(clustering_alg_params["bandwidth"]))

    iterations = enhanced_parameters['max_iter']
    max_intervals = 100
    delta = enhanced_parameters['delta']
    BIC = enhanced_parameters['bic']
    method = enhanced_parameters['method'] # method can be: BFS, DFS, randomized

    print("iterations", iterations)
    print("delta", delta)
    print("method", method)

    cov = enhanced_Cover(interval, overlap)
    g_classic = generate_mapper_graph(data_new, lens, cov, clusterer, refit_cover = True)

    multipass_cover = mapper_xmeans_centroid(data_new, lens, enhanced_Cover(interval, overlap), clusterer, iterations, max_intervals, BIC=BIC, delta=delta, method=method)

    g_multipass = generate_mapper_graph(data_new, lens, multipass_cover, clusterer, refit_cover=False)
    mapper_result = _parse_enhanced_graph(g_multipass, data)
    connected_components = compute_cc(mapper_result)

    if len(categorical_cols) > 0:
        for node in mapper_result['nodes']:
            vertices = node['vertices']
            data_categorical_i = data_categorical.iloc[vertices]
            node['categorical_cols_summary'] = {}
            for col in categorical_cols:
                node['categorical_cols_summary'][col] = data_categorical_i[col].value_counts().to_dict()
    print("classic",cov.intervals)
    print("xmeans",multipass_cover.intervals)
    return jsonify(mapper=mapper_result, connected_components=connected_components, classic_cover=cov.intervals.tolist(), adaptive_cover=multipass_cover.intervals.tolist())

def _parse_enhanced_graph(graph, data_array=[], if_cli=False):
    if len(data_array)>0:
        col_names = data_array.columns
        data_array = np.array(data_array)
    data = {"nodes":[], "links":[]}

    nodes_detail = {}
    name2id = {}
    i = 1
    for node in graph.nodes:
        node_name = get_node_id(node)
        name2id[node_name] = i
        cluster = node.members.tolist()
        nodes_detail[i] = cluster
        if len(data_array)>0:
            cluster_data = data_array[cluster]
            cluster_avg = np.mean(cluster_data, axis=0)
            cluster_avg_dict = {}
            for j in range(len(col_names)):
                cluster_avg_dict[col_names[j]] = cluster_avg[j]
            data['nodes'].append({
                "id": str(i),
                "size": len(cluster),
                "avgs": cluster_avg_dict,
                "vertices": cluster
                })    
        else:
            if if_cli:
                if "avgs" in graph['nodes'].keys():
                    data['nodes'].append({
                        "id": str(i),
                        "id_orignal": key,
                        "size": len(graph['nodes'][key]),
                        "vertices": cluster,
                        "categorical_cols_summary": graph['nodes'][key]["categorical_cols_summary"],
                        "avgs":graph['nodes'][key]["avgs"]
                        }),
                else:
                    data['nodes'].append({
                        "id": str(i),
                        "id_orignal": key,
                        "size": len(graph['nodes'][key]),
                        "vertices": cluster,
                        "categorical_cols_summary": graph['nodes'][key]["categorical_cols_summary"],
                        }),
            else:
                data['nodes'].append({
                    "id": str(i),
                    "size": len(graph['nodes'][key]),
                    "vertices": cluster
                    })
        i += 1

    with open(APP_STATIC+"/uploads/nodes_detail.json","w") as f:
        json.dump(nodes_detail, f)

    for link in graph.edges:
        node1, node2 = get_node_id(link[0]), get_node_id(link[1])
        data["links"].append({"source": name2id[node1], "target":name2id[node2]})
    return data

def get_node_id(node):
    interval_idx = node.interval_index
    cluster_idx = node.cluster_index
    node_id = "node"+str(interval_idx)+str(cluster_idx)
    return node_id

@app.route('/linear_regression', methods=['POST','GET'])
def linear_regression():
    json_data = json.loads(request.form.get('data'))
    selected_nodes = json_data['nodes']
    y_name = json_data['dep_var']
    X_names = json_data['indep_vars']
    print(y_name, X_names)
    with open(APP_STATIC+"/uploads/nodes_detail.json") as f:
        nodes_detail = json.load(f)
    data = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    if len(selected_nodes) > 0:
        selected_rows = []
        for node in selected_nodes:
            selected_rows += nodes_detail[node]
        selected_rows = list(set(selected_rows))
        data = data.iloc[selected_rows, :]
        data.index = range(len(data))
    y = data.loc[:,y_name]
    X = data.loc[:,X_names]
    X2 = sm.add_constant(X)
    reg = sm.OLS(y, X2)
    print(y,X2)
    result = reg.fit()
    conf_int = np.array(result.conf_int())
    conf_int_new = []
    for i in range(conf_int.shape[0]):
        conf_int_new.append(list(conf_int[i,:]))
    print(result.summary())
    return jsonify(params=list(result.params), pvalues=list(result.pvalues), conf_int=conf_int_new, stderr=list(result.bse))

@app.route('/pca', methods=['POST','GET'])
def pca():
    '''
    Dimension reduction using PCA
    n_components = 2
    '''
    selected_nodes = json.loads(request.form.get('data'))['nodes']
    print(selected_nodes)
    data = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    with open(APP_STATIC+"/uploads/cols_info.json") as f:
        cols_dict = json.load(f)
    cols = cols_dict['cols_numerical']
    print(cols)
    with open(APP_STATIC+"/uploads/nodes_detail.json") as f:
        nodes_detail = json.load(f)
    if len(selected_nodes) > 0:
        selected_rows = []
        for node in selected_nodes:
            selected_rows += nodes_detail[node]
        selected_rows = list(set(selected_rows))
        data = data.iloc[selected_rows, :]
        data.index = range(len(data))
    pca = PCA(n_components=2)
    data_new = pca.fit_transform(data.loc[:,cols])
    data_new = pd.DataFrame(data_new)
    data_new.columns = ['pc1', 'pc2']
    print(data.shape)
    print(data_new)
    # clustering
    if len(selected_nodes)>0:
        data_new['kmeans_cluster'] = KMeans(n_clusters=min(len(selected_nodes), 6), random_state=0).fit(data_new).labels_
    else:
        # data_new['kmeans_cluster'] = KMeans(n_clusters=10, random_state=0).fit(data_new).labels_
        data_new['kmeans_cluster'] = KMeans(n_clusters=6, random_state=0).fit(data_new).labels_
    data_new = data_new.to_json(orient='records')
    return jsonify(pca=data_new)

@app.route('/update_cluster_details', methods=['POST','GET'])
def update_cluster_details():
    label_column = request.get_data().decode('utf-8')
    df = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv") 
    with open(APP_STATIC+"/uploads/cols_info.json") as f:
        cols_dict = json.load(f)
    labels = df[label_column]
    if label_column in cols_dict['cols_numerical']:
        labels = np.round(labels,2)
    labels = list(labels)
    return jsonify(labels=labels)

def run_mapper(data_array, col_names, interval, overlap, clustering_alg, clustering_alg_params, filter_function, filter_parameters=None):
        """This function is called when the form is submitted. It triggers construction of Mapper. 

        Each parameter of this function is defined in the configuration.

        To customize the Mapper construction, you can inherit from :code:`KeplerMapperConfig` and customize this function.


        Parameters
        -------------

        interval: int
            Number of intervals 

        overlap: float
            Percentage of overlap. This value will be divided by 100 to produce proporition.
        
        dbscan_eps: float
            :code:`eps` parameter for the DBSCAN clustering used in Kepler Mapper construction.
        
        dbscan_min_samples: int
            :code:`min_samples` parameter for the DBSCAN clustering used in Kepler Mapper construction.

        filter_function: str
            Projection for constructing the lens for Kepler Mapper.

        """
        # data_array = np.array(data_array)

        km_result, lens_dict = _call_kmapper(data_array, col_names, 
            interval,
            overlap,
            clustering_alg,
            clustering_alg_params,
            filter_function,
            filter_parameters
        )
        return _parse_result(km_result, lens_dict, data_array)

def _call_kmapper(data, col_names, interval, overlap, clustering_alg, clustering_alg_params, filter_function, filter_parameters=None):
    mapper = KeplerMapper()
    if len(col_names) == 1:
        data_new = np.array(data[col_names[0]]).reshape(-1,1)
    else:
        data_new = np.array(data[col_names])

    lens_dict = {}
    if len(filter_function) == 1:
        f = filter_function[0]
        if f in data.columns:
            lens = data[f]
        else:
            lens = compute_lens(f, data_new, mapper, filter_parameters)
        lens_dict[f] = lens

    elif len(filter_function) == 2:
        lens = []
        for f in filter_function:
            if f in data.columns:
                lens_f = np.array(data[f]).reshape(-1,1)
            else:
                lens_f = compute_lens(f, data_new, mapper, filter_parameters)
            lens.append(lens_f)
            lens_dict[f] = lens_f
        lens = np.concatenate((lens[0], lens[1]), axis=1)
    # clusterer = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean', n_jobs=8)
    cover = Cover(n_cubes=interval, perc_overlap=overlap)
    if clustering_alg == "DBSCAN":
        graph = mapper.map_parallel(lens, data_new, clusterer=cluster.DBSCAN(eps=float(clustering_alg_params["eps"]), min_samples=int(clustering_alg_params["min_samples"])), cover=cover)
    elif clustering_alg == "Agglomerative Clustering":
        graph = mapper.map_parallel(lens, data_new, clusterer=cluster.AgglomerativeClustering(n_clusters=None, linkage=clustering_alg_params["linkage"], distance_threshold=float(clustering_alg_params["dist"])), cover=cover)
        # graph = mapper.map_parallel(lens, data_new, clusterer=cluster.AgglomerativeClustering( linkage=clustering_alg_params["linkage"]), cover=Cover(n_cubes=interval, perc_overlap=overlap))
    elif clustering_alg == "Mean Shift":
        graph = mapper.map_parallel(lens, data_new, clusterer=cluster.MeanShift(bandwidth=float(clustering_alg_params["bandwidth"])), cover=cover)
        # graph = mapper.map_parallel(lens, data_new, clusterer=cluster.MeanShift(bandwidth=1), cover=Cover(n_cubes=interval, perc_overlap=overlap))
        
    # graph = mapper.map(lens, data_new, clusterer=cluster.DBSCAN(eps=eps, min_samples=min_samples), cover=Cover(n_cubes=interval, perc_overlap=overlap))
    return graph, lens_dict

def compute_lens(f, data, mapper, filter_parameters=None):
    data_array = np.array(data)
    if f in ["sum", "mean", "median", "max", "min", "std", "l2norm"]:
        lens = mapper.fit_transform(data_array, projection=f).reshape(-1,1)
    elif f == "Density":
        density_kernel = filter_parameters['density_kernel']
        density_bandwidth = filter_parameters['density_bandwidth']
        print("density", density_kernel, density_bandwidth)
        kde = KernelDensity(kernel=density_kernel, bandwidth=density_bandwidth).fit(data_array)
        lens = kde.score_samples(data_array).reshape(-1,1)
        scaler = MinMaxScaler()
        lens = scaler.fit_transform(lens)
    elif f == "Eccentricity":
        p = filter_parameters['eccent_p']
        distance_matrix = filter_parameters['eccent_dist']
        print("eccent", p, distance_matrix)
        pdist = distance.squareform(distance.pdist(data_array, metric=distance_matrix))
        lens = np.array([(np.sum(pdist**p, axis=1)/len(data_array))**(1/p)]).reshape(-1,1)
    elif f == "PC1":
        pca = PCA(n_components=min(2, data_array.shape[1]))
        lens = pca.fit_transform(data_array)[:,0].reshape(-1,1)
    elif f == "PC2":
        if data_array.shape[1] > 1:
            pca = PCA(n_components=2)
            lens = pca.fit_transform(data_array)[:,1].reshape(-1,1)
    # else:
    #     lens = np.array(data[f]).reshape(-1,1)
    return lens


def _parse_result(graph, lens_dict={}, data_array=[], if_cli=False):
    print("parsing result")
    if len(data_array)>0:
        col_names = data_array.columns
        data_array = np.array(data_array)
    data = {"nodes": [], "links": []}
    # nodes
    node_keys = graph['nodes'].keys()
    name2id = {}
    i = 1
    nodes_detail = {}
    for key in node_keys:
        name2id[key] = i
        cluster = graph['nodes'][key]
        nodes_detail[i] = cluster
        cluster_avg_dict = {}
        for lens in lens_dict:
            cluster_data = lens_dict[lens][cluster]
            cluster_avg = np.mean(cluster_data)
            cluster_avg_dict[lens] = cluster_avg
        if len(data_array)>0:
            cluster_data = data_array[cluster]
            cluster_avg = np.mean(cluster_data, axis=0)
            for j in range(len(col_names)):
                cluster_avg_dict[col_names[j]] = cluster_avg[j]
            data['nodes'].append({
                "id": str(i),
                "size": len(graph['nodes'][key]),
                "avgs": cluster_avg_dict,
                "vertices": cluster
                })
        else:
            if if_cli:
                if "avgs" in graph['nodes'][key]:
                    data['nodes'].append({
                        "id": str(i),
                        "id_orignal": key,
                        "size": len(graph['nodes'][key]),
                        "vertices": cluster,
                        "categorical_cols_summary": graph['nodes'][key]["categorical_cols_summary"],
                        "avgs":graph['nodes'][key]["avgs"]
                        }),
                else:
                    print("cc")
                    data['nodes'].append({
                        "id": str(i),
                        "id_orignal": key,
                        "size": len(graph['nodes'][key]),
                        "vertices": cluster,
                        "categorical_cols_summary":for_label_scaffold(APP_STATIC+'/uploads/processed_data.csv',cluster)
                        }),
            else:
                data['nodes'].append({
                    "id": str(i),
                    "size": len(graph['nodes'][key]),
                    "vertices": cluster
                    })
        i += 1
    
    with open(APP_STATIC+"/uploads/nodes_detail.json","w") as f:
        json.dump(nodes_detail, f)

    # links
    links = set()
    for link_from in graph['links'].keys():
        for link_to in graph['links'][link_from]:
            from_id = name2id[link_from]
            to_id = name2id[link_to]
            left_id = min(from_id, to_id)
            right_id = max(from_id, to_id)
            links.add((left_id, right_id))
    for link in links:
        data['links'].append({"source": link[0], "target": link[1]})
    return data

def compute_cc(graph): 
    '''
    Compute connected components for the mapper graph
    '''
    G = nx.Graph()
    for node in graph['nodes']:
        nodeId = int(node['id'])-1
        G.add_node(nodeId)
    for edge in graph['links']:
        sourceId = int(edge['source'])-1
        targetId = int(edge['target'])-1
        G.add_edge(sourceId, targetId)
    cc = nx.connected_components(G)
    cc_list = []
    for c in cc:
        cc_list.append(list(c))
    return cc_list

def get_selected_data(selected_nodes):
    data = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    with open(APP_STATIC+"/uploads/cols_info.json") as f:
        cols_dict = json.load(f)
    cols = cols_dict['cols_numerical']
    with open(APP_STATIC+"/uploads/nodes_detail.json") as f:
        nodes_detail = json.load(f)
    if len(selected_nodes) > 0:
        selected_rows = []
        for node in selected_nodes:
            selected_rows += nodes_detail[node]
        selected_rows = list(set(selected_rows))
        data = data.iloc[selected_rows, :]
        data.index = range(len(data))
    return data, cols

@app.route('/module_extension', methods=['POST','GET'])
def module_extension():
    module_info = ""
    if os.path.exists(APP_STATIC+"/uploads/new_modules.json"):
        with open(APP_STATIC+"/uploads/new_modules.json") as f:
            module_info = json.load(f)
    return module_info

@app.route('/module_computing', methods=['POST','GET'])
def module_computing():
    json_data = json.loads(request.form.get('data'))
    selected_nodes = json_data['nodes']
    data, cols = get_selected_data(selected_nodes)
    module_info = json_data['module_info']
    data_new = call_module_function(data, cols, module_info)
    # data_new['kmeans_cluster'] = KMeans(n_clusters=4, random_state=0).fit(data_new).labels_
    # data_new = data_new.to_json(orient='records')
    # return jsonify(module_result=data_new)
    return data_new
    # # kNN graph
    # from pynndescent import NNDescent
    # df = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    # activations = df.iloc[:, 0:512]
    # k=5
    # index = NNDescent(activations, n_neighbors=15, metric='euclidean')
    # out = index.query(activations, k=k)
    # dist = out[1]
    # s_dist=np.sort(dist, axis=0)
    # s_dist = list(s_dist[:,k-1].astype("str"))
    # print(s_dist)
    # return jsonify(s_dist=s_dist)

def call_module_function(data, cols, module_info):
    mod_name, func_name = module_info['function-name'].rsplit('.',1)
    mod = importlib.import_module(mod_name)
    method_to_call = getattr(mod, func_name)
    if module_info['module-type'] == "unsupervised_learning":
        result = method_to_call(**module_info['function-parameters'])
        data_new = result.fit_transform(data.loc[:,cols])
        data_new = pd.DataFrame(data_new)
        data_new_cols = []
        for i in range(data_new.shape[1]):
            data_new_cols.append("col"+str(i+1))
        data_new.columns = data_new_cols
        data_new['kmeans_cluster'] = KMeans(n_clusters=4, random_state=0).fit(data_new).labels_
        data_new = data_new.to_json(orient='records')
        data_new = jsonify(module_result=data_new)
    elif module_info['module-type'] == "supervised_learning":
        y = data.loc[:,module_info['input-variables']['dependent']]
        X = data.loc[:,module_info['input-variables']['independent']]
        X2 = sm.add_constant(X)
        reg = method_to_call(np.asarray(y), np.asarray(X2))
        result = reg.fit()
        conf_int = np.array(result.conf_int())
        conf_int_new = []
        for i in range(conf_int.shape[0]):
            conf_int_new.append(list(conf_int[i,:]))
        print(result.summary())
        data_new = jsonify(params=list(result.params), pvalues=list(result.pvalues), conf_int=conf_int_new, stderr=list(result.bse))
    return data_new

@app.route('/send_structure', methods=['POST','GET'])
def send_structure():
   import base64
   selected_vertex_id = request.get_data().decode('utf-8')
   vertices = selected_vertex_id.split(',')
   my_string = []

   # Picking the right scaffold column
   col_names = linecache.getline('./CLI_examples/processed_data.csv', 1)
   check = col_names.split(',')[-2]
   if check == 'Scaffold':
        k = -1
   else:
        k = -2
   #df = pd.read_csv("CLI_examples/processed_data.csv") 
   print("DEBUG:",k)
   for i in range(len(vertices)):
       vertices[i] = int(vertices[i])
       print(vertices)
       line = linecache.getline("./CLI_examples/processed_data.csv", vertices[i]+2)
       structure = line.split(',')[k]
   #print(df.iloc[0]['Structure'])
       #structure = df.iloc[vertices[i]]['Structure']
       draw_structure.draw_chem(structure)
       with open("./app/sample.png", "rb") as img_file:
            my_string.append(base64.b64encode(img_file.read()).decode("utf-8"))
   return json.dumps({"success": 1, "image1":my_string[0],"image2":my_string[1]})

@app.route('/knn', methods=['POST','GET'])
def for_KNN():
    # # kNN graph
    min_samples = json.loads(request.form.get('data'))['min_samples']
    min_samples = int(min_samples)
    print("EE: ",min_samples)
    from pynndescent import NNDescent
    df = pd.read_csv(APP_STATIC+"/uploads/processed_data.csv")
    activations = df.iloc[:, 0:299]
    k = min_samples
    index = NNDescent(activations, metric='euclidean')
    out = index.query(activations, k=k)
    dist = out[1]
    s_dist=np.sort(dist, axis=0)
    print(s_dist)
    s_dist = list(s_dist[:,k-1].astype("str"))
    return jsonify(s_dist=s_dist)