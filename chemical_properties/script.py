import linecache
import json

with open("./anchor_final_100_50_1_10_TSNE.json") as file:
    mapper = json.load(file)


for i in mapper["mapper"]["nodes"]:

    sum = 0
    count = 0
    print(i["id"])

    for j in i["vertices"][0:min(len(i["vertices"]),4)]:

        line = linecache.getline("./processed_data.csv",j+2)
        struc = line.split(",")[-1]
        for k in range(2000000):
            #print(k)
            line = linecache.getline("./processed_data_solubility.csv",k+2)
            temp_struc = line.split(",")[-1]
            if(struc == temp_struc):
                toxicity = line.split(",")[-2]
                break
        
        toxicity = toxicity[1:]
        toxicity = float(toxicity)
        sum = sum + toxicity
        count = count + 1

    i["avgs"]["MHFP6_avg"] = sum/count

with open("./anchor_solubility_final_100_50_1_10.json","w") as fp:
    json.dump(mapper,fp)