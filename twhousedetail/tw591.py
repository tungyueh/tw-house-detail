import json

from bs4 import BeautifulSoup

from twhousedetail.community import Community
from twhousedetail.web import get_page_source


class Tw591(Community):
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
        print('\t'.join(titles))


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
