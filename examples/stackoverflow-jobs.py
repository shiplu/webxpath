import sys
from pprint import pprint
import argparse
from expression import *
from parser import Parser


class StackOverflow(Parser):
    cover = XPath('//div[@id="mainbar"]/header/div//img/@src') | Index(0)
    title = XPath('//h1[@class="fs-headline1 mb4"]/a/text()') | Index(0) | F(str.strip)
    company = XPath(
        '//h1[@class="fs-headline1 mb4"]/following-sibling::div/a/text()'
    ) | Index(0)
    location = (
        XPath(
            '//h1[@class="fs-headline1 mb4"]/following-sibling::div/a/following-sibling::span/text()'
        )
        | Join("")
        | StripNonAlNum()
    )
    description = (
        XPath(
            '//h2[contains(text(), "Job description")]/following-sibling::div//text()'
        )
        | Join("")
        | F(str.strip)
    )


if __name__ == "__main__":
    parser = StackOverflow()
    data = parser.parse(sys.argv[1])
    pprint(data)
