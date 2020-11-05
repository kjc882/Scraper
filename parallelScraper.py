#Web Scraper for scraping individual Google Scholar Profiles
#Running Scrapers in Parallel for faster Crawling
#Created by 
#Kieran Chang, CS Undergraduate 2019
#University of Missouri

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

import scrapy
from scrapy.crawler import CrawlerProcess

import time
import sys
import csv
import threading

global chrome_options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

global url
url = ''
url = input("Please Enter the Scholar URL")

while not url:
	url = input("Please Enter the Scholar URL\n")

global fheader
fheader = ['title', 'author', 'date', 'journal', 'volume', 'issue', 'pages', 'publisher', 'abstract']

global scraperNum
scraperNum = 0

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = '../chromedriver')
driver.get(url)

# j = 0
# while(j == 0):
# 	try:
# 		driver.find_element(By.XPATH, '//*[@id="gsc_bpf_more"]').click()
# 		time.sleep(.3)
# 	except:
# 		break 

# 	print("still looping")

# 	j += 1

totalPapersStr = driver.find_element(By.XPATH, '//*[@id="gsc_a_nn"]').text
totalPapers = int(totalPapersStr[11:len(totalPapersStr)])
divided = int(totalPapers / 4)
leftovers = totalPapers % 4
print(totalPapers, divided, leftovers, "\n\n\n\n")
driver.close()

class ScholarSpider(scrapy.Spider):

	name = "scholar_spider"
	allowed_domains = ['scholar.google.com']
	start_urls = [url]

	def __init__(self, spiNum): 
		self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = '../chromedriver')
		self.all_items = []
		with open('scraper.csv', 'w') as writeFile:
			self.writer = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			self.writer.writerow(fheader)
		self.driver.get(url)
		j = 0
		while(j < 5):
			try:
				self.driver.find_element(By.XPATH, '//*[@id="gsc_bpf_more"]').click()
				time.sleep(.3)
			except:
				break 

			print("still looping")

			j += 1
		self.parse(spiNum)

	def process_elements(self):
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
			# print("im in process_elements about to try title")
			title = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_title"]').text

		except Exception as e:
			print(e)

		try:
			abstract_holder = self.driver.find_element_by_xpath('//*[@id="gsc_vcd_descr"]/div/div').text
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
				# print(e)
				break

		# print("process_elements if statement")
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
		# print("\n")
		# for x in range(len(single_item_info)):
		# 	print(single_item_info[x]),
		# print("\nwriting item to csv File and adding item to all_items list")
		with open('scraper.csv', 'a', encoding = 'utf-8') as writeFile:
			self.writer = csv.writer(writeFile, delimiter=',')
			self.writer.writerow(single_item_info)
		self.all_items.append(single_item_info)
		single_item_info.clear()
		return 1

	def parse(self, spiNum):

		i = spiNum * divided + 1

		while(i != ((spiNum + 1) * divided) + 1 and i <= totalPapers):
			print(i)
			try:
				selector = '//*[@id="gsc_a_b"]/tr[' + str(i) + ']/td[1]/a'
				wait = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, selector)))
				time.sleep(.3)
				# print("clicking on article")
				self.driver.find_element_by_xpath(selector).click()
				# print("waiting for pop-up to load")
				wait = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[@id="gsc_vcd_title"]')))
				# print("jumping to scrape")
				self.process_elements()
				self.driver.execute_script("window.history.go(-1)")
				# print("scraping section loop")
				i += 1

			except Exception as e: 
				print(e)
				break

t1 = threading.Thread(target = ScholarSpider(0))
t2 = threading.Thread(target = ScholarSpider(1))
t3 = threading.Thread(target = ScholarSpider(2))
t4 = threading.Thread(target = ScholarSpider(3))

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()