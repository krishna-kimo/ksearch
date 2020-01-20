import yaml
from settings import DATA_FILE_PATH

def get_keywords():
    with open(DATA_FILE_PATH) as f:
        data = yaml.full_load(f)
        keywords = []

        for detail in data.values():
            for _item in details:
                _words = _item.get('keywords', [])
                for _word in _words:
                    keywords.append(_word)
    f.close()
    return keywords
