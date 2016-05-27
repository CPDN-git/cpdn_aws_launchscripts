#!/bin/bash
# Boot script for AWS Ubuntu VM to run CPDN local test wu

# Install required packages for Ubuntu
sudo apt-get update
sudo apt-get -y install awscli lib32stdc++6 lib32z1

# Install Packages required for Amazon Linux (would also need changes to scripts):
#yum -y update
#yum -y install compat-libstdc++-33.i686 compat-libstdc++-33.x86_64 libstdc++48.i686 libstdc++48.x86_64

# Print date to see how long this has taken
date

# Set up test run, copying data from s3 bucket
TEST_DIR=/home/ubuntu/test
mkdir $TEST_DIR
aws s3 sync s3://cpdn-local-run/aws_test $TEST_DIR --region=us-east-1
cd $TEST_DIR/slots/0

# Set executable
chmod +x $TEST_DIR/slots/0/run_aws_multiproc_test.sh
chmod +x $TEST_DIR/projects/reqs.comlab.ox.ac.uk_cpdn/wah2_7.51_i686-pc-linux-gnu
chmod +x $TEST_DIR/projects/reqs.comlab.ox.ac.uk_cpdn/wah2_7.07_i686-pc-linux-gnu

# Set which runit script to use
export RUNIT=run_aws_test2.sh
chmod +x $TEST_DIR/slots/0/$RUNIT

# Set workunit
export WORKUNIT=wah2_eu2_g61b_1966_1_short
#export WORKUNIT=wah2_eu2_g61b_1966_short_newstash
#export WORKUNIT=wah2_eu50_1001_1996_3month
#export WORKUNIT=wah2_eu50_aabbz_2008_1year
#export WORKUNIT=wah2_eu50_aabcd_2008_3month
#export WORKUNIT=wah2_eu50_ifbh_2008_extra_dumps
#export WORKUNIT=wah2_eu2_g61b_1966_3month
#export WORKUNIT=wah2_eu50_v2_ifbh_2008_3month

# Note specifying a integer after this script will restrict the number of simulations to set up
# e.g. ./run_aws_multiproc_test.sh 3 will submit 3 simulations
# otherwise one simulation per cpu core will be submitted
echo "Starting cpdn run..."
./run_aws_multiproc_test.sh
