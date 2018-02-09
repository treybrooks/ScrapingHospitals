# -*- coding: utf-8 -*-
import random
import requests
import re
import scrapy
# from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from hospital_finder.items import HCAFinderItem

def extract_title(soupy_html_address):
    title = soupy_html_address.find(class_='location-title')
    link = title.find('a')

    name = link.text
    url = link.get('href')

    return {
        'facility': name,
        'url': url
    }

def extract_address(soupy_html_address):
    street_address = soupy_html_address.find('span', attrs={'itemprop': 'streetAddress'}).text
    city = soupy_html_address.find('span', attrs={'itemprop': 'addressLocality'}).text

    regions = soupy_html_address.find_all('span', attrs={'itemprop': 'addressRegion'})
    for item in regions:
        if item.text.isdigit():
            zip_code = item.text
        else:
            state_code = item.text

    phone_pattern = re.compile('(\d{3})\D*(\d{3})\D*(\d{4})')
    phone_field = soupy_html_address.find('span', attrs={'itemprop': 'telephone'}).text

    matches = re.search(phone_pattern, phone_field)
    phone_number = ''.join(matches.groups())

    return {
        'address': street_address,
        'city': city,
        'state_code': state_code,
        'zip_code': zip_code,
        'phone': phone_number
    }

def process_facility(facility):
    soup = BeautifulSoup(facility.get_attribute('innerHTML'), 'lxml')
    data = dict()
    data.update(extract_address(soup))
    data.update(extract_title(soup))
    return data

def get_state_urls(locations_page):
    request = requests.get(locations_page)
    soup = BeautifulSoup(request.text, 'html5lib')

    regex = re.compile('\?state=\w{2}')
    links = []
    for link in soup.find_all('a', attrs={'href': regex}):
        links.append(urljoin('https://hcahealthcare.com/', link['href']))
    return links

class HcaSpiderSpider(scrapy.Spider):
    name = 'hca_spider'
    allowed_domains = ['https://hcahealthcare.com/']
    start_urls = get_state_urls('https://hcahealthcare.com/locations/browse.dot')
    # start_urls = [ # use this if you start messing with your parser
    #     'https://hcahealthcare.com/locations/?state=ID'
    # ]

    def __init__(self):
        window_resolutions = [
            (1024, 768),
            (1280, 800),
            (1366, 768),
            (1440, 900)
        ]

        self.driver = webdriver.PhantomJS('../node_modules/phantomjs-prebuilt/lib/phantom/bin/phantomjs')
        self.driver.set_window_size(*random.choice(window_resolutions))

    def parse(self, response):
        """ This function parses a sample Author response. Some contracts are mingled
        with this docstring.

        @url https://hcahealthcare.com/locations/?state=ID
        @returns items 2
        @returns requests 0
        @scrapes facility address city state_code zip_code phone url
        """
        self.driver.get(response.url)
        delay = 3 # seconds
        try:
            myElem = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="location1"]')))
            self.logger.debug( "Page is ready!")
        except TimeoutException:
            self.logger.debug( "Loading took too much time!")

        facility_data = []
        facilities = self.driver.find_elements(By.XPATH, './/div[@id="locations-map-view"]//div[contains(@data-id, "location")]')

        for location in facilities:
            item = HCAFinderItem()
            data = process_facility(location)
            for k, v in data.items():
                item[k] = v
            facility_data.append(item)

        return facility_data
