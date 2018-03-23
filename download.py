#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import os, gc, time
import urllib.request, urllib.parse

from pyquery import PyQuery


def logtime(url, conntime, e):
    if conntime > 5:
        print("%s used %fs %s" % (url, conntime, e))

def conn(url, headers):
    c = 0
    while True:
        try:
            start = time.time()
            request = urllib.request.Request(url, headers=headers)  
            response = urllib.request.urlopen(request, timeout=10)  
            html = response.read()
            conntime = time.time() - start
            logtime(url, conntime, None)
            return html
        except Exception as e:
            c += 1
            conntime = time.time() - start
            logtime(url, conntime, e)
            if c > 5:
                print("err: %s %s" % (url, e))
                return None
            else:
                time.sleep(0.5)
def download(url, basepath, urlprefix, proc=set(), force=False):

    if not url.startswith(urlprefix) or url in proc:
        return

    urlobj = urllib.parse.urlparse(url)
    outpath = os.path.join(basepath, os.path.dirname(urlobj.path)[1:])
    outpath = os.path.realpath(outpath)
    if not os.path.isdir(outpath):
        os.makedirs(outpath)
    filename = os.path.basename(urlobj.path)
    if filename == '':
        filename = 'index.htm'
    outfile = os.path.join(outpath, filename)

    headers = {  
        "User-Agent":'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',  
        "host": urlobj.hostname 
    }
    if force or not os.path.isfile(outfile):
        html = conn(url, headers)
        if html is None:
            return
        with open(outfile, 'wb') as f:
            f.write(html)
    else:
        with open(outfile, 'rb') as f:
            html = f.read()
    proc.add(url)
    pyq = PyQuery(html)
    for a in pyq('a'):
        href = a.get('href')
        newurl = urllib.parse.urljoin(url, href)
        download(newurl, basepath, urlprefix, proc, force)
    del html, pyq
    gc.collect()


if __name__ == "__main__":
    url = 'http://www.stats.gov.cn/tjsj/tjbz/index.html'
    basepath = '/007/data/www.stats.gov.cn'
    download(url, basepath, 'http://www.stats.gov.cn/tjsj/tjbz/')
