#!/usr/bin/python
#
# Python script to analyse benchmarks of local cpdn tests in AWS
# This creates a plot of timings for different instance types
# This also produces pricing and weighting information needed for submitting spot fleets
#
# Peter Uhe, May 2016
#
import os,sys
import numpy as np
import matplotlib.pyplot as plt
import csv
from aws_pythonsdk_benchmarks import get_instance_info



def plot_timings():
	### Plot up the timings
	# 
	plt.figure()
	ax=plt.gca()

	#for type, instances in runs.iteritems():
	for i,type in enumerate(types):
		print '\n',type,'\n'
		instances=runs[type]
		for id,times in instances.iteritems():
			print id, len(times),times.max(),times.std()
			plt.plot([i]*len(times),times,'b.')
			plt.plot([i],[times.max()],'rx',mew=3)
		
	plt.xticks(typex,rotation=90)
	plt.ylabel('run time (minutes)')
	ax.set_xticklabels(types)
	plt.show()

def write_timings(csv_fname):
	with open(csv_fname, 'wb') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(['Instance type','hourly price','vCPUs','run time (min)','model days per instance hour','price per year run']) 
		for type in types:
			hourly_price=instance_price[type]
			vcpus=0
			mean_timing=0.
			n=len(runs[type])
			for id,timings in runs[type].iteritems():
				vcpus=max(vcpus,len(timings))
				mean_timing+=timings.max()
			mean_timing=mean_timing/n
			runs_per_hour=vcpus/mean_timing*60.
			year_run_price=hourly_price*mean_timing/60./vcpus*360.
			csvwriter.writerow([type,hourly_price,vcpus,mean_timing,runs_per_hour,year_run_price])


### Check for any new benchmark tests ###
#
#os.system('aws s3 sync s3://benchmarkinglogs ../benchmarkinglogs')
#os.system('grep -r real ../benchmarkinglogs/wah2_eu2_g61b_1966_1_short/*/timing*.txt >timing_list.txt')

runs={}

### Loop over each workunit to generate the dictionary of timings
#
with open('timing_list.txt','r') as f:
	for line in f:
		instance,timing=line.split()
		
		# Get run time in minutes
		# Assume timing in the format XXmYY.ZZZs
		min,sec=timing.split('.')[0].split('m')
		minutes=int(min)+int(sec)/60.
		
		# Get instance info
		arr=instance.split('/')
		run_name=arr[1]
		instance_type=arr[2]
		tmp=arr[3].split('_')
		instance_id=tmp[1]
		instance_proc=tmp[2].split('.')[0]
		
		# Create dictionary of run lengths
		if not runs.has_key(instance_type):
			runs[instance_type]={}
		# Append this workunit to the list of runs for this instance (or create a new list)
		try:
			runs[instance_type][instance_id]=np.append(runs[instance_type][instance_id],minutes)
		except:
			runs[instance_type][instance_id]=np.array([minutes])
			

	types=runs.keys()
	types.sort()
	typex=range(len(types))



instance_price=get_instance_info()

write_timings('instance_comparison.csv')
#plot_timings()
		
