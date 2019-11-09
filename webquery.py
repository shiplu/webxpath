import os
import sys
import urllib.request, urllib.error, urllib.parse
import hashlib
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
    xpaths, url = xpaths_url()

    root = etree.HTML(urlcontent(url), base_url=url)
    for xpath in xpaths:
        for el in root.xpath(xpath):
            print(el)


def xpaths_url():
    if len(sys.argv) < 3:
        print("XPath and Website sould be passed as command-line argument", file=sys.stderr)
        print("Syntax: webquerymx.py url xpath1 xpath2 xpath3 ...", file=sys.stderr)
        sys.exit(1)

    args = sys.argv
    url = args[1]
    xpaths = args[2:]

    log("XPaths: %s" % xpaths)
    log("URL: %s" % url)
    return xpaths, url


if __name__ == '__main__':
    main()
