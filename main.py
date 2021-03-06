import re, requests, time, itchat,webbrowser
import sqlite3
from bs4 import BeautifulSoup


def get_html(url):
    r = requests.get(url)
    if r.status_code == 200:
        html = BeautifulSoup(r.content, 'lxml')
        return html


def parse_html(html):
    tags = html.find_all('div', 'box money_ner')
    infos = list()
    for i in tags:
        # 确定在html里面找各个数据,如果找不到,则返回None
        # todo 这里用了很多try-except, 能不能修改得更简洁
        try:
            # 总价
            total_price = i.find_all('div', 'money_text')[0].text

            # 购买链接
            href = 'https://www.dd373.com' + i.find_all('a', 'titleText')[0]['href']

            try:
            # 单价('xxxx万金/元')
                single_price = i.find_all('span', 'red')[0].parent.text or i.find_all(text=re.compile('1元=\d+\.\d+[万金|个]'))[0]
            except:
                single_price=None

            # 纯单价(数字)

            try:
                raw_single_price = float(re.search(r'(?<=1元=)\d+\.\d+(?=[万金|个|组])', single_price).group())
            except:
                raw_single_price=re.search('[\d|\.]+',total_price).group()

            # 商品数量
            try:
                amount = i.find_all('div', 'num left')[0].text.strip()
            except:
                amount=0

            # print(f'total price:{total_price}, single price:{raw_single_price}, amount:{amount}, {href}')
            info = {
                'total_price': total_price,
                'href': href,
                'raw_single_price': raw_single_price,
                'amount': amount
            }

            print(info)
            infos.append(info)
        except:
            pass
    return infos
    pass


def report_info(infos, raw_single_price=178, report_type="print"):
    count = 0
    for i in infos:
        if i['raw_single_price'] > raw_single_price:
            print(i)
            count += 1
            if report_type == 'print':
                print(i)
            elif report_type == 'wechat':
                itchat.send(str(i), toUserName='filehelper')
            else:
                assert 'wrong report type!'
    if count == 0:
        print(time.ctime(), '暂时没有符合条件的!当前最低价格:%s'%infos[0].get('raw_single_price'))
    pass



def write_db(info={'amount': '1', 'href': 'https://www.dd373.com/buy/third-259134718.html', 'raw_single_price': 110.0, 'total_price': '20.00元'},table_name='test'):
    '''
    下面是info格式
  {'amount': '',  'href': 'https://www.dd373.com/buy/third-259134709.html',  'raw_single_price': 110.0, 'total_price': '10.00元'}
    '''
    # 写入sqlite数据库

    # INSERT INTO test VALUES("2018-07-22","12元","www.baidu.com",18.10,"");
    conn=sqlite3.connect('dd373.db')
    c=conn.cursor()
    # todo 如果没有表,新建


    # 如有表:
    # 如果有同样的数据在表里, 则不写入(价格,url,数量都不变)
    c.execute(f'''
    SELECT * FROM {table_name} WHERE href="{info['href']}" AND amount="{info['amount']}" AND total_price="{info[
    'total_price']}"; 
    ''')
    query_result=c.fetchone()
    if query_result is not None:
        conn.commit()
        conn.close()
        return None


    # 写入数据到表table (时间,总价,url,单价,数量)
    c.execute(
        f"INSERT INTO {table_name} VALUES ('{time.ctime()}','{info['total_price']}','{info['href']}',"
        f"'{info['raw_single_price']}','{info['amount']}');"
    )
    # 提交
    conn.commit()
    conn.close()
    # 成功写入则返回成功写入的表名和最新单价.
    return (table_name,info.get('raw_single_price'))


    pass


def price_parse(infos,table_name):
    # 价格排序: 放入一个数据列表,返回最便宜且有货的那一条数据.

    # 如果是金币和价格表,则返回raw_single_price最高的; 如果是宝石,则返回raw_single_price最低的!
    if 'gold' in table_name or 'manao' in table_name:
        reverse=True
    elif 'gem' in table_name:
        reverse=False

    infos.sort(key=lambda x:x.get('raw_single_price'),reverse=reverse)

    # 筛选出有amount(有货)的最低价商品
    for info in infos:
        if info.get('amount')<'1' or not info.get('amount').isnumeric():
            pass
        else:
            return info
    pass


def main(url,table_name):

    html = get_html(url)
    infos = parse_html(html)
    # 用price_parse筛选出有货的最低价 && 写入数据库
    info=price_parse(infos,table_name)
    result=write_db(info,table_name)
    if result is None:
        print(f"{time.ctime()}, no data has been found...")
    else:
        print(f"{time.ctime()}, writing database: {result}")


def alert(target_price=130,table_name='wjc_gold'):
    # 监测玩具城金币价格>1:target_price_gold的




    # 查询数据库

    conn=sqlite3.connect('dd373.db')
    c=conn.cursor()
    query=c.execute(f'SELECT raw_single_price,href FROM {table_name} WHERE time=(SELECT MAX(time) FROM {table_name});')
    query_result=query.fetchone()
    conn.close()

    raw_single_price,href=query_result
    # if 'gold' in table_name or 'manao' in table_name:
    #     if float( raw_single_price )>target_price:
    #         print(f'{time.ctime()}发现低于{target_price}的商品上架! {href}')
    #         return href
    #
    #     else:
    #         print(f'{time.ctime()}  未监测到合适价格.')
    #         return none
    # elif 'gem' in table_name:
    #     if float( raw_single_price )<target_price:
    #         print(f'{time.ctime()}发现低于{target_price}的商品上架! {href}')
    #         return href
    #
    #     else:
    #         print(f'{time.ctime()}  未监测到合适价格.')
    #         return None
    #
    # pass


    if 'gold' in table_name or 'manao' in table_name:
        match=float( raw_single_price )>=target_price
    elif 'gem' in table_name:
        match=float( raw_single_price )<=target_price



    if match:
        print(f'{time.ctime()}发现低于{target_price}的商品上架! {href}')
        return href
    else:
        print(f'{time.ctime()}  未监测到合适价格.')
        return None

def main_start(alert_on=True,target_price=140,alert_table_name='wjc_gold'):
    # 轮番查询玩具城各个材料的价格,写入db
    url_dict={
        'wjc_gem_str_lv7':'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-6c8cj0-49ravp-01wbns_1676vw-0-0-pu-0-0-0.html',
        'wjc_gold': 'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-tr1r70-0-0-0-0-0-0-0-0.html',
        'wjc_manao':'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-knrc07-0-0-0-0-0-0-0-0.html',
        'wjc_xiaomanao':'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-fqujdj-0-0-0-0-0-0-0-0.html',
        'nwz_gold':'https://www.dd373.com/s/1xj2qx-wjm3vp-qmfpmj-0-0-0-tr1r70-0-0-0-0-0-0-0-0.html',
        'tly_gold':'https://www.dd373.com/s/1xj2qx-wjm3vp-rs23j0-0-0-0-tr1r70-0-0-0-0-0-0-0-0.html',
    }


    openweb_url=None
    while True:
        for table_name,url in url_dict.items():
            try:
                main(url,table_name)

                # 监测模块,(开关, 防重复播报)
                if alert_on==True:
                    query_result=alert(target_price=target_price,table_name=alert_table_name)
                    if (query_result is None) or (query_result==openweb_url):
                        pass
                    else:
                        openweb_url=query_result
                        webbrowser.open(openweb_url)

                time.sleep(15)
            except:
                time.sleep(15)
                pass





if __name__ == '__main__':
    # todo 测试功能:
    ## 1.能否访问网页
    
    ## 2.能否正常解析页面
    
    
    # 开始运行:

    # itchat.auto_login(hotReload=True) # todo 这里要做成class内置
    # itchat.send('DD373爬虫开始运行!', toUserName='filehelper')
    # print('开始运行!')
    # for i in range(3600):
    #     main2(target_price_gold=130,target_price_manao=55)

    # 轮番查询玩具城各个材料的价格,写入db
    main_start(alert_on=True,target_price=65,alert_table_name='wjc_gem_str_lv7')
    # alert()
