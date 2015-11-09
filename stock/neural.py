import pybrain
import sqlite3
from collections import namedtuple

db = sqlite3.connect("stock.db")
c = db.cursor()

quotes_data = []
def getQuotesForStock(code):
	sqlfmt = "select * from Quote where code=? order by date"
	records = c.execute(sqlfmt, (code,))
	if not records:
		return None
	
	quotes = []
	Row = namedtuple("Row", ["id", "code", "date", "open","close", "high", "low", "volume"])
	up_run_len = 0
	down_run_len = 0

	for i,record in enumerate(records): 
		row = Row(*record)
		rise = (row.close-quotes[-1]["close"])*1.0/row.close if quotes else 0.0
		dayrise = (row.close-row.open)*1.0/row.open
		vibe = (row.high-row.low)*1.0/row.open

		if len(quotes)>0:
			ema12_yesterday = quotes[-1]['ema12']
			ema26_yesterday = quotes[-1]['ema26']
			avg_yesterday = quotes[-1]['avg']
		else:
			ema12_yesterday = row.close
			ema26_yesterday = row.close
			avg_yesterday = 0.0

		ema12 = (2.0/13.0)*row.close + (11.0/13.0)*ema12_yesterday
		ema26 = (2.0/28.0)*row.close + (26.0/28.0)*ema26_yesterday
		macd = ema26 - ema12
		avg = (2.0/10.0)*macd+(8.0/10.0)*avg_yesterday
		diff = macd - avg

		if rise > 0.05:
			cat = 0
		elif rise >0:
			cat = 1
		elif rise>-0.05:
			cat = 2
		else:
			cat = 3

		quote = {
			"open": row.open,
			"close": row.close,
			"rise": rise,
			"dayrise": dayrise,
			"vibe": vibe,
			"macd": macd,
			"ema12": ema12,
			"ema26": ema26,
			"avg": avg,
			"diff": diff,
			"volume": row.volume,
			"cat": cat
		}
		quotes.append(quote)
	return quotes


train_data = []
train_results = []
test_data = []
test_results = []

def loadData():
	codes_query = "select exchange, code from Code"
	rows = c.execute(codes_query)
	codes = [row[1]+"."+row[0] for row in rows]

	for code in codes:
		quotes = getQuotesForStock(code)
		last_index = 85 if len(quotes)>85 else len(quotes)
		for i in range(3, last_index):
			last = quotes[i-1]
			last1 = quotes[i-2]
			last2 = quotes[i-3]
			train_data.append({
					"rise": last["rise"],
					"rise1": last1["rise"],
					"rise2": last2["rise"],
					"dayrise": last["dayrise"],
					"dayrise1": last1["dayrise"],
					"dayrise2": last2["dayrise"],
					"vibe": last["vibe"],
					"vibe1": last1["vibe"],
					"vibe2": last2["vibe"],
					"macd": last["macd"],
					"avg": last["avg"],
					"diff": last["diff"],
					"volume": last["volume"],
				})
			train_results.append(quotes[i]["cat"])
		if len(quotes)>85:
			for i in range(85, len(quotes)):
				last = quotes[i-1]
				last1 = quotes[i-2]
				last2 = quotes[i-3]
				test_data.append({
						"rise": last["rise"],
						"rise1": last1["rise"],
						"rise2": last2["rise"],
						"dayrise": last["dayrise"],
						"dayrise1": last1["dayrise"],
						"dayrise2": last2["dayrise"],
						"vibe": last["vibe"],
						"vibe1": last1["vibe"],
						"vibe2": last2["vibe"],
						"macd": last["macd"],
						"avg": last["avg"],
						"diff": last["diff"],
						"volume": last["volume"],
					})
				test_results.append(quotes[i]["cat"])

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet, ClassificationDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.tools.xml.networkreader import NetworkReader

net = None
def trainNet():
	global net
	print "Preparing dataset ..."
	ds = ClassificationDataSet(13, 1, nb_classes=4)
	for data in zip(train_data, train_results):
		ds.addSample(tuple(data[0].values()), [data[1]])
	ds._convertToOneOfMany()

	print "Training network ..."
	net = buildNetwork(ds.indim, 5, ds.outdim, outclass=SoftmaxLayer)
	trainer = BackpropTrainer(net, dataset=ds, momentum=0.1, verbose=True, weightdecay=0.01)
	
	for i in range(10):
		print "Training loop %d ..."%i
		trainer.trainEpochs(3)

	print "Saving network ..."
	NetworkWriter.writeToFile(net, 'network.xml')


def loadNet():
	global net
	net = NetworkReader.readFrom('network.xml') 

def testNet():
	correct = 0
	total = 0
	ts = ClassificationDataSet(13, 1, nb_classes=4)
	for data in zip(test_data, test_results):
		print data
		ts.addSample(tuple(data[0].values()), [data[1]])
	ts._convertToOneOfMany()

	for t in ts:
		ret = net.activate(t[0])
		print "ret: %s actual: %s"%(ret, t[1])

		largest = max(ret)
		ret = [1 if x==largest else 0 for x in ret]
		
		if all([ret[k]==t[1][k] for k in range(4)]):
			correct += 1
		total += 1
	print "%d of %d correct for trainer"%(correct, total)

if __name__ == "__main__":
	print "Loading data ..."
	loadData()
	# print "Start training..."
	# trainNet()
	print "Loading Network ..."
	loadNet()
	print "Testing Network ..."
	testNet()