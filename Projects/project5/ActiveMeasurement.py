# This file is used to run a program to perform Active measuremnts


import commands
import SocketServer
import sys

#Class to handle Socket request
class Handler(SocketServer.BaseRequestHandler):

    def handle(self):

        # Get the IP of the client
        IP = self.request.recv(1024)

        #print 'IP=' + IP

        latency = ''

        try:

            # Use Scamper to determine the latency of the Requesting Client identified by the IP
            scamperCommand = "scamper -c 'ping -c 1' -i "+IP

            # Get the output of the system command
            output = commands.getoutput(scamperCommand)
            print "Output=" + output
            #Parse and get the Latency
            latency = output.split("\n")[1].split("time=")[1].split(" ")[0]

        except Exception:
            latency = 'Error'

        #print latency

        # Send latency to requester
        self.request.sendall(latency)

        return

def main(argv):

    port = int(argv[1])
    addr = ('', port)

    # Start an active measurement system which listenes to a given port
    server = SocketServer.TCPServer(addr, Handler);


    print 'Active Measurement Server Listening at ' + str(port) + "..."


    server.serve_forever()

if __name__ == '__main__':
    main(sys.argv)