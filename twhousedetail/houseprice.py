import os

from bs4 import BeautifulSoup

from twhousedetail.web import get_page_source
from twhousedetail.community import Community


class HousePriceCommunity(Community):
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
        print('-' * (len(titles) * 2 * 4))


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


class HousePriceSales:
    def __init__(self):
        self._prefix = 'price-buy'
        if not os.path.exists(self._prefix):
            os.mkdir(self._prefix)

    def _html_path(self, html_name):
        return f'{self._prefix}/{html_name}.html'

    def _result_path(self):
        return f'{self._prefix}.txt'

    def save(self, url):
        count = 0
        soup = BeautifulSoup(get_page_source(url, minimize=True),
                             'html.parser')
        for sale in soup.find_all('li', {
            'class': 'bg-white border-solid flex space-x-5 border-gray-200 text-base py-10 px-6 text-c-dark-900 group align-middle hover:bg-[#f8f7f6] border-b'}):
            url = self._get_url(sale)
            count += 1
            url_sequence_number = url[len('https://buy.houseprice.tw/house/'):]
            html_name = url_sequence_number.split('/')[0]
            if os.path.exists(self._html_path(html_name)):
                continue
            url = 'https://buy.houseprice.tw/house/' + html_name
            print(f'Save {url} to {self._html_path(html_name)} ...')
            with open(self._html_path(html_name), 'w') as fp:
                fp.write(get_page_source(url, minimize=True))
        print(f'Total: {count}')

    def _get_url(self, sale):
        for a in sale.find_all('a'):
            url = a.get('href')
            if url and 'buy' in url:
                return url

    def show(self):
        count = 0
        self._show_titles()
        with open(self._result_path(), 'w') as fp:
            for file in os.listdir(self._prefix):
                count += 1
                name, _ = os.path.splitext(file)
                result = self._get_sale(name)
                print(result)
                fp.write(f'{result}\n')
        print(f'Total: {count}')
        print(f'Saved to {self._result_path()}')

    def _get_sale(self, name):
        with open(self._html_path(name), 'r') as fp:
            html_doc = fp.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        vue_container = soup.find('div', {'id': 'vue-container'})
        case_info = vue_container.find('section',
                                       {'class': 'case_info buyHouse_info'})
        address = ''
        for p in case_info.find_all('p'):
            if not p:
                continue
            if '地址' in p.text:
                address = p.text[len('地址 / '):]
        sale_price = price_per_size = total_size = main_size = land_size = ''
        for li in case_info.find_all('li'):
            if not li:
                continue
            if '最低' in li.text:
                sale_price = li.text[len('最低'):-1]
            elif '每坪' in li.text:
                price_per_size = li.text[len('每坪'):-1]
            elif '主建物' in li.text:
                main_size = li.text.split()[2]
            elif '建物' in li.text:
                total_size = li.text.split()[2]
            elif '土地' in li.text:
                land_size = li.text.split()[2]
        building_type = community = floor_info = car = height = age = ''
        for br in case_info.find_all('br'):
            if not br:
                continue
            if '型態' in br.next_sibling:
                building_type = get_value(br.next_sibling)
            elif '社區' in br.next_sibling:
                community = get_value(br.next_sibling)
            elif '格局' in br.next_sibling:
                floor_info = get_value(br.next_sibling)
            elif '車位' in br.next_sibling:
                car = get_value(br.next_sibling)
            elif '樓層' in br.next_sibling:
                height = get_value(br.next_sibling)
            elif '屋齡' in br.next_sibling:
                age = get_value(br.next_sibling)[:-1]
        feature = soup.select_one('a[title][href*=list]')
        feature = feature.text if feature else ''
        buy = soup.find('div', {'class': 'buyHouse_detail_tb_wrap close'})
        similar = ''
        if buy:
            for td in buy.find_all('td'):
                if '相似物件刊登' not in td.text:
                    continue
                similar = td.text[len('這個待售房屋，共有 '):-len(' 筆相似物件刊登')]
        url = vue_container.find('a', {'class': 'cover-image'}).get('href')
        result = [
            community,
            age,
            height,
            car,
            total_size,
            main_size,
            land_size,
            floor_info,
            sale_price,
            price_per_size,
            similar,
            feature,
            building_type,
            address,
            url
        ]
        return '\t'.join(result)

    @staticmethod
    def _show_titles():
        titles = [
            '社區',
            '屋齡',
            '樓層',
            '車位',
            '建物',
            '主建物',
            '土地',
            '格局',
            '出價',
            '單價',
            '相似物件',
            '特色',
            '型態',
            '地址',
            '連結'
        ]
        print('\t'.join(titles))
        print('-' * (len(titles) * 2 * 4))


def get_value(br_text):
    elements = []
    for br in br_text.split('/'):
        elements.append(br.replace(' ', ''))
    return '/'.join(elements[1:])
