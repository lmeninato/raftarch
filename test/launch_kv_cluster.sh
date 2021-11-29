#!/usr/bin/env bash

echo 'Launching node with port 5001'
python3 kvstore.py 8001 localhost:5001 localhost:5000 localhost:5002 > /dev/null 2>&1 &
echo 'Launching node with port 5002'
python3 kvstore.py 8002 localhost:5002 localhost:5000 localhost:5001 > /dev/null 2>&1 &
echo 'Launching head node with port 5000'
python3 kvstore.py 8000 localhost:5000 localhost:5001 localhost:5002