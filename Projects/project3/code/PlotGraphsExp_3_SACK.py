# Utility script to parse results for experiment 3

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

    sequenceNumberDict = {}
    delayTime = {}
    cbrDelayDict = {}
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

    tcpThroughputDict = {}
    latencyTcpPerTimeIntervalDict = {}
    latencyCbrPerTimeIntervalDict = {}

    cbrThroughputDict = {}

    if file.endswith('.tr'):
        with open("trace_files/"+file, 'r') as f:
            lines = f.readlines()
        for l in lines:
            line = l.split()

            # If source is node1 and tcp packet has been enqueued, increment packetsSent
            if line[0] == '+' and line[2] == '0' and line[3] == '1' and line[4] == 'tcp' and line[7] == '1':
                # Add sequence number to the dictionary to check identify retransmitted packets
                if line[10] in sequenceNumberDict:
                    sequenceNumberDict[line[10]] = False
                else:
                    sequenceNumberDict[line[10]] = True
                # Record packetID start time to a dictionary
                if line[10] not in delayTime:
                    delayTime[line[10]] = float(line[1])

            if line[0] == '+' and line[2] == '4' and line[3] == '1' and line[4] == 'cbr' and line[7] == '2':

                # Record packetID start time to a dictionary
                if line[10] not in cbrDelayDict:
                    cbrDelayDict[line[10]] = float(line[1])

            # If source is node1 and tcp packet has been enqueued, increment packetsSent
            if line[0] == 'r' and line[2] == '2' and line[3] == '3' and line[4] == 'tcp' and line[7] == '1':
                packetsSent += 1
                bytesSent += float(line[5])
                # Record simulation duration

                if "." in line[1]:
                    timeIntStart = float(line[1].split(".")[0])
                else:
                    timeIntStart = float(line[1])

                # If packetID start time has been recorded, subtract end time - start time to get end to end delay
                if line[10] in delayTime:
                    if timeIntStart not in latencyTcpPerTimeIntervalDict:
                        tr = []
                        tr.append(float(line[1]) - delayTime[line[10]])
                        latencyTcpPerTimeIntervalDict[timeIntStart] = tr
                    else:
                        tr = latencyTcpPerTimeIntervalDict.get(timeIntStart)
                        tr.append(float(line[1]) - delayTime[line[10]])
                        latencyTcpPerTimeIntervalDict[timeIntStart] = tr

                    #delayTime[line[10]] = float(line[1]) - delayTime[line[10]]



                if timeIntStart not in tcpThroughputDict:
                    tr = []
                    tr.append(float(line[5]))
                    tcpThroughputDict[timeIntStart] = tr
                else:
                    tr = tcpThroughputDict.get(timeIntStart)
                    tr.append(float(line[5]))
                    tcpThroughputDict[timeIntStart] = tr

            if line[0] == 'r' and line[2] == '2' and line[3] == '5' and line[4] == 'cbr' and line[7] == '2':
                packetsSent += 1
                bytesSent += float(line[5])
                # Record simulation duration

                if "." in line[1]:
                    timeIntStart = float(line[1].split(".")[0])
                else:
                    timeIntStart = float(line[1])

                if timeIntStart not in cbrThroughputDict:
                    tr = []
                    tr.append(float(line[5]))
                    cbrThroughputDict[timeIntStart] = tr
                else:
                    tr = cbrThroughputDict[timeIntStart]
                    tr.append(float(line[5]))
                    cbrThroughputDict[timeIntStart] = tr

                # If packetID start time has been recorded, subtract end time - start time to get end to end delay
                if line[10] in cbrDelayDict:
                    if timeIntStart not in latencyCbrPerTimeIntervalDict:
                        tr = []
                        tr.append(float(line[1]) - cbrDelayDict[line[10]])
                        latencyCbrPerTimeIntervalDict[timeIntStart] = tr
                    else:
                        tr = latencyCbrPerTimeIntervalDict.get(timeIntStart)
                        tr.append(float(line[1]) - cbrDelayDict[line[10]])
                        latencyCbrPerTimeIntervalDict[timeIntStart] = tr


with open("results/exp3/SACK-RED.csv", 'w') as f:
    f.write("Time,THROUGHPUT-CBR,THROUGHPUT-TCP,TCP-LATENCY,CBR-LATENCY\n")
    for key in sorted(tcpThroughputDict):
        bytesPerSecond = sum(tcpThroughputDict.get(key))
        if key not in cbrThroughputDict:
            totalCbrBytes = 0
        else:
            totalCbrBytes = sum(cbrThroughputDict.get(key))

        if key not in latencyCbrPerTimeIntervalDict:
            latencyPerCbrTimeInterval = 0
        else:
            latencyPerCbrTimeInterval = sum(latencyCbrPerTimeIntervalDict.get(key))/float(len(latencyCbrPerTimeIntervalDict.get(key)))

        latencyPerTimeInterval = sum(latencyTcpPerTimeIntervalDict.get(key)) / float(len(latencyTcpPerTimeIntervalDict.get(key)))


        f.write(str(key)+","+str(8*totalCbrBytes/float(1000000)) +
                "," + str(8*bytesPerSecond/float(1000000))+
                "," + str(latencyPerTimeInterval)+
                "," + str(latencyPerCbrTimeInterval)+"\n")
f.close()
