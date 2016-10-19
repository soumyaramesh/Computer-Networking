import socket, sys
from struct import *
import random
import time


#Function to determine HOST Machine IP
def getMyMachineIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    return sock.getsockname()[0]



# Global Declarations
HOST = ''
URL = ''
SOURCE_IP = ''
DEST_IP = ''



#Randomizing sending port and sequence number
SOURCE_PORT = random.randint(12000, 65000)
DEST_PORT = 80
SEQ_NUMBER = random.randint(10000, 99999999)
ACK_NUMBER = 0
TTL = 64
PACKET_ID = random.randint(0, 65535)


#Function to implement checksum
def checksum(data):

    csum = 0
    it = 0


    while it<len(data):
        if it == len(data) - 1:
            each = ord(data[it])
        else:
            each = ord(data[it]) + (ord(data[it+1]) << 8 )

        csum = csum + each
        it = it+2

    csum = (csum>>16) + (csum & 0xffff);
    csum = csum + (csum >> 16);


    csum = ~csum & 0xffff

    return csum

# Utility function to send a single Packet through a socket
def sendPacket(sendSocket, message, seq, ack,synFlag,ackFlag,pushFlag,finFlag,cwnd):

    # IP Section

    ipVersion = 4
    ipHeaderLen = 5
    ipTypeOfService = 0
    ipTotalLength = 0
    ipIdentification = PACKET_ID
    ipOffset = 0
    ipTTL = TTL
    ipProtocol = socket.IPPROTO_TCP
    ipChecksum = 0
    ipSrcAddr = socket.inet_aton(SOURCE_IP)
    ipDestAddr = socket.inet_aton(DEST_IP)

    ipIHL = (ipVersion << 4) + ipHeaderLen


    packedIpHeader = pack('!BBHHHBBH4s4s' , ipIHL, ipTypeOfService, ipTotalLength, ipIdentification, ipOffset, ipTTL, ipProtocol, ipChecksum, ipSrcAddr, ipDestAddr)

    # Declaring TCP Section
    tcpSrc = SOURCE_PORT
    tcpDest = DEST_PORT
    tcpSeqNo = seq
    tcpAck = ack
    tcpDataOffset = 5

    # Declaring TCP Flags
    tcpFinFlag = finFlag
    tcpSynFlag = synFlag
    tcpRstFlag = 0
    tcpPushFlag = pushFlag
    tcpAckFlag = ackFlag
    tcpUrgFlag = 0
    tcpWindow = socket.htons(cwnd)
    tcpChecksum = 0
    tcpUrgPtr = 0

    tcpOffset = (tcpDataOffset << 4) + 0
    allTcpFlags = tcpFinFlag + (tcpSynFlag << 1) + (tcpRstFlag << 2) + (tcpPushFlag <<3) + (tcpAckFlag << 4) + (tcpUrgFlag << 5)



    #PACK tcp header
    packedTcpHeader = pack('!HHLLBBHHH', tcpSrc, tcpDest, tcpSeqNo, tcpAck, tcpOffset, allTcpFlags,  tcpWindow, tcpChecksum, tcpUrgPtr)


    usrData = message



    sourceAddress = socket.inet_aton(SOURCE_IP)
    destAddress = socket.inet_aton(DEST_IP)
    placeholder = 0
    protocol = socket.IPPROTO_TCP

    # Determine total length ( header + data)
    totTcpLen = len(packedTcpHeader) + len(usrData)


    # include total length
    psh = pack('!4s4sBBH' , sourceAddress , destAddress , placeholder , protocol , totTcpLen);
    psh = psh + packedTcpHeader + usrData;

    tcpChecksum = checksum(psh)



    packedTcpHeader = pack('!HHLLBBH' , tcpSrc, tcpDest, tcpSeqNo, tcpAck, tcpOffset, allTcpFlags,  tcpWindow) + pack('H' , tcpChecksum) + pack('!H' , tcpUrgPtr)


    # Complete Packet
    packet = packedIpHeader + packedTcpHeader + usrData


    sendSocket.sendto(packet, (DEST_IP, DEST_PORT))

    return


# Utility function to receive packets
def receivePacket(r,packetSequenceNumber,expectedServerSeq,sendSocket, message, seq, ack,synFlag,ackFlag,pushFlag,finFlag,cwnd):


    # Time out check
    startTime = time.time()

    timeOutccured = 0

    while True:



        packet = r.recvfrom(65565)


        packet = packet[0]

        #Slice packet header
        ip_header = packet[0:20]


        unpackIpHeader = unpack('!BBHHHBBH4s4s' , ip_header)

        verIhl = unpackIpHeader[0]

        ihl = verIhl & 0xF

        iphLen = ihl * 4


        headerTCP = packet[iphLen:iphLen+20]


        unpackedTcpHeader = unpack('!HHLLBBHHH' , headerTCP)

        #Extract ports, acks and seqs
        destPort = unpackedTcpHeader[1]
        sequence = unpackedTcpHeader[2]
        acknowledgement = unpackedTcpHeader[3]
        reservedDataOffset = unpackedTcpHeader[4]

        #Extract flags
        flags = unpackedTcpHeader[5]


        tcph_length = reservedDataOffset >> 4


        data = ''

        # Check if packet is for intended destination port
        if destPort == SOURCE_PORT:

            endTime = time.time()
            if endTime - startTime > 60:

                #Timeout occured
                timeOutccured = 1
                sendPacket(sendSocket, message, seq, ack,synFlag,ackFlag,pushFlag,finFlag,cwnd)
                continue;

            if expectedServerSeq!= -1 and acknowledgement == packetSequenceNumber and sequence == expectedServerSeq:

                h_size = iphLen + tcph_length * 4


                #Extract data segment
                data = packet[h_size:]


            return acknowledgement, sequence+1,data,flags,timeOutccured


def main(argv):

    try:

        #create 2 Sockets. One for receiving .One for sending.
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            r = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except socket.error, msg:
            print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        global HOST
        global URL
        global DEST_IP
        global SOURCE_IP
        input = argv[1]

        #URL PARSING

        if("://" not in input):
            print "Please enter a valid URL ! "
            sys.exit(0)
        pattern = "http://"
        hostIndex = input.rindex(pattern) + len(pattern)
        resourceIndex = input.find('/',hostIndex)
        if resourceIndex!=-1 and input[resourceIndex:]!='/':
            HOST = input[hostIndex:resourceIndex]
            URL = input[resourceIndex:]
            lastIndex = URL.rindex('/')

            outputFile = URL[lastIndex+1:]

        else:
            HOST = input[hostIndex:]
            if HOST.endswith('/'):
                HOST = HOST[:len(HOST)-1]
            URL = '/'
            outputFile = "index.html"

        if "." not in outputFile:
            outputFile = "index.html"
            if not URL.endswith('/'):
                URL += '/'


        DEST_IP = socket.gethostbyname(HOST)
        SOURCE_IP = getMyMachineIP()

        # Start 3-Way Handshake

        sendPacket(s, '', SEQ_NUMBER, 0, 1, 0, 0,0,1);

        newSequenceNumber, newAckNumber, data,flags,timeOut = receivePacket(r, SEQ_NUMBER+1,-1,s, '', SEQ_NUMBER, 0, 1, 0, 0,0,1)

        sendPacket(s, '', newSequenceNumber, newAckNumber, 0, 1, 0,0,2);

        # Three way handshake is done. Proceed to make Get Request

        httpMessage = "GET " + URL + " HTTP/1.0\n" + "Host: " + HOST + "\r\n\r\n"


        sendPacket(s, httpMessage, newSequenceNumber, newAckNumber, 0, 1, 1,0,3);

        expectedServerSeq = newAckNumber

        final_data = ''
        count = 0
        i = 0
        cwin = 3
        newSequenceNumber += len(httpMessage)

        # Loop until we get a HTTP 200 and Fin
        while True:

            if i == 0:
                newSequenceNumber, newAckNumber, data, flags,timeOut = receivePacket(r, newSequenceNumber,expectedServerSeq,s, httpMessage, newSequenceNumber, newAckNumber, 0, 1, 1,0,3)
            else:
                newSequenceNumber, newAckNumber, data, flags,timeOut = receivePacket(r, newSequenceNumber,expectedServerSeq,s, '', newSequenceNumber, newAckNumber, 0, 1, 0,0,cwin)


            # Reset Congestion window incase of a timout
            if timeOut:
                cwin  = 1
            else:
                cwin = cwin *2


            if(cwin>1000):
                cwin = 1000

            expectedServerSeq += len(data)

            if not data == '':
                sendPacket(s, '', newSequenceNumber, newAckNumber, 0, 1, 0,0,cwin);

                if 'HTTP/1.1 200 OK\r' in data and 'Content-Type:' in data:

                    data = data.split("\r\n\r\n")[1]
                    final_data += data
                else:
                    final_data += data


            # Fin set.
            if flags == 25:
                sendPacket(s, '', newSequenceNumber, newAckNumber+len(data), 0, 1, 0,1,cwin);
                break

            i = i+1


        # Write output to disk
        text_file = open(outputFile, "w")
        text_file.write(final_data)
        text_file.close()

        #Close sockets
        s.close()
        r.close()

    except:
        print "Uh oh. Some thing terrible happened. Here's what may have happened:\n" + str(sys.exc_info())
        s.close()
        r.close()

if __name__ == "__main__":
   main(sys.argv)
