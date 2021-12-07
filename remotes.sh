#! /usr/bin/bash

# run this to update code on remote servers
ssh va2083@apt175.apt.emulab.net "cd raftarch && git pull origin master"
ssh va2083@apt166.apt.emulab.net "cd raftarch && git pull origin master"
ssh va2083@apt187.apt.emulab.net "cd raftarch && git pull origin master"
ssh va2083@apt184.apt.emulab.net "cd raftarch && git pull origin master"

# kill any python3 processes to ensure no ports are taken
ssh va2083@apt175.apt.emulab.net "pkill python3"
ssh va2083@apt166.apt.emulab.net "pkill python3"
ssh va2083@apt187.apt.emulab.net "pkill python3"
ssh va2083@apt184.apt.emulab.net "pkill python3"


ssh va2083@apt175.apt.emulab.net "python3 raftarch/remote_gateway.py"

ssh va2083@apt166.apt.emulab.net "python3 raftarch/launch_db_node.py http://10.10.1.4:8000 10.10.1.1:5001 10.10.1.2:5001 10.10.1.3:5001 &"
ssh va2083@apt187.apt.emulab.net "python3 raftarch/launch_db_node.py http://10.10.1.4:8000 10.10.1.2:5001 10.10.1.1:5001 10.10.1.3:5001 &"
ssh va2083@apt184.apt.emulab.net "python3 raftarch/launch_db_node.py http://10.10.1.4:8000 10.10.1.3:5001 10.10.1.1:5001 10.10.1.2:5001 &"

# for interactive use
ssh va2083@apt175.apt.emulab.net "python3 raftarch/client.py"

# benchmark no failures
ssh va2083@apt175.apt.emulab.net "python3 raftarch/no_failures.py"
scp va2083@apt175.apt.emulab.net:~/no_failure.csv benchmarks_remote/

# benchmark with failures (including leader) at 10s
ssh va2083@apt175.apt.emulab.net "python3 raftarch/leader_failure.py"
scp va2083@apt175.apt.emulab.net:~/results_leader_failure.csv benchmarks_remote/

