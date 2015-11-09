import sqlite3
from collections import namedtuple
import json

# initialize database
db = sqlite3.connect("stock.db")
c = db.cursor()
from rules import build_rule_tree, NULL_BRANCH

def getQuotesForStock(code):
	sqlfmt = "select * from Quote where code=? order by date"
	records = c.execute(sqlfmt, (code,))
	if not records:
		return None
	
	quotes = []
	Row = namedtuple("Row", ["id", "code", "date", "open","close", "high", "low", "volume"])
	up_run_len = 0
	down_run_len = 0
	for record in records:
		row = Row(*record)
		
		diff = (row.close-row.open)*100.0/row.open
		# print diff
		if diff < -3:
			diff =-5
		elif diff > 3:
			diff = 5
		else:
			diff =0

		high = (row.high-row.open)*100.0/row.open
		# print "high:%f"%high
		if high >9:
			high = 9
		elif high>5:
			high =5
		else:
			high =0

		vibe = (row.high-row.low)*100.0/row.open
		# print "vibe:%f"%vibe
		if vibe >10:
			vibe = 18
		elif vibe >6:
			vibe = 10
		else:
			vibe = 0

		d = (row.close-row.open)*100.0/row.open
		if d > 9:
			result = "up9"
		elif d >1:
			result = "up3"
		elif d<-9:
			result = "down9"
		elif d <-1:
			result = "down3"
		else:
			result = "stable"

		quote = {
			"diff": diff,
			"high": high,
			"vibe": vibe,
			"goUpNDays": up_run_len if up_run_len<5 else 4,
			"goDownNDdays": down_run_len if down_run_len<5 else 4,
			"T1Diff": quotes[-1]['diff'] if len(quotes)>0 else 0,
			"T2Diff": quotes[-2]['diff'] if len(quotes)>1 else 0,
			"T3Diff": quotes[-3]['diff'] if len(quotes)>2 else 0,
			"T1High": quotes[-1]['high'] if len(quotes)>0 else 0,
			"T2High": quotes[-2]['high'] if len(quotes)>1 else 0,
			"T3High": quotes[-3]['high'] if len(quotes)>2 else 0,
			"T1Vibe": quotes[-1]['vibe'] if len(quotes)>0 else 0,
			"T2Vibe": quotes[-2]['vibe'] if len(quotes)>1 else 0,
			"T3Vibe": quotes[-3]['vibe'] if len(quotes)>2 else 0,
			"result": result
		}
		if diff>0:
			down_run_len=0
			up_run_len+=1
		else:
			up_run_len=0
			down_run_len+=1
		quotes.append(quote)
	return quotes

def train():
	rulelist, tree = build_rule_tree()
	codes_query = "select exchange, code from Code where id>=1191"
	rows = c.execute(codes_query)
	codes = [row[1]+"."+row[0] for row in rows]

	for code in codes:
		quotes = getQuotesForStock(code)
		for quote in quotes:
			traverse(quote, tree)

	f = open("rules.txt", 'w')
	for rule in rulelist:	
			if is_valid_rule(rule):
				print rule
				rulestr = json.dumps(rule)
				f.write(rulestr)
				f.write("\n")


MIN_SUPPORT = 200
MIN_CONFIDENCE = 0.7
def is_valid_rule(rule):
	if rule['count']<MIN_SUPPORT:
		return False

	for c in ("up3", "up9", "stable", "down3", "down9"):
		if rule['stats'][c]*1.0/rule['count']>MIN_CONFIDENCE:
			return True
	return False


def traverse(quote, node):
	if not node:
		return
	if node.name=="LEAF":
		node.rule['count']+=1
		node.rule['stats'][quote['result']]+=1
		return
	else:
		val = quote[node.name]
		traverse(quote, node.getBranch(val))
		traverse(quote, node.getBranch(NULL_BRANCH))


if __name__=="__main__":
	train()