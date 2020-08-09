import os
import sys
import hashlib
import urllib.request, urllib.parse, urllib.error
import argparse
from datetime import datetime, timedelta

from lxml import etree
import prettytable

from webxpath import config

NAME = "RESOURCE"


def log(message):
    if config.LOG:
        args = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        print("[XPATH] %s - %s" % args, file=sys.stderr)


def md5(data):
    return hashlib.md5(data.encode()).hexdigest()


def is_url(url):
    return urllib.parse.urlparse(url).scheme != ""


def urlcontent(url):

    # If its a url just return as it is
    if not is_url(url):
        with open(url) as f:
            content = f.read()
        return content

    # Use the md5 of the url as the cache file name
    cachefile = os.path.join(".cache", "%s.htm" % md5(url))

    # if the file is dowloaded more than 1 hours ago
    # it'll be redownloaded

    current_dt = datetime.now()
    try:
        file_creation_dt = datetime.fromtimestamp(os.path.getctime(cachefile))
    except OSError:
        # if file doesn't exist we just set an old date
        # which is guranteed to make this file old enough
        file_creation_dt = current_dt - timedelta(hours=4)

    if (current_dt - file_creation_dt) > timedelta(hours=3):
        req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
        content = urllib.request.urlopen(req).read().decode(encoding="utf-8")
        with open(cachefile, "w") as f:
            f.write(content)
    else:
        with open(cachefile, "r") as f:
            content = f.read()

    return content


def main():
    cmd_args = cmdline_args()

    root = etree.HTML(urlcontent(cmd_args.url), base_url=cmd_args.url)

    if cmd_args.table:
        tbl = prettytable.PrettyTable()
        tbl.valign = "t"
        tbl.align = "l"

        cols = []
        for xpath in cmd_args.xpath:
            cols.append((xpath, [str(el).strip() for el in root.xpath(xpath)]))

        log("cols: %s" % cols)
        max_row_len = max([len(matches) for col, matches in cols])
        log("max len = %s" % max_row_len)
        tbl.add_column("SL", list(range(1, max_row_len + 1)))

        xpathmap = dict(
            [
                (xpath, "%s-%02d" % (NAME, idx))
                for (idx, xpath) in enumerate(cmd_args.xpath, 1)
            ]
        )

        for xpath, matches in cols:
            if len(matches) < max_row_len:
                padded_list = [""] * (max_row_len - len(matches))
                matches.extend(padded_list)
            tbl.add_column(xpathmap[xpath], matches, align="l")

        print(tbl)

        print(("%s Ref.:" % NAME))
        for xpath, name in sorted(list(xpathmap.items()), key=lambda u: u[1]):
            print(("%2s - %s" % (name, xpath)))

    else:

        for xpath in cmd_args.xpath:
            print("Xpath: %s" % xpath)
            for position_match in enumerate(root.xpath(xpath), 1):
                print("%3s %s" % (position_match))


def cmdline_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--table",
        action="store_true",
        default=False,
        help="Shows matches in a table",
    )
    parser.add_argument("url", help="url to query")
    parser.add_argument("xpath", nargs="+", help="xpath to apply")
    return parser.parse_args()


if __name__ == "__main__":
    main()
