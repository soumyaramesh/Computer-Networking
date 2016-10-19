# Utility script to parse results for experiment 2

import os

traceFiles = []
tlist = []
glist = []
dlist = []
llist = []

goodputArr = {}
throughputArr = {}
dropRateArr = {}
latencyArr = {}
dropRateAvg = {}
latencyAvg = {}
throughputAvg = {}
goodputAvg = {}

traceFiles = os.listdir('trace_files')
for file in traceFiles:

    delayTime = {}
    simulationStartTime = -1.0
    simulationEndTime = -1.0
    goodputMbps = 0.0
    throughputMbps = 0.0
    packetsSent = 0
    packetsReceived = 0
    packetsReceivedInOrder = 0
    prevSequenceNumber = -1
    bytesSent = 0
    bytesReceived = 0
    bytesReceivedInOrder = 0
    packetDropRate = 0.0
    packetsDropped = 0
    totalDelay = 0.0
    latency = 0.0

    if file.endswith('.tr'):
        with open("trace_files/"+file, 'r') as f:
            lines = f.readlines()
        for l in lines:
            line = l.split()
            # If source is node1 and tcp packet has been enqueued, increment packetsSent
            if line[0] == '+' and line[2] == '4' and line[3] == '1' and line[4] == 'tcp' and line[7] == '2':
                packetsSent += 1
                bytesSent += float(line[5])
                # Record simulation duration
                if simulationStartTime == -1.0:
                    simulationStartTime = float(line[1])
                    simulationEndTime = float(line[1])
                else:
                    simulationEndTime = float(line[1])
                # Record packetID start time to a dictionary
                if line[10] not in delayTime:
                    delayTime[line[10]] = float(line[1])

            # If tcp packet has been received at destination 5, add to throughput
            elif line[0] == 'r' and line[2] == '2' and line[3] == '5' and line[4] == 'tcp' and line[7] == '2':
                packetsReceived += 1
                bytesReceived += float(line[5])

                # If packetID start time has been recorded, subtract end time - start time to get end to end delay
                if line[10] in delayTime:
                    delayTime[line[10]] = float(line[1]) - delayTime[line[10]]

                # If packet has been received in order, add to goodput
                if int(line[10]) == (prevSequenceNumber + 1):
                    packetsReceivedInOrder += 1
                    bytesReceivedInOrder += float(line[5])
                    prevSequenceNumber = int(line[10])

            # If a tcp packet(not including re-transmissions) has been dropped, increment packet drop count
            elif line[0] == 'd' and line[7] == '2' and line[4] == 'tcp' and 'A' not in line[6]:
                packetsDropped += 1

        simulationTime = simulationEndTime - simulationStartTime
        throughputMbps = bytesReceived*8/float(simulationTime*1000000)
        goodputMbps = bytesReceivedInOrder*8/float(simulationTime*1000000)
        packetDropRate = (packetsSent - packetsReceived) / float(packetsSent)
        for packetID in delayTime.keys():
            totalDelay += delayTime[packetID]
        latency = totalDelay/len(delayTime)
        fileKey = float(file.split("_")[1])

        if fileKey not in throughputArr:
            throughputArr[fileKey] = [throughputMbps]
        else:
            tlist = throughputArr.get(fileKey)
            tlist.append(throughputMbps)

        if fileKey not in goodputArr:
            goodputArr[fileKey] = [goodputMbps]
        else:
            glist = goodputArr.get(fileKey)
            glist.append(goodputMbps)

        if fileKey not in dropRateArr:
            dropRateArr[fileKey] = [packetDropRate]
        else:
            dlist = dropRateArr.get(fileKey)
            dlist.append(packetDropRate)

        if fileKey not in latencyArr:
            latencyArr[fileKey] = [latency]
        else:
            llist = latencyArr.get(fileKey)
            llist.append(latency)
#        print "file=" + str(file) + " Packets Dropped " + str(packetsDropped)+ " Throughput = " + str(throughputMbps)
# + " Goodput = " + str(goodputMbps) + " Drop Rate = " + str(packetDropRate) + " Latency = " + str(latency)

for t in throughputArr.keys():
    tlist = throughputArr.get(t)
    throughputAvg[t] = sum(tlist)/float(len(tlist))

for g in goodputArr.keys():
    glist = goodputArr.get(g)
    goodputAvg[g] = sum(glist)/float(len(glist))

for d in dropRateArr.keys():
    dlist = dropRateArr.get(d)
    dropRateAvg[d] = sum(dlist)/float(len(dlist))

for l in latencyArr.keys():
    llist = latencyArr.get(l)
    latencyAvg[l] = sum(llist)/float(len(llist))

with open("results/exp2/Newreno-Vegas-2.csv", 'w') as f:
    f.write("CBR,THROUGHPUT,GOODPUT,DROP RATE,LATENCY\n")
    for key in sorted(throughputAvg):
        f.write(str(key) + "," + str(throughputAvg[key]) + "," +
                str(goodputAvg[key]) + "," + str(dropRateAvg[key]) + "," + str(latencyAvg[key]) + "\n")

f.close()
