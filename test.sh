#!/bin/bash 

curr_dir=$PWD

cd $curr_dir/webapp

rm -f *.pyc 

python3 test_ss2json.py 

rm -f *.pyc 

cd $curr_dir