from blitz import *
from commons.targeting import TargetingConfig
from commons.skills import *
from evade import checkEvade
import json, time
from pprint import pprint

blitz_script_info = {
	"script": "Auto Spell",
	"author": "leryss",
	"description": "Automatically casts spells on targets. Skillshots are cast using movement speed prediction. Works great for MOST skills but fails miserably for a few (for example yuumis Q)",
}

cast_keys = {
	'Q': 0,
	'W': 0,
	'E': 0,
	'R': 0
}

last_attacked = 0

def blitz_load_cfg(cfg):
	global cast_keys
	cast_keys = json.loads(cfg.get_str('cast_keys', json.dumps(cast_keys)))
	
def blitz_save_cfg(cfg):
	global cast_keys
	cfg.set_str('cast_keys', json.dumps(cast_keys))

def blitz_draw_settings(game, ui):
	global cast_keys
	for slot, key in cast_keys.items():
		cast_keys[slot] = ui.keyselect(f'Key to cast {slot}', key)
	draw_prediction_info(game, ui)
	
def GetBestTargetsInRange(game, atk_range = 0):
	num = 10000
	if atk_range == 0:
		atk_range = game.player.atkRange
	for champ in game.champs:
		if champ and champ.is_visible and champ.is_enemy_to(game.player) and champ.isTargetable and champ.is_alive and game.distance(game.player, champ) <= atk_range:
			if is_last_hitable(game, game.player, champ):
				return champ
			elif champ.health <= num:
				num = champ.health
				return champ
			elif champ.health >= num and not is_last_hitable(game, game.player, champ):
				return champ

def blitz_update(game, ui):
	global cast_keys, last_attacked
	global checkEvade
	
	if game.player.is_alive:
		for slot, key in cast_keys.items():
			if game.was_key_pressed(key):
				skill = getattr(game.player, slot)
				b_is_skillshot = is_skillshot(skill.name)
				# print(float(get_range(game, skill.name, slot)))
				skill_range = get_skillshot_range(game, skill.name, slot) if b_is_skillshot else float(get_range(game, skill.name, slot))
				target = GetBestTargetsInRange(game, skill_range)
				if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
					if target and not checkEvade():
							if b_is_skillshot:
								cast_point = castpoint_for_collision(game, skill, game.player, target)
							else:
								cast_point = target.pos
							if cast_point:
								cast_point = game.world_to_screen(cast_point)
								if not IsCollisioned(game, target):
									old_cpos = game.get_cursor()
									game.move_cursor(cast_point)
									skill.trigger(False)
									time.sleep(0.02)
									game.move_cursor(old_cpos)