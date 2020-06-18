import sys
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

    def canonical_url(self, url):
        """By overriding this method canonical url can be used"""
        return url

    def parse(self, url):
        canonical_url = self.canonical_url(url)
        content = webquery.urlcontent(canonical_url)
        root = etree.HTML(content, base_url=canonical_url)
        data = {}
        for name, expr in self.fields.items():
            try:
                data[name] = expr.parse(root)
            except Exception as ex:
                print("{} {} for '{}'".format(ex, expr, name))
                raise
        data['url'] = canonical_url
        return data
