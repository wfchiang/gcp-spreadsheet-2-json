#!/bin/bash 

curr_dir=$PWD

rm -f *.pyc 

python3 $curr_dir/webapp/unit_tests.py 

rm -f *.pyc 