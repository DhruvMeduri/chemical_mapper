import json

with open('./sample.json', 'r') as f:
    # Load the JSON data into a Python dictionary
    mapper = json.load(f)


file1 = open("./graph_points.vtk","w")
file1.write("# vtk DataFile Version 2.0\nvtk output\nASCII\nDATASET POLYDATA\n")
file1.write("POINTS "+str(len(mapper["nodes"])) + " float" + "\n")
for i in mapper["nodes"]:
    file1.write(str(i["x"]) + " 0 " + str(i["y"]) + "\n" )

with open('./anchor_final_500_40_5_5.json', 'r') as f:
    # Load the JSON data into a Python dictionary
    mapper = json.load(f)

# This is for rendering the edges of the mapper graph

def find_index(id,list):
     index=0
     for i in list:
        if(i['id']==str(id+1)):
            return index
        index = index + 1
          
          
'''
file1.write("LINES " + str(len(mapper["mapper"]["links"])) + " " + str(3*len(mapper["mapper"]["links"])) + "\n")
for i in mapper["mapper"]["links"]:
    file1.write("2 " + str(find_index(i["source"]-1,mapper["mapper"]["nodes"])) + " " + str(find_index(i["target"]-1,mapper["mapper"]["nodes"])) + "\n")
'''

file1.write("POINT_DATA "+str(len(mapper["mapper"]["nodes"]))+"\n")
file1.write("FIELD FieldData 1\n")
file1.write("Category 1 " + str(len(mapper["mapper"]["nodes"])) + " string\n")
#file1.write("SCALARS toxicity float 1\n")
#file1.write("LOOKUP_TABLE default\n")

for i in mapper["mapper"]["nodes"]:
        max_key = max(i["categorical_cols_summary"]["scaffold"], key=i["categorical_cols_summary"]["scaffold"].get)
        file1.write(str(max_key) + "\n")
'''
count = 1
for i in mapper["mapper"]["nodes"]:
        file1.write(str(i["avgs"]["MHFP6_avg"]) + "\n")
        count = count +1
'''

