#!/bin/bash


port=5000
if [ $# -gt 0 ]; then
  port=$1

echo $port
python3 testingThreads.py $port

fi