import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_page_source(url, load_by_scroll=False, wait_photo=False,
                    minimize=False):
    options = Options()
    if not minimize:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    if minimize:
        driver.minimize_window()
    driver.get(url)
    if load_by_scroll:
        scroll_to_bottom(driver)
    if wait_photo:
        wait_photo_loading(driver)
    page_source = driver.page_source
    driver.quit()
    return page_source


def scroll_to_bottom(driver):
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, 0);")  # trigger web to load
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if soup.find('div', {'class': 'loadend'}):
            return


def wait_photo_loading(driver):
    for _ in range(5):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")  # trigger web to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        photo_album_cover = soup.find('img', {'class': 'photo-album-cover'})
        building_map_photo_url = soup.find('img',
                                           {'class': 'building-map-photo'})
        if photo_album_cover and building_map_photo_url:
            break
