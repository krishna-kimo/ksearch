from scrapy import Item, Field
from collections import OrderedDict


class DynamicItem(Item):
    def __init__(self, *args, **kwargs):
        super(DynamicItem, self).__init__()
        self._values = OrderedDict()
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in OrderedDict(*args, **kwargs).items():
                self[k] = v

    def __setitem__(self, key, value):
        self._values[key] = value
        self.fields[key] = {}
