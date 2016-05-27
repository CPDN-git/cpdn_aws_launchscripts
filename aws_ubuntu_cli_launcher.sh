#!/bin/bash
#
# Example script using the AWS CLI to run EC2 instances
# BenchmarkingLogs iam-role gives instances access to s3 buckets
# boot script to set up the instances is the UserData: aws_bootscript_multiproc.sh
#
#
# first guess at spot price and volumesize:
#		large -> .05	VolumeSize -> 8
#		xlarge -> .1	VolumeSize -> 8
#		2xlarge -> .2	VolumeSize -> 8
#		4large -> .4	VolumeSize -> 12
#		8xlarge -> 1.	VolumeSize -> 24
#
# Subnets:
# subnet-5a4b8b03: us-east-1a 
# subnet-f08a69db: us-east-1c
# subnet-ec95349b: us-east-1d
# subnet-b58e2988: us-east-1e
#
# IAM Role:
# # BenchmarkingLogs iam-role (arn:aws:iam::677365467450:instance-profile/BenchmarkingLogs) 
# gives instances access to s3 buckets: read from "cpdn-local-run" and read/write to benchmarkinglogs
#
# Amazon Machine Images
# ami-d05e75b8 Ubuntu (May need changing as updates are made)
# ami-f5f41398 Amazon Linux (would need modification to the bootscripts to work). 
#
# Boot scripts:
# Local tests: use this UserData script: aws_bootscript_multiproc.sh
# Boinc runs: use aws_ubuntu_cli_launcher.sh (at the moment this is hard coded to wah2) 

if [ "$#" -eq 0 ];then
	echo "Usage:  aws_ubuntu_cli_launcher.sh <bootscript>"
	echo "Please enter the name of the boot/UserData script to use"
	exit
fi

aws ec2 request-spot-instances \
--spot-price 0.1 \
--instance-count 1 \
--profile testuser \
--launch-specification \
"{\
	\"ImageId\": \"ami-d05e75b8\", \
	\"KeyName\": \"pu_key\", \
	\"SecurityGroupIds\": [ \"sg-32b55654\" ], \
	\"InstanceType\": \"c4.large\", \
	\"IamInstanceProfile\": {\"Arn\": \"arn:aws:iam::677365467450:instance-profile/BenchmarkingLogs\" }, \
	\"UserData\": \"`base64 $1`\", \
	\"SubnetId\": \"subnet-5a4b8b03\", \
	\"BlockDeviceMappings\": [{\"DeviceName\": \"/dev/sda1\",\"Ebs\":{\"VolumeSize\":8}}] \
"}
