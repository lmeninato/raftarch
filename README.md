Run the following in separate terminals:
```
python3 setup_infra.py

python3 client.py
```

You just like regular db, you can set and get values.

This would auto update the leader upon election and can handle leader dying.

# Cloudlab

Nodes:
- apt166.apt.emulab.net (10.10.1.1)
- apt187.apt.emulab.net (10.10.1.2)
- apt184.apt.emulab.net (10.10.1.3)
- apt175.apt.emulab.net (10.10.1.4)

Command support:

```
get x
set x y (does lock/unlock by default)
lock x (timeout = 30s)
unlock x
txn client_id; get/set/lock/unlock commands separated by ;
eg:
txn 5; lock a; get b; set a 5; unlock a;
```