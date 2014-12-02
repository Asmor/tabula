#!/usr/bin/python

import random
import re
import sys

diceRegex = "^(\d+)d(\d+)(?:([-x+*/])(\d+))?"
tableGroups = {}

class TableGroup(object):
	def __init__(self, name):
		self.name = name
		filename = "{0}.txt".format(name)
		self.tables = parseFile(filename)["tables"]
		for table in self.tables:
			self.tables[table].setTableGroup(self)
		tableGroups[self.name] = self

	def getTable(self, name):
		return self.tables[name.lower()]

	def rollOnTable(self, name):
		if name.lower() in self.tables:
			raw = str(self.getTable(name).getRandom())
			return re.sub(" +", " ", raw)
		else:
			return "[No table named '{0}' in {1}]".format(name, self.name)

class Table(object):
	def __init__(self, raw):
		self.name = ""
		self.entries = []
		self.appendText = ""
		self.imports = []
		for line in raw.split("\n"):
			if line == "":
				continue
			if line.startswith("#"):
				self.name = line[1:].strip()
			elif line.startswith("!"):
				self.setDirective(line[1:].strip())
			else:
				matches = re.match("^(\d+ )?(.*)", line)
				weight = matches.group(1)
				if weight == None:
					weight = 1;
				weight = int(weight)
				tokens = tokenize(matches.group(2))
				for i in range(0, weight):
					self.entries.append(Entry(tokens))

	def executeImports(self):
		for tableName in self.imports:
			if tableName in self.tableGroup.tables:
				importTable = self.tableGroup.tables[tableName]
				for importEntry in importTable.entries:
					self.entries.append(importEntry)
			else:
				print "Unable to import {0}, not found in table group {1}".format(tableName, self.tableGroup.name)

	def getRandom(self):
		result = str(random.choice(self.entries))
		if self.appendText != "":
			result = "{0} {1}".format(result, self.appendText)
		return result

	def setDirective(self, directive):
		if directive.lower().startswith("append "):
			self.appendText = directive[6:].strip()
		elif directive.lower().startswith("import "):
			self.imports.append(directive[6:].strip())
		else:
			print "Unsure how to parse directive: {0}".format(directive)

	def setTableGroup(self, tableGroup):
		self.tableGroup = tableGroup
		for entry in self.entries:
			entry.setTableGroup(self.tableGroup)
		self.executeImports()

class Entry(object):
	def __init__(self, tokens):
		self.tokens = tokens

	def setTableGroup(self, tableGroup):
		self.tableGroup = tableGroup
		for token in self.tokens:
			token.setTableGroup(self.tableGroup)

	def __str__(self):
		parts = []
		for token in self.tokens:
			parts.append(str(token))
		return "".join(parts)

class Token(object):
	def __init__(self, value):
		self.value = value

	def setTableGroup(self, tableGroup):
		self.tableGroup = tableGroup

	def __str__(self):
		dice = re.match(diceRegex, self.value)

		if dice != None:
			text = parseDice(dice)
		elif self.value.startswith("["):
			text = parseExpression(self.value[1:-1], self.tableGroup)
		else:
			text = self.value

		return text

def parseFile(filename):
	tables = {}

	try:
		file = open(filename, "r")
		text = file.read()
	except IOError as ex:
		print "Error opening {0}: {1}".format(filename, ex.strerror)
		return {
			"filename": filename,
			"tables": tables,
		}

	for rawtable in re.findall("^#[^#]*", text, re.M):
		table = Table(rawtable)
		tables[table.name.lower()] = table

	return {
		"filename": filename,
		"tables": tables,
	}

def parseDice(dice):
	number = int(dice.group(1))
	size   = int(dice.group(2))
	op     = dice.group(3)
	mod    = int(dice.group(4) or 0)
	total = 0
	for i in range(0, number):
		total = total + random.randint(1, size)

	if op == "+":
		total += mod
	elif op == "-":
		total -= mod
	elif op == "*":
		total *= mod
	elif op == "x":
		total *= mod
	elif op == "/":
		total /= mod

	return str(total)

def parseExpression(expr, defaultTableGroup):
	if expr.lower()[0:4].lower() == "list":
		listMatch = re.match("^List (\d+(?:d\d+(?:[-x+*/]\d+)?)?)\s*((?:[-_.\w]+)?\s*->\s*.*)", expr, re.I)
		if listMatch != None:
			return parseList(listMatch, defaultTableGroup);
		else:
			return "[Unable to parse list: {0}]".format(expr)

	lookupMatch = re.match("([-_.\w]+)?\s*->\s*(.*)", expr)
	
	if lookupMatch != None:
		source = lookupMatch.group(1)
		table = lookupMatch.group(2)
		if source == None:
			return defaultTableGroup.rollOnTable(table)

		if source not in tableGroups:
			TableGroup(source)

		return tableGroups[source].rollOnTable(table)

	return "[Unsure how to interpret: {0}]".format(expr)

def parseList(listMatch, defaultTableGroup):
	results = {}
	resultsText = []
	amount = listMatch.group(1).strip()
	table = listMatch.group(2).strip()

	diceMatch = re.match(diceRegex, amount)
	if diceMatch != None:
		amount = parseDice(diceMatch)

	amount = int(amount)

	for i in range(0, amount):
		result = parseExpression(table, defaultTableGroup)
		if result not in results:
			results[result] = 0

		results[result] += 1

	for result in results:
		qty = results[result]
		if (qty > 1):
			resultsText.append("{0}x {1}".format(str(qty), result))
		else:
			resultsText.append(result)

	return ", ".join(resultsText)

def tokenize(str):
	tokens = []
	for subtoken in re.findall("\[[^]]*]|[^[]+", str):
		subtoken = subtoken
		if subtoken[0] == "[":
			tokens.append(Token(subtoken))
		else:
			dieSplit = re.split("(\d+d\d+(?:[-x+*/]\d+)?)", subtoken)
			for token in dieSplit:
				token = token
				if (token != ""):
					tokens.append(Token(token))
	return tokens

if __name__ == '__main__':
	# TableGroup("treasure")
	# for table in treasure.tables:
	# 	print table
	# print tableGroups["treasure"].rollOnTable("CR 0 Hoard")
	# print treasure.getTable("10 gp Gemstone").getRandom()
	# print tokenize("6d6*100 cp, 3d6*100 sp, 2d6*10 gp, and [-> CR 0 Treasure Hoard Items]")
	pass

if len(sys.argv) >= 3 and len (sys.argv) <= 4:
	group = sys.argv[1]
	table = sys.argv[2]
	quantity = 1
	if len(sys.argv) == 4:
		quantity = int(sys.argv[3])

	TableGroup(group)
	for i in range(0, quantity):
		print tableGroups[group].rollOnTable(table) + "\n"
else:
	print "Usage: {0} tablegroup 'Table name' [quantity]".format(sys.argv[0])
