import os

from bs4 import BeautifulSoup

from twhousedetail.web import get_page_source
from twhousedetail.community import Community


class HousePrice(Community):
    @staticmethod
    def prefix():
        return 'price'

    @staticmethod
    def _get_list_html_doc(url):
        html_doc = get_page_source(url, minimize=True)
        with open('price.html', 'w') as fp:
            fp.write(html_doc)
        return html_doc

    @staticmethod
    def _list_name_and_url(soup: BeautifulSoup):
        for list_con_link in soup.find_all('a',
                                           {'class': 'list_con_link group'}):
            name = list_con_link.find('h3', {'class': 'title_list'}).text
            href = list_con_link.get('href')
            url = f'https://community.houseprice.tw{href}'
            yield name, url

    @staticmethod
    def _get_html_doc(url):
        return get_page_source(url, minimize=True)

    @staticmethod
    def _get_name(html_doc):
        return Building(BeautifulSoup(html_doc, 'html.parser')).name()

    @staticmethod
    def get_info(html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        result = Building(soup).info()
        return result

    @staticmethod
    def _get_map(html_doc):
        pass

    @staticmethod
    def _show_titles():
        titles = ['名稱', '平均單價', '最新成交單價', '實價登錄最低 ~ 最高單價區間',
                  '特色', '地址', '類型', '土地使用分區', '國小學區', '國中學區',
                  '屋齡', '樓高', '坪數', '公設比', '主結構', '建設公司', '機構',
                  '營造公司', '公共設施', '戶數', '管理方式', '車位型態', '垃圾清運',
                  '待售筆數', '待售總價', '議價率', '交通', '學校', '醫療', '購物',
                  '嫌惡設施', '連結']
        print('\t'.join(titles))
        print('-' * len('\t'.join(titles)))


class Building:
    def __init__(self, soup: BeautifulSoup):
        self._soup = soup

    def name(self):
        return self._soup.find('div',
                               {'class': 'detail_header'}).find('h1').text

    def info(self):
        detail_content = self._soup.find('div', {'class': 'detail_content'})
        title = ''
        for content in detail_content.find_all('li'):
            if '平均單價' in content.text:
                price_avg = content.text[len('平均單價'):]
            elif '最新成交單價' in content.text:
                price_newest = content.text[len('最新成交單價'):]
            elif '實價登錄最低' in content.text:
                price_range = content.text[len('實價登錄最低 ~ 最高單價區間'):]
            else:
                title = content.text
        for detail_footer in self._soup.find_all('div',
                                                 {'class': 'detail_footer'}):
            for item_title in detail_footer.find_all('li'):
                key = item_title.find('span', {'class', 'item-title'}).text
                value = item_title.text[len(key):]
                if key == '交屋時間':
                    return
                if key == '型態' and '預售屋' in value:
                    return
                if key == '地址':
                    address = value
                elif key == '類型':
                    building_type = value
                elif key == '土地使用分區':
                    use_plan = value
                elif key == '國小學區':
                    elementary = value
                elif key == '國中學區':
                    high_school = value
                elif key == '屋齡':
                    age = value
                elif key == '樓高':
                    height = value
                elif key == '坪數':
                    size = value
                elif key == '公設比':
                    ratio = value
                elif key == '主結構':
                    structure = value
                elif key == '建設公司':
                    construction_company = value
                    group = ''
                    for spliter in ['-', ',', '、']:
                        if spliter in value:
                            for v in value.split(spliter):
                                if '機構' in v:
                                    group = v
                elif key == '營造公司':
                    building_company = value
                elif key == '公共設施':
                    public_util = value
                elif key == '戶數':
                    house_number = value
                elif key == '管理方式':
                    management = value
                elif key == '車位型態':
                    car = value
                elif key == '垃圾清運':
                    garbage = value
        relative = self._soup.find('header',
                                   {'class': 'relative title_2'}).find('p')
        to_sell = None
        for span in relative.find_all('span'):
            if not to_sell:
                to_sell = span.text
            else:
                to_sell_range = span.text
        bargain_content = ''
        for bargain in self._soup.find_all('div',
                                           {'class': 'bargain_content'}):
            if '議價率' in bargain.text:
                bargain_content = bargain.find('span',
                                               {'class': 'price_txt'})
                bargain_content = bargain_content.text.split()[0]
                break
        for nav in self._soup.find('ul', {'class': 'nav-wrap'}):
            key = nav.text.split('(')[0]
            value = nav.text.split('(')[1][:-1]
            if key == '交通':
                traffic = value
            elif key == '學校':
                school = value
            elif key == '醫療':
                hospital = value
            elif key == '購物':
                shopping = value
            elif key == '嫌惡設施':
                nimby = value
        url = self._soup.find('link', {'rel': 'canonical'}).get('href')
        result = [self.name(), price_avg, price_newest, price_range, title,
                  address, building_type, use_plan, elementary, high_school,
                  age,
                  height, size, ratio, structure, construction_company, group,
                  building_company, public_util, house_number, management,
                  car, garbage, to_sell, to_sell_range, bargain_content,
                  traffic, school, hospital, shopping, nimby, url]
        return '\t'.join(result)
