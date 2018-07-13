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
            single_price = i.find_all('span', 'red')[0].parent.text or i.find_all(text=re.compile('1元=\d+\.\d+万金'))[0]
            # 纯单价(数字)
            raw_single_price = float(re.search(r'(?<=1元=)\d+\.\d+(?=万金)', single_price).group())
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


def report_info(infos, raw_single_price=178, report_type='print'):
    # todo 这里把info发邮箱或者wechat
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
        print(time.ctime(), '暂时没有符合条件的!')
    pass


def main():
    while True:
        # this url is 玩具城金币价格 page
        target_url = 'https://www.dd373.com/s/1xj2qx-wjm3vp-r9xvef-0-0-0-tr1r70-0-0-0-0-0-0-0-0.html'
        html = get_html(target_url)
        infos = parse_html(html)
        report_info(infos)
        
        time.sleep(60)


if __name__ == '__main__':
    # todo 测试功能:
    ## 1.能否访问网页
    
    ## 2.能否正常解析页面
    
    
    # 开始运行:
    # itchat.auto_login(hotReload=True) # todo 这里要做成class内置
    # itchat.send('DD373爬虫开始运行!', toUserName='filehelper')
    main()
