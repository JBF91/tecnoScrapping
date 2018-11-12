# -*- coding: utf-8 -*-

import tecno_scrape
import os

dirname, filename = os.path.split(os.path.abspath(__file__))

scrape = tecno_scrape.TecnoScrape()
data = scrape.do_scraping(max_pages=20, first_page=1)
data.to_csv('%s/%s'%(dirname, 'dataset.csv'), sep=',' , encoding='utf-8')