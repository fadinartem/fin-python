import time
import re
import os

import openpyxl
import splinter
from splinter import Browser
import requests

class WrongDatesError(Exception):
	def __init__(self):
		print ('These dates cannot be processed. Enter a range or a single date')
		print ('To enter multiple periods/dates, separate them with a "+"')

class Auxiliary():
	def std_periods_append(self, destination, dates):
		if len(dates) is 6:
			if len(dates[2]) is 2 and int(dates[2]) < 50:
			#converting year 14 to 2014
				dates[2] = '20%s' % dates[2]
			elif len(dates[2]) is 2 and int(dates[2]) > 50:
				dates[2] = '19%s' % dates[2]
			if len(dates[5]) is 2 and int(dates[5]) < 50:
				dates[5] = '20%s' % dates[5]
			elif len(dates[5]) is 2 and int(dates[5]) > 50:
				dates[5] = '19%s' % dates[5]
			destination.append(dates[:])
		elif len(dates) is 3:
			if len(dates[2]) is 2 and int(dates[2]) < 50:
				dates[2] = '20%s' % dates[2]
			elif len(dates[2]) is 2 and int(dates[2]) > 50:
				dates[2] = '19%s' % dates[2]	
			dates[3:6] = dates[0:3]
			destination.append(dates[:])
		else:
			raise WrongDatesError
		return destination
	
	def parse_comma_separated_line(self, line):
		result = []
		chunk = ''
		while line:
			for char in line:
				if char is not ',':
					chunk += char
				elif char is ',':
					result.append(chunk)
					chunk = ''
				line = line[1:]
			else:
				if chunk:
					result.append(chunk[:-1]) #stripping \n
		return result

	def date_parse (self, raw_dates):
		"""Parsing text date input into a list of lists with 6 date parameters"""
		per = []
		result = []
		while raw_dates:
			if re.match('[0-9]+',raw_dates):
				piece = re.match('[0-9]+',raw_dates).group(0)
				raw_dates = raw_dates [len(piece):]
				per.append (piece)
			elif re.match('[+&,;]|and',raw_dates):
				result = self.std_periods_append(result, per)
				per.clear()
				raw_dates = raw_dates [1:]
			else: 
				raw_dates = raw_dates [1:]
		if len(per) > 0: 
			result = self.std_periods_append(result, per)
		else: 
			pass
		return result
	
	def parse_tickers(self, raw_tickers):
		"""Parsing text date input into a list of tickers"""
		result = []
		while raw_tickers:
			if re.match('[A-Z]+',raw_tickers):
				piece = re.match('[A-Z]+',raw_tickers).group(0)
				raw_tickers = raw_tickers [len(piece):]
				result.append (piece)
			else: 
				raw_tickers = raw_tickers [1:]
		return result
	
	def european_dates_to_american(self, ed):
		"""Take a list of 6 dates european and return the same format list American"""
		return [ed[1],ed[0],ed[2],ed[4],ed[3],ed[5]]



class Retreiver():
	def __init__(self, folder):
		self.aux = Auxiliary()
		self.folder = folder
		self.tickers = None
		
	def click(self, destination):
		try:
			self.browser.find_by_text(destination).first.click()
		except splinter.exceptions.ElementDoesNotExist:
			self.browser.click_link_by_text(destination)
		
	def retreive(self):
		print ('Please enter the period for retrieval.')
		raw_dates = input ('Dates in European format: dd/mm/yyyy\n>')
		eurodates = self.aux.date_parse(raw_dates)[0]
		dates = self.aux.european_dates_to_american(eurodates)
		raw_tickers = input ('Tickers:\n>')
		self.tickers = self.aux.parse_tickers(raw_tickers)

		self.browser = Browser('chrome')
		for ticker in self.tickers:
			self.browser.visit('https://beta.finance.yahoo.com/quote/%s/history' % ticker)
			time.sleep(5)
			input_boxes = self.browser.find_by_tag('input')
			for i in range(0,6):
				input_boxes[i+2].fill(dates[i]) #we need 3-8 inputs
			self.click('Apply')
			download_link = self.browser.find_link_by_text('Download data').first
			response = requests.get(download_link['href'])
			with open('%s//%s.csv' % (self.folder, ticker), 'wb') as f:
				f.write(response.content)		
		self.browser.quit()
		
	def put_together(self):
		if not self.tickers:
			self.tickers = []
			for f in os.listdir(self.folder):
				self.tickers.append(f[:-4])
		target = openpyxl.Workbook()
		sheet = target.active
		sheet.append(self.tickers)
		for filename in os.listdir(self.folder):
			source = open('%s//%s' %(self.folder, filename), 'r', encoding='utf-8')
			sheet = target.create_sheet()
			sheet.title = filename[:-4] #strip out the extension
			for line in source:
				sheet.append(self.aux.parse_comma_separated_line(line))
			source.close()
		target.save('Historical_data_together.xlsx')
	
if __name__ == '__main__':
	r = Retreiver(folder='Individual quotes')
	answer = input ('Retreive tickers? Y/N\n>')
	if answer is 'Y':
		r.retreive()
	answer = input ('Consolidate? Y/N\n>')
	if answer is 'Y':
		r.put_together()
