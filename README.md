To run the most simple KV cluster example:

```
chmod +x test/launch_kv_cluster.sh
# this will block
./test/launch_kv_cluster.sh

# in a separate terminal (try changing the values to see how keys/values change)
python3 test/test.py
```


Vinayak's modifications:

Clone the repository: https://github.com/va6996/PySyncObj/  
It has a few modifications for our system.

Run the following in separate terminals:
```
python3 setup_infra.py

python3 client.py
```

You just like regular db, you can set and get values.

This would auto update the leader upon election and can handle leader dying.
