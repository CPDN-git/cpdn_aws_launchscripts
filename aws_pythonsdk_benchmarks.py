#!/usr/bin/python
# Script to do stuff with the python AWS API, boto3
import boto3
from datetime import datetime
import os
import base64

client = boto3.client('ec2')

# This function launches one or more EC2 instance 
# using the input parameters provided
# Submits request though the AWS CLI (TODO could do this natively in python boto3 API)
def launch_test(instance_type,count,max_price,zone,volumesize):

	# Dictionary of availability zones and the subnet to use for each. 
	subnet_map={'us-east-1a':'subnet-5a4b8b03',
	'us-east-1c':'subnet-f08a69db',
	'us-east-1d':'subnet-ec95349b',
	'us-east-1e':'subnet-b58e2988'}
		
	# Convert boot script into base64 data
	with open('/Users/pete/src/AWS/aws_bootscript_multiproc.sh','r') as f:
		userdata=base64.b64encode(f.read())
	
	# Write out launch specification json file
	#
	launch_json=open('launch.json','w')
	launch_spec='{"ImageId": "ami-d05e75b8", \
	"KeyName": "pu_key", \
	"SecurityGroupIds": [ "sg-32b55654" ], \
	"InstanceType": "'+instance_type+'", \
	"IamInstanceProfile": {"Arn": "arn:aws:iam::677365467450:instance-profile/BenchmarkingLogs" }, \
	"UserData": "'+userdata+'", \
	"SubnetId": "'+subnet_map[zone]+'", \
	"BlockDeviceMappings": [{"DeviceName": "/dev/sda1","Ebs":{"VolumeSize":'+str(volumesize)+'}}] \
	}'
	launch_json.write(launch_spec)
	launch_json.close()
	
	# Run aws cli command
	cmd='aws ec2 request-spot-instances \
--spot-price '+str(max_price)+' \
--instance-count '+str(count)+' \
--profile testuser \
--launch-specification file://launch.json'
	print cmd
	os.system(cmd)


# List of Volume Sizes needed (dependent on number of CPUs):
# NOTE: commented out instances are not available with HVM virtualisation 
#  and would require a different submission process
volume_size={'c4.large':8,
			'c4.xlarge':8,
			'c4.2xlarge':8,
			'c4.4xlarge':12,
			'c4.8xlarge':24,
			'm4.large':8,
			'm4.xlarge':8,
			'm4.2xlarge':8,
			'm4.4xlarge':12,
			'm4.10xlarge':30,
			'm3.medium':8,
			'm3.large':8,
			'm3.xlarge':8,
			'm3.2xlarge':8,
			'c3.large':8,
			'c3.xlarge':8,
			'c3.2xlarge':8,
			'c3.4xlarge':12,
			'c3.8xlarge':24,
			'r3.large':8,
			'r3.xlarge':8,
			'r3.2xlarge':8,
			'r3.4xlarge':12,
			'r3.8xlarge':24,
			'i2.xlarge':8,
			'i2.2xlarge':8,
			'i2.4xlarge':12,
			'i2.8xlarge':24,
#			'm1.small':8,
#			'm1.medium':8,
#			'm1.large':8,
#			'm1.xlarge':8,
#			'c1.medium':8,
#			'c1.xlarge':8,
			'cc2.8xlarge':24,
#			'm2.xlarge':8,
#			'm2.2xlarge':8,
#			'm2.4xlarge':12,
			'cr1.8xlarge':24,
			'hi1.4xlarge':12,
#			'hs1.8xlarge':12,
#			't1.micro':8
}



### Launch instances in best availability zone ###
#
def launch_instances():
	### Just test a few instances at a time ###
	#
	#instances=['c3.2xlarge','c4.4xlarge','cc2.8xlarge','m3.large']
	#instances=['c4.large','c4.xlarge','c4.2xlarge','c4.8xlarge']
	#instances=['m4.xlarge','m4.2xlarge','m4.4xlarge','m4.10xlarge']
	#instances=['m3.medium','m3.xlarge','m3.2xlarge','m4.large']
	#instances=['c3.large','c3.xlarge','c3.4xlarge','c3.8xlarge']
	#instances=['r3.large','r3.xlarge','r3.2xlarge','r3.4xlarge','r3.8xlarge']
	#instances=['i2.xlarge','i2.2xlarge','i2.4xlarge','i2.8xlarge']
	#instances=['cr1.8xlarge','hi1.4xlarge']
	instances=[]

	# Loop over instances and determine lowest current spot price and which availability zone that corresponds to
	for inst in instances:
	#	print inst
		prices=client.describe_spot_price_history(StartTime=datetime.now(),InstanceTypes=[inst], ProductDescriptions=['Linux/UNIX (Amazon VPC)'])['SpotPriceHistory']
		min_price=9999999
		for dict in prices:
			if float(dict['SpotPrice'])<min_price:
				min_zone=dict['AvailabilityZone']
				min_price=float(dict['SpotPrice'])
		# Launch tests for this instance (using bid price of 5 * current price)
		launch_test(inst,3,5.*min_price,min_zone,volume_size[inst])

### Go through all Instance types and work out best AZ and spot price
#
def get_instance_info():
	best_zone={}
	spot_price={}

	# Loop over instances and determine lowest current spot price and which availability zone that corresponds to
	for inst,size in volume_size.iteritems():	
		prices=client.describe_spot_price_history(StartTime=datetime.now(),InstanceTypes=[inst], ProductDescriptions=['Linux/UNIX (Amazon VPC)'])['SpotPriceHistory']
		min_price=9999999
		for dict in prices:
			if float(dict['SpotPrice'])<min_price:
				min_zone=dict['AvailabilityZone']
				min_price=float(dict['SpotPrice'])
		best_zone[inst]=min_zone
		spot_price[inst]=min_price
	
#	instances=volume_size.keys()
#	instances.sort()
#	for inst in instances:
#		print inst,best_zone[inst],spot_price[inst]
	
	return spot_price
		
if __name__=='__main__':
	launch_instances()
	
