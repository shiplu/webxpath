import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import hashlib
import argparse
import urllib.parse
from datetime import datetime, timedelta

from lxml import etree
import config

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
    cachefile = os.path.join('.cache', "%s.htm" % md5(url))

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
        req = urllib.request.Request(url, headers={'User-Agent': config.USER_AGENT})
        content = urllib.request.urlopen(req).read().decode(encoding='utf-8')
        with open(cachefile, 'w') as f:
            f.write(content)
    else:
        with open(cachefile, 'r') as f:
            content = f.read()

    return content


def main():
    cmd_args = cmdline_args()

    root = etree.HTML(urlcontent(cmd_args.url), base_url=cmd_args.url)
    for xpath in cmd_args.xpath:
        for el in root.xpath(xpath):
            print(el)


def cmdline_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help="url to query")
    parser.add_argument('xpath', nargs='+', help='xpath to apply')
    return parser.parse_args()


if __name__ == '__main__':
    main()
