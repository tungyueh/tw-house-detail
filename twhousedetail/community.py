import os

from bs4 import BeautifulSoup

from twhousedetail.web import get_page_source


class Community:
    def __init__(self, region):
        self._region = region
        if not os.path.exists(self._folder_path()):
            os.mkdir(self._folder_path())

    @staticmethod
    def prefix():
        raise NotImplementedError()

    def _folder_path(self):
        return f'{self.prefix()}{self._region}'

    def _result_path(self):
        return f'{self.prefix()}{self._region}.txt'

    def _html_path(self, name):
        return f'{self.prefix()}{self._region}/{name}.html'

    def _md_path(self):
        return f'{self.prefix()}{self._region}.md'

    def list(self, url, overwrite=False):
        html_doc = self._get_list_html_doc(url)
        soup = BeautifulSoup(html_doc, 'html.parser')
        count = 0
        for name, community_url in self._list_name_and_url(soup):
            name = name.replace('/', '-')
            count += 1
            if not overwrite and os.path.exists(self._html_path(name)):
                print(f'Skip {self._html_path(name)} due to already exist')
                continue
            self.save(community_url, name)
        print(f'Total: {count}')

    @staticmethod
    def _get_list_html_doc(url):
        raise NotImplementedError()

    @staticmethod
    def _list_name_and_url(soup: BeautifulSoup):
        raise NotImplementedError()

    def save(self, url, name=None):
        html_doc = self._get_html_doc(url)
        name = name if name else self._get_name(html_doc)
        print(f'Save {url} to {self._html_path(name)} ...')
        with open(self._html_path(name), 'w') as fp:
            fp.write(html_doc)
        print(f'Saved {self._html_path(name)}')

    @staticmethod
    def _get_html_doc(url):
        raise NotImplementedError()

    @staticmethod
    def _get_name(html_doc):
        raise NotImplementedError()

    def show_all(self):
        self._show_titles()
        result = self.get_all()
        with open(self._result_path(), 'w') as result_fp:
            result_fp.write('\n'.join(result))
        print('\n'.join(result))
        total = len(os.listdir(self._folder_path()))
        skip = total - len(result)
        print(f'Total: {total}, Skip: {skip}')
        print(f'Saved to {self._result_path()}')

    def get_all(self):
        result = []
        for file in os.listdir(self._folder_path()):
            name, _ = os.path.splitext(file)
            with open(self._html_path(name), 'r') as fp:
                html_doc = fp.read()
            community_info = self.get_info(html_doc)
            if community_info:
                result.append(community_info)
        return result

    @staticmethod
    def get_info(html_doc):
        raise NotImplementedError()

    def map(self):
        with open(self._md_path(), 'w') as md_fp:
            md_fp.write(f'# {self._region}\n')
            total = 0
            for file in os.listdir(self._folder_path()):
                name, _ = os.path.splitext(file)
                with open(self._html_path(name), 'r') as fp:
                    html_doc = fp.read()
                md_fp.write(self._get_map(html_doc) + '\n')
                total += 1
        print(f'Total: {total}')
        print(f'Saved to {self._md_path()}')

    @staticmethod
    def _get_map(html_doc):
        raise NotImplementedError()

    @classmethod
    def show_one(cls, url):
        cls._show_titles()
        html_doc = get_page_source(url)
        result = cls.get_info(html_doc)
        print(result)

    @staticmethod
    def _show_titles():
        raise NotImplementedError()
