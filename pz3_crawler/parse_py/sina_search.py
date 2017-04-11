import json

class sina_search(object):
    def __init__(self):
        pass

    def main(self, url, content, config):
        raw = json.loads(content)
        result_list = raw["result"]['list']
        return result_list