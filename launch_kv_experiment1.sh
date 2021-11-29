#!/usr/bin/env bash

echo 'Launching node with port 5001'
./experiments.py localhost:5001 localhost:5000 localhost:5002 > /dev/null 2>&1 &
echo 'Launching node with port 5002'
./experiments.py localhost:5002 localhost:5000 localhost:5001 > /dev/null 2>&1 &
echo 'Launching head node with port 5000'
./experiments.py localhost:5000 localhost:5001 localhost:5002

# clean up all python3 processes
# sudo pkill python3
