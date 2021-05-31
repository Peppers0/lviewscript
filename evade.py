from blitz import *
from commons.targeting import TargetingConfig
from commons.utils import *
import json, time
import itertools, math
from commons.skills import *
from copy import copy
from math import *
from champions import index

blitz_script_info = {
	"script": "Evade",
	"author": "https://github.com/bckd00r / bckd00r",
	"description": "Evade module with blitzLoL"
}

fast_evade = False
draw_evade_line = False
evade_with_flash = False

is_evading = False

extra_bounding_radius = 0

evades = False
targeting = TargetingConfig()

cast_keys = {
	'Q': False,
	'W': False,
	'E': False,
	'R': False
}

def blitz_load_cfg(cfg):
	global evades, fast_evade, draw_evade_line, cast_keys, evade_with_flash, extra_bounding_radius
	evades          = cfg.get_bool("evades", False)
	evade_with_flash = cfg.get_bool("evade_with_flash", False)
	fast_evade 	    = cfg.get_bool("fast_evade", False)
	draw_evade_line = cfg.get_bool("draw_evade_line", False)
	extra_bounding_radius   = cfg.get_float("extra_bounding_radius", 0)
	cast_keys       = json.loads(cfg.get_str('cast_keys', json.dumps(cast_keys)))
	
def blitz_save_cfg(cfg):
	global evades, fast_evade, draw_evade_line, cast_keys, evade_with_flash, extra_bounding_radius
	cfg.set_bool("evades",          evades)
	cfg.set_bool("evade_with_flash",          evade_with_flash)
	cfg.set_bool("fast_evade", 		   	fast_evade)
	cfg.set_bool("draw_evade_line", draw_evade_line)
	cfg.set_float("extra_bounding_radius", extra_bounding_radius)
	cfg.set_str('cast_keys', json.dumps(cast_keys))
	
def blitz_draw_settings(game, ui):
	global evades, fast_evade, draw_evade_line, cast_keys, evade_with_flash, extra_bounding_radius
	ui.separator()
	ui.text("SkillStealer BY (BCKD00R)")
	evades            = ui.checkbox("Evade skills", evades)
	fast_evade        = ui.checkbox("Fast evade", fast_evade)
	evade_with_flash  = ui.checkbox("Evade with flash", evade_with_flash)
	draw_evade_line   = ui.checkbox("Draw line", draw_evade_line)
	extra_bounding_radius   = ui.sliderfloat("Extra bounding radius", extra_bounding_radius, 0, 500.0)
	for slot, key in cast_keys.items():
		cast_keys[slot] = ui.checkbox(f'Use with evade {slot}', key)
			
def GetDistanceSqr(p1, p2):
    p2 = p2
    d = p1.sub(p2)
    d.y = (p1.y) - (p2.y)
    return d.x * d.x + d.y * d.y

def GetDistance(p1, p2):
    squaredDistance = GetDistanceSqr(p1, p2)
    return sqrt(squaredDistance)

def evade(game, evade_pos):
	global is_evading
	is_evading = True
	before_cpos = game.get_cursor()
	game.move_cursor(evade_pos)
	game.press_right_click()
	time.sleep(0.02)
	game.move_cursor(before_cpos)
	is_evading = False

def evadeWithAbility(game, pos):
	global is_evading
	is_evading = True
	spell = getSkill(SummonerSpellType.Flash)
	if spell and IsReady(game, spell):
		game.move_cursor(evade_pos)
		game.press_right_click()
		spell.trigger()
		time.sleep(0.02)
		game.move_cursor(before_cpos)
	is_evading = False

def checkEvade():
	global is_evading
	return is_evading

def evade_skills(game, player):
	global targeting, evades, fast_evade, draw_evade_line, cast_keys, extra_bounding_radius
	player_pos = game.world_to_screen(game.player.pos)
	for missile in game.missiles:
		if not player.is_alive or missile.is_ally_to(player):
			continue
		if not is_skillshot(missile.name):
			continue
		spell = get_missile_parent_spell(missile.name)
		if not spell:
			continue
		end_pos = missile.end_pos.clone()
		start_pos = missile.start_pos.clone()
		curr_pos = missile.pos.clone()
		br = player.gameplay_radius + extra_bounding_radius
		canEvade = CanHeroEvade(game, curr_pos, missile, spell)
		if game.point_on_line(game.world_to_screen(curr_pos), game.world_to_screen(end_pos), game.world_to_screen(player.pos), br * 2):
			if game.point_on_line(game.world_to_screen(start_pos), game.world_to_screen(end_pos), game.world_to_screen(player.pos), br * 1):
				if canEvade:
					if spell.flags & SFlag.Line:
						pos = getEvadePos(game, start_pos, end_pos, player.pos, br * 2, missile, spell)
					elif spell.flags & SFlag.Area:
						r = game.get_spell_info(spell.name)
						pos = getEvadePos(game, start_pos, end_pos, player.pos, br * 2, missile, spell)
					else:
						pos = getEvadePos(game, start_pos, end_pos, player.pos, br * 2, missile, spell)
					if draw_evade_line:
						game.draw_line(game.world_to_screen(pos), game.world_to_screen(player.pos), 2, Color.ORANGE)
					if player.pos.distance(pos) < 600 * 600:
						evade(game, game.world_to_screen(pos))
						is_evading = True
					else:
						if spell.danger > 3 and evade_with_flash:
							evadeWithAbility(game, pos)
						is_evading = False

				
def blitz_update(game, ui):
	global evades
	
	player = game.player

	if game.player.is_alive and game.player.is_visible and game.is_point_on_screen(game.player.pos):
		if evades:
			evade_skills(game, player)
					
				