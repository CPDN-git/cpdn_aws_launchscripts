#!/usr/bin/python
# Script to do stuff with the python AWS API, boto3
import boto3
from datetime import datetime,timedelta
import os
import base64
from aws_pythonsdk_benchmarks import get_instance_info
from analyse_benchmarks import get_benchmarks,get_weights
from copy import deepcopy



# This function launches one or more EC2 instance 
# using the input parameters provided
# Submits request though the AWS CLI (TODO could do this natively in python boto3 API)
def launch_fleet(instance_types,targetCapacity,bootscript,dry_run=False,region='us-east-1'):

	client = boto3.client('ec2',region_name=region)
	
	print "Getting instance info..."
	instance_price=get_instance_info()
	print "Got prices"
	types,runs=get_benchmarks()
	print "Got Benchmarks"
	weights=get_weights(types,runs)
	print "Got weighting factors"

	if region=='us-east-1':
		ami_image="ami-fce3c696" # Ubuntu 14.04
		security_group="sg-32b55654" # Allow ssh
		# Dictionary of availability zones and the subnet to use for each. 
		subnet_map={
		'us-east-1a':'subnet-5a4b8b03',
		'us-east-1c':'subnet-f08a69db',
		'us-east-1d':'subnet-ec95349b',
		'us-east-1e':'subnet-b58e2988'
		}
		key='pu_key'
	elif region=='us-west-2':
		ami_image="ami-9abea4fb" # Ubuntu 14.04
		security_group='sg-67488a01' # Allow ssh
		subnet_map={
		'us-west-2a':'subnet-22ebde47',
		'us-west-2c':'subnet-8b0163d2',
		'us-west-2b':'subnet-df8dc6a8'
		}
		key='pu_key_oregon'
	

	# List of Volume Sizes needed (dependent on number of CPUs):
	# NOTE: commented out instances are not available with HVM virtualisation 
	#	and would require a different submission process
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
	
	launch_template={
		"ImageId": ami_image,
		"InstanceType": "c3.large",
		"KeyName": key,
		"EbsOptimized": False,
		"WeightedCapacity": 2,
		"SpotPrice": "0.0525",
		"IamInstanceProfile": {"Arn": "arn:aws:iam::677365467450:instance-profile/BenchmarkingLogs"},
		"BlockDeviceMappings": [
			{
				"DeviceName": "/dev/sda1",
				"Ebs": {
					"DeleteOnTermination": True,
					"VolumeType": "gp2",
					"VolumeSize": 8,
#					"SnapshotId": "snap-f70deff0"
				}
			}
		],
		"Placement": {"AvailabilityZone": "us-east-1a"},
		"UserData": "IyEvYmluL2Jhc2gKIyBCb290IHNjcmlwdCBmb3IgQVdTIFVidW50dSBWTSB0byBydW4gQ1BETiBydW5zIHRocm91Z2ggYm9pbmMKCiMgSW5zdGFsbCByZXF1aXJlZCBwYWNrYWdlcyBmb3IgVWJ1bnR1CnN1ZG8gYXB0LWdldCB1cGRhdGUKc3VkbyBhcHQtZ2V0IC15IGluc3RhbGwgYXdzY2xpIGxpYjMyc3RkYysrNiBsaWIzMnoxIGJvaW5jCgojIFByaW50IGRhdGUgdG8gc2VlIGhvdyBsb25nIHRoaXMgaGFzIHRha2VuCmRhdGUKCiMgQ29ubmVjdCB0byBib2luYyBwcm9qZWN0CmNkIC92YXIvbGliL2JvaW5jLWNsaWVudAojIE5vdGUsIHVzZSB3ZWFrIGtleSBoZXJlIHdoaWNoIGFsbG93cyBjb25uZWN0aW5nIHRvIHRoZSBhY2NvdW50IGJ1dCBubyBvdGhlciBwcml2aWxlZGdlcwovdXNyL2Jpbi9ib2luY2NtZCAtLXByb2plY3RfYXR0YWNoICBjbGltYXRlcHJlZGljdGlvbi5uZXQgNzE5MDkwXzI3NjdhZjMwMTFiMjFiMzVmMzkzMzA2NWQ3YzJmMzE3CgojIFdhaXQgNjUgbWludXRlcyB0byBhbGxvdyBib2luYyB0byBnZXQgdGFza3MgKGJlY2F1c2Ugb25lIGhvdXIgdGltZW91dCkKIyBUaGVuIHByZXZlbnQgYm9pbmMgZnJvbSBnZXR0aW5nIG5ldyB3b3JrCnNsZWVwIDM5MDAgCi91c3IvYmluL2JvaW5jY21kIC0tcHJvamVjdCAgY2xpbWF0ZXByZWRpY3Rpb24ubmV0IG5vbW9yZXdvcmsKCiMgV2FpdCB1bnRpbCBtb2RlbCBydW5zIGhhdmUgZmluaXNoZWQKIyBOT1RFOiB0aGlzIGlzIGhhcmRjb2RlZCB0byBjaGVjayBmb3Igd2FoMgplY2hvICJQb2xsaW5nIHdoZXRoZXIgc2NyaXB0IGlzIHN0aWxsIHJ1bm5pbmciCndoaWxlIHBzIC1lIHwgZ3JlcCB3YWgyOyBkbwogICAgICAgIHNsZWVwICA2MCAjIFdhaXQgYSBtaW51dGUKZG9uZQoKIyBDbGVhbiB1cCBhbmQgc2h1dCBkb3duCi91c3IvYmluL2JvaW5jY21kIC0tcHJvamVjdCAgY2xpbWF0ZXByZWRpY3Rpb24ubmV0IGRldGFjaApzbGVlcCA1CnN1ZG8gc2h1dGRvd24gLWggbm93Cg==",
		"NetworkInterfaces": [
			{
				"DeviceIndex": 0,
				"SubnetId": "subnet-5a4b8b03",
				"DeleteOnTermination": True,
				"AssociatePublicIpAddress": True,
				"Groups": [
					security_group
				]
			}
		]
	}
	
	# Convert boot script into base64 data
	with open(bootscript,'r') as f:
		userdata=base64.b64encode(f.read())
	
	launch_specs=[]
	# Loop over instance types and 
	for instance_type in instance_types:
		print instance_type
		for az,subnet in subnet_map.iteritems():
			print subnet
			launch_spec=deepcopy(launch_template) 
			launch_spec["InstanceType"]=instance_type
			launch_spec["WeightedCapacity"]=weights[instance_type]/weights["c4.large"]*2.
			launch_spec["SpotPrice"]=str(instance_price[instance_type]*5.)
			launch_spec["BlockDeviceMappings"][0]["Ebs"]["VolumeSize"]=volume_size[instance_type]*3 # For Mexico region make disk much larger
			launch_spec["Placement"]["AvailabilityZone"]=az
			launch_spec["NetworkInterfaces"][0]["SubnetId"]=subnet
			launch_spec["UserData"]=userdata
			launch_specs.append(launch_spec)
			
	print launch_specs
	
	SpotFleetRequestConfig={
		"IamFleetRole": "arn:aws:iam::677365467450:role/aws-ec2-spot-fleet-role",
		"AllocationStrategy": "lowestPrice",
		"TargetCapacity": targetCapacity,
		"SpotPrice": "0.0525",
#		"ValidFrom": datetime.now()+timedelta(0,10), #Start 10 seconds from now 
#		"ValidUntil": str(datetime.now()+timedelta(30)), # End 30 days from now
		"TerminateInstancesWithExpiration": False,
		"LaunchSpecifications":launch_specs
	}
	
#	Check by exporting to JSON
#	import json
#	with open('test_config.json', 'w') as outfile:
#		json.dump(SpotFleetRequestConfig, outfile,indent=4)
	
	print "requesting spot fleet..."
	response = client.request_spot_fleet(DryRun=dry_run,SpotFleetRequestConfig=SpotFleetRequestConfig)
	print "Done"
	print 'spot fleet id is:',response['SpotFleetRequestId']
	return response['SpotFleetRequestId']

if __name__=='__main__':
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
	
	# Choose 12 cheapest instance types at time (by price per year run)
	# This is the list for cheapest instances in us-west-2 (oregon)
	instances=[
	'm4.4xlarge',
	'c4.large',
	'm4.large',
	'c4.xlarge',
	'm4.2xlarge',
	'm4.xlarge',
	'c4.2xlarge',
	'c3.large',
	'm3.large',
	'c4.4xlarge',
	'm3.2xlarge',
	'r3.large']
	spot_fleet_id=launch_fleet(instances,40,'aws_bootscript_boinc.sh',dry_run=False,region='us-west-2')