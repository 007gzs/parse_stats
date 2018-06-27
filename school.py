#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from pyquery import PyQuery
from download import download_and_save


if __name__ == "__main__":
    basepath = '/007/data/school'
    paths = ['juniorschool', 'collegeschool', 'highschool']
    provs = {
        '1101': '北京',
        '3101': '上海',
        '1201': '天津',
        '5001': '重庆',
        '2301': '黑龙江',
        '2201': '吉林',
        '2101': '辽宁',
        '3701': '山东',
        '1401': '山西',
        '6101': '陕西',
        '1301': '河北',
        '4101': '河南',
        '4201': '湖北',
        '4301': '湖南',
        '4601': '海南',
        '3201': '江苏',
        '3601': '江西',
        '4401': '广东',
        '4501': '广西',
        '5301': '云南',
        '5201': '贵州',
        '5101': '四川',
        '1501': '内蒙古',
        '6401': '宁夏',
        '6201': '甘肃',
        '6301': '青海',
        '5401': '西藏',
        '6501': '新疆',
        '3401': '安徽',
        '3301': '浙江',
        '3501': '福建',
        '7101': '澳门',
        '8101': '香港',
        '8200': '海外',
    }


    with open("out.xls", 'wb') as f:
        f.write(b'school_id\tcity_code\tprov_name\tschool_type\tschool_name\n')
        for path in paths:
            for prov, prov_name in provs.items():
                url = "http://support.renren.com/%s/%s.html" % (path, prov)
                html = download_and_save(url, basepath)
                if not html:
                    continue
                pyq = PyQuery(html)
                areanames = {a.get("onclick").split("'")[1]: a.text_content() for a in pyq('#schoolCityQuList a')}
                ids = [ul.get('id') for ul in pyq('ul')]
                for ulid in ids:
                    if not ulid.startswith("city_qu_"):
                        continue
                    city_id = ulid[8:]
                    for a in pyq("#"+ulid+" a"):
                        schoolid = a.get('href')
                        schoolname = a.text_content()
                        f.write(b'\t'.join(map(lambda x: x.encode("utf-8"), [schoolid, prov_name, city_id, path, schoolname])))
                        f.write(b'\n')
            
            # for a in pyq('ul'):
            #     href = a.get('href')
            #     newurl = urllib.parse.urljoin(url, href)
            #     download(newurl, basepath, urlprefix, proc, force)
            
