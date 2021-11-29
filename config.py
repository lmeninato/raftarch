import yaml

def get_heirarchical_config(path):
    with open(path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

def set_cluster_addr_mapping_from_config(mapping, config):
    for cluster in config.keys():
        mapping[config[cluster]['name']] = config[cluster]['head']