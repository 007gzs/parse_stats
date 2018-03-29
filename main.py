#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import json
import datetime

from pyquery import PyQuery


class HtmlReader():

    def __init__(self, rootpath, path, file):
        self.rootpath = rootpath
        if file.startswith("/"):
            self.file = os.path.realpath(os.path.join(rootpath, file[1:]))
        else:
            self.file = os.path.realpath(os.path.join(path, file))
        self.path = os.path.dirname(self.file)
        with open(self.file, 'rb') as f:
            self.html = f.read()
            for encode in ['utf-8', 'gbk']:
                try:
                    self.html = self.html.decode(encode)
                    break
                except UnicodeDecodeError as e:
                    pass
        self.pyq = PyQuery(self.html)

    def open(self, file):
        return HtmlReader(self.rootpath, self.path, file)


def get_text_href(td):
    a = td.find('a')
    if a is not None:
        return a.text, a.get('href')
    else:
        return td.text, None

def parse_trs(stat, trs, ret, codetype):
    for tr in trs:
        item = dict()
        tds = tr.findall('td')
        item['code'], href1 = get_text_href(tds[0])
        item['name'], href2 = get_text_href(tds[1])
        if href1 is None:
            href1 = href2
        if href2 is None:
            href2 = href1
        assert href1 == href2, '%s, %s, %s' % (href1, href2, stat.file)
        if codetype is not None:
            if codetype == 'village' and len(tds) > 2:
                item['towntypecode'] = item['name']
                item['name'] = tds[2].text

            item['codetype'] = codetype
            if codetype not in ('town', 'village'):
                item['shortcode'] = item['code'][:6]
        
        if href1 is not None:
            item['children'] = list()
            try:
                child = stat.open(href1)
            except Exception as e:
                pass
            else:
                parse_data(child, item['children'])
        ret.append(item)


def parse_province(stat, trs, ret, codetype):
    for province in trs('a'):
        item = dict()
        item['name'] = province.text
        item['codetype'] = codetype
        href = province.get('href')
        item['code'] = href.split('.')[0] + ('0' * 10)
        item['shortcode'] = item['code'][:6]
        item['children'] = list()
        child = stat.open(href)
        parse_data(child, item['children'])
        ret.append(item)


def parse_data(stat, ret):
    parse_trs(stat, stat.pyq('.citytr'), ret, 'city')
    parse_trs(stat, stat.pyq('.countytr'), ret, 'county')
    parse_trs(stat, stat.pyq('.towntr'), ret, 'town')
    parse_trs(stat, stat.pyq('.villagetr'), ret, 'village')


def parse_admincode(ROOT_PATH, year='2016'):
    stat = HtmlReader(ROOT_PATH, '', '/tjsj/tjbz/tjyqhdmhcxhfdm/%s/index.html' % year)
    data = list()
    parse_province(stat, stat.pyq('.provincetr'), data, 'province')
    with open('admincode_%s.json' % year, "w") as f:
        json.dump(data,f, indent=2)

    
def parse_itemcode(ROOT_PATH):
    files = ['/tjsj/tjbz/tjypflml/index.html', 
             '/tjsj/tjbz/tjypflml/index_1.html', 
             '/tjsj/tjbz/tjypflml/index_2.html', 
             '/tjsj/tjbz/tjypflml/index_3.html', 
             '/tjsj/tjbz/tjypflml/index_4.html']

    data = list()
    for file in files:
        stat = HtmlReader(ROOT_PATH, '', file)
        for a in stat.pyq('.center_list_contlist li a'):
            if a.get('target') == '_self':
                continue

            item = dict()
            texts = a.text_content().split('-')

            item['name'] = texts[1].rstrip('2010')
            item['code'] = texts[0]
            href = a.get('href')
            item['children'] = list()
            child = stat.open(href)
            parse_data(child, item['children'])
            data.append(item)

    with open('itemcode.json', "w") as f:
        json.dump(data,f, indent=2)

if __name__ == "__main__":
    ROOT_PATH = '/007/data/www.stats.gov.cn'
    # parse_admincode(ROOT_PATH, '2016')
    parse_itemcode(ROOT_PATH)
    for year in ['2010', '2011', '2012', '2013', '2014', '2015', '2016']:
        print("%s : %s start " % (datetime.datetime.now(), year))
        parse_admincode(ROOT_PATH, year)
