import requests
import datetime
from cStringIO import StringIO
import csv
import sqlite3
import re
from collections import namedtuple
import time
import random

# initialize database
db = sqlite3.connect("stock.db")
c = db.cursor()

# This should only be called once to load codes from txt into sqlite
def loadCodesIntoDB():
	regex = re.compile("(.*)\(([0-9]{6})\)")

	hu = open("hushi.txt", 'r')
	huCnt = 0-9
	for row in hu.readlines():
		records = row.split()
		for record in records:
			mo = regex.match(record)
			if not mo:
				print "Cannot parse record "+record
				continue
			name, code = mo.group(1), mo.group(2)
			sqlfmt = "insert into Code (exchange, code, name) values ('ss', ?, ?)"
			c.execute(sqlfmt, (code, unicode(name, encoding='gbk')))
			huCnt += 1
		db.commit()
	print "Import %d Hushi stocks"%huCnt

	shen = open("shenshi.txt", 'r')
	shenCnt = 0
	for row in shen.readlines():
		records = row.split()
		for record in records:
			mo = regex.match(record)
			if not mo:
				print "Cannot parse record "+record
				continue
			name, code = mo.group(1), mo.group(2)
			sqlfmt = "insert into Code (exchange, code, name) values ('sz', ?, ?)"
			c.execute(sqlfmt, (code, unicode(name,encoding='gbk')))
			shenCnt += 1
		db.commit()
	print "Import %d ShenShi stocks"%shenCnt

invalid_codes = []
def fetchQuotesForDates(code, fromDate, toDate):
	urlfmt = "http://ichart.yahoo.com/table.csv?s=%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv"
	if fromDate>toDate:
		raise Exception(msg="Invalid Dates")
	fromYear, fromMonth, fromDay = fromDate.year, fromDate.month-1, fromDate.day
	toYear, toMonth, toDay = toDate.year, toDate.month-1, toDate.day
	url = urlfmt%(code, fromMonth, fromDay, fromYear, toMonth, toDay, toYear)
	response = requests.get(url)
	if response.status_code != 200:
		print "Returns status code %d"%response.status_code
		invalid_codes.append(code)
		return None
	f = StringIO(response.content)
	quotes_reader = csv.reader(f)

	if not next(quotes_reader, None): # skip the header
		print "Fail to fetch quotes data for %s"%code

	Row = namedtuple('Row', ['date', 'open', 'high', 'low', 'close', 'volumn','adjclose'])
	sqlfmt = "insert or replace into Quote (id, code, date, open, high, low, close, volumn) values \
			((select id from Quote where code=? and date=?), ?, ?, ?, ?, ?, ?, ?)"
	for row in quotes_reader:
		r = Row(*row)
		c.execute(sqlfmt, (code, r.date, code, r.date, r.open, r.high, r.low, r.close, r.volumn))
	db.commit()

# Refresh quotes data up to today
def refreshQuotesData():	
	codes_query = "select exchange, code from Code where id>=1179"
	rows = c.execute(codes_query)
	codes = [row[1]+"."+row[0] for row in rows]

	startDate = datetime.date(2015, 1, 1)
	endDate = datetime.date.today()

	for code in codes:
		print "<<<< Start Fetching %s <<<<"%code
		fetchQuotesForDates(code, startDate, endDate)
		print "<<<< End Fetching %s <<<<"%code
		seconds = random.randint(3,8)
		time.sleep(seconds)


if __name__=="__main__":
	requests.adapters.DEFAULT_RETRIES = 5
	refreshQuotesData()
