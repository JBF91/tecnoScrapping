# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import pdb
import re
from user_agent import generate_user_agent
import pandas as pd
import time
from collections import namedtuple
from random import randint

JobOffer = namedtuple('Oferta', 'name id link puesto contrato jornada localizacion date company min_salario max_salario')

class TecnoScrape():
	regex = re.compile(r'[\n\r\t]')

	def __init__(self):
		self.url_base = 'https://www.tecnoempleo.com'
		self.url_subdomain = '/busqueda-empleo.php?cp=,29,&pagina=%s'
		#self.df = pd.DataFrame(columns=JobOffer._fields)
		self.df = None
		self.data = []

	def scrape_page(self, page_number=1):
		headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
		print headers
		page = requests.get('%s%s%s'%(self.url_base, self.url_subdomain, page_number), timeout=5, headers=headers)
		soup = BeautifulSoup(page.content, 'html.parser')
		self.scrape_list(soup)

	def scrape_list(self, page=None):
		sections = page.find_all('article', {'class': 'g-bg-gray-light-v4--hover'}, onclick=True)
		for content in sections:
			self.scrape_section(section=content)

	def scrape_section(self, section):
		_link = section.find('a')
		_url = _link['href'].strip()
		_id = _link['href'].split('/')[-1].strip()
		_name = _link.get_text().strip()
		_salario = self.clean_icon_tags('fa-wallet', section)
		_puesto = self.clean_icon_tags('fa-user', section)
		_contrato = self.clean_icon_tags('fa-clipboard', section)
		_jornada = self.clean_icon_tags('fa-clock', section)
		_localizacion = self.clean_subtitle_tags('fa-map-marker-alt', section)
		_date = self.clean_subtitle_date('fa-calendar-alt', section)
		_company = self.clean_company_name(section)
		_min_salario = self.clean_salario(salario=_salario)[0]
		_max_salario = self.clean_salario(salario=_salario)[1]

		self.data.append(JobOffer(name=_name, id=_id, link=_url, puesto=_puesto, 
		jornada=_jornada, contrato=_contrato, localizacion=_localizacion, date=_date,
		 company=_company, min_salario = _min_salario, max_salario=_max_salario))

	def clean_salario(self, salario=False):
		if not salario:
			return ['','']
		else:
			try:
				min = salario.split('-')[0].split()[0]
				max = salario.split('-')[1].split()[0]
				return [min, max]
			except:
				return ['','']

	def clean_company_name(self, section):
		company_tag = section.select('h4 > a')
		if company_tag:
			try:
				company_tag = company_tag[0].text.strip()
				company_tag = company_tag.replace('|', '').strip()
				company_tag = self.regex.sub(" ", company_tag)
				return company_tag
			except:
				return ''
		else:
			return ''

	def clean_subtitle_date(self, tag, section):
		subtitle_tag = section.findAll('i', {'class': tag})
		if subtitle_tag:
			try:
				subtitle_tag = subtitle_tag[0].find_next_sibling('b').text
				subtitle_tag = subtitle_tag.replace('|', '').strip()
				subtitle_tag = self.regex.sub(" ", subtitle_tag)
				return subtitle_tag
			except:
				return ''
		else:
			return ''

	def clean_subtitle_tags(self, tag, section):
		subtitle_tag = section.findAll('i', {'class': tag})
		if subtitle_tag:
			try:
				subtitle_tag = subtitle_tag[0].find_next_sibling('a').text
				subtitle_tag = subtitle_tag.replace('|', '').strip()
				subtitle_tag = self.regex.sub(" ", subtitle_tag)
				return subtitle_tag
			except:
				return ''
		else:
			return ''

	
	def clean_icon_tags(self, tag, section):
		icon_tag = section.findAll('i', {'class': tag})
		if icon_tag:
			try:
				icon_tag = icon_tag[0].nextSibling.strip()
				icon_tag = icon_tag.replace('|', '').strip()
				icon_tag = self.regex.sub(" ", icon_tag)
				return icon_tag
			except:
				return ''
		else:
			return ''

	def do_scraping(self, max_sleep_time=10, min_sleep_time=5, max_pages=5, first_page=1):
		print 'Iniciando Scrapping: \n'
		print 'MaxSleep: %s | MinSleep: %s |First Page: %s | Max Pages: %s \n' %(max_sleep_time, min_sleep_time, first_page, max_pages)

		for i in range(first_page, (first_page + max_pages)) :
			print 'Scrapping Página: %s' %i
			self.scrape_page(page_number=i)
			sleep_time = randint(min_sleep_time, max_sleep_time)
			print 'Sleeping... %s' %sleep_time
			time.sleep(sleep_time)


		self.df = pd.DataFrame.from_records(self.data, columns=JobOffer._fields)

		return self.df
		