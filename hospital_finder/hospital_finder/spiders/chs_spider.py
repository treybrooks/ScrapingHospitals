# -*- coding: utf-8 -*-
import random
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from hospital_finder.items import CHSFinderItem

class ChsSpiderSpider(scrapy.Spider):
    name = 'chs_spider'
    allowed_domains = ['http://www.chs.net/serving-communities/locations/']
    start_urls = ['http://www.chs.net/serving-communities/locations/']

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
        self.driver.get(response.url)
        delay = 3 # seconds
        try:
            myElem = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, './/div[@class="chs-imap-list-container"]')))
            self.logger.debug( "Page is ready!")
        except TimeoutException:
            self.logger.debug( "Loading took too much time!")

        facility_data = []
        facilities = self.driver.find_elements(By.XPATH, './/div[@class="chs-imap-list-item"]')

        for location in facilities:
            item = CHSFinderItem()

            city_state = location.find_element(By.XPATH, './/span[@class="chs-imap-list-item-contact"]').get_attribute('innerHTML')
            city, state = city_state.split(', ')
            item['city'] = city
            item['state'] = state

            fac_url = location.find_element(By.XPATH, './/a[@class="chs-imap-list-item-link"]')
            item['facility'] = fac_url.get_attribute('innerHTML')
            item['url'] = fac_url.get_attribute('href')

            facility_data.append(item)

        return facility_data
