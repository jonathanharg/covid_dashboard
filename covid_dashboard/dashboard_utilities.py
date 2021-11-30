import json
# TODO: Actually read config file
def get_config(*keys):
    # TODO: Create default_config.json, copy default_config.json to config.json if it does not exist
    # TODO: Error handling etc.
    with open('config.json') as data:
        config = json.load(data)
    result = []
    if len(keys) == 1:
        result = config[keys[0]]
    else:
        for key in keys:
            result.append(config[key])
    return result