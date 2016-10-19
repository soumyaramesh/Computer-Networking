
# Grepping for phone specific Stuff
os=$(grep -ic "Android" $1)

#"Operating System Build Number"
build=$( grep -ic "MHC19Q" $1)

# IMEI
imei=$( grep -ic "35362707271577" $1)

#"Wifi Mac Address"
mac=$( grep -ic "64:bc:0c:7e:26:6c" $1)

# "Advertiser ID"
adID=$( grep -ic "7d87e7f9-9c6a-4d76-92a7-efb28e40155c" $1)

#Grepping for Location specific information

# Address
addr=$( grep -ic "Judge Street" $1)

# "User's zipcode"
zip1=$( grep -ic "02120" $1)


# Grepping for User specific information

# "GPS- Latitude"
lat=$( grep -c "40.7" $1)

# "GPS- Longitude"
lon=$( grep -c "74.0" $1)

# "Zipcode"
zip2=$( grep -ic "10028" $1)

#"Home Address"
addr2=$( grep -ic "New York" $1)

# "Username"
uname=$( grep -ic "trahkrub123" $1)

# "Password"
pass=$( grep -ic "projectRecon567" $1)

# "Email"
email=$( grep -ic "trahkrub@gmail.com" $1)

# "First Name"
fname=$( grep -ic "Alexander" $1)

# "Last name"
lName=$( grep -ic "Burkhart" $1)

# "Birthdate"
bday=$( grep -ic "01 Jan 1990" $1)


# Results

#echo  $1  $os "\t" $build "\t" $imei "\t" $mac "\t" $adID "\t" $addr "\t" $zip1 "\t" $lat "\t" $lon "\t" $zip2 "\t" $addr2 "\t" $uname "\t" $pass "\t" $email "\t" $fname "\t" $lName

echo  $1  " OS="$os " Build=" $build " IMEI=" $imei " MAC=" $mac " AD_ID=" $adID " Physical-Addr=" $addr " PhysicalZIP=" $zip1 " LAT=" $lat " LONG=" $lon " ZIP=" $zip2 " ADDR=" $addr2 " UNAME=" $uname " PASS=" $pass " EMAIL=" $email " FNAME=" $fname " LASTNAME=" $lName " BDAY="$bday
echo "\n"



