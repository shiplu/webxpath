import webquery
from lxml import etree
import inspect
from expression import Expression
from collections import defaultdict


class Parser(object):
    registry = defaultdict(dict)

    @classmethod
    def __init_subclass__(cls):
        for name, member in inspect.getmembers(cls):
            if isinstance(member, Expression):
                cls.registry[cls.__name__][name] = member

    @property
    def fields(self):
        cls = self.__class__
        return cls.registry[cls.__name__]

    def parse(self, url):
        content = webquery.urlcontent(url)
        root = etree.HTML(content, base_url=url)
        data = {name: expr.parse(root) for name, expr in self.fields.items()}
        data['url'] = url
        return data
