from itertools import count
import re


class BaseExpression(object):
    def __init__(self, statement, next=None):
        self.statement = statement
        self.next = next

    def __repr__(self):
        objs = [self]
        ptr = self
        while ptr.next is not None:
            ptr = ptr.next
            objs.append(ptr)
        return ' | '.join(['%s(%r)' % (e.__class__.__name__, e.statement) for e in objs])

    def __eq__(self, other):
        return other is not None and self.statement == other.statement and self.next == other.next

    def __or__(self, other):
        if self is other or self == other:
            return self

        if self.next is None:
            self.next = other
        else:
            self.next.__or__(other)

        return self


class Expression(BaseExpression):

    def parse(self, inp):
        cur = self
        for iteration in count():
            result = cur.extract(inp)
            if cur.next is not None:
                cur = cur.next
                inp = result
            else:
                return result

    def extract(self, input):
        """Must process input and return some output"""
        raise NotImplementedError


class Index(Expression):
    def extract(self, input):
        if isinstance(input, (tuple, list)) and len(input) > self.statement:
            return input[self.statement]


class Join(Expression):
    def extract(self, inputs):
        return self.statement.join(inputs)


class Split(Expression):
    def extract(self, input):
        return input.split(self.statement)


class XPath(Expression):
    def extract(self, input):
        return input.xpath(self.statement)


class F(Expression):
    def extract(self, input):
        return self.statement(input)


class RegEx(Expression):
    def extract(self, input):
        match = re.search(self.statement, input)
        if match:
            return match[1]


class Fixed(Expression):
    def extract(self, input):
        return self.statement
