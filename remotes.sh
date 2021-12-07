#! /usr/bin/bash

ssh va2083@apt166.apt.emulab.net "python3 raftarch/launch_db_node.py 10.10.1.1:5001 10.10.1.2:5001 10.10.1.3:5001"
ssh va2083@apt187.apt.emulab.net "python3 raftarch/launch_db_node.py 10.10.1.2:5001 10.10.1.1:5001 10.10.1.3:5001"
ssh va2083@apt184.apt.emulab.net "python3 raftarch/launch_db_node.py 10.10.1.3:5001 10.10.1.1:5001 10.10.1.2:5001"

ssh va2083@apt175.apt.emulab.net "git clone https://github.com/lmeninato/raftarch.git"
