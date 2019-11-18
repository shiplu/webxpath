import webquery
from lxml import etree


class Parser(object):
    def parse(self, url):
        content = webquery.urlcontent(url)
        root = etree.HTML(content, base_url=url)
        data = {name: expr.parse(root) for name, expr in self.fields.items()}
        data['url'] = url
        return data
