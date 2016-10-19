import subprocess


cdnname = "cs5700cdn.example.com"
port = 44300
origin = "ec2-54-88-98-7.compute-1.amazonaws.com"
username = 'raghu147'
keyfile = '/home/raghu/.ssh/id_dsa'


print "Calling make..."
make = subprocess.Popen(['make'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

subprocess.call(['chmod', '+x', 'deployCDN'])
subprocess.call(['chmod', '+x', 'runCDN'])
subprocess.call(['chmod', '+x', 'stopCDN'])


#
# print "Calling deployCDN..."
# try:
#         out = subprocess.Popen(['./deployCDN', "-p", "%i" % port, "-o", "%s" % origin,"-n", "%s" % cdnname, "-u", "%s" % username, "-i", "%s" % keyfile], stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]
#         print ' '.join(["./deployCDN", "-p", "%i" % port, "-o", "%s" % origin, "-n", "%s" % cdnname, "-u", "%s" % username, "-i", "%s" % keyfile])
#         print out
# except:
#         print 'Unable to execute deployCDN'
#         correct_scripts = False
# else:
#         correct_scripts = True
#
# print "Calling runCDN..."
# try:
#         out = subprocess.call(['./runCDN', "-p", " %i" % port, "-o", " %s" % origin,
#                                "-n", "%s" % cdnname, "-u", "%s" % username, "-i", "%s" % keyfile])
#         print out
# except:
#         print 'Unable to execute startCDN'
#         correct_scripts = False

#Do testing here before calling the line below
print "Calling stopCDN..."

out = subprocess.call(['./stopCDN', "-p %i" % port, "-o %s" % origin,
                           "-n %s" % cdnname, "-u %s" % username, "-i %s" % keyfile])
print out

# dig @129.10.117.186 -p 44000 cs5700cdn.example.com
#ssh raghu147@cs5700cdnproject.ccs.neu.edu