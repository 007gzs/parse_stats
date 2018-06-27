#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from pyquery import PyQuery
from download import download_and_save


if __name__ == "__main__":
    basepath = '/007/data/school'
    paths = ['juniorschool', 'collegeschool', 'highschool']
    provs = {
        1: '北京',
        2: '上海',
        3: '天津',
        4: '重庆',
        5: '黑龙江',
        6: '吉林',
        7: '辽宁',
        8: '山东',
        9: '山西',
        10: '陕西',
        11: '河北',
        12: '河南',
        13: '湖北',
        14: '湖南',
        15: '海南',
        16: '江苏',
        17: '江西',
        18: '广东',
        19: '广西',
        20: '云南',
        21: '贵州',
        22: '四川',
        23: '内蒙古',
        24: '宁夏',
        25: '甘肃',
        26: '青海',
        27: '西藏',
        28: '新疆',
        29: '安徽',
        30: '浙江',
        31: '福建',
        32: '台湾',
        33: '香港',
        34: '澳门',
        35: '海外',
    }
    city_info = {}
    municipalitys = {1:"1101", 2:"3101", 3:"1201", 4:"5001", 33:"8101"}
    url = "http://s.xnimg.cn/a58580/js/cityArray.js"
    js = download_and_save(url, basepath).decode()
    for line in js.split('\n'):
        line = line.strip()
        prov_id = None
        citys = None
        if line.startswith("var _city_") and line.endswith(";"):
            data = line[10:-2].split("=[")
            if len(data) == 2:
                prov_id = int(data[0])
                citys = {d.split(':')[0]: d.split(':')[1] for d in map(lambda x: x.strip()[1:-1], data[1].split(","))}
        if prov_id is None:
            print(line)
        else:
            assert prov_id not in city_info
            city_info[prov_id] = citys
    for k, v in municipalitys.items():
        city_info[k] = {v: provs[k]}
    err = []
    with open("out.xls", 'wb') as f:
        f.write(b'school_id\tcity_code\tprov_name\tcity_name\tarea_name\tschool_type\tschool_name\n')
        for school_type in paths:
            for prov_id, prov_name in provs.items():
                for city_id, city_name in city_info[prov_id].items():
                    url = "http://support.renren.com/%s/%s.html" % (school_type, city_id)
                    html = download_and_save(url, basepath)
                    if not html:
                        continue

                    pyq = PyQuery(html)
                    areanames = {a.get("onclick").split("'")[1]: a.text_content() for a in pyq('#schoolCityQuList a')}
                    if 'city_qu_%s' % city_id not in areanames:
                        areanames['city_qu_%s' % city_id] = city_name
                    ids = [ul.get('id') for ul in pyq('ul')]
                    for ulid in ids:
                        if not ulid.startswith("city_qu_"):
                            continue
                        city_code = ulid[8:]
                        for a in pyq("#"+ulid+" a"):
                            schoolid = a.get('href')
                            if hasattr(a, 'text_content'):
                                schoolname = a.text_content()
                            else:
                                schoolname = a.text
                            if not schoolname:
                                err.append([schoolid, city_code, prov_name, areanames[ulid], school_type, schoolname.strip()])
                            f.write(b'\t'.join(map(lambda x: x.encode("utf-8"), [schoolid, city_code, prov_name, city_name, areanames[ulid], school_type, schoolname.strip()])))
                            f.write(b'\n')
        print(err)
            # for a in pyq('ul'):
            #     href = a.get('href')
            #     newurl = urllib.parse.urljoin(url, href)
            #     download(newurl, basepath, urlprefix, proc, force)
            
