import socket, sys
from struct import *
import random
import time
import binascii
import traceback
import struct
import subprocess, shlex
import fcntl

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

    packedTcpHeader = pack('!HHLLBBHHH', tcpSrc, tcpDest, tcpSeqNo, tcpAck, tcpOffset, allTcpFlags,
                      tcpWindow, tcpChecksum, tcpUrgPtr)

    usrData = message

    sourceAddress = socket.inet_aton(SOURCE_IP)
    destAddress = socket.inet_aton(DEST_IP)
    placeholder = 0
    protocol = socket.IPPROTO_TCP

    # Determine total length ( header + data)
    totTcpLen = len(packedTcpHeader) + len(usrData)


    packWithChecksum = pack('!4s4sBBH' , sourceAddress , destAddress , placeholder , protocol , totTcpLen);
    packWithChecksum = packWithChecksum + packedTcpHeader + usrData;

    tcp_check = checksum(packWithChecksum)


    packedTcpHeader = pack('!HHLLBBH' , tcpSrc, tcpDest, seq, ack, tcpOffset, allTcpFlags,  tcpWindow) + \
                      pack('H' , tcp_check) + pack('!H' , tcpUrgPtr)


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


    packedIpHeader = pack('!BBHHHBBH4s4s' , ipIHL, ipTypeOfService, ipTotalLength, ipIdentification, ipOffset, ipTTL,
                          ipProtocol, ipChecksum, ipSrcAddr, ipDestAddr)

    finalIpCheckSum = checksum(packedIpHeader)

    ip_tot_len = 20 + len(packedTcpHeader) + len(message)


    fullIP = pack('!BBHHHBB',ipIHL, ipTypeOfService, ip_tot_len, ipIdentification, ipOffset, ipTTL, ipProtocol) +\
    pack('H',finalIpCheckSum)+ pack('!4s4s',ipSrcAddr, ipDestAddr)



    sourceMacAddress = getSourceMacAddress('eth0').replace(":","")


    destMacAddress = doARPRequest()


    src_addr = binascii.unhexlify(sourceMacAddress)
    dst_addr = binascii.unhexlify(destMacAddress)


    ethernetFrame = pack('!6s6sH',dst_addr,src_addr,0x0800)
    packet = ethernetFrame + fullIP + packedTcpHeader + usrData


    sendSocket.sendto(packet, ('eth0', 0))


    return


# Utility function to receive packets
def receivePacket(r,packetSequenceNumber,expectedServerSeq,sendSocket, message, seq, ack,synFlag,ackFlag,pushFlag,finFlag,cwnd):


    # Time out check
    startTime = time.time()

    timeOutccured = 0

    while True:
        packet = r.recvfrom(65565)

        # Extract packet from tuple string,address
        packet = packet[0]

        #parse ethernet header
        eth_length = 14

        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH' , eth_header)
        eth_protocol = socket.ntohs(eth[2])


        #Parse IP packets, IP Protocol number = 8
        if eth_protocol == 8 :
            #Parse IP header
            #take first 20 characters for the ip header
            ip_header = packet[eth_length:20+eth_length]

            unpackIpHeader = unpack('!BBHHHBBH4s4s' , ip_header)

            verIhl = unpackIpHeader[0]

            ihl = verIhl & 0xF

            iphLen = ihl * 4

            protocol = unpackIpHeader[6]


            # We are interested only in TCP packets
            if protocol == 6 :
                t = iphLen + eth_length
                headerTCP = packet[t:t+20]

                unpackedTcpHeader = unpack('!HHLLBBHHH' , headerTCP)

                # Extract the destination port to filter packets and sequence and ack to verify order
                destPort = unpackedTcpHeader[1]
                sequence = unpackedTcpHeader[2]
                acknowledgement = unpackedTcpHeader[3]
                reservedDataOffset = unpackedTcpHeader[4]

                #Extract flags
                flags = unpackedTcpHeader[5]


                tcph_length = reservedDataOffset >> 4


                #get data from the packet
                h_size = eth_length + iphLen + tcph_length * 4
                data = packet[h_size:]

                # Check if packet is for intended destination port
                if destPort == SOURCE_PORT:

                    endTime = time.time()
                    if endTime - startTime > 60:

                        #Timeout occured
                        timeOutccured = 1
                        sendPacket(sendSocket, message, seq, ack,synFlag,ackFlag,pushFlag,finFlag,cwnd)
                        continue;



                    if expectedServerSeq == -1:
                        return acknowledgement, sequence+1,data,flags,timeOutccured
                    else:
                        if acknowledgement == packetSequenceNumber and sequence == expectedServerSeq:
                            return acknowledgement, sequence+1,data,flags,timeOutccured


def main(argv):
    if len(argv) < 2 :
            print "Please enter a URL argument"
    try:


        #create 2 Sockets. One for receiving .One for sending.
        try:
            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,socket.ntohs(0x0800))
            r = socket.socket(socket.AF_PACKET , socket.SOCK_RAW,socket.ntohs(0x0800))
        except socket.error, msg:
            print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        # bind send socket with eth interface
        s.bind(('eth0', 0))

        global HOST
        global URL
        global DEST_IP
        global SOURCE_IP

        input = argv[1]

        #URL PARSING

        if("://" not in input):
            print "Please enter a valid URL ! "
            sys.exit(0)
        padding = 6
        httpSuccess = True
        pattern = "http://"
        #Extract host and resource from given input
        hostIndex = input.rindex(pattern) + len(pattern)
        resourceIndex = input.find('/',hostIndex)

        #Determine output file
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
            #increment cwnd on successful ACK
                cwin = cwin *2


            if(cwin>1000):
                cwin = 1000


            #If data exists, send ack for the data received
            if not data == '' and len(data) != padding:
                expectedServerSeq += len(data)
                sendPacket(s, '', newSequenceNumber, newAckNumber, 0, 1, 0,0,cwin);

                if 'HTTP/1.1 200 OK\r' in data and 'Content-Type:' in data:

                    data = data.split("\r\n\r\n")[1]
                    final_data += data
                else:
                    final_data += data
                #If 200 OK was not found, report error and exit
                if not httpSuccess:
                    print "Http 200 status code was not found. Please retry."
                    sys.exit(0)

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

    except Exception, err:

        print "\nAn Error has occured Here's the stacktrace ----- \n\n"
        traceback.print_exc()

        s.close()
        r.close()


#Method to get the gateway IP
def getGateWayIP():
    splitstr = 'ip r l'
    shlexSplit = shlex.split(splitstr)
    splitIP = subprocess.check_output(shlexSplit)
    defaultGateway = splitIP.split('default via')[-1].split()[0]
    hostIP  = splitIP.split('src')[-1].split()[0]
    return defaultGateway,hostIP


#Method to get source Mac address
def getSourceMacAddress(eth):
    x = 0x8927
    packedEth = struct.pack('256s', eth[:15])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp = fcntl.ioctl(s.fileno(), x , packedEth )
    return ':'.join(['%02x' % ord(i) for i in temp[18:24]])

#Method to resolve dest mac address
def doARPRequest():

    hardwareType = 1  # hardware type = 1 for ethernet
    macSrc = getSourceMacAddress('eth0').replace(":","")
    protType = 0x0800  # protocol type ip
    macTarget = '000000000000' #tempMac
    mlen = 6  # length of hardware address
    protolen = 4  # length of IP address
    oc = 1  # operational code = 1 for req
    gatewayIP ,hostIP = getGateWayIP()
    #constructing the arp header
    arpHeader = struct.pack('!HHBBH6s4s6s4s',hardwareType,
                           protType,mlen,protolen,oc,
                           binascii.unhexlify(macSrc),socket.inet_aton(hostIP),
                           binascii.unhexlify(macTarget),
                           socket.inet_aton(gatewayIP))

    #Ethernet Header fields
    ethDest = 'ffffffffffff' #broadcast
    ethProt = 0x0806
    # constructing the ethernet header
    ethernetHeader = struct.pack('!6s6sH',binascii.unhexlify(ethDest),binascii.unhexlify(macSrc),ethProt) + arpHeader

    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    r = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0806))

    s.bind(('eth0', 0))
    s.sendto(ethernetHeader, ('eth0', 0))


    while True:
        data = r.recv(65535)
        dstr = str(binascii.b2a_hex(data))

        srcMAC = dstr[0:12]
        if srcMAC == macSrc:
            targetMac = dstr[12:24]
            s.close()
            r.close()
            return targetMac
            break;

    s.close()
    r.close()


if __name__ == "__main__":
   main(sys.argv)