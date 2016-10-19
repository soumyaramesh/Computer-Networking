# Experiment 2 TCP file
#arguments <cbr-rate> <out-file> <name-file> <tcp-1> <tcp-2> <offset>
# New simulator object
set ns [new Simulator]

#Colors for data flows (for NAM)
$ns color 1 Blue
$ns color 2 Green
$ns color 3 Red

#Open NAM trace file
set nf [open [lindex $argv 1] w]
$ns namtrace-all $nf

#Open the Trace file
set tf [open [lindex $argv 2] w]
$ns trace-all $tf

#Define a 'cleanup' procedure

proc cleanup {} {
        global ns nf tf
        $ns flush-trace

        #Close the NAM trace file
        close $nf

        #Close the Trace file
        close $tf

        #Execute NAM on the trace file
        exit 0
}

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n2 $n5 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10

#Node positions for NAM
$ns duplex-link-op $n1 $n2 orient right-down
$ns duplex-link-op $n5 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n3 $n6 orient right-down

#Monitor the queue for link (n2-n3). (for NAM)
$ns duplex-link-op $n2 $n3 queuePos 0.5


#Setup a TCP connection-1 and Sink-1
set tcp1 [new Agent/[lindex $argv 3]] 
$tcp1 set class_ 2
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1

#Setup a FTP over TCP connection
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP


#Setup a TCP connection-2 and Sink-2
set tcp2 [new Agent/[lindex $argv 4]]
$tcp2 set class_ 2
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2

#Setup a FTP over TCP connection
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP


#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 3

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ [lindex $argv 0]
$cbr set random_ false

set tcp_start [ expr 1.0 + [lindex $argv 5]]

#Schedule events for the CBR and FTP agents
$ns at 1.0 "$cbr start"	
$ns at $tcp_start "$ftp1 start"
$ns at $tcp_start "$ftp2 start"
$ns at 9.0 "$ftp1 stop"
$ns at 9.0 "$ftp2 stop"
$ns at 9.5 "$cbr stop"

#Detach tcp and sink agents 
$ns at 9.5 "$ns detach-agent $n1 $tcp1 ; $ns detach-agent $n4 $sink1"
$ns at 9.5 "$ns detach-agent $n5 $tcp2 ; $ns detach-agent $n6 $sink2"


$ns at 10.0 "cleanup"

#Run the simulation
$ns run
