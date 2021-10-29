# -*- coding = utf-8 -*-
# @Time : 2021/10/25 14:08
# @Author : zdd
# @File : law.py
# @Software : PyCharm

import urllib.request
import urllib.parse
import json
import xlwt

law_status = {
    "3": "尚未生效",
    "1": "有效",
    "5": "已修改",
    "9": "已废止"
}

def main():
    url = "https://flk.npc.gov.cn/api/?type=dfxfg&searchType=title%3Baccurate&sortTr=f_bbrq_s%3Bdesc&gbrqStart=&gbrqEnd=&sxrqStart=&sxrqEnd=&sort=true&size=10&_=1635142000499&page="
    law_list = lawList(url)
    saveData(law_list, "国家法律法规.xls")

def lawList(url):
    page = 1
    law_list = []
    while 1:
        next_url = url + str(page)
        json_str = getForJson(next_url)
        law_dict = json.loads(json_str)
        law_array = law_dict["result"]["data"]
        totalSizes = law_dict["result"]["totalSizes"]
        for law in law_array:
            lawDetails(r"https://flk.npc.gov.cn/api/detail", law_list, law)
        if 10 <= page*10:
            break
        page += 1
    return law_list

def lawDetails(url, law_list, law):
    url = url + "?id=" + law["id"]
    json_str = getForJson(url)
    law_dict = json.loads(json_str)
    law["docUrl"] = "https://wb.flk.npc.gov.cn/" + law_dict["result"]["body"][0]["path"]
    law_list.append(law)
    print(law)

def saveData(dataList, savePath):
    workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = workbook.add_sheet("国家法律法规", cell_overwrite_ok=True)
    title = ("标识", "法律标题", "制定机关", "公布日期", "施行日期", "法律效力位阶", "时效性", "详情页url", "法律文档下载地址")
    count = len(dataList)
    for i in range(0, 9):
        sheet.write(0, i, title[i])
    for i in range(0, count):
        data = dataList[i]
        sheet.write(i + 1, 0, data["id"])
        sheet.write(i + 1, 1, data["title"])
        sheet.write(i + 1, 2, data["office"])
        sheet.write(i + 1, 3, data["publish"])
        sheet.write(i + 1, 4, data["expiry"])
        sheet.write(i + 1, 5, data["type"])
        sheet.write(i + 1, 6, law_status[data["status"]])
        sheet.write(i + 1, 7, data["url"])
        sheet.write(i + 1, 8, data["docUrl"])
    workbook.save(savePath)

def getForJson(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36 SLBrowser/6.0.1.6181"
    }
    request = urllib.request.Request(url=url, headers=head)
    json_str = ""
    try:
        response = urllib.request.urlopen(request)
        json_str = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return json_str

if __name__ == '__main__':
    main()