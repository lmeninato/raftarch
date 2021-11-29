import requests

def set_key(node, key, value, sync=False):
    return requests.post(node, params = {key: [value, sync]})

def get_key_value(node, key):
    return requests.get(node, params = {'key': key})

if __name__ == "__main__":
    node = 'http://localhost:8000'
    set_key(node, "abc", "123345", False)
    resp = get_key_value(node, "abc")
    print(resp.text)
    