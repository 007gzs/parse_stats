#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import queue
import json
import csv


MINGZU = ['蒙古族','回族','藏族','维吾尔族','苗族','彝族','壮族','布依族','朝鲜族','满族','侗族','瑶族','白族',
          '土家族','哈尼族','哈萨克族','傣族','黎族','傈僳族','佤族','畲族','高山族','拉祜族','水族','东乡族',
          '纳西族','景颇族','柯尔克孜族','土族','达斡尔族','仫佬族','羌族','布朗族','撒拉族','毛南族','仡佬族',
          '锡伯族','阿昌族','普米族','塔吉克族','怒族','乌孜别克族','俄罗斯族','鄂温克族','德昂族','保安族',
          '裕固族','京族','塔塔尔族','独龙族','鄂伦春族','赫哲族','门巴族','珞巴族','基诺族',]

def proc_itemcode():
    with open('itemcode.json') as f:
        itemcode = json.load(f)
    children = queue.Queue()
    out = []
    for item in itemcode:
        data = {'name':item['name'], 'code':item['code'], 'parent_code':'0'}
        children.put((data, item['children']))
        out.append(data)
    while not children.empty():
        parent, child = children.get()
        for item in child:
            data = {'name':item['name'], 'code':item['code'], 'parent_code':parent['code']}
            if 'towntypecode' in item:
                data['desc'] = data['name']
                data['name'] = item['towntypecode']
            if item['code'] == parent['code']:
                desc = data.get('desc', None)
                if desc is not None:
                    if 'desc' not in parent:
                        parent['desc'] = desc
                    elif parent['desc'] != desc:
                        print("err %s %s %s" % (parent['code'], parent['desc'], desc))
                    if 'children' in item:
                        print('err %s %s' % (parent['code'], item['children']))
                continue

            if 'children' in item:
                children.put((data, item['children']))
            out.append(data)
    csvheaders = ['code', 'parent_code', 'name', 'desc']
    with open('itemcode.csv', 'w') as f:
        writer = csv.DictWriter(f, csvheaders)
        writer.writeheader()
        writer.writerows(out)

def rstrip(data, chars):
    if len(data) <= 2:
        return data
    ret = data.rstrip(chars)
    if len(ret) < 2:
        ret = data
    return ret

def get_short_name(name, parent_short_name, parent_full_short_name, code_type):

    if name in ('市辖区', '省直辖县级行政区划', '自治区直辖县级行政区划'):
        return parent_short_name, parent_full_short_name
    short_name = name

    short_name = rstrip(short_name, '自治县')
    short_name = rstrip(short_name, '自治区')
    short_name = rstrip(short_name, '自治旗')
    short_name = rstrip(short_name, '自治州')
    short_name = rstrip(short_name, '办事处')
    short_name = rstrip(short_name, '居委会')
    short_name = rstrip(short_name, '地区')
    if len(short_name) > 2 and code_type in ('province', 'city', 'county'):
        short_name = rstrip(short_name, '省')
        short_name = rstrip(short_name, '市')
        if not short_name.endswith('新区') and not short_name.endswith('矿区'):
            short_name = rstrip(short_name, '区')
        short_name = rstrip(short_name, '县')
        short_name = rstrip(short_name, '旗')
        short_name = rstrip(short_name, '镇')
        short_name = rstrip(short_name, '村')
    while len(short_name) > 2 and short_name.endswith('族'):
        for mz in MINGZU:
            short_name = rstrip(short_name, mz)
    lastlen = len(short_name)
    while True:
        for mz in MINGZU:
            if len(mz) <= 2:
                continue
            short_name = rstrip(short_name, mz.rstrip('族'))
        if lastlen == len(short_name):
            break
        lastlen = len(short_name)
    if short_name == parent_short_name:
        return parent_short_name, parent_full_short_name
    if not parent_full_short_name:
        return short_name, short_name
    return short_name, parent_full_short_name + " " + short_name

def proc_admincode():
    with open('admincode_2016.json') as f:
        admincode = json.load(f)
    children = queue.Queue()
    out = []
    temp = set()
    for item in admincode:
        data = dict()
        data['adcode'] = item['code']
        data['parent_code'] = '000000000000'
        data['name'] = item['name']
        data['full_name'] = item['name']
        data['short_name'], data['full_short_name'] = get_short_name(item['name'], '', '', item['codetype'])
        data['code_type'] = item['codetype']
        data['town_type_code'] = item.get('town_type_code', '')
        children.put((data, item['children']))
        out.append(data)
        temp.add(data['short_name'][-1])
    while not children.empty():
        parent, child = children.get()
        for item in child:
            data = dict()
            data['adcode'] = item['code']
            data['parent_code'] = parent['adcode']
            data['name'] = item['name']
            if item['name'] is None:
                print(item['code'])
                item['name'] = ''
            data['full_name'] = parent['full_name'] + ' ' + item['name']
            data['short_name'], data['full_short_name'] = get_short_name(item['name'], parent['short_name'], parent['full_short_name'], item['codetype'])
            data['code_type'] = item['codetype']
            data['town_type_code'] = item.get('town_type_code', '')
            if 'children' in item:
                children.put((data, item['children']))
            out.append(data)
            if data['short_name'] == '':
                print(data)
            else:
                temp.add(data['short_name'][-1])
    print(temp)
    csvheaders = ['adcode', 'parent_code', 'name', 'full_name', 'short_name', 'full_short_name', 'code_type', 'town_type_code']
    with open('admincode.csv', 'w') as f:
        writer = csv.DictWriter(f, csvheaders)
        writer.writeheader()
        writer.writerows(out)
if __name__ == "__main__":
    proc_itemcode()
    # proc_admincode()
