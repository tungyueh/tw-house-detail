import json
import os

from bs4 import BeautifulSoup

from twhousedetail.community import Community
from twhousedetail.web import get_page_source


class Tw591Community(Community):
    @staticmethod
    def prefix():
        return '591'

    @staticmethod
    def _get_list_html_doc(url):
        html_doc = get_page_source(url, load_by_scroll=True)
        return html_doc

    @staticmethod
    def _list_name_and_url(soup: BeautifulSoup):
        for card in soup.find_all('a', {'class': 'community-card'}):
            community_info = card.find('div', {'class': 'community-info'})
            name = community_info.find('h3').text
            yield name, card.get('href')

    @staticmethod
    def _get_html_doc(url):
        return get_page_source(url, wait_photo=True)

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
        soup = BeautifulSoup(html_doc, 'html.parser')
        return Building(soup).map()

    @staticmethod
    def _show_titles():
        titles = ['名稱', '成交均價', '二手銷售均價', '議價率', '實價登錄',
                  '二手市場在售', '特色', '位置', '屋齡', '總戶數', '公設比',
                  '建蔽率', '建築型態', '用途規劃', '建築構造', '管委會',
                  '物業公司', '管理費', '基地面積', '土地分區', '樓棟規劃',
                  '樓層規劃', '格局規劃', '連結']
        print('-' * len('\t'.join(titles)))
        print('-' * (len(titles) * 2 * 4))


class Building:
    def __init__(self, soup: BeautifulSoup):
        self._soup = soup

    def name(self):
        soup = self._soup.find('script', {'type': 'application/ld+json'})
        name = json.loads(soup.text)['name']
        return name

    def url(self):
        json_result = json.loads(
            self._soup.find('script', {'type': 'application/ld+json'}).text
        )
        for item in json_result['itemListElement']:
            if item['name'] == self.name():
                url = item['item']
                return url

    def map(self):
        photo_album_cover = self._soup.find(
            'img', {'class': 'photo-album-cover'}
        )
        building_map_photo_url = self._soup.find(
            'img', {'class': 'building-map-photo'}
        )
        result = [f'## [{self.name()}]({self.url()})']
        if photo_album_cover and photo_album_cover.get('data-src'):
            photo_album_cover = photo_album_cover.get('data-src')
            result.append(f'![]({photo_album_cover})')
        if building_map_photo_url and building_map_photo_url.get(
                'data-src'):
            building_map_photo_url = building_map_photo_url.get('data-src')
            result.append(f'![]({building_map_photo_url})')
        return '\n'.join(result)

    def info(self):
        address = self._soup.find('li', {'class': 'address lg'})
        life = address.find('em', {'class': 'life'})
        feature = life.text if life else ''
        location = address.text[len(feature):]
        price_info = self._soup.find('ul', {'class': 'price-info'})
        price = price_info.find('p', {'class': 'price'})
        price = price.text if price else ''
        price_average = price_info.find('p', {'class': 'price average'})
        price_average = price_average.text.split()[0] if price_average else ''
        raw_bubble_rate = price_info.find('span', {'class': 'bubble rate'})
        bubble_rate = raw_bubble_rate.text[3:] if raw_bubble_rate else ''
        count_info = self._soup.find('ul', {'class': 'count-info'})
        done_sell = count_info.text.split()[1]
        to_sell = count_info.text.split()[4]
        detail_info = self._soup.find('ul', {'class': 'detail-info'})
        for item in detail_info.find_all('li', {'class': 'detail-info-item'}):
            key = item.find('h6').text
            value = item.find('p').text
            if key == '建案類別':
                return
            elif key == '屋齡':
                house_age = value[:-1]
            elif key == '總戶數':
                house_number = value
            elif key == '公設比':
                ratio_of_public = value
            elif key == '建蔽率':
                building_coverage_ratio = value
            elif key == '建築型態':
                building_type = value
            elif key == '用途規劃':
                use_plan = value
            elif key == '建築構造':
                building_structure = value
            elif key == '管委會':
                management_committee = value
            elif key == '物業公司':
                property_management = value
            elif key == '管理費':
                management_fee = value
            elif key == '基地面積':
                base_area = value
            elif key == '土地分區':
                land_use_zone = value
            elif key == '樓棟規劃':
                building_plan = value
            elif key == '樓層規劃':
                floor_plan = value
            elif key == '格局規劃':
                room_plan = value
            else:
                print(f'unknown: {key} {value}')
        result = [(self.name()), price, price_average, bubble_rate, done_sell,
                  to_sell,
                  feature, location,
                  house_age, house_number, ratio_of_public,
                  building_coverage_ratio, building_type, use_plan,
                  building_structure, management_committee,
                  property_management,
                  management_fee, base_area, land_use_zone, building_plan,
                  floor_plan, room_plan, (self.url())]
        return '\t'.join(result)


class Tw591Sales:
    def __init__(self):
        self._prefix = '591-buy'
        if not os.path.exists(self._prefix):
            os.mkdir(self._prefix)

    def _folder_path(self, community_name):
        return f'{self._prefix}/{community_name}'

    def _html_path(self, community_name, html_name):
        return f'{self._folder_path(community_name)}/{html_name}'

    def _result_path(self):
        return f'{self._prefix}.txt'

    def save(self, url):
        count = 0
        html_doc = get_page_source(url)
        soup = BeautifulSoup(html_doc, 'html.parser')
        community_name = soup.find('header', {'class': 'header-bar'})
        community_name = community_name.find('h2').text.split('·')[0]
        if not os.path.exists(self._folder_path(community_name)):
            os.mkdir(self._folder_path(community_name))
        for info in soup.find_all('a'):
            href = info.get('href')
            if not href or 'detail' not in href:
                continue
            count += 1
            html_name = href.split('/')[-1]
            html_path = self._html_path(community_name, html_name)
            print(f'Save {href} to {html_path} ...')
            with open(html_path, 'w') as fp:
                fp.write(get_page_source(href))
        print(f'Total: {count}')

    def show(self):
        count = 0
        self._show_titles()
        with open(self._result_path(), 'w') as fp:
            for _, dirs, _ in os.walk(self._prefix):
                for d in dirs:
                    for result in self._get_community_sales(d):
                        count += 1
                        print(result)
                        fp.write(f'{result}\n')
        print(f'Total: {count}')
        print(f'Saved to {self._result_path()}')

    def _get_community_sales(self, community_name):
        for file in os.listdir(self._folder_path(community_name)):
            yield self._get_sale(community_name, file)

    def _get_sale(self, community_name, html_name):
        with open(self._html_path(community_name, html_name), 'r') as fp:
            html_doc = fp.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        info_price_num = soup.find('span',
                                   {'class': 'info-price-num'}).text
        info_price_per = soup.find('div', {'class': 'info-price-per'}).text
        single_price = soup.find('span', {'class': 'single-price'}).text
        single_price = info_price_per[len(single_price) + 1:]
        floor_info = age = size = ''
        for floor in soup.find_all('div', {'class': 'info-floor-left'}):
            key = floor.find('div', {'class': 'info-floor-value'}).text
            value = floor.find('div', {'class': 'info-floor-key'}).text
            if key == '格局':
                floor_info = value
            elif key == '屋齡':
                age = value
            elif key == '權狀坪數':
                size = value
        height = face = community = address = ''
        for addr in soup.find_all('div', {'class': 'info-addr-content'}):
            key = addr.find('span', {'class': 'info-addr-key'}).text
            value = addr.find('span', {'class': 'info-addr-value'}).text
            if key == '樓層':
                height = value
            elif key == '朝向':
                face = value
            elif key == '社區':
                community = value
            elif key == '地址':
                address = value
        host_name = soup.find('span', {'class': 'info-span-name'}).text
        host_detail = soup.find('div', {'class': 'info-detail-show'}).text
        host_detail = ' '.join(host_detail.split())
        now = building_type = decorate = management_fee = rent = use = car = \
            main_size = share_size = sub_size = land_size = ''
        for house in soup.find_all('div', {'class': 'detail-house-item'}):
            if not house.find('div', {'class': 'detail-house-key'}):
                continue
            key = house.find('div', {'class': 'detail-house-key'}).text
            value = house.find('div', {'class': 'detail-house-value'}).text
            if key == '現況':
                now = value
            elif key == '型態':
                building_type = value
            elif key == '裝潢程度':
                decorate = value
            elif key == '管理費':
                management_fee = value[:-1]
            elif key == '帶租約':
                rent = value
            elif key == '法定用途':
                use = value
            elif key == '車位':
                car = value
            elif key == '主建物':
                main_size = value[:-1]
            elif key == '共用部分':
                share_size = value[:-1]
            elif key == '附屬建物':
                sub_size = value[:-1]
            elif key == '土地坪數':
                land_size = value[:-1]
        car_size = ''
        if '車位' in size and main_size and share_size:
            size_with_out_car = float(main_size) + float(share_size) + \
                                float(sub_size)
            total_size = float(size[:size.find('坪')])
            car_size = str(total_size - size_with_out_car)
        url = soup.find('meta', {'property': 'og:url'}).get('content')

        result = [
            community,
            age,
            height,
            car,
            size,
            main_size,
            sub_size,
            share_size,
            car_size,
            land_size,
            floor_info,
            face,
            info_price_num,
            single_price,
            decorate,
            host_detail,
            host_name,
            management_fee,
            rent,
            use,
            now,
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
            '權狀坪數',
            '主建物',
            '附屬建物',
            '共用部分',
            '車位坪數',
            '土地坪數',
            '格局',
            '朝向',
            '出價',
            '單價',
            '裝潢程度',
            '經紀業',
            '仲介',
            '管理費',
            '法定用途',
            '帶租約',
            '現況',
            '型態',
            '地址',
            '連結'
        ]
        print('\t'.join(titles))
        print('-' * (len(titles) * 2 * 4))
