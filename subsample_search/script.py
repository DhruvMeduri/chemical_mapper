import linecache

#line1 = linecache.getline("processed_data_1.csv",1)
#with open("./processed_data_subsampled_MAE_pretrained.csv", "w") as text_file:
#    text_file.write(line1)

for i in range(3458,1000000):
    line1 = linecache.getline("processed_data_1.csv",i+2)
    print(i)
    for j in range(2000000):
        line2 = linecache.getline("processed_data.csv",j+2)
        structure1 = line1.split(",")[-1]
        structure2 = line2.split(",")[-1]
        if(structure1==structure2):
            with open("./processed_data_subsampled_MAE_pretrained.csv", "a") as text_file:
                text_file.write(line2)
            break

