#-*- coding = utf-8 -*-
#@Time : 2020/9/4 16:48
#@Author : zdd
#@File : douban.py
#@Software : PyCharm

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import xlwt
import pymysql

def main():
    baseurl = "https://movie.douban.com/top250?start="
    print("-------------------开始爬取数据-------------------")
    dataList = getData(baseurl)
    print("-------------------爬取数据完成-------------------")
    savaPath = "豆瓣电影top250.xls"
    print("-------------------开始保存数据-------------------")
    # saveData(dataList, savaPath)
    # saveToMysql(dataList)
    print("-------------------保存数据完成-------------------")

findUrl = re.compile(r'<a href="(.*?)">')
findName = re.compile(r'<span class="title">(.*?)</span>')
findImg = re.compile(r'<img.*src="(.*)" width="100"', re.S)
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*?)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)

# 解析页面
def getData(baseurl):
    dataList = []
    for i in range(0, 10):
        url = baseurl + str(i*25)
        html = askUrl(url)
        bs = BeautifulSoup(html, "html.parser")
        item_list = bs.select("div[class='item']")
        for item in item_list:
            data = []
            item = str(item)

            # 获取电影链接
            movieUrl = re.findall(findUrl, item)[0]
            data.append(movieUrl)

            # 获取电影名字
            name = re.findall(findName, item)
            if len(name) == 2:
                data.append(name[0])
                # 去除空格\xa0
                foreignName = name[1]
                foreignName = "".join(foreignName.split())
                foreignName = re.sub(r'/', '', foreignName)
                data.append(foreignName)
            else:
                data.append(name[0])
                data.append("")

            # 获取电影图片路径
            img = re.findall(findImg, item)[0]
            data.append(img)

            # 获取电影评分
            rating = re.findall(findRating, item)[0]
            data.append(rating)

            # 获取评价人数
            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)

            # 获取电影概述
            inqs = re.findall(findInq, item)
            if len(inqs) != 0:
                inq = inqs[0]
                data.append(inq)
            else:
                data.append("")

            bd = re.findall(findBd, item)[0]

            # 获取电影简介
            # 去除空格\xa0
            bd = "".join(bd.split())
            bd = bd.strip()
            bd = re.sub('<br/>', '', bd)
            data.append(bd)
            dataList.append(data)
            print(data)
    return dataList

# 保存数据至excle文件中
def saveData(dataList, savePath):
    workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = workbook.add_sheet("豆瓣电影top250", cell_overwrite_ok=True)
    title = ("电影详情链接", "电影中文名", "电影外文名", "电影图片", "电影评分", "评价人数", "电影概述", "电影简述")
    for i in range(0, 8):
        sheet.write(0, i, title[i])
    for i in range(0, 250):
        data = dataList[i]
        for j in range(0, 8):
            sheet.write(i+1, j, data[j])
    workbook.save(savePath)

# 访问页面获取内容
def askUrl(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36 SLBrowser/6.0.1.6181"
    }
    request = urllib.request.Request(url=url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

# 将爬取的数据存储到mysql数据库中
def saveToMysql(dataList):
    # 连接数据库
    conn = pymysql.connect(host="localhost", port=3306, user="root", password="root", database="my_test")
    # 得到游标
    cursor = conn.cursor()
    for i in range(0, 250):
        data = dataList[i]
        sql = 'INSERT INTO douban_movie (MovieLink,MovieChineseName,MovieForeignName,MovieImgPath,MovieRating,MovieJudgeNum,MovieInq,MovieBd) VALUES('
        sql = sql + '"' + data[0] + '","' + data[1] + '","' + data[2] + '","' + data[3] + '",' + data[4] + ',' + data[5] + ',"' + data[6] + '","' + data[7] + '");'
        cursor.execute(sql)
    conn.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    conn.close()

if __name__ == "__main__":
    main()
    print("爬虫执行完成")