import re, requests, time, itchat
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
        try:

            # 总价
            total_price = i.find_all('div', 'money_text')[0].text
            # 购买链接
            href = 'https://www.dd373.com' + i.find_all('a', 'titleText')[0]['href']
            # 单价('xxxx万金/元')
            single_price = i.find_all('span', 'red')[0].parent.text or i.find_all(text=re.compile('1元=\d+\.\d+[万金|个]'))[0]
            # 纯单价(数字)
            raw_single_price = float(re.search(r'(?<=1元=)\d+\.\d+(?=[万金|个|组])', single_price).group())
            # 商品数量
            amount = i.find_all('div', 'num left')[0].text.strip()
            
            # print(f'total price:{total_price}, single price:{raw_single_price}, amount:{amount}, {href}')
            info = {
                'total_price': total_price,
                'href': href,
                'raw_single_price': raw_single_price,
                'amount': amount
            }
            
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
    import sqlite3
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



    pass


def price_parse(infos):
    # 价格排序
    infos.sort(key=lambda x:x.get('raw_single_price'),reverse=True)

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
    info=price_parse(infos)

    if write_db(info,table_name) is None:
        print(f"{time.ctime()}, no data has been found...")
    else:
        print(f"{time.ctime()}, writing database...")


def main_start():
    # 轮番查询玩具城各个材料的价格,写入db
    url_dict={
        'wjc_gold': 'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-tr1r70-0-0-0-0-0-0-0-0.html',
        'wjc_manao':'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-knrc07-0-0-0-0-0-0-0-0.html',
        'wjc_xiaomanao':'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-fqujdj-0-0-0-0-0-0-0-0.html'
    }
    while True:
        for table_name,url in url_dict.items():
            main(url,table_name)
            time.sleep(30)

def main2(target_price_gold=140,target_price_manao=50,report_type='print'):
    # 监测玩具城金币价格>1:target_price_gold的
    print('金币价格',end='')
    target_url = 'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-tr1r70-0-0-0-0-0-0-0-0.html'
    html = get_html(target_url)
    infos = parse_html(html)
    report_info(infos,raw_single_price=target_price_gold,report_type=report_type)




    # 监测玩具城玛瑙价格>1:50的
    print('玛瑙价格',end='')
    target_url = 'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-knrc07-0-0-0-0-0-0-0-0.html'
    html = get_html(target_url)
    infos = parse_html(html)
    report_info(infos,raw_single_price=target_price_manao,report_type=report_type)
    time.sleep(60)
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
    main_start()
