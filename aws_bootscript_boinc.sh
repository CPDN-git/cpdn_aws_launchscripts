#!/bin/bash
# Boot script for AWS Ubuntu VM to run CPDN runs through boinc

# Install required packages for Ubuntu
sudo apt-get update
sudo apt-get -y install awscli lib32stdc++6 lib32z1 boinc

# Print date to see how long this has taken
date

# Connect to boinc project
cd /var/lib/boinc-client
project='http://vorvadoss.oerc.ox.ac.uk/cpdnboinc_dev'

# Note, use weak key here which allows connecting to the account but no other priviledges
#/usr/bin/boinccmd --project_attach  climateprediction.net 719090_2767af3011b21b35f3933065d7c2f317
#/usr/bin/boinccmd --project_attach http://vorvadoss.oerc.ox.ac.uk/cpdnboinc_dev 18_5fb8e5a06e3df0d9f3d5f96279bb6301
/usr/bin/boinccmd --project_attach $project 4_ea54e29df214e285ec05ff607f3333ae

# Get instance information
TYPE=`curl http://169.254.169.254/latest/meta-data/instance-type`
EC2ID=`curl http://169.254.169.254/latest/meta-data/instance-id`
BATCH='dev_test1'

# Wait 65 minutes to allow boinc to get tasks (because one hour timeout)
sleep 3900 

# List workunits running on this instance:
/usr/bin/boinccmd --get_tasks|grep '^\   name' > tasks.txt

# Then prevent boinc from getting new work
#/usr/bin/boinccmd --project  $project nomorework
/usr/bin/boinccmd --project  $project detach_when_done

echo "Polling whether boinc is still connected"
# Note could also check against --get_tasks (if not detaching)
while /usr/bin/boinccmd --get_project_status|grep '1)'; do
	# check spot termination
	if curl -s http://169.254.169.254/latest/meta-data/spot/termination-time | grep -q .*T.*Z; then 
		# Update project in case we have successful tasks to report
		/usr/bin/boinccmd --project $project update 
		# Report instance uptime
		uptime > timing.txt
		aws s3 cp timing.txt    s3://benchmarkinglogs/$BATCH/$TYPE/terminated_${EC2ID}.txt --region=us-east-1
		aws s3 cp tasks.txt    s3://benchmarkinglogs/$BATCH/$TYPE/tasks_${EC2ID}.txt --region=us-east-1
		sleep 10
		/usr/bin/boinccmd --project $project detach
	fi
	sleep  60 # Wait a minute
done

# Make sure the project has reported (not needed if detach_when_done)
#sleep 30
#/usr/bin/boinccmd --project $project update 
#sleep 30
#/usr/bin/boinccmd --project $project detach

# TODO upload report of successful exit and uptime. 
df -h |grep xvda1 > diskusage.txt
uptime > timing.txt
aws s3 cp timing.txt    s3://benchmarkinglogs/$BATCH/$TYPE/complete_${EC2ID}.txt --region=us-east-1
aws s3 cp tasks.txt    s3://benchmarkinglogs/$BATCH/$TYPE/tasks_${EC2ID}.txt --region=us-east-1
aws s3 cp diskusage.txt    s3://benchmarkinglogs/$BATCH/$TYPE/diskusage_${EC2ID}.txt --region=us-east-1

# Clean up and shut down
#sleep 5
sudo shutdown -h now
