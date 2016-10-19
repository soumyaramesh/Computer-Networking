# Utility script to consolidate results for experiment 1
import os


fillCollection = []
fileCount = 0

traceFiles = os.listdir('results/exp1')
for file in traceFiles:
    fillCollection.append([])
    if file.endswith('.csv'):
        with open("results/exp1/"+file, 'r') as f:
            lines = f.readlines()
            for l in lines:
                line = l.split(",")
                row = ""
                for v in line:

                    if v.endswith("\n"):
                        v = v.split("\n")[0]
                    row += v+","
                fillCollection[fileCount].append(row)

    fileCount += 1



with open("results/exp1/combined.csv", 'w') as f:

    for x in range(0, 99):
        singleLine1 = fillCollection[0][x]
        singleLine2 = fillCollection[1][x]
        singleLine3 = fillCollection[2][x]
        singleLine4 = fillCollection[3][x]

        f.write(str(singleLine1)+","+str(singleLine2)+","+str(singleLine3)+","+str(singleLine4)+"\n")


f.close()