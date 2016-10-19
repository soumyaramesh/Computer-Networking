# Experiment 3 TCP file
#argv <out-file> <trace-file> <TCP Variant> <Queue Variant> <tcp-offset-time>

# New simulator object
set ns [new Simulator]

#Colors for data flows (for NAM)
$ns color 1 Blue
$ns color 2 Red

#Open NAM trace file
set nf [open [lindex $argv 0] w]
$ns namtrace-all $nf

#Open the Trace file
set tf [open [lindex $argv 1] w]
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
$ns duplex-link $n1 $n2 10Mb 10ms [lindex $argv 3]
$ns duplex-link $n2 $n3 10Mb 10ms [lindex $argv 3]
$ns duplex-link $n2 $n5 10Mb 10ms [lindex $argv 3]
$ns duplex-link $n3 $n4 10Mb 10ms [lindex $argv 3]
$ns duplex-link $n3 $n6 10Mb 10ms [lindex $argv 3]

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


#Setup a TCP connection and Sink
set tcp [new Agent/[lindex $argv 2]]  
$tcp set class_ 2
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP


#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ 7mb
$cbr set random_ false



#Schedule events for the CBR and FTP agents
$ns at 0.1 "$ftp start"
$ns at 9.0 "$cbr start"
$ns at 25.0 "$ftp stop"
$ns at 25.0 "$cbr stop"

#Detach tcp and sink agents 
$ns at 25.0 "$ns detach-agent $n1 $tcp ; $ns detach-agent $n4 $sink"

$ns at 25.5 "cleanup"

#Run the simulation
$ns run
