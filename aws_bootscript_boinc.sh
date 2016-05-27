#!/bin/bash
# Boot script for AWS Ubuntu VM to run CPDN runs through boinc

# Install required packages for Ubuntu
sudo apt-get update
sudo apt-get -y install awscli lib32stdc++6 lib32z1 boinc

# Print date to see how long this has taken
date

# Connect to boinc project
cd /var/lib/boinc-client
# Note, use weak key here which allows connecting to the account but no other priviledges
/usr/bin/boinccmd --project_attach  climateprediction.net 719090_2767af3011b21b35f3933065d7c2f317

# Wait 65 minutes to allow boinc to get tasks (because one hour timeout)
# Then prevent boinc from getting new work
sleep 3900 
/usr/bin/boinccmd --project  climateprediction.net nomorework

# Wait until model runs have finished
# NOTE: this is hardcoded to check for wah2
echo "Polling whether script is still running"
while ps -e | grep wah2; do
        sleep  60 # Wait a minute
done

# Clean up and shut down
/usr/bin/boinccmd --project  climateprediction.net detach
sleep 5
sudo shutdown -h now
