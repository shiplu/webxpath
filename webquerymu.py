import os
import sys
import urllib2
import hashlib
import urlparse
from datetime import datetime, timedelta

from lxml import etree
import prettytable
import config

NAME="RESOURCE"


def log(message):
    if config.LOG:
        args = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        print >> sys.stderr, "[XPATH] %s - %s" % args

def md5(data):
    return hashlib.md5(data).hexdigest()

def is_url(url):
    return urlparse.urlparse(url).scheme != ""

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
        req = urllib2.Request(url, headers={'User-Agent': config.USER_AGENT})
        content = urllib2.urlopen(req).read()
        with open(cachefile, 'w') as f:
            f.write(content)
    else:
        with open(cachefile, 'r') as f:
            content = f.read()

    return content

def main():
    xpath, urls = xpath_urls()

    tbl = prettytable.PrettyTable()
    tbl.valign = 't'
    tbl.align = 'l'

    cols = []
    for url in urls:
        root = etree.HTML(urlcontent(url), base_url=url)
        cols.append((url, [unicode(el).strip() for el in root.xpath(xpath)]))

    log("cols: %s" % cols)
    max_row_len = max([len(matches) for col, matches in cols])
    log("max len = %s" % max_row_len)
    tbl.add_column("SL", range(1, max_row_len+1))

    urlmap = dict([(url, "%s-%02d" % (NAME, idx)) for (idx, url) in enumerate(urls, 1)])

    for url, matches in cols:
        if len(matches) < max_row_len:
            padded_list = [""]*(max_row_len - len(matches))
            matches.extend(padded_list)
        tbl.add_column(urlmap[url], matches, align='l')

    print tbl

    print "%s Reference:" % NAME
    for url, name in sorted(urlmap.items(), key=lambda u: u[1]):
        print "%2s - %s" % (name, url)


def xpath_urls():
    if len(sys.argv) < 3:
        print >> sys.stderr, "XPath and Website sould be passed as command-line argument"
        print >> sys.stderr, "Syntax: webquery.py xpath path1 path2 path3 ..."
        print >> sys.stderr, "A `path` can be any url or file location ..."
        sys.exit(1)

    args = sys.argv
    xpath = args[1]
    urls = args[2:]

    log("XPath: %s" % xpath)
    log("PATHs: %s" % urls)
    return xpath, urls

if __name__ == '__main__':
    main()
