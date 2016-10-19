import socket
import threading
import operator

# Port on which Active Measurement System runs
ACTIVE_MEASUREMENT_PORT = 58793

# EC2 Host list with indexing
hostlist = {1:'ec2-54-85-32-37.compute-1.amazonaws.com',
                 2:'ec2-54-193-70-31.us-west-1.compute.amazonaws.com',
                 3:'ec2-52-38-67-246.us-west-2.compute.amazonaws.com',
                 4:'ec2-52-51-20-200.eu-west-1.compute.amazonaws.com',
                 5:'ec2-52-29-65-165.eu-central-1.compute.amazonaws.com',
                 6:'ec2-52-196-70-227.ap-northeast-1.compute.amazonaws.com',
                 7:'ec2-54-169-117-213.ap-southeast-1.compute.amazonaws.com',
                 8:'ec2-52-63-206-143.ap-southeast-2.compute.amazonaws.com',
                 9:'ec2-54-233-185-94.sa-east-1.compute.amazonaws.com'}



hostIPMapping = {'ec2-54-85-32-37.compute-1.amazonaws.com': '54.85.32.37',
                 'ec2-54-193-70-31.us-west-1.compute.amazonaws.com':'54.193.70.31',
                 'ec2-52-38-67-246.us-west-2.compute.amazonaws.com':'52.38.67.246',
                 'ec2-52-51-20-200.eu-west-1.compute.amazonaws.com':'52.51.20.200',
                 'ec2-52-29-65-165.eu-central-1.compute.amazonaws.com':'52.29.65.165',
                 'ec2-52-196-70-227.ap-northeast-1.compute.amazonaws.com':'52.196.70.227',
                 'ec2-54-169-117-213.ap-southeast-1.compute.amazonaws.com':'54.169.117.213',
                 'ec2-52-63-206-143.ap-southeast-2.compute.amazonaws.com':'52.63.206.143',
                 'ec2-54-233-185-94.sa-east-1.compute.amazonaws.com':'54.233.185.94'}



# Dictonary to hold the Latencies of a particular IP request
latencyDict = {1:9999,2:9999,3:9999,4:9999,5:9999,6:9999,7:9999,8:9999,9:9999}

threads = []

ipDcit = {}

# Resource Lock to read/write into/from 'latencyDict'
dictLock = threading.Lock()

class myThread (threading.Thread):

    def __init__(self, numb,host,port,clientIP):
        threading.Thread.__init__(self)
        self.numb = numb
        self.port = int(port)
        self.host = host
        self.clientIP = clientIP

    def run(self):

        try:
            # Create a Socket
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


            # Bind to host,port
            print "Talking to host:" + self.host
            clientsocket.connect((self.host, ACTIVE_MEASUREMENT_PORT))

            # Send out Client IP to EC2 Measurement System
            clientsocket.settimeout(2.0)
            clientsocket.send(self.clientIP)


            # Get the Latency from the EC2 host
            data = clientsocket.recv(1024)

            clientsocket.close()

            # Update Latency dictionary in a thread safe way
            updateLatencyDict(self.numb,data)
        except Exception:
            print "An errored while trying to communicate with " + self.host
            clientsocket.close()



# Update Latency Dictionary in a thread safe manner
def updateLatencyDict(index,data):

    if data == 'Error':
        return
    dictLock.acquire()
    latencyDict[index] = float(data)
    dictLock.release()




# Given a Client IP, returns the best EC2 host
def getBestIP(clientIP):

    global latencyDict


    try:

        # Check if Client IP is not in Memmory-Cache
        if clientIP not in ipDcit:
            numb = 1

            # Loop through Host List, create a thread to find the latency for each host
            for item in hostlist:



                host = hostlist[item]

                port = ACTIVE_MEASUREMENT_PORT

                # Create a new Thread
                thread = myThread(numb,host,port,clientIP)
                thread.start()

                threads.append(thread)
                numb += 1


            # Wait for all threads to finish
            for t in threads:
                t.join()


            print "Latency Dict "
            print latencyDict

            # Sort Dictionary by value
            sortedDict = sorted(latencyDict.items(), key=operator.itemgetter(1))

            print "Sorted Latency Dict "
            print sortedDict
            #print sortedDict


            index = sortedDict[0][0]
            #print 'index=' + str(index)
            #print "Host="+hostlist[index]


            bestIP = hostIPMapping[ hostlist[index]]

            ipDcit[clientIP] = bestIP

            latencyDict = {1:9999,2:9999,3:9999,4:9999,5:9999,6:9999,7:9999,8:9999,9:9999}

            # Return bestIP to caller
            return bestIP

        else:

            # Client is in memory-cache

            latencyDict = {1:9999,2:9999,3:9999,4:9999,5:9999,6:9999,7:9999,8:9999,9:9999}

            # Return bestIP to caller
            return ipDcit[clientIP]


    except Exception ,e:

        # Error occured . Return Default IP
        print ' Uh oh:' + e.message
        return '54.85.32.37'






