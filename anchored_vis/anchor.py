import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

import json

import os
os.environ["OPENBLAS_NUM_THREADS"] = "16"  # Restrict OpenBLAS to use only one >

def anchor(filename):
    with open(filename, 'r') as f:
        # Load the JSON data into a Python dictionary
        mapper = json.load(f)

    print("SAMPLING POINTS FROM THE MAPPER NODES")
    sub_sample = []
    sub_mapper = []
    count = 0
    print("NUMBER OF NODES: ",len(mapper["mapper"]["nodes"]))
    for i in mapper["mapper"]["nodes"]:
        #temp_sample = list(np.random.choice(i["vertices"],min(10000,len(i["vertices"]))))
        temp_sample = list(i["vertices"])
        #sub_sample = sub_sample+temp_sample
        #temp_range = range(count,count+len(temp_sample))
        #count = count+len(temp_sample)
        sub_mapper.append(temp_sample)
    print("SAMPLING COMPLETED")

    print(sub_mapper)

    print("LOADING DATASET")
    df = pd.read_csv("./CLI_examples/processed_data.csv")
    df = np.array(df)
    df = df[:, :-3]
    print(df)
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    tsne = TSNE(n_components=2,n_jobs=16,random_state=0)
    #pca = PCA(n_components=2)
    print("DOING TSNE")
    red = tsne.fit_transform(df)
    print("TSNE DONE")
    print("SIZE: ",red.shape)



    node_anchors = []
    for i in range(len(mapper["mapper"]["nodes"])):
        anchor_x = 0
        anchor_y = 0
        for j in sub_mapper[i]:
            anchor_x = red[j][0] + anchor_x
            anchor_y = red[j][1] + anchor_y
        
        mapper["mapper"]["nodes"][i]['avgs']['anchor_x'] = anchor_x/len(sub_mapper[i])
        mapper["mapper"]["nodes"][i]['avgs']['anchor_y'] = anchor_y/len(sub_mapper[i])
        node_anchors.append([anchor_x/len(sub_mapper[i]),anchor_y/len(sub_mapper[i])])


    from sklearn.cluster import KMeans
    node_anchors = np.array(node_anchors)
    kmeans = KMeans(n_clusters=15, random_state=0, n_init="auto").fit(node_anchors)

    for i in range(len(mapper["mapper"]["nodes"])):

        mapper["mapper"]["nodes"][i]['avgs']['cluster'] = int(kmeans.labels_[i]) 


    k_clusters = []
    for i in kmeans.cluster_centers_:
        k_clusters.append({"x":i[0],"y":i[1]})

    mapper["mapper"]["k_clusters"] = k_clusters

    with open(filename, "w") as f:
        json.dump(mapper, f)


# color_col = df[sub_sample,-2]

# for i in range(len(color_col)):

#     if color_col[i]=='C1CCCCC1':
#         color_col[i] = 'red'
#     if color_col[i] == "O=C(Nc1ccccc1)c1ccccc1":
#         color_col[i] = 'blue'
#     if color_col[i]=="c1ccc(-c2ccccc2)cc1":
#         color_col[i] = 'grey'
#     if color_col[i]=="c1ccc(COc2ccccc2)cc1":
#         color_col[i] = 'brown'
#     if color_col[i]=="c1ccc(Cc2ccccc2)cc1":
#         color_col[i] = 'green'
#     if color_col[i] == "c1ccc2[nH]ccc2c1":
#         color_col[i] = 'pink'
#     if color_col[i] == "c1ccc2ccccc2c1":
#         color_col[i] = 'gold'
#     if color_col[i] == "c1ccc2ncccc2c1":
#         color_col[i] = 'yellow'
#     if color_col[i] == "c1ccccc1":
#         color_col[i] = "darkblue"
#     if color_col[i] == "c1ccncc1":
#         color_col[i] = 'black'


# df = df[sub_sample,:-3]
# print(df.shape)
# print("LOADING AND PROCESSING DATASET COMPLETED")


# plt.scatter(red[:,0],red[:,1],c=color_col)
# plt.savefig("./GraphMAE_finetuned_500_40_5_5_TSNE.png")
# plt.show()

# # Now to generate the vtk file
# file1 = open("./graph_points_TSNE.vtk","w")
# file1.write("# vtk DataFile Version 2.0\nvtk output\nASCII\nDATASET POLYDATA\n")
# file1.write("POINTS "+str(len(red)) + " float" + "\n")
# for i in red:
#     file1.write(str(i[0]) + " " + str(i[1]) + " 0\n" )

# file1.write("POINT_DATA "+str(len(red))+"\n")
# file1.write("FIELD FieldData 1\n")
# file1.write("Category 1 " + str(len(red)) + " string\n")
# for i in color_col:
#         file1.write(str(i) + "\n")