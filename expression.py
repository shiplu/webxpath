from itertools import count
import re
from copy import deepcopy


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

    def __copy__(self):
        return type(self)(self.statement, self.next)

    def __deepcopy__(self, memo):
        cls = self.__class__
        clone = cls.__new__(cls)
        memo[id(self)] = clone

        clone.next = None
        clone.statement = self.statement
        if self.next is not None:
            clone.next = deepcopy(self.next, memo)

        return clone

    def __or__(self, other):
        if self is other or self == other:
            return self

        clone = deepcopy(self)

        if clone.next is None:
            clone.next = other
        else:
            clone.next = clone.next | other

        return clone


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


if __name__ == '__main__':
    string = "a b c\td\ne\n"
    my_expression = Split("\t") | Join(" ") | Split("\n") | Join(" ") | F(str.strip) | Split(" ")
    new_my_expression = my_expression | Index(0)
    assert my_expression is not new_my_expression
    assert (my_expression | Index(0)).parse(string) == 'a'
    assert my_expression.parse(string) == ['a', 'b', 'c', 'd', 'e']
    another_expression = Join("") | Split("c") | Index(1)
    assert another_expression.parse(my_expression.parse(string)) == "de"
