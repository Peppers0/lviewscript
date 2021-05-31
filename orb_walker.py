from blitz import *
from evade import checkEvade
from commons import skills
from commons.items import *
from commons.skills import *
from commons.utils import *
import time, json, random

blitz_script_info = {
	"script": "Orbwalker",
	"author": "leblebi",
	"description": "Automatically kites enemies. Also has last hit built in"
}

champ_ids = []
tracks = {}
tracked_champ_id = 0

last_attacked = 0
last_moved = 0

lasthit_key = 0
key_orbwalk = 0
laneclear_key = 0
attack_move_key = 0

draw_killable_minion = False
draw_killable_minion_fade = False

max_atk_speed = 0

cast_keys = {
	'Q': False,
	'W': False,
	'E': False,
	'R': False
}

def blitz_load_cfg(cfg):
	global lasthit_key, key_orbwalk, max_atk_speed, laneclear_key, cast_keys, draw_killable_minion, draw_killable_minion_fade, attack_move_key
	global targeting
	
	lasthit_key 	= cfg.get_int("lasthit_key", 0)
	attack_move_key 	= cfg.get_int("attack_move_key", 0)	
	key_orbwalk     = cfg.get_int("key_orbwalk", 0)	
	laneclear_key   = cfg.get_int("laneclear_key", 0)
	draw_killable_minion   = cfg.get_bool("draw_killable_minion", False)
	draw_killable_minion_fade   = cfg.get_bool("draw_killable_minion_fade", False)
	max_atk_speed   = cfg.get_float("max_atk_speed", 1.5)
	cast_keys       = json.loads(cfg.get_str('cast_keys', json.dumps(cast_keys)))
	
def blitz_save_cfg(cfg):
	global lasthit_key, key_orbwalk, max_atk_speed, laneclear_key, cast_keys, draw_killable_minion, draw_killable_minion_fade, attack_move_key
	global targeting
		
	cfg.set_int("lasthit_key", lasthit_key)
	cfg.set_int("attack_move_key", attack_move_key)
	cfg.set_int("laneclear_key", laneclear_key)
	cfg.set_int("key_orbwalk", key_orbwalk)
	cfg.set_bool("draw_killable_minion", draw_killable_minion)
	cfg.set_bool("draw_killable_minion_fade", draw_killable_minion_fade)
	cfg.set_float("max_atk_speed", max_atk_speed)
	cfg.set_str("cast_keys", json.dumps(cast_keys))
	
def blitz_draw_settings(game, ui):
	global lasthit_key, key_orbwalk, max_atk_speed, laneclear_key, cast_keys, draw_killable_minion, draw_killable_minion_fade, attack_move_key
	global targeting
	
	champ_name = game.player.name
	max_atk_speed   = ui.sliderfloat("Max attack speed", max_atk_speed, 0.5, 3.0)
	lasthit_key 	= ui.keyselect("Last hit key", lasthit_key)
	attack_move_key 	= ui.keyselect("Attack move key", attack_move_key)
	draw_killable_minion 	= ui.checkbox("Draw killable minions", draw_killable_minion)
	draw_killable_minion_fade 	= ui.checkbox("Draw killable minions fade effect", draw_killable_minion_fade)
	laneclear_key		= ui.keyselect("Laneclear key", laneclear_key)
	key_orbwalk     = ui.keyselect("Orbwalk activate key", key_orbwalk)
	for slot, key in cast_keys.items():
		cast_keys[slot] = ui.checkbox(f'Use {slot}', key)
	
def GetBestTargetsInRange(game, atk_range = 0):
	num = 9999999999
	if atk_range == 0:
		atk_range = game.player.atkRange
	for champ in game.champs:
		if champ and champ.is_visible and champ.is_enemy_to(game.player) and champ.isTargetable and champ.is_alive and game.distance(game.player, champ) <= atk_range and game.is_point_on_screen(champ.pos):
			if is_last_hitable(game, game.player, champ):
				return champ
			elif champ.health <= num:
				num = champ.health
				return champ
			elif champ.health >= num and not is_last_hitable(game, game.player, champ):
				return champ

def GetBestMinionsInRange(game, atk_range = 0):
	num = 9999999999
	if atk_range == 0:
		atk_range = game.player.atkRange
	for minion in game.minions:
		if minion and minion.is_visible and minion.is_enemy_to(game.player) and minion.isTargetable and minion.is_alive and game.distance(game.player, minion) <= atk_range and game.is_point_on_screen(minion.pos):
			if is_last_hitable(game, game.player, minion):
				num = minion.health
				return minion
			elif minion.health <= num:
				num = minion.health
				return minion
			elif minion.health >= num and not is_last_hitable(game, game.player, minion):
				return minion

def drawKillableMinions(game, fade_effect):
	minion = GetBestMinionsInRange(game)
	if minion:
		if fade_effect:
			percentHealth = (minion.health / minion.max_health) * 100
			value = 255 - (minion.health * 2)
			game.draw_circle_world(minion.pos, minion.gameplay_radius * 2, 100, 1, Color(0.0, 1.0, value, 1.0))
		if not fade_effect:
			game.draw_circle_world(minion.pos, minion.gameplay_radius * 2, 100, 2, Color.ORANGE)

# def harass(game):
# 	global cast_keys
# 	old_cpos = game.get_cusor()
# 	for slot, key in cast_keys.items():
# 		skill = getSkill(game, slot)
# 		if skill and IsReady(game, skill):
# 			target = GetBestTargetsInRange(game, skill.cast_range)
# 			if not IsCollisioned(game, target):
# 				game.move_cursor(game.world_to_screen(target.pos))
# 				skill.trigger(False)
# 				time.sleep(0.02)
# 				game.move_cursor(old_cpos)

def blitz_update(game, ui):
	global last_attacked, last_moved, max_atk_speed
	global lasthit_key, key_orbwalk, laneclear_key, attack_move_key
	global cast_keys
	global champ_ids, tracks, tracked_champ_id
	global checkEvade, draw_killable_minion, draw_killable_minion_fade

	if draw_killable_minion_fade:
		drawKillableMinions(game, True)
	elif draw_killable_minion:
		drawKillableMinions(game, False)

	self = game.player

	if self.is_alive and self.is_visible and game.is_point_on_screen(self.pos):
		self = game.player

		atk_speed = self.base_atk_speed * self.atk_speed_multi
		b_windup_time = (1.0/self.base_atk_speed) * game.player.basic_atk_windup
		c_atk_time = 1.0/atk_speed
		max_atk_time = 1.0/max_atk_speed

		color = Color.ORANGE
		color.a = 0.5

		target = GetBestTargetsInRange(game)

		t = game.time

		if not checkEvade():
			if game.is_key_down(key_orbwalk):
				if target:
					game.draw_circle_world(target.pos, target.gameplay_radius * 1, 100, 2, Color.ORANGE)
				if t - last_attacked >= c_atk_time and target:
					old_cpos = game.get_cursor()
					last_attacked = t
					game.move_cursor(game.world_to_screen(target.pos))
					game.press_right_click()
					time.sleep(0.02)
					game.move_cursor(old_cpos)
				else:
					dt = t - last_attacked
					if dt > b_windup_time and t - last_moved > 0.10:
						last_moved = t
						game.press_right_click()
			if game.is_key_down(lasthit_key):
				target = GetBestMinionsInRange(game, True)
				if t - last_attacked >= c_atk_time and target:
					old_cpos = game.get_cursor()
					last_attacked = t
					game.move_cursor(game.world_to_screen(target.pos))
					game.press_right_click()
					time.sleep(0.02)
					game.move_cursor(old_cpos)
				else:
					dt = t - last_attacked
					if dt > b_windup_time and t - last_moved > 0.10:
						last_moved = t
						game.press_right_click()
			if game.is_key_down(laneclear_key):
				target = GetBestMinionsInRange(game)
				if t - last_attacked >= c_atk_time and target:
					old_cpos = game.get_cursor()
					last_attacked = t
					game.move_cursor(game.world_to_screen(target.pos))
					game.press_right_click()
					time.sleep(0.02)
					game.move_cursor(old_cpos)
				else:
					dt = t - last_attacked
					if dt > b_windup_time and t - last_moved > 0.10:
						last_moved = t
						game.press_right_click()

