import socket, sys
import binascii
import struct
import traceback


from Client import getBestIP

# scamper -c 'ping -c 1' -i 139.130.4.5 |awk 'NR==2 {print $7}'

CDN_NAME = 'cs5700cdn.example.com'

# Method to get current Host IP
def getMyMachineIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))

    machineIP =  sock.getsockname()[0]
    sock.close()
    return machineIP

def main(args):


    try:


        if len(args) != 6:

            print " Use this format  :  ./dnsserver.sh -p <high port number> - n <name> "
            exit(0)

        port = int(args[3])
        Name = args[5]

        domainName = Name.replace(".","")



        s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s1.bind((getMyMachineIP(),port))

        print 'DNS Server bound to port:' + str(port)

        # Wait for DNS Request
        while True:

            data = s1.recvfrom(65535)

            #Client IP
            clientAddress = str(data[1][0])

            #print 'Client Address ' + clientAddress

            request = str(binascii.b2a_hex(data[0]))

            #print "ENTIRE REQUEST="+request
            fullPacket = data[0]


            #Header
            header = fullPacket[:12]
            question = fullPacket[12:]

            #print "HEADER=" + request[:12]
            #print "QUESTION=" + request[12:]
            id,flags,qcount,acount,nscount,arcount = struct.unpack('>HHHHHH',header)

            # Read one octet at a time

            start = 0

            query = ''
            # Get the entire question
            while True:

                size = binascii.b2a_hex(question[start:start+1])

                if str(size) == '00':
                    break;

                start += 1

                query += binascii.b2a_hex(question[start:start+int(size,16)])
                start += int(size,16)



            name =  str(query).decode("hex")

            # Look for CDN Specific name
            if domainName == name:

                #Get the best IP for the client
                ec2hostIP = getBestIP(clientAddress)
                print 'DNS Resolved ' + name + ' to ' + ec2hostIP

                splits = ec2hostIP.split('.')

                ec2IPhex = ''

                for x in range(0, 4):
                    val = hex(int(splits[x])).replace('0x','')
                    if len(val) == 1:
                        ec2IPhex += '0' + val
                    else:
                        ec2IPhex += val

                #Build answer
                answer = binascii.a2b_hex('c00c00010001000002580004'+ec2IPhex)

                flags = 33152
                newHeader = struct.pack('>HHHHHH',id,flags,1,1,0,0)

                #Build complete response
                response = newHeader + question[:start+5] + answer


                #Send response back to client
                s1.sendto(response, data[1])

            else:
                print 'Reqeust came from an invalid domain'


        s1.close()


    except Exception, err:
        traceback.print_exc()
        s1.close()


if __name__ == "__main__":
   main(sys.argv)
