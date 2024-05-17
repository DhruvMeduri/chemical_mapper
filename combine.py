import pandas as pd
import itertools
import csv
import json
import numpy as np
def read_point(path,line_number):
    with open(path) as f:
        whole = next(itertools.islice(csv.reader(f), line_number, None))
        point = whole[:-3]
        point = np.array(point)
        point = np.asarray(point,dtype=float)
        return point

def get_cube_cluster(key):
    str = key.split("_")
    return [int(str[0].replace("cube","")),int(str[1].replace("cluster",""))]



def compare_arrays(array1,array2,filename,epsilon):
    for i in array1:
        for j in array2:
            if np.linalg.norm(read_point(filename,i)-read_point(filename,j)<epsilon):
                return True
    return False

def merge_blocks(blocks,filename,epsilon):
    final_blocks = blocks.copy()
    flag = 0
    crit = []
    for i in range(len(blocks)):
        for j in range(i):
            if compare_arrays(blocks[i],blocks[j],filename,epsilon):
                crit = [i,j]
                flag = 1
                break


    if flag == 1:
        final_blocks.pop(crit[0])
        final_blocks.pop(crit[1])
        final_blocks.append(blocks[crit[0]]+blocks[crit[1]])
        return merge_blocks(final_blocks,filename,epsilon)
    if flag == 0:
        return final_blocks





def combine_mapper(path1,path2,filename,epsilon,intervals):
    f1 = open(path1)
    data1 = json.load(f1)

    f2 = open(path2)
    data2 = json.load(f2)

    merged_data = {"nodes":{},"edges":{}}
    cluster_count = np.zeros(intervals)

    for k in range(intervals):
        print(k)
        temp_blocks = []
        for i in data1['nodes'].keys():
            if get_cube_cluster(i)[0] == k:
                temp = [x+1 for x in data1['nodes'][i]]
                temp_blocks.append(temp)

        for j in data2['nodes'].keys():
            if get_cube_cluster(j)[0] == k:
                temp = [x+52 for x in data2['nodes'][j]]
                temp_blocks.append(temp)
        
        temp_blocks = merge_blocks(temp_blocks,filename,epsilon)
        #print(temp_blocks)
        



                            
    #with open('result.json', 'w') as fp:
    #    json.dump(merged_data, fp)


combine_mapper('./CLI_examples/check1.json','./CLI_examples/check2.json','check.csv',7,10)



