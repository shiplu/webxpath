import sys
import inspect
from collections import defaultdict

from lxml import etree

from webxpath import webquery
from webxpath.expression import Expression, Template


class Parser(object):
    registry = defaultdict(dict)

    @classmethod
    def __init_subclass__(cls):
        for name, member in inspect.getmembers(cls):
            if isinstance(member, (Expression, Template)):
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

        data = {"url": canonical_url}
        templates = {}

        # process only Expressions and save template strings
        for name, expr in self.fields.items():
            if isinstance(expr, Expression):
                try:
                    data[name] = expr.parse(root)
                except Exception as ex:
                    print("{} {} for '{}'".format(ex, expr, name))
                    raise
            elif isinstance(expr, Template):
                templates[name] = expr

        # Post process template urls
        for name, template in templates.items():
            data[name] = template.format(**data)
        return data
