# This is for writing the chemical molecules for a given path

import json
import linecache
import numpy as np
import random
# I want to do some node analysis
file = open('CLI_examples/final.json')
graph = json.load(file)
adj = np.zeros(shape = (len(graph['mapper']['nodes']),len(graph['mapper']['nodes'])))
edges = graph['mapper']['links']

for edge in edges:
    adj[edge['source']-1][edge['target']-1] = 1
    adj[edge['target']-1][edge['source']-1] = 1

# Now to compute a transition matrix
trans = np.zeros(shape = (len(graph['mapper']['nodes']),len(graph['mapper']['nodes'])))
sum = 0
for i in range(len(graph['mapper']['nodes'])):
    temp = adj[i]
    sum = np.sum(temp)
    if sum!=0:
        trans[i] = temp/sum

# Now to compute the path we compute a random walk
 
query = 209
pos = np.zeros(len(graph['mapper']['nodes']))
pos[query-1] = 1
check = np.matmul(pos,trans)
length = 100
path = [query]
choice_samples = range(len(graph['mapper']['nodes']))
for i in range(length):
    temp = np.matmul(pos,trans)
    temp = random.choices(choice_samples,weights=temp,k=1)
    path.append(temp[0]+1)
    pos = np.zeros(len(graph['mapper']['nodes']))
    pos[temp] = 1
print(path)
            
# Now coming to extracting the structures
count = 0
dic = {}
for i in path:
    array = graph['mapper']['nodes'][i-1]['vertices']
    temp = random.sample(array,min(len(array),20))
    temp_struct = []
    for j in temp:
        struct = linecache.getline('CLI_examples/processed_data.csv', j+2).split(',')[-1][:-1]
        temp_struct.append(struct)
    dic[count] = {'time_step':count,'node':i,'structures':temp_struct}
    count = count + 1

print(dic)

with open("./CLI_examples/downstream.json","w") as outfile:
    json.dump(dic,outfile)

    



