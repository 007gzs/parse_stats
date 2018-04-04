#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import queue
import xmltodict

DIFF_PX = 5
class Text:
    def __init__(self, pagenum, top, left, width, height, text):
        self.pagenum = int(pagenum)
        self.top = int(top)
        self.left = int(left)
        self.width = int(width)
        self.height = int(height)
        self.text = text
    def __str__(self):
        return '%s : %s' % (self.pos(), self.text)
    def __lt__(self, other):
        return self.cmp(other) < 0
    def __gt__(self, other):
        return self.cmp(other) > 0
    def __eq__(self, other):
        return self.cmp(other) == 0
    def __le__(self, other):
        return self.cmp(other) <= 0
    def __ge__(self, other):
        return self.cmp(other) >= 0
    def __ne__(self, other):
        return self.cmp(other) != 0

    def single_row(self, other):
        return self.pagenum == other.pagenum and abs(self.top - other.top) < DIFF_PX
    def single_col(self, other):
        return abs(self.left - other.left) < DIFF_PX
    def pos(self):
        return '%d, %d, %d, %d' % (self.row, self.pagenum, self.top, self.left)
    def cmp(self, other):
        if self.pagenum > other.pagenum:
            return 1
        elif self.pagenum < other.pagenum:
            return -1
        else:
            if self.top - other.top > DIFF_PX:
                return 1
            elif self.top - other.top < -DIFF_PX:
                return -1
            else:
                if self.left - other.left > DIFF_PX:
                    return 1
                elif self.left - other.left < -DIFF_PX:
                    return -1
                else:
                    return 0
class Row:
    def __init__(self):
        self.texts = []
    def add(self, text):
        if len(self.texts) == 0:
            self.texts.append(text)
            return True
        if self.texts[0].single_col(text):
            return False
        
        for t in self.texts:
            if t.single_col(text):
                t.text += text.text
                return True
        self.texts.append(text)
        self.texts.sort()
        return True
    def check(self):
        if len(self.texts) != 3:
            print("============== %s" % self)
            return False
        if self.texts[0].text == 'Code' and self.texts[1].text == 'Translation Name' and self.texts[2].text == 'English Name':
            return False
        parent_code = self.texts[0].text
        while parent_code.endswith('00'):
            parent_code = parent_code[:-2]
        parent_code = parent_code[:-2]
        parent_code += '0' * 8
        parent_code = parent_code[0:8]
        return {'code': self.texts[0].text, 'name':self.texts[1].text.replace("'", ''), 'en_name':self.texts[2].text, 'parent_code': parent_code}

    def __str__(self):
        return ','.join([text.text for text in self.texts])

class Page:
    def __init__(self):
        self.rows = []
        self.rows.append(Row())
    def add(self, text):
        row = self.rows[-1]
        if not row.add(text):
            row = Row()
            row.add(text)
            self.rows.append(row)

def parse_xml(file):
    with open(file, 'rb') as fp:
        data = xmltodict.parse(fp.read())
    pages = data['pdf2xml']['page']
    texts = []
    for page in pages:
        for text in page['text']:
            texts.append(Text(page['@number'], text['@top'], text['@left'], text['@width'], text['@height'], text['#text']))
    texts.sort()
    return texts

def parse_zh_xml():
    texts = parse_xml('unspsc/zh.xml')
    last = None
    page = Page()
    for text in texts:
        if text.text in ('UNSPSC Codeset Chinese- Simplified Translation', 
                    '11/30/2012', 
                    'UNSPSC v06_1101',
                    'Page %d of 702' % text.pagenum,
                    '© 2013 United Nations Development Programme (UNDP).',
                    'UNSPSC® is a registered trademark of UNDP.'
                    ):
            continue
        page.add(text)
        # if last is None:
        #     text.row = 1
        #     row = Row()
        #     rows.append(row)
        # else:
        #     if text.single_row(last):
        #         text.row = last.row
        #     else:
        #         text.row = last.row + 1
        #         row = Row()
        #         rows.append(row)
        # row.add(text)
        # last = text
        # print("%s" % text)
    sql = 'INSERT INTO `unspsc` (`code`, `parent_code`, `name`, `en_name`, `full_name`, `full_en_name`) values \n'
    temp = {}
    root = {}
    root['code'] = '00000000'
    root['name'] = ''
    root['en_name'] = ''
    root['full_name'] = ''
    root['full_en_name'] = ''
    root['children'] = []
    temp[root['code']] = root
    for row in page.rows:
        data = row.check()
        if data == False:
            continue
        data['children'] = []
        temp[data['code']] = data
        temp[data['parent_code']]['children'].append(data)
    children = queue.Queue()
    children.put((root, root['children']))
    
    while not children.empty():
        parent, child = children.get()

        for item in child:
            full_name = parent['full_name']
            if full_name != '':
                full_name += ' '
            if parent['name'] != item['name']:
                item['full_name'] = full_name + item['name']
            else:
                item['full_name'] = full_name

            full_en_name = parent['full_en_name']
            if full_en_name != '':
                full_en_name += '. '
            if parent['en_name'] != item['en_name']:
                item['full_en_name'] = full_en_name + item['en_name']
            else:
                item['full_en_name'] = full_en_name

            sql += '('
            sql += ','.join(["'%s'" % item[k] for k in ('code', 'parent_code', 'name', 'en_name', 'full_name', 'full_en_name')])
            sql += '),\n'
            if len(item['children']) > 0:
                children.put((item, item['children']))

    sql = sql[:-2]
    sql += ';\n'
    with open('zh.sql', 'w') as f:
        f.write(sql)
    # for k, v in rows.items():
    #     if v != 3:
    #         print("%s %s" % (k, v))

if __name__ == '__main__':
    parse_zh_xml()
    # parse_xml('en.xml')