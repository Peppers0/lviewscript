from blitz import *
import math, itertools, time
from . import items
from enum import Enum

Version = "sdfjsdkfsd"
MissileToSpell = {}
SpellsToEvade = {}
Spells         = {}
ChampionSpells = {}

class SFlag:
	Targeted        = 1
	Line            = 2
	Cone            = 4
	Area            = 8
	
	CollideWindwall = 16
	CollideChampion = 32
	CollideMob      = 64
	
	
	CollideGeneric   = CollideMob      | CollideChampion | CollideWindwall
	SkillshotLine    = CollideGeneric  | Line

class Spell:
	def __init__(self, name, missile_names, flags, delay = 0.0, danger = 1):
		global MissileToSpell, Spells
		
		self.flags = flags
		self.name = name
		self.missiles = missile_names
		self.delay = delay
		self.danger = danger
		Spells[name] = self
		for missile in missile_names:
			MissileToSpell[missile] = self
			
	delay    = 0.0
	danger 	 = 1
	flags    = 0
	name     = "?"
	missiles = []
	skills = []

ChampionSpells = {
}