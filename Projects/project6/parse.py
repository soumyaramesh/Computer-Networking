
import glob
import os



logFiles = glob.glob("logs/*.log")


#os.system('echo  "\t\t\t\t\t\t" "OS" "\t" "Build" "\t" "IMEI" "\t" "MAC" "\t" "AdID" "\t" "Addr1" "\t" "Zip" "\t" "Lat" "\t" "Long" "\t" "Zip" "\t" "Addr2" "\t" "Uname" "\t" "Pass" "\t" "Email" "\t" "Fname" "\t" "Lname"')
for eachFile in logFiles:
    os.system("./grepForStuff.sh "+eachFile)

logFiles = glob.glob("logs/*.log")

addrSet = {}

# Exclude these domains
defaultSet = {'soundcloud','letgo','theweatherchannel','smule'}


# Loop through each log file
for eachFile in logFiles:
    count  = 0
    with open(eachFile) as f:
        for line in f:
	    # Read every GET Request
            if "GET\t" in line:
                startIndex = line.find("GET")
                remaining = line[startIndex:]

                splitArray = remaining.split("\t")
		
		# Extract Host Name
                hostName = splitArray[1]

                notDefault = True
		#Check if present in Host list
                for default in defaultSet:
                    if default in hostName:
                        notDefault = False
                        break;
		# Add if required
                if notDefault:
                    if hostName not in addrSet:
                        addrSet[hostName] = str(1)
                    else:
                        val = int(addrSet[hostName])
                        addrSet[hostName] = str(val + 1)

		#Read every post REQUEST
            if "POST\t" in line:
                startIndex = line.find("POST")
                remaining = line[startIndex:]


                splitArray = remaining.split("\t")

                hostName = splitArray[1]
                notDefault = True
                for default in defaultSet:
                    if default in hostName:
                        notDefault = False
                        break;

		#Add if necessary
                if notDefault:
                    if hostName not in addrSet:
                        addrSet[hostName] = str(1)
                    else:
                        val = int(addrSet[hostName])
                        addrSet[hostName] = str(val + 1)



print "Sites Contacted "
for addr in addrSet:
    print addr + ":" + addrSet[addr]
