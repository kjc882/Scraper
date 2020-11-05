#Web Scraper for scraping individual Google Scholar Profiles
#Created by 
#Kieran Chang, CS Undergraduate 2019
#University of Missouri

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from pathlib import Path

import scrapy
import time
import sys
import csv
import os

if len(sys.argv) < 3:
    print("Proper Usage: python scraper.py [scholar link] [userID]")

global chrome_options
chrome_options = Options()
chrome_options.add_argument('headless')

global url
url = ''
url = str(sys.argv[1])

global id
id = ''
id = str(sys.argv[2])

global fheader
fheader = ['link', 'title', 'author', 'date', 'journal', 'volume', 'issue', 'pages', 'publisher', 'abstract']

class ScholarSpider(scrapy.Spider):

	name = "scholar_spider"
	allowed_domains = ['scholar.google.com']
	start_urls = [url]

	def __init__(self): 
		self.driver = webdriver.Chrome(options=chrome_options, executable_path = '../chromedriver')
		self.all_items = []
		fileName = 'scraper' + id + '.csv'
		my_file = Path(fileName)
		if not my_file.exists():
			with open('scraper' + id + '.csv', 'w') as writeFile:
				self.writer = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				self.writer.writerow(fheader)
			self.parse()
		self.checkDupes()

	def process_elements(self):
		link = 'NULL'
		title = 'NULL'
		author = 'NULL'
		date = 'NULL'
		journal = 'NULL'
		volume = 'NULL'
		issue = 'NULL'
		pages = 'NULL'
		publisher = 'NULL'
		abstract = 'NULL'
		abstract_holder = ''
		selector = ''
		holder_name = ''

		try:
			print("getting link")
			link = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_title"]/a').get_attribute("href")

		except Exception as e:
			print(e)
			print("failed to get link")

		try:
			print("im in process_elements about to try title")
			title = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_title"]').text

		except Exception as e:
			print(e)

		try:
			abstract_holder = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_descr"]').text
			abstract = abstract_holder.strip("\xe2\x80\xa6")

		except Exception as e:
			print(e)

		i = 0

		while(1):
			i += 1
			try:
				selector = '//*[@id="gsc_vcd_table"]/div[' + str(i) + ']/div[1]'
				holder_name = self.driver.find_element_by_xpath(selector).text
				selector = '//*[@id="gsc_vcd_table"]/div[' + str(i) + ']/div[2]'
				if holder_name == "Authors":
					author = self.driver.find_element_by_xpath(selector).text
				if holder_name == "Publication date":
					date = self.driver.find_element_by_xpath(selector).text
				if holder_name == "Journal":
					journal = self.driver.find_element_by_xpath(selector).text
				if holder_name == "Volume":
					volume = self.driver.find_element_by_xpath(selector).text
				if holder_name == "Issue":
					issue = self.driver.find_element_by_xpath(selector).text
				if holder_name == "Pages":
					pages = self.driver.find_element_by_xpath(selector).text
				if holder_name == "Publisher":
					publisher = self.driver.find_element_by_xpath(selector).text
			except Exception as e:
				print(e)
				break

		print("process_elements if statement")
		single_item_info = []
		single_item_info.extend((
			link,
			title,
			author,
			date,
			journal,
			volume,
			issue,
			pages,
			publisher,
			abstract
		))
		print("\n")
		print("\nwriting item to csv File and adding item to all_items list")
		with open('scraper' + str(id) + '.csv', 'a', encoding = 'utf-8') as writeFile:
			self.writer = csv.writer(writeFile, delimiter=',')
			self.writer.writerow(single_item_info)
		self.all_items.append(single_item_info)
		single_item_info.clear()
		return 1

	def parse(self):
		#directs selenium browser to scholar page
		self.driver.get(url)

		self.driver.set_page_load_timeout(10)
		self.driver.find_element(By.XPATH, '//*[@id="gsc_a_ha"]').click()
		time.sleep(3)
		j = 0

		while(j < 10):
			try:
				self.driver.find_element(By.XPATH, '//*[@id="gsc_bpf_more"]').click()
				time.sleep(.3)
			except:
				break 

			print("still looping")

			j += 1

		i = 1
		j = 0

		while(1):
			print(i)
			try:
				selector = '//*[@id="gsc_a_b"]/tr[' + str(i) + ']/td[1]/a'
				wait = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, selector)))
				time.sleep(.3)
				print("clicking on article")
				self.driver.find_element_by_xpath(selector).click()
				print("waiting for pop-up to load")
				wait = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[@id="gsc_vcd_title"]')))
				print("jumping to scrape")
				self.process_elements()
				self.driver.execute_script("window.history.go(-1)")
				print("scraping section loop")
				i+=1

				if(i%100 == 0):
					self.driver.close()
					print("opening new driver")
					self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = '../chromedriver')
					self.driver.get(url)
					while(j < 10):
						try:
							self.driver.find_element(By.XPATH, '//*[@id="gsc_bpf_more"]').click()
							time.sleep(.3)
						except:
							break 

						print("still looping")

						j += 1

				j = 0

			except Exception as e: 
				print(e)
				break

	def checkDupes(self):
		self.driver.get(url)

		self.driver.set_page_load_timeout(10)
		self.driver.find_element(By.XPATH, '//*[@id="gsc_a_ha"]').click()
		time.sleep(3)

		i = 0

		with open('scraper' + id + '.csv', 'r') as readFile:
			self.reader = csv.reader(readFile, delimiter = ',')
			next(self.reader)

			for row in self.reader:
				if i == 1:
					break
				else:
					i += 1

			name = row[0]
			print(name)

		j = 0

		while(j < 10):
			try:
				self.driver.find_element(By.XPATH, '//*[@id="gsc_bpf_more"]').click()
				time.sleep(.3)
			except:
				break 

			print("still looping")

			j += 1

		i = 1
		j = 0
		k = 1

		while(k > 0):
			print(i)
			try:
				selector = '//*[@id="gsc_a_b"]/tr[' + str(i) + ']/td[1]/a'
				wait = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, selector)))
				time.sleep(.3)
				print("clicking on article")
				self.driver.find_element_by_xpath(selector).click()
				print("waiting for pop-up to load")
				wait = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[@id="gsc_vcd_title"]')))
				print("jumping to scrape")
				
				title = 'NULL'
				author = 'NULL'
				date = 'NULL'
				journal = 'NULL'
				volume = 'NULL'
				issue = 'NULL'
				pages = 'NULL'
				publisher = 'NULL'
				abstract = 'NULL'
				abstract_holder = ''
				selector = ''
				holder_name = ''

				try:
					print("im in process_elements about to try title")
					title = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_title"]').text

				except Exception as e:
					print(e)

				try:
					abstract_holder = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_descr"]/div/div').text
					abstract = abstract_holder.strip("\xe2\x80\xa6")

				except Exception as e:
					print(e)

				l = 0

				while(1):
					l += 1
					try:
						selector = '//*[@id="gsc_vcd_table"]/div[' + str(l) + ']/div[1]'
						holder_name = self.driver.find_element_by_xpath(selector).text
						selector = '//*[@id="gsc_vcd_table"]/div[' + str(l) + ']/div[2]'
						if holder_name == "Authors":
							author = self.driver.find_element_by_xpath(selector).text
						if holder_name == "Publication date":
							date = self.driver.find_element_by_xpath(selector).text
						if holder_name == "Journal":
							journal = self.driver.find_element_by_xpath(selector).text
						if holder_name == "Volume":
							volume = self.driver.find_element_by_xpath(selector).text
						if holder_name == "Issue":
							issue = self.driver.find_element_by_xpath(selector).text
						if holder_name == "Pages":
							pages = self.driver.find_element_by_xpath(selector).text
						if holder_name == "Publisher":
							publisher = self.driver.find_element_by_xpath(selector).text
					except Exception as e:
						print(e)
						break

				print("process_elements if statement")
				single_item_info = []
				single_item_info.extend((
					title,
					author,
					date,
					journal,
					volume,
					issue,
					pages,
					publisher,
					abstract
				))

				fileName = 'temp_scraper' + id + '.csv'
				my_file = Path(fileName);

				if name in title:
					k = 0
					print("duplicate found, exiting")
					break

				elif not my_file.exists():
					with open('temp_scraper' + str(id) + '.csv', 'w', encoding = 'utf-8') as writeFile:
						self.writer = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
						self.writer.writerow(fheader)
					with open('temp_scraper' + str(id) + '.csv', 'a', encoding = 'utf-8') as writeFile:
						self.writer = csv.writer(writeFile, delimiter=',')
						self.writer.writerow(single_item_info)

				else:
					with open('temp_scraper' + str(id) + '.csv', 'a', encoding = 'utf-8') as writeFile:
						self.writer = csv.writer(writeFile, delimiter=',')
						self.writer.writerow(single_item_info)

				self.driver.execute_script("window.history.go(-1)")
				print("scraping section loop")
				i+=1

				if(i%100 == 0):
					self.driver.close()
					print("opening new driver")
					self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = '../chromedriver')
					self.driver.get(url)
					while(j < 10):
						try:
							self.driver.find_element(By.XPATH, '//*[@id="gsc_bpf_more"]').click()
							time.sleep(.3)
						except:
							break 

						print("still looping")

						j += 1

				j = 0

			except Exception as e: 
				print(e)
				break

		fileName = 'temp_scraper' + id + '.csv'
		my_file = Path(fileName);

		if my_file.exists():
			with open('temp_scraper' + id + '.csv', 'a') as writeFile:
				with open('scraper' + id + '.csv', 'r') as readFile:
					self.reader = csv.reader(readFile, delimiter = ',')
					next(readFile)
					self.writer = csv.writer(writeFile, lineterminator = '\n')
					for row in readFile:
						writeFile.write(row)
			os.remove('scraper' + id + '.csv')
			os.rename('temp_scraper' + id + '.csv', 'scraper' + id + '.csv')

ScholarSpider()