tabula
======

A python script for interpreting text files as random tables

Usage
=====

Tables are organized into table groups, and each table group is a text file. For example, the "treasure" table group is in "treasure.txt". Note that table group names, and thus the filenames, must only consist of letters and hyphens.

Pass the name of the table group and the table as arguments to execute it, i.e.

	./tabula.py table-group "table name"

You can also specify a quantity to make multiple rolls

	./tabula.py table-group "table name" qty

Try it out!
-----------
tabula comes with tables for generating random treasure for D&D 5th edition. This will give you a treasure hoard suitable for a CR 5 monster

	./tabula.py treasure 'cr 5 hoard'

And this will give you 10 random items from Magic Item table A

	./tabula.py magic-items a 10

Formatting
==========

The formatting for the files is inspired by markdown, and intended to be easy to write and easy to modify, but still rich and powerful

Basics
------

A simple table consists of a name and then a series of entries. The name must start with a single hash tag, and every line that doesn't start with a hash tag or an exclamation point is an entry.

Example:

	# Colors
	red
	blue
	yellow

Weighting
---------

By default, every entry in the table is equally likely to be rolled. They each have a weight of 1. If a line begins with a number, that will be used as the weight for that line.

Example:

	# Townsfolk
	6 peasant
	3 guard
	mayor

In this example, you've got a 60% chance of getting a peasant, a 30% chance of getting a guard, and a 10% chance of getting a mayor

Dice
----

Dice expressions are supported and will be rolled, in the standard RPG format. XdY will roll X dice each with Y sides and then sum them up. You can also add, subtract, multiply, or divide a modifier.

Example

	# Money
	1d6 cp
	2d8+10 sp
	5d12-3 ep
	3d10x1000 gp
	4d100/5 pp

Lookups
-------

Table entries can also have results based on other tables. These table lookups must be enclosed in brackets, and are in the format [ table-group -> table name ]. table-group is optional, and if omitted it's assumed the table you're looking for is in the same table group as the table performing the lookup.

Example:

	adjectives.txt
		# Base Colors
		red
		blue
		yellow

		# Colors
		Bright [-> Base Colors]
		[-> Base Colors]
		Dull [-> Base Colors]

	objects.txt
		# Vehicle
		[adjectives -> Colors] [-> Vehicle types]

		# Vehicle types
		car
		plane
		boat

In this example, the Vehicle table only has one entry, but that entry is constructed by taking a random entry from the Colors table in adjectives.txt (which is further based on the Base colors table in the same file) and a random entry from the Vehicle types table.

Note that the table names are case insensitive, so [-> vehicle types] is equivalent to [-> Vehicle types] and even [-> VEHICLE TYPES]

Lists
-----

You can also do a number of lookups with a list, in the format [List qty table-group -> table name]. As with normal lookups, table-group is optional and will default to the same group as the table calling it. Qty should either be a number or a dice expression.

Example:

	# Christmas Checklist
	[List 1d12 -> gifts]

	# Gifts
	Partridge in a pear tree
	Turtle Dove
	French Hen
	Calling Bird
	Gold Ring
	Goose-a-Laying
	Swan-a-Swimming
	Maid-a-Milking
	Lady Dancing
	Lord-a-Leaping
	Piper Piping
	Drummer Drumming

Directives
----------

Tabula also supports directives, which must start with an exclamation point. Directives modify how the table behaves. 

**Append**: The text of the append directive will be appended to all results this table generates

Example:

	# 1000 gp gemstones
	! Append (1,000 gp)
	Black opal
	Blue sapphire
	Emerald
	Fire opal
	Opal
	Star ruby
	Star sapphire
	Yellow sapphire

**Import**: The import directive copies all entries from the specified table into this table. The entries will have the same weight in this table as they did in their source table. Note that the source table must be in the same table group.

Example:

	# Weapon
	! Import simple melee weapons
	! Import simple ranged weapons
	! Import martial melee weapons
	! Import martial ranged weapons
