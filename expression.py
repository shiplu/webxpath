from itertools import count
import re
from copy import deepcopy


class BaseExpression(object):
    __slots__ = ['statement', 'next']

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


class Strip(Expression):
    def extract(self, input):
        lstripped = re.sub(r'^' + self.statement, '', input)
        rstripped = re.sub(self.statement + r'$', '', lstripped)
        return rstripped


class StripNonAlNum(Expression):
    def __init__(self, next=None):
        statement = re.compile(r'^[^A-z0-9]+'), re.compile(r'[^A-z0-9]+$')
        super().__init__(statement, next)

    def extract(self, input):
        lpat, rpat = self.statement
        lstripped = lpat.sub('', input)
        rstripped = rpat.sub('', lstripped)
        return rstripped


class F(Expression):
    def extract(self, input):
        return self.statement(input)


class RegEx(Expression):
    def extract(self, input):
        match = re.search(self.statement, input)
        if match:
            return match[1]


class DedupRe(Expression):
    """Squeeze repeated patterns. Good for removing repeated characters.
    The statement is a regex of single unit. The unit can be a single
    character like bellow example or a word.

    Example:
    >>> DedupRe('[a-z]').extract('aaaabcddde')
    abcde
    """

    def __init__(self, statement, next=None):
        super().__init__(re.compile(r'(%s)\1+' % statement), next)

    def extract(self, input):
        return self.statement.sub('\\1', input)


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
