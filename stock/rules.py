from itertools import combinations, combinations_with_replacement
from copy import copy

trend_indicators = {
	"names": ("goUpNDays", "goDownNDdays"),
	"values": (0,1,2,3,4)
}
diff_indicators = {
	"names": ("T1Diff", "T2Diff", "T3Diff"),
	"values": (-5,0,5)
}
high_indicators = {
	"names": ("T1High", "T2High", "T3High"),
	"values": (0, 5, 9)
}
vibe_indicators = {
	"names": ("T1Vibe", "T2Vibe", "T3Vibe"),
	"values": (0, 10, 18)
}
	
resultCandidates = ["down9", "down3", "stable","up3", "up9"]

RULE_LENGTH_LIMIT = 5

def getNextRule():
	for rule in pick_trend_rule():
		yield rule
	
def pick_trend_rule():
	# first, skip trend rules
	for rule in pick_tday_rule("diff", {}):
		yield rule
	for name in trend_indicators['names']:
		for val in trend_indicators["values"]:
			r = {name: val}
			for rule in pick_tday_rule("diff", r):
				yield rule

def pick_tday_rule(t, rule):
	if t=="diff":
		indicators = diff_indicators
		next = "high"
	elif t=="high":
		indicators = high_indicators
		next = "vibe"
	elif t=="vibe":
		indicators = vibe_indicators
		next = "finish"
	else: # finish
		next = None
		yield rule
	if t!="finish":
		for r in pick_tday_rule(next, rule):
			yield r
		rest = RULE_LENGTH_LIMIT - len(rule.keys())
		upper_bound = min(rest+1, 4)
		for i in range(1,upper_bound):
			for combo in get_all_combos(i, indicators['values'], []):
				r = copy(rule)
				for k,v in enumerate(combo):
					r[indicators['names'][k]]=v

				for rr in pick_tday_rule(next, r):
					yield rr

def get_all_combos(i, vals, current):
	if len(current) == i:
		yield current
	else:
		for v in vals:
			newlist = copy(current)
			newlist.append(v)
			for combo in get_all_combos(i, vals, newlist):
				yield combo

NULL_BRANCH = -65535
class TreeNode:
	def __init__(self, name, options=[]):
		self.name = name
		self.branches = {}
		for option in options:
			self.branches[option]=None
		self.branches[NULL_BRANCH]=None
	def setLevel(self, level):
		self.level = level
	def setRule(self, rule):
		self.rule = rule
	def getBranch(self, val):
		return self.branches[val]
	def setBranch(self, val, node):
		self.branches[val] = node

	def __str__(self):
		if self.level>2:
			return "\t"*self.level + "..."
		s = "\t"*self.level + "+"+self.name+"\n"
		for b in self.branches:
			s += "\t"*self.level + str(b)+"\n"
			if self.branches[b]:
				s += str(self.branches[b])
		s += "\n"
		return s

def getOptionsForLevel(level):
	if level in trend_indicators['names']:
		return trend_indicators['values']
	if level in diff_indicators['names']:
		return diff_indicators['values']
	if level in high_indicators['names']:
		return high_indicators['values']
	if level in vibe_indicators['names']:
		return vibe_indicators['values']

def build_rule_tree():
	levels = trend_indicators["names"]+diff_indicators["names"]+high_indicators["names"]+vibe_indicators["names"]
	print levels
	root = TreeNode("goUpNDays", trend_indicators['values'])
	root.setLevel(0)
	rulelist = []
	node_count = 0
	leaf_count = 0 
	rule_count = 0
	for r in getNextRule():
		rule_count += 1
		rule = {
			"conditions": r,
			"count": 0,
			"stats": {key:0 for key in resultCandidates}
		}
		rulelist.append(rule)
		# insert the rule into tree
		node = root
		for i,level in enumerate(levels):
			branch = NULL_BRANCH
			if level in r.keys():
				branch = r[level]
			newNode = node.getBranch(branch)
			if newNode:
				node = newNode
			else:
				if i==len(levels)-1:
					newNode = TreeNode("LEAF")
					newNode.setRule(rule)
					leaf_count +=1
				else:
					nextlevel = levels[i+1]
					newNode = TreeNode(nextlevel, getOptionsForLevel(nextlevel))
					node_count+=1
				newNode.setLevel(i+1)
				node.setBranch(branch, newNode)
				node = newNode
	# print "Nodes:%d, LEAFS: %d, RULES: %d"%(node_count, leaf_count, rule_count)
	return rulelist, root

def printRuleForPath(tree, path):
	node = tree
	for i,p in enumerate(path):
		print i
		node = node.getBranch(p)
	print node.rule


if __name__== "__main__":	
	# cnt = 0
	# for rule in getNextRule():
	# 	cnt += 1
	# 	print rule
	# print "RULES COUNT:%d"%cnt
	rulelist, tree = build_rule_tree()
	# printRuleForPath(tree, [0, NULL_BRANCH, -5, 0, NULL_BRANCH, 0, NULL_BRANCH, NULL_BRANCH, 18, NULL_BRANCH, NULL_BRANCH])
