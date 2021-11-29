#!/usr/bin/env bash

echo 'Launching node with port 5001'
python3 kvstore.py 8004 localhost:5004 localhost:5003 localhost:5005 > /dev/null 2>&1 &
echo 'Launching node with port 5002'
python3 kvstore.py 8005 localhost:5005 localhost:5003 localhost:5004 > /dev/null 2>&1 &
echo 'Launching head node with port 5000'
python3 kvstore.py 8003 localhost:5003 localhost:5004 localhost:5005