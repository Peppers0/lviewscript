from blitz import *
import math, itertools, time
from . import items
from enum import Enum
from . import utils
import json
from re import search

Version = "sdfjsdkfsd"
MissileToSpell = {}
SpellsToEvade = {}
Spells         = {}
ChampionSpells = {}

class HitChance(Enum):
	Immobile = 8
	Dashing = 7
	VeryHigh = 6
	High = 5
	Medium = 4
	Low = 3
	Impossible = 2
	OutOfRange = 1
	Collision = 0

_HitChance = HitChance.Impossible

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
	
class DangerLevels:
	Easy 			= 1
	Fastes 			= 2
	UseSpell 		= 3
	VeryDangerous	= 4

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
			if len(missile) < 1:
				MissileToSpell[name] = self
			MissileToSpell[missile] = self
			
	delay    = 0.0
	danger 	 = 1
	flags    = 0
	name     = "?"
	missiles = []
	skills = []


ChampionSpells = {
	"aatrox": [
		Spell("aatroxw",                ["aatroxw"],                               SFlag.SkillshotLine)
	],
	"rell": [
		Spell("rellq",                ["rellq_vfxmis"],                               SFlag.SkillshotLine)
	],
	"twistedfate": [
		Spell("wildcards",                ["sealfatemissile"],                               SFlag.SkillshotLine)
	],
	"missfortune": [
		Spell("missfortunericochetshot",                ["missfortunericochetshot"],                               SFlag.Cone)
	],
	"zoe": [
		Spell("zoeqmissile",                ["zoeqmissile"],                               SFlag.SkillshotLine),
		Spell("zoeq2",                ["zoeqmis2"],                               SFlag.SkillshotLine),
		Spell("zoee",                ["zoeemis"],                               SFlag.SkillshotLine),
		Spell("zoeebubble",                ["zoeec"],                               SFlag.Area)
	],
	"ornn": [
		Spell("ornnq",                ["ornnqmissile"],                               SFlag.SkillshotLine),
		Spell("ornnrwave",                ["ornnrwave2"],                               SFlag.SkillshotLine)
	],
	"kassadin": [
		Spell("riftwalk",                ["riftwalk"],                               SFlag.Area),
		Spell("forcepulse",                [],                               SFlag.Cone)
	],
	"quinn": [
		Spell("quinnq",                ["quinnq"],                               SFlag.CollideGeneric)
	],
	"aurelionsol": [
		Spell("aurelionsolq",           ["aurelionsolqmissile"],                   SFlag.SkillshotLine),
		Spell("aurelionsolr",           ["aurelionsolrbeammissile"],               SFlag.SkillshotLine)
	],
	"ahri": [                                                                      
		Spell("ahriorbofdeception",     ["ahriorbmissile"],                        SFlag.SkillshotLine),
		Spell("ahriseduce",             ["ahriseducemissile"],                     SFlag.SkillshotLine)
	],
	"ashe": [
		Spell("enchantedcrystalarrow",  ["enchantedcrystalarrow"],                 SFlag.SkillshotLine),
		Spell("volley",  ["volleyrightattack"],                 SFlag.Cone)
	],
	"shen": [                           
		Spell("shene",           ["shene"], 			SFlag.Line)
	],
	"elise": [                           
		Spell("elisehumane",           ["elisehumane"], 			SFlag.SkillshotLine)
	],
	"sylas": [                           
		Spell("sylase2",           ["sylase2"], 			SFlag.SkillshotLine),
		Spell("sylasq",           [], 			SFlag.Area),
		Spell("sylasqline",           [], 			SFlag.Line)
	],
	"camille": [                           
		Spell("camillee",           ["camilleemissile"], 			SFlag.SkillshotLine)
	],
	"kennen": [                           
		Spell("kennenshurikenhurlmissile1",           ["kennenshurikenhurlmissile1"], 			SFlag.SkillshotLine)
	],
	"darius": [                           
		Spell("dariuscleave",           [],	SFlag.Area),
		Spell("dariusaxegrabcone",      ["dariusaxegrabcone"], SFlag.Cone)
	],
	"brand": [
		Spell("brandwildfiremissile",                 ["brandwildfire"], SFlag.Area),
		Spell("brandwildfire",                 ["brandwildfiremissile"], SFlag.Area),
		Spell("brandw",                 ["basespell"], SFlag.Area),
		Spell("brandq",                 ["brandqmissile"],                         SFlag.SkillshotLine)
	],
	"pyke": [
		Spell("pykeqrange",                 ["pykeqrange"],                         SFlag.SkillshotLine)
	],
	"amumu": [
		Spell("bandagetoss",                 ["sadmummybandagetoss"],                         SFlag.Line | SFlag.CollideWindwall)
	],
	"caitlyn": [
		Spell("caitlynpiltoverpeacemaker", ["caitlynpiltoverpeacemaker", "caitlynpiltoverpeacemaker2"],          SFlag.Line | SFlag.CollideWindwall),
		Spell("caitlynyordletrap",         [],                                                                   SFlag.Area),
		Spell("caitlynentrapment",         ["caitlynentrapmentmissile"],                                         SFlag.SkillshotLine)
	],
	"chogath": [                        
		Spell("rupture",                ["rupture"],                                        SFlag.Area),
		Spell("feralscream",            ["feralscream"],                                        SFlag.Cone | SFlag.CollideWindwall)
	],
	"drmundo": [
		Spell("infectedcleavermissilecast", ["infectedcleavermissile"],            SFlag.SkillshotLine)
	],
	"bard": [
		Spell("bardq", ["bardqmissile"],            SFlag.SkillshotLine),
		Spell("bardr", ["bardr"],            SFlag.Area)
	],
	"diana": [
		Spell("dianaq",                 ["dianaqinnermissile", "dianaqoutermissile", "dianaq"], SFlag.Cone | SFlag.CollideWindwall),
		Spell("dianaarcarc",                 ["dianaarcarc"], 	SFlag.Cone | SFlag.CollideWindwall)
	],
	"qiyana": [
		Spell("qiyanaq_rock",                 ["qiyanaq_rock"], SFlag.SkillshotLine, 0.25, DangerLevels.Fastes),
		Spell("qiyanaq_grass",                 ["qiyanaq_grass"], SFlag.SkillshotLine, 0.25, DangerLevels.Fastes),
		Spell("qiyanaq_water",                 ["qiyanaq_water"], SFlag.SkillshotLine, 0.25, DangerLevels.Fastes),
		Spell("qiyanar",                 ["qiyanarmis"], SFlag.SkillshotLine, 0.25, DangerLevels.UseSpell),
		Spell("dianaarcarc",                 ["dianaarcarc"], 	SFlag.Cone)
	],
	"ekko": [
		Spell("ekkoq",                  ["ekkoqmis"],                              SFlag.Line | SFlag.Area, 0.0, DangerLevels.Easy),
		Spell("ekkow",                  ["ekkowmis"],                              SFlag.Area, 0.0, DangerLevels.Fastes),
		Spell("ekkor",                  ["ekkor"],                              SFlag.Area, 0.0, DangerLevels.UseSpell)
	],
	"kogmaw": [
		Spell("kogmawq",                  ["kogmawq"],                              SFlag.SkillshotLine),
		Spell("kogmawvoidooze",                  ["kogmawvoidoozemissile"],                              SFlag.SkillshotLine),
		Spell("kogmawlivingartillery",                  ["kogmawlivingartillery"],                              SFlag.Area)
	],
	"fizz": [
		Spell("fizzr",                  ["fizzrmissile"],                          SFlag.SkillshotLine, 0.0, DangerLevels.UseSpell)
	],
	"vi": [
		Spell("vi-q",                  ["viqmissile"],                          SFlag.SkillshotLine),
	],
	"viktor": [
		Spell("viktorgravitonfield",                  ["viktordeathraymissile"],                          SFlag.SkillshotLine)
	],
	"irelia": [
		Spell("ireliae2",                ["ireliaemissile"],                        SFlag.Line | SFlag.CollideWindwall),
		Spell("ireliaw2",                ["ireliaw2"],                        SFlag.SkillshotLine),
		Spell("ireliar",                ["ireliar"],                               SFlag.SkillshotLine)
	],
	"katarina": [
		Spell("katarinae",                [],                        SFlag.Targeted)
	],
	"illaoi": [
		Spell("illaoiq",                [],                                        SFlag.Area),
		Spell("illaoie",                ["illaoiemis"],                            SFlag.SkillshotLine)
	],
	"heimerdinger": [
		Spell("heimerdingerwm",                ["heimerdingerwattack2", "heimerdingerwattack2ult"],                                        SFlag.SkillshotLine),
		Spell("heimerdingere",                ["heimerdingerespell"],                            SFlag.Area)
	],
	"jarvaniv": [
		Spell("jarvanivdemacianstandard",   [],                            SFlag.Area),
        Spell("jarvanivdragonstrike",                [],                        SFlag.SkillshotLine),
		Spell("jarvanivqe", [],                                       SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall)
	],
	"janna": [
		Spell("jannaq",                ["howlinggalespell"],                        SFlag.SkillshotLine)
	],
	"jayce": [
		Spell("jayceshockblast",                ["jayceshockblastmis"],                        SFlag.SkillshotLine),
		Spell("jayceqaccel",                ["jayceshockblastwallmis"],                        SFlag.SkillshotLine)
	],
	"khazix": [
		Spell("khazixw",                ["khazixwmissile"],                        SFlag.SkillshotLine),
		Spell("khazixwlong",            ["khazixwmissile"],                        SFlag.SkillshotLine),
		Spell("khazixe",            ["khazixe"],                        SFlag.Area)
	],
	"ezreal": [                         
		Spell("ezrealq",                ["ezrealq"],                               SFlag.SkillshotLine),
		Spell("ezrealw",                ["ezrealw"],                               SFlag.SkillshotLine),
		Spell("ezrealr",                ["ezrealr"],                               SFlag.SkillshotLine)
	],
	"kalista": [                         
		Spell("kalistamysticshot",                ["kalistamysticshotmis", "kalistamysticshotmistrue"],                               SFlag.SkillshotLine, 0.0, DangerLevels.UseSpell),
	],
	"alistar": [                         
		Spell("pulverize",                ["koco_missile"],                               SFlag.Area),
	],
	"lissandra": [                         
		Spell("lissandraq",                ["lissandraqmissile"],                               SFlag.SkillshotLine),
		Spell("lissandraqshards",                ["lissandraqshards"],                               SFlag.SkillshotLine),
		Spell("lissandrae",                ["lissandraemissile"],                               SFlag.SkillshotLine),
	],
	"galio": [
		Spell("galioq", 					[], 							SFlag.Area),
		Spell("galioe", 					[], 							SFlag.SkillshotLine)
	],
	"evelynn": [
		Spell("evelynnq",               ["evelynnq"],                              SFlag.SkillshotLine),
		Spell("evelynnr",               ["evelynnr"],                              SFlag.Cone)
	],
	"graves": [                         
		Spell("gravesqlinespell",       ["gravesqlinemis", "gravesqreturn"],       SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall),
		Spell("gravessmokegrenade",     ["gravessmokegrenadeboom"],                SFlag.Area | SFlag.CollideWindwall),
		Spell("graveschargeshot",       ["graveschargeshotshot"],                  SFlag.Line | SFlag.CollideWindwall),
		Spell("graveschargeshotfxmissile2",       ["graveschargeshotfxmissile2"],                  SFlag.Cone)
	],
	"leesin": [                         
		Spell("blindmonkqone",          ["blindmonkqone"],                         SFlag.SkillshotLine)
	],
	"leona": [
		Spell("leonazenithblade",       ["leonazenithblademissile"],               SFlag.SkillshotLine, 0.25, DangerLevels.Fastes),
		Spell("leonasolarflare",        ["leonasolarflare"],                                        SFlag.Area)
	],
	"leblanc": [
		Spell("leblancslide",               ["leblancslide"],                                        SFlag.Area),
		Spell("leblancr",               ["leblancslidem"],                                        SFlag.Area),
		Spell("leblance",               ["leblancsoulshackle"],                       SFlag.SkillshotLine),
		Spell("leblancsoulshacklem",               ["leblancsoulshacklem"],                       SFlag.SkillshotLine)
	],
	"lucian": [
		Spell("lucianq",                ["lucianq"],                          SFlag.SkillshotLine, 0.4, DangerLevels.Fastes),
		Spell("lucianw",                ["lucianwmissile"],                          SFlag.SkillshotLine),
		Spell("lucianrmis",                ["lucianrmissile"],                          SFlag.SkillshotLine, 0, DangerLevels.UseSpell)
	],
	"gragas": [
		Spell("gragasq",                ["gragasqmissile"],                          SFlag.Area),
		Spell("gragase",                ["gragase"],                          SFlag.SkillshotLine),
		Spell("gragasr",                [],                          SFlag.Area, 0.0, DangerLevels.UseSpell),
		Spell("gragasrfow",                ["gragasrboom"],                          SFlag.Area)
	],
	"tristana": [
		Spell("tristanaw",                ["rocketjump"],                          SFlag.Area)
	],
	"rengar": [
		Spell("rengare",                ["rengaremis"],                            SFlag.SkillshotLine),
		Spell("rengareemp",             ["rengareempmis"],                         SFlag.SkillshotLine),
	],
	"ryze": [
		Spell("ryzeq",           ["ryzeq"],                                 SFlag.SkillshotLine)
	],
	"blitzcrank": [
		Spell("rocketgrab",           ["rocketgrabmissile"],                                 SFlag.SkillshotLine, 0.0, DangerLevels.Fastes),
	],
	"corki": [
		Spell("phosphorusbomb",           ["phosphorusbombmissile"],                                 SFlag.Area),
		Spell("missilebarrage",           ["missilebarragemissile"],                                 SFlag.SkillshotLine),
		Spell("missilebarrage2",           ["missilebarragemissile2"],                                 SFlag.SkillshotLine),
	],
	"varus": [
		Spell("varusq",                 ["varusqmissile"],                         SFlag.Line | SFlag.CollideWindwall),
		Spell("varuse",                 ["varusemissile"],                         SFlag.Area),
		Spell("varusr",                 ["varusrmissile"],                         SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall, delay=0.0, danger=3)
	],
	"varus": [
		Spell("varusq",                 ["varusqmissile"],                         SFlag.Line | SFlag.CollideWindwall),
		Spell("varuse",                 ["varusemissile"],                         SFlag.Area),
		Spell("varusr",                 ["varusrmissile"],                         SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall, delay=0.0, danger=3)
	],
	"tryndamere": [                         
		Spell("slashcast",    ["slashcast"],                SFlag.SkillshotLine)
	],
	"twitch": [                         
		Spell("twitchvenomcask",    ["twitchvenomcaskmissile"],                SFlag.Area)
	],
	"velkoz": [
		Spell("velkozq",                 ["velkozqmissile"],                         SFlag.Line | SFlag.CollideWindwall),
		Spell("velkozqsplit",                 ["velkozqmissilesplit"],                         SFlag.Line | SFlag.CollideWindwall),
		Spell("velkozqsplitactivate",                 ["velkozqmissilesplit"],                         SFlag.Line | SFlag.CollideWindwall),
		Spell("velkozw", 								["velkozwmissile"], 				SFlag.Line | SFlag.CollideWindwall			),
		Spell("velkoze",                 					["velkozemissile"],                         SFlag.Area)
	],
	"lux": [                            
		Spell("luxlightbinding",        ["luxlightbindingmis", "luxlightbindingdummy"],                    SFlag.SkillshotLine),
		Spell("luxlightstrikekugel",    ["luxlightstrikekugel"],                   SFlag.Area),
	],
	"nautilus": [                            
		Spell("nautilusanchordragmissile",        ["nautilusanchordragmissile"],                    SFlag.SkillshotLine, 0.25, DangerLevels.Fastes | DangerLevels.UseSpell)
	],
	"malzahar": [                            
		Spell("malzaharq",        ["malzaharq"],                    SFlag.SkillshotLine)
	],
	"skarner": [                            
		Spell("skarnerfracture",        ["skarnerfracturemissile"],                    SFlag.SkillshotLine)
	],
	"talon": [                            
		Spell("talonw",        ["talonwmissileone"],                    SFlag.SkillshotLine),
		Spell("talonrakereturn",        ["talonwmissiletwo"],                    SFlag.SkillshotLine)
	],
	"ziggs": [                          
		Spell("ziggsq",                  ["ziggsqspell", "ziggsqspell2", "ziggsqspell3"],                              SFlag.Area | SFlag.CollideWindwall),
		Spell("ziggsw",                 ["ziggsw"],                                                                   SFlag.Area | SFlag.CollideWindwall),
		Spell("ziggse",                 ["ziggse2"],                                                                  SFlag.Area | SFlag.CollideWindwall),
		Spell("ziggsr",                 ["ziggsrboom", "ziggsrboommedium", "ziggsrboomlong", "ziggsrboomextralong"],  SFlag.Area),
	],
	"kartush": [                          
		Spell("karthuslaywastea2",   ["karthuslaywastea3", "karthuslaywastea1", "karthuslaywastedeada1", "karthuslaywastedeada2", "karthuslaywastedeada3"],   SFlag.Area | SFlag.CollideWindwall),
	],
	"jhin": [                           
		Spell("jhinw",                  ["jhinwmissile"],                                 SFlag.Line),
		Spell("jhine",                  ["jhinetrap"],                             SFlag.Area),
		Spell("jhinrshot",              ["jhinrshotmis", "jhinrshotmis4"],         SFlag.SkillshotLine)
	],
	"swain": [
		Spell("swainshadowgrasp",                  ["swainshadowgrasp"],                                 SFlag.Area | SFlag.CollideWindwall),
		Spell("swaine",                  ["swaine"],                             SFlag.SkillshotLine),
		Spell("swainereturn",              ["swainereturnmissile"],         SFlag.SkillshotLine)
	],
	"nasus": [
		Spell("nasuse",                 [],                                        SFlag.Area)
	],
	"nami": [
		Spell("namiq",                  ["namiqmissile"],                          SFlag.Area),
		Spell("namir",                  ["namirmissile"],                          SFlag.Line | SFlag.CollideWindwall)
	],
	"nidalee": [
		Spell("javelintoss",            ["javelintoss"],                           SFlag.SkillshotLine),
		Spell("bushwhack",              [],                                        SFlag.Area)
	],
	"malphite": [
		Spell("malphiter",                ["ufslash"],                                        SFlag.SkillshotLine)
	],
	"reksai": [
		Spell("reksaiqburrowed",                ["reksaiqburrowedmis"],                                        SFlag.SkillshotLine)
	],
	"thresh": [
		Spell("threshq",                ["threshqmissile"],                        SFlag.SkillshotLine),
		Spell("thresheflay",                ["threshemissile1"],                        SFlag.SkillshotLine)
	],
	"morgana": [                        
		Spell("morganaq",               ["morganaq"],                              SFlag.SkillshotLine),
		Spell("morganaw",               [],                       SFlag.Area)
	],
	"mordekaiser": [                        
		Spell("mordekaiserq",               [],                              SFlag.SkillshotLine),
		Spell("mordekaisere",               [],                       SFlag.SkillshotLine)
	],
	"samira": [                        
		Spell("samiraqgun",               ["samiraqgun"],                              SFlag.SkillshotLine),
	],
	"pantheon": [
		Spell("pantheonq",              ["pantheonqmissile"],                      SFlag.Line | SFlag.CollideWindwall),
		Spell("pantheonr",              ["pantheonrmissile"],                      SFlag.Area)
	],
	"annie": [                                                                     
		Spell("anniew",                 [],                                        SFlag.Cone | SFlag.CollideWindwall),
		Spell("annier",                 [],                                        SFlag.Area)
	],
	"hecarim": [                                                                     
		Spell("hecarimult",                 ["hecarimultmissile"],                                        SFlag.SkillshotLine),
		Spell("hecarimrcircle",                 [],                                        SFlag.Area)
	],
	"olaf": [
		Spell("olafaxethrowcast",       ["olafaxethrow"],                          SFlag.Line | SFlag.CollideWindwall)
	],
	"anivia": [
		Spell("flashfrost",             ["flashfrostspell"],                       SFlag.Line | SFlag.CollideWindwall)
	],
	"zed": [
		Spell("zedq",       ["zedqmissile"],                          SFlag.Line),
		Spell("zedw",       ["zedwmissile"],                          SFlag.Area)
	],
	"xerath": [
		Spell("xeratharcanopulse",             ["xeratharcanopulse"],                       SFlag.Area),
		Spell("xeratharcanopulsechargup",             ["xeratharcanopulsechargup"],                       SFlag.Area),
		Spell("xeratharcanebarrage2",            ["xeratharcanebarrage2"],                                        SFlag.Area),
		Spell("xerathmagespear",           ["xerathmagespearmissile"],                                        SFlag.Line | SFlag.CollideWindwall),
		Spell("xerathrmissilewrapper",           ["xerathlocuspulse"],                                        SFlag.Area),
	],
	"urgot": [
		Spell("urgotq",                 ["urgotqmissile"],                         SFlag.Area | SFlag.CollideWindwall, delay = 0.2),
		Spell("urgotr",                 ["urgotr"],                                SFlag.Line | SFlag.CollideWindwall | SFlag.CollideChampion)
	],
	"poppy": [
		Spell("poppyq",                 ["poppyq"],                         SFlag.SkillshotLine | SFlag.CollideWindwall),
		Spell("poppyrspell",                 ["poppyrmissile"],                                SFlag.SkillshotLine | SFlag.CollideWindwall)
	],
	"gnar": [
		Spell("gnarq",                 ["gnarqmissile"],                         SFlag.SkillshotLine),
		Spell("gnarqreturn",                 ["gnarqmissilereturn"],                                SFlag.SkillshotLine),
		Spell("gnarbigq",                 ["gnarbigqmissile"],                                SFlag.SkillshotLine),
		Spell("gnarbigw",                 ["gnarbigw"],                                SFlag.SkillshotLine),
		Spell("gnare",                 ["gnare"],                                SFlag.Area),
		Spell("gnarbige",                 ["gnarbige"],                                SFlag.Area),
		Spell("gnarr",                 [""],                                SFlag.Area)
	],
	"senna": [
		Spell("sennaqcast",             ["sennaqcast"],                                SFlag.SkillshotLine),
		Spell("sennaw",                 ["sennaw"],                                SFlag.SkillshotLine),
		Spell("sennar",                 ["sennar"],                                SFlag.Line)
	],
	"shyvana": [
		Spell("shyvanafireball",        ["shyvanafireballmissile"],                SFlag.SkillshotLine),
		Spell("shyvanafireballdragon2", ["shyvanafireballdragonmissile"],          SFlag.SkillshotLine)
	],
	"singed": [
		Spell("megaadhesive",           ["singedwparticlemissile"],                SFlag.Area)
	],
	"fiora": [
		Spell("fioraw",           ["fiorawmissile"],                SFlag.SkillshotLine)
	],
	"sivir": [
		Spell("sivirq",                 ["sivirqmissile"],                         SFlag.Cone)
	],
	"kaisa": [
		Spell("kaisaw",                 ["kaisaw"],                         SFlag.Line | SFlag.CollideWindwall)
	],
	"karma": [
		Spell("karmaq",                 ["karmaqmissile", "karmaqmissilemantra"],                         SFlag.Line | SFlag.CollideWindwall),
		Spell("karmaqmantracircle",                 [],                         SFlag.Line | SFlag.CollideWindwall)
	],
	"braum": [
		Spell("braumq",                 ["braumqmissile"],                         SFlag.SkillshotLine),
		Spell("braumrwrapper",                 ["braumrmissile"],                         SFlag.SkillshotLine)
	],
	"soraka": [
		Spell("sorakaq",                ["sorakaqmissile"],                        SFlag.Area),
		Spell("sorakae",                [],                                        SFlag.Area)
	],
	"rakan": [
		Spell("rakanq",                ["rakanqmis"],                        SFlag.SkillshotLine),
		Spell("rakanw",                [],                                        SFlag.Area, delay=0.5)
	],
	"xayah": [
		Spell("xayahq",                ["xayahqmissile1", "xayahqmissile2"],      SFlag.SkillshotLine)
	],
	"sona": [
		Spell("sonar",                  ["sonar"],                                 SFlag.Line | SFlag.CollideWindwall)
	],
	"akali": [
		Spell("akalie",                  ["akaliemis"],                                 SFlag.Line | SFlag.CollideWindwall)
	],
	"kayle": [
		Spell("kayleq",                 ["kayleqmis"],                             SFlag.SkillshotLine)
	],
	"yasuo": [
		Spell("yasuoq1",                  ["yasuoq1"],                             SFlag.SkillshotLine),
		Spell("yasuoq2",                  ["yasuoq12_no"],                             SFlag.SkillshotLine),
		Spell("yasuoq2wrapper",                 [],                             SFlag.SkillshotLine),
		Spell("yasuoq3",                 ["yasuoq3mis"],                             SFlag.SkillshotLine)
	],
	"yone": [
		Spell("yoneq3",                 ["yoneq3missile"],                             SFlag.SkillshotLine),
	],
	"yuumi": [
		Spell("yuumiq",                 [],                             SFlag.Cone)
	],
	"zac": [
		Spell("zacq",                   ["zacqmissile"],                           SFlag.SkillshotLine),
		Spell("zace",                   [],                                        SFlag.Area)
	],
	"zyra": [
		Spell("zyraq",                  ["zyraq"],                                        SFlag.Cone),
		Spell("zyraw",                  ["zyraw"],                                        SFlag.Area),
		Spell("zyrae",                  ["zyrae"],                                 SFlag.SkillshotLine),
		Spell("zyrar",                  ["zyrar"],                                         SFlag.Area | SFlag.CollideChampion | SFlag.CollideWindwall),
		Spell("zyrapassivedeathmanager",                  ["zyrapassivedeathmanager"],                                        SFlag.SkillshotLine)
	],
	"zilean": [
		Spell("zileanq",                ["zileanqmissile"],                        SFlag.Area | SFlag.CollideWindwall)
	],
	"maokai": [
		Spell("maokaiq",                ["maokaiqmissile"],                        SFlag.SkillshotLine)
	],
	"orianna": [
		Spell("orianaizunacommand",     ["orianaizuna"],                           SFlag.Line | SFlag.Area | SFlag.CollideWindwall)
	],
	"warwick": [
		Spell("warwickr",               [],                                        SFlag.Area | SFlag.CollideChampion),
		Spell("warwickrchannel",               [],                                        SFlag.Area | SFlag.CollideChampion)
	],
	"taric": [
		Spell("tarice", 			["tarice"], 			SFlag.SkillshotLine)
	],
	"cassiopeia": [
		Spell("cassiopeiar", 			["cassiopeiar"], 			SFlag.Cone),
		Spell("cassiopeiaq", 			["cassiopeiaq"], 			SFlag.Area)
	],
	"viego": [
		Spell("viegoq", 			[], 			SFlag.Line | SFlag.CollideWindwall),
		Spell("viegowcast", ["viegowmis"], SFlag.Line | SFlag.CollideWindwall),
		Spell("viegorr", [], SFlag.Area)
	],
	"syndra": [
		Spell("syndraq", 			["syndraqspell"], 			SFlag.Area),
		Spell("syndrawcast", 			["syndraw_special"], 			SFlag.Area),
		Spell("syndrae5", 			["syndrae5", "syndraespheremissile"], 			SFlag.Area),
		Spell("syndraqe", 			["syndrae"], 			SFlag.Area),
		Spell("syndrae", 			["syndrae", "syndraespheremissile"], 			SFlag.Area)
	],
	"draven": [
		Spell("dravendoubleshot", 			["dravendoubleshotmissile"], 			SFlag.SkillshotLine),
		Spell("dravenrcast", 			["dravenr"], 			SFlag.SkillshotLine)
	],
	"kayn": [
		Spell("kaynq", 			[], 			SFlag.CollideWindwall),
		Spell("kaynw", 			["kaynw_1234"], 			SFlag.SkillshotLine),
		Spell("kaynassw", 			[], 			SFlag.SkillshotLine)
	],
	"jinx": [
		Spell("jinxwmissile", 			["jinxwmissile"], 			SFlag.SkillshotLine),
		Spell("jinxe", 			["jinxehit"], 			SFlag.Area),
		Spell("jinxr", 			["jinxr"], 			SFlag.SkillshotLine)
	],
	"cassiopeia": [
		Spell("cassiopeiaq", 			["cassiopeiaq"], 			SFlag.Area),
		Spell("cassiopeir", 			["cassiopeiar"], 			SFlag.Cone),
	],
	"seraphine": [
		Spell("seraphineq", 			["seraphineqinitialmissile"], 			SFlag.Area),
		Spell("seraphineecast", 			["seraphineemissile"], 			SFlag.SkillshotLine),
		Spell("seraphiner", 			["seraphiner"], 			SFlag.SkillshotLine),
		Spell("seraphinerfow", 			[], 			SFlag.SkillshotLine),
	],
	"lulu": [
		Spell("luluq", 			["luluqmissile"], 			SFlag.SkillshotLine),
		Spell("luluqpix", 			["luluqmissiletwo"], 			SFlag.SkillshotLine)
	],
	"aphelios": [
		Spell("aphelioscalibrumq", 			["aphelioscalibrumq"], 			SFlag.SkillshotLine),
		Spell("apheliosr", 			["apheliosrmis"], 			SFlag.SkillshotLine)
	],
	"neeko": [
		Spell("neekoq", 			["neekoq"], 			SFlag.Area),
		Spell("neekoe", 			["neekoe", "neekoq"], 			SFlag.SkillshotLine | SFlag.CollideWindwall)
	],
	"allchampions": [
		Spell("arcanecomet", 			["perks_arcanecomet_mis", "perks_arcanecomet_mis_arc"], 			SFlag.Area)
	],
	"lillia": [
		Spell("lilliaw", 			[], 			SFlag.Area | SFlag.CollideWindwall),
		Spell("lilliae", 			["lilliae"], 			SFlag.SkillshotLine),
		Spell("lilliae2", 			["lilliaerollingmissile"], 			SFlag.SkillshotLine)
	],
	"tahmkench": [
		Spell("tahmkenchq", 			["tahmkenchqmissile"], 			SFlag.SkillshotLine)
	],
	"sett": [
		Spell("settw", 			["settw"], 			SFlag.Cone),
		Spell("sette", 			[], 			SFlag.SkillshotLine)
	]
}

def draw_prediction_info(game, ui):
	global ChampionSpells, Version
	
	ui.separator()
	ui.text("Using LPrediction " + Version, Color.PURPLE)
	if is_champ_supported(game.player):
		ui.text(game.player.name.upper() + " has skillshot prediction support", Color.GREEN)
	else:
		ui.text(game.player.name.upper() + " doesnt have skillshot prediction support", Color.RED)
	
	if ui.treenode(f'Supported Champions ({len(ChampionSpells)})'):
		for champ, spells in sorted(ChampionSpells.items()):
			ui.text(f"{champ.upper()} {' '*(20 - len(champ))}: {str([spell.name for spell in spells])}")
			
		ui.treepop()

def to_lower(dictionary):

    def try_iterate(k):
        return lower_by_level(k) if isinstance(k, dict) else k

    def try_lower(k):
        return k.lower() if isinstance(k, str) else k

    def lower_by_level(data):
        return dict((try_lower(k), try_iterate(v)) for k, v in data.items())

    return lower_by_level(dictionary)

def get_range(game, skill_name, slot):
	# convertedSkillName = None
	spelldb_range = 0
	with open("SpellDB.json", "r") as read_file:
		champ = json.loads(read_file.read())
		convertedSkillShot = {k.lower() if isinstance(k, str) else k: v.lower() if isinstance(v, str) else v for k,v in champ[game.player.name.capitalize()][slot].items()}
		if convertedSkillShot['name'] == skill_name:
			spelldb_range = convertedSkillShot['rangeburn']
			# convertedSkillName = search(convertedSkillShot['name'], skill_name)

	return spelldb_range

def get_skillshot_range(game, skill_name, slot):
	global Spells

	# with open("SpellDB.json", "r") as read_file:
	# 	champ = json.loads(read_file.read())
	# 	convertedSkillShot = {k.lower() if isinstance(k, str) else k: v.lower() if isinstance(v, str) else v for k,v in champ[game.player.name.capitalize()][slot].items()}
	# 	if convertedSkillShot['name'] == skill_name:
	# 		spelldb_range = convertedSkillShot['rangeburn']

	# convertedSkillName = search(convertedSkillShot['name'], skill_name)

	if skill_name not in Spells:
		raise Exception("Not a skillshot")

	# Get the range of the missile if it has a missile
	skillshot = Spells[skill_name]
	if len(skillshot.missiles) > 0:
		return game.get_spell_info(skillshot.missiles[0]).cast_range
		
	# If it doesnt have a missile get simply the cast_range from the skill
	info = game.get_spell_info(skill_name)
	return info.cast_range * 2.0 if is_skillshot_cone(skill_name) else info.cast_range

def is_skillshot(skill_name):
	global Spells, MissileToSpell
	return skill_name in Spells or skill_name in MissileToSpell
	
def get_missile_parent_spell(missile_name):
	global MissileToSpell, Spells
	return MissileToSpell.get(missile_name, None)
	
def is_champ_supported(champ):
	global ChampionSpells
	return champ.name in ChampionSpells
	
def is_skillshot_cone(skill_name):
	if skill_name not in Spells:
		return False
	return Spells[skill_name].flags & SFlag.Cone
	
def is_last_hitable(game, player, enemy):
	missile_speed = player.basic_missile_speed + 1
		
	hit_dmg = items.get_onhit_physical(player, enemy) + items.get_onhit_magical(player, enemy)
	
	hp = enemy.health
	atk_speed = player.base_atk_speed * player.atk_speed_multi
	t_until_basic_hits = game.distance(player, enemy)/missile_speed#(missile_speed*atk_speed/player.base_atk_speed)

	for missile in game.missiles:
		if missile.dest_id == enemy.id:
			src = game.get_obj_by_id(missile.src_id)
			if src:
				t_until_missile_hits = game.distance(missile, enemy)/(missile.speed + 1)
			
				if t_until_missile_hits < t_until_basic_hits:
					hp -= src.base_atk

	return hp - hit_dmg <= 0

def fast_prediction(game, spell, caster, target, range):
	global Spells

	t = target.pos.sub(caster.pos).length() / spell.speed
	t += spell.travel_time

	target_dir = target.pos.sub(target.prev_pos).normalize()
	if math.isnan(target_dir.x):
		target_dir.x = 0.0
	if math.isnan(target_dir.y):
		target_dir.y = 0.0
	if math.isnan(target_dir.z):
		target_dir.z = 0.0

	if target_dir.x == 0.0 and target_dir.z == 0.0:
		return target.pos

	result = target.pos.add(target_dir.scale((t + spell.speed) * target.movement_speed))

	return result

def castpoint_for_collision(game, spell, caster, target):
	global Spells

	if spell.name not in Spells:
		return target.pos
	
	# Get extra data for spell that isnt provided by blitz
	spell_extra = Spells[spell.name]
	if len(spell_extra.missiles) > 0:
		missile = game.get_spell_info(spell_extra.missiles[0])
	else:
		missile = spell
		
	t_delay = spell.delay + spell_extra.delay
	if missile.travel_time > 0.0:
		t_missile = missile.travel_time
	else:
		t_missile = (missile.cast_range / missile.speed) if len(spell_extra.missiles) > 0 and missile.speed > 0.0 else 0.0		
	# Get direction of target
	target_dir = target.pos.sub(target.prev_pos).normalize()
	if math.isnan(target_dir.x):
		target_dir.x = 0.0
	if math.isnan(target_dir.y):
		target_dir.y = 0.0
	if math.isnan(target_dir.z):
		target_dir.z = 0.0
	#print(f'{target_dir.x} {target_dir.y} {target_dir.z}')

	# If the spell is a line we simulate the main missile to get the collision point
	if spell_extra.flags & SFlag.Line:
		
		iterations = int(missile.cast_range/30.0)
		step = t_missile/iterations

		last_dist = 99999999
		last_target_pos = target.pos
		for i in range(iterations):
			t = i*step
			target_future_pos = target.pos.add(target_dir.scale((t_delay + t)*target.movement_speed))
			spell_dir = target_future_pos.sub(caster.pos).normalize().scale(t*missile.speed)
			spell_future_pos = caster.pos.add(spell_dir)
			dist = target_future_pos.distance(spell_future_pos)
			if dist < missile.width / 2.0:
				return target_future_pos
			elif dist > last_dist:
				return last_target_pos
			else:
				last_dist = dist
				last_target_pos = target_future_pos
				
		return target.pos
		
	# If the spell is an area spell we return the position of the player when the spell procs
	elif spell_extra.flags & SFlag.Area:
		return target.pos.add(target_dir.scale(t_delay * target.movement_speed))
	else:
		return target.pos

def GetSpellHitTime(game, spell, missile, pos):
	player = game.player
	if spell.flags & SFlag.Line:
		if missile.speed == 0:
			return max(0, spell.delay)
		spellPos = game.world_to_screen(missile.pos)
		return 1000 * spellPos.distance(pos) / missile.speed
	elif spell.flags & SFlag.Area:
		return max(0, spell.delay)
	
	return float("inf")

def CanHeroEvade(game, projection, missile, spell):
	heroPos = game.world_to_screen(game.player.pos)
	evadeTime = 0.0
	spellHitTime = 0.0
	speed = game.player.movement_speed
	delay = 0.0
	player = game.player
	if spell.flags & SFlag.Line:
		evadeTime = 1000 * (missile.cast_radius - heroPos.distance(game.world_to_screen(projection)) + player.gameplay_radius) / speed
		spellHitTime = GetSpellHitTime(game, spell, missile, game.world_to_screen(projection))
	elif spell.flags & SFlag.Area:
		evadeTime = 1000 * (missile.cast_radius - heroPos.distance(game.world_to_screen(projection))) / speed
		spellHitTime = GetSpellHitTime(game, spell, missile, game.world_to_screen(projection))
	return spellHitTime - missile.delay > evadeTime

def IsCollisioned(game, target):
	self = game.player

	for minion in game.minions:
		if minion.is_enemy_to(game.player) and minion.is_alive:
			if not game.is_point_on_screen(minion.pos):
				continue
			localWorldPos = game.world_to_screen(self.pos)
			targetWorldPos = game.world_to_screen(target.pos)
			minionWorldPos = game.world_to_screen(minion.pos)
			# print(game.point_on_line(targetWorldPos, localWorldPos, minionWorldPos, target.gameplay_radius * 2.0))
			if game.point_on_line(localWorldPos, targetWorldPos, minionWorldPos, minion.gameplay_radius * 2.0):
				return True
			else:
				return False
			
def isLeftOfLineSegment(pos, start, end):
	return (end.x - start.x) * (pos.y - start.y) - (end.y - start.y) * (pos.x - start.x) > 0

def getEvadePos(game, start_pos, end_pos, current, br, missile, spell):
	
	self = game.player

	player_dir = self.pos.sub(self.prev_pos).normalize()
	if math.isnan(player_dir.x):
		player_dir.x = 0.0
	if math.isnan(player_dir.y):
		player_dir.y = 0.0
	if math.isnan(player_dir.z):
		player_dir.z = 0.0

	direction = end_pos.sub(start_pos)
	
	pos3 = end_pos.add(Vec3(direction.z * -float(1.0), direction.y, direction.x * float(1.0)))
	pos4 = end_pos.add(Vec3(direction.z * float(1.0), direction.y, direction.x * -float(1.0)))
	
	direction2 = pos3.sub(pos4)
	direction2 = game.clamp2d(direction2, br)

	direction3 = Vec3(0, 0, 0)
	direction3.x = -direction2.x 
	direction3.y = -direction2.y
	direction3.z = -direction2.z

	if isLeftOfLineSegment(game.world_to_screen(current), game.world_to_screen(start_pos), game.world_to_screen(end_pos)):
		return current.add(direction3)
	else:
		return current.add(direction2)

# def getEvadePos(game, start_pos, end_pos, current, br, missile, spell):
	
# 	self = game.player

# 	player_dir = self.pos.sub(self.prev_pos).normalize()
# 	if math.isnan(player_dir.x):
# 		player_dir.x = 0.0
# 	if math.isnan(player_dir.y):
# 		player_dir.y = 0.0
# 	if math.isnan(player_dir.z):
# 		player_dir.z = 0.0

# 	original = game.getEvadePoints(game.world_to_screen(current), game.world_to_screen(start_pos), game.world_to_screen(end_pos))[1]

# 	distanceToEvadePoint = original.distance(game.world_to_screen(game.player.pos))

# 	if distanceToEvadePoint < 600 * 600:
# 		sideDistance = game.world_to_screen(start_pos).distance(game.world_to_screen(end_pos))
# 		direction = end_pos.sub(start_pos).normalize()
# 		s = 0
# 		if distanceToEvadePoint < 200 * 200 and sideDistance > 90 * 90:
# 			s = 5
# 			for j in s:
# 				candidate = original.add(direction.scale(j))
	
# 	# evPos = start_pos.add(direction.scale(start_pos.distance(end_pos)))

# 	return candidate