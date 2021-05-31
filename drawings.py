from blitz import *
from time import time
from commons.skills import *
from commons.items import *
import itertools, math
from copy import copy
import array

blitz_script_info = {
	"script": "Drawings",
	"author": "leryss",
	"description": "Draws indicators for different things"
}

turret_ranges   = False
enemy_ranges = False
attack_range    = False
minion_last_hit = False
draw_spell_range = False

skillshots            = False
skillshots_predict    = False
skillshots_min_range  = 0
skillshots_max_speed  = 0
skillshots_show_ally  = False
skillshots_show_enemy = False

cast_keys = {
	'Q': 0,
	'W': 0,
	'E': 0,
	'R': 0
}

def blitz_load_cfg(cfg):
	global turret_ranges, enemy_ranges, attack_range, draw_spell_range
	global skillshots, skillshots_predict, skillshots_min_range, minion_last_hit, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
	turret_ranges        = cfg.get_bool("turret_ranges", True)
	enemy_ranges      = cfg.get_bool("enemy_ranges", True)
	minion_last_hit      = cfg.get_bool("minion_last_hit", True)
	draw_spell_range         = cfg.get_bool("draw_spell_range", True)
	attack_range         = cfg.get_bool("attack_range", True)
	                     
	skillshots            = cfg.get_bool("skillshots", True)
	skillshots_show_ally  = cfg.get_bool("skillshots_show_ally", True)
	skillshots_show_enemy = cfg.get_bool("skillshots_show_enemy", True)
	skillshots_predict   = cfg.get_bool("skillshots_predict", True)
	skillshots_min_range  = cfg.get_float("skillshots_min_range", 500)
	skillshots_max_speed  = cfg.get_float("skillshots_max_speed", 2500)
	
def blitz_save_cfg(cfg):
	global turret_ranges, enemy_ranges, attack_range, draw_spell_range
	global skillshots, skillshots_predict, skillshots_min_range, minion_last_hit, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
	cfg.set_bool("turret_ranges",         turret_ranges)
	cfg.set_bool("enemy_ranges",       enemy_ranges)
	cfg.set_bool("minion_last_hit",       minion_last_hit)
	cfg.set_bool("draw_spell_range",          draw_spell_range)
	cfg.set_bool("attack_range",          attack_range)
	
	cfg.set_bool("skillshots",            skillshots)
	cfg.set_bool("skillshots_show_ally",  skillshots_show_ally)
	cfg.set_bool("skillshots_show_enemy", skillshots_show_enemy)
	cfg.set_bool("skillshots_predict",    skillshots_predict)
	cfg.set_float("skillshots_min_range", skillshots_min_range)
	cfg.set_float("skillshots_max_speed", skillshots_max_speed)
	
def blitz_draw_settings(game, ui):
	global turret_ranges, enemy_ranges, attack_range, minion_last_hit, draw_spell_range
	global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
	turret_ranges   = ui.checkbox("Turret ranges", turret_ranges)
	enemy_ranges = ui.checkbox("Draw enemy ranges", enemy_ranges)
	minion_last_hit = ui.checkbox("Minion last hit", minion_last_hit)
	draw_spell_range    = ui.checkbox("Champion spell range", draw_spell_range)
	attack_range    = ui.checkbox("Champion attack range", attack_range)
	
	ui.separator()
	ui.text("Skillshots (Experimental)")
	skillshots            = ui.checkbox("Draw skillshots", skillshots)
	skillshots_show_ally  = ui.checkbox("Show for allies", skillshots_show_ally)
	skillshots_show_enemy = ui.checkbox("Show for enemies", skillshots_show_enemy)
	skillshots_predict   = ui.checkbox("Show prediction", skillshots_predict)
	skillshots_min_range  = ui.dragfloat("Minimum skillshot range", skillshots_min_range, 100, 0, 3000)
	skillshots_max_speed  = ui.dragfloat("Maximum skillshot speed", skillshots_max_speed, 100, 1000, 5000)
	
	draw_prediction_info(game, ui)

def draw_rect(game, start_pos, end_pos, radius, color):
	
	dir = Vec3(end_pos.x - start_pos.x, 0, end_pos.z - start_pos.z).normalize()
				
	left_dir = Vec3(dir.x, dir.y, dir.z).rotate_y(90).scale(radius)
	right_dir = Vec3(dir.x, dir.y, dir.z).rotate_y(-90).scale(radius)
	
	p1 = Vec3(start_pos.x + left_dir.x,  start_pos.y + left_dir.y,  start_pos.z + left_dir.z)
	p2 = Vec3(end_pos.x + left_dir.x,    end_pos.y + left_dir.y,    end_pos.z + left_dir.z)
	p3 = Vec3(end_pos.x + right_dir.x,   end_pos.y + right_dir.y,   end_pos.z + right_dir.z)
	p4 = Vec3(start_pos.x + right_dir.x, start_pos.y + right_dir.y, start_pos.z + right_dir.z)
	
	color.a = 0.2
	# game.draw_triangle_world_filled(p1, p2, p3, color)
	# game.draw_triangle_world_filled(p1, p3, p4, color)
	game.draw_rect_world(p1, p2, p3, p4, 1, color)

def draw_atk_range(game, player):
	color = Color.CYAN
	color.a = 0.1
	if player.is_alive and player.is_visible and game.is_point_on_screen(player.pos):	
		game.draw_circle_world_filled(player.pos, player.atkRange + player.gameplay_radius, 50, color)
		color = Color.WHITE
		color.a = 5.0
		game.draw_circle_world(player.pos, player.atkRange + player.gameplay_radius, 100, 5, color)

def draw_spell_ranges(game, player):
	global cast_keys
	ColorRed = Color.RED
	ColorRed.a = 0.1
	ColorWhite = Color.WHITE
	ColorWhite.a = 0.1
	if player.is_alive and player.is_visible and game.is_point_on_screen(player.pos):
		for slot, key in cast_keys.items():
			skill = getattr(game.player, slot)
			for champ in game.champs:
				range = champ.base_atk_range + champ.gameplay_radius
				dist = champ.pos.distance(player.pos) - range
				if dist <= player.gameplay_radius:
					if skill.cast_range > 0 and not skill.cast_range > 2500:
						game.draw_circle_world(player.pos, skill.cast_range, 100, 5, ColorRed)
				else:
					if skill.cast_range > 0 and not skill.cast_range > 2500:
						game.draw_circle_world(player.pos, skill.cast_range, 100, 5, ColorWhite)

def draw_recall_states(game, player):
	p = game.world_to_screen(player.pos)
	p.y += 130
	p.x -= 23
	for champ in game.champs:
		if champ.is_alive and champ.is_visible:
			if champ.recallState > 0:
				p.y += 15
				game.draw_line(p, p.add(Vec2(150, 0)), 15, Color.WHITE)
				game.draw_text(p.add(Vec2(55, -6)), str(champ.name).capitalize(), Color.BLUE)

def draw_turret_ranges(game, player):
	color = Color.ORANGE
	for turret in game.turrets:
		if turret.is_alive and turret.is_enemy_to(player) and game.is_point_on_screen(turret.pos):
			range = turret.atk_range + 30
			dist = turret.pos.distance(player.pos) - range
			if dist <= player.gameplay_radius:
				color.a = 0.08
				game.draw_circle_world_filled(turret.pos, range, 100, color)
				color.a = 0.2
				game.draw_circle_world(turret.pos, range, 100, 5, color)
			else:
				color.a = 0.08 
				game.draw_circle_world_filled(turret.pos, range, 100, color)
				color.a = 0.2
				game.draw_circle_world(turret.pos, range, 100, 5, color)

def draw_minion_last_hit(game, player):
	color = Color.WHITE
	for minion in game.minions:
		if minion.is_visible and minion.is_alive and minion.is_enemy_to(player) and game.is_point_on_screen(minion.pos):
			if is_last_hitable(game, player, minion):
				p = game.hp_bar_pos(minion)
				color.a = 5.0
				game.draw_rect(Vec4(p.x - 34, p.y - 9, p.x + 32, p.y + 1), color, 0, 2)
		
def draw_champ_ranges(game, player):
	ColorRed = Color.RED
	ColorRed.a = 0.1
	ColorGreen = Color.GREEN
	ColorGreen.a = 0.1
	for champ in game.champs:
		if champ.is_alive and champ.is_visible and champ.is_enemy_to(player) and game.is_point_on_screen(champ.pos) and champ.movement_speed > 0:
			range = champ.base_atk_range + champ.gameplay_radius
			dist = champ.pos.distance(player.pos) - range
			if dist <= player.gameplay_radius:
				game.draw_circle_world_filled(champ.pos, champ.base_atk_range + champ.gameplay_radius, 100, ColorRed)
				game.draw_circle_world(champ.pos, champ.base_atk_range + champ.gameplay_radius, 100, 3, ColorGreen)
			else:
				game.draw_circle_world_filled(champ.pos, champ.base_atk_range + champ.gameplay_radius, 100, ColorGreen)
				ColorRed.a = 0.5
				game.draw_circle_world(champ.pos, champ.base_atk_range + champ.gameplay_radius, 100, 3, ColorRed)

def draw_predictions(game, player):
	color = Color.ORANGE
	for champ in game.champs:
		if champ.is_alive and champ.is_visible and champ.is_enemy_to(player) and game.is_point_on_screen(champ.pos):
			pos = game.hp_bar_pos(champ)
			pos.x += 57
			pos.y -= 52
			percent = (champ.health / champ.max_health) % get_onhit_physical(game.player, champ) * 100
			for i in range(int(percent)):
				offset = i*1
				game.draw_rect_filled(Vec4(pos.x - offset - 5, pos.y + 24, pos.x - offset, pos.y + 26), Color.YELLOW)
			# xPos = p.x + 164
			# yPos = p.y + 122.5

			# damage = champ.health - player.base_atk + player.bonus_atk
			# x1 = xPos + ((champ.health / champ.max_health) * 102)
			# x2 = xPos + (((damage > 0 and damage or 0) / champ.max_health) * 102)
			# game.draw_rect_filled(Vec4(p.x - 50 + 10 + ((champ.health / champ.max_health) * 100), p.y - 25, p.x + 10 - 50 + (((damage > 0 and damage or 0) / champ.max_health) * 100), p.y - 12), color, 1)
			return False

def pos_calculator(game, player):
	ColorRed = Color.RED
	ColorRed.a = 0.3
	ColorGreen = Color.GREEN
	ColorGreen.a = 0.3
	for champ in game.champs:
		if champ.is_alive and champ.is_visible and champ.is_enemy_to(player) and game.is_point_on_screen(champ.pos) and champ.movement_speed > 0:
			champ_dir = champ.pos.sub(champ.prev_pos).normalize()
			if math.isnan(champ_dir.x):
				champ_dir.x = 0.0
			if math.isnan(champ_dir.y):
				champ_dir.y = 0.0
			if math.isnan(champ_dir.z):
				champ_dir.z = 0.
			champ_future_pos = champ.pos.add(champ_dir.scale(champ.movement_speed))
			t = champ.pos.distance(champ_future_pos) / champ_future_pos.distance(champ_dir.scale(champ.movement_speed)) * 1000
			if t < 1:
				continue
			pos = game.world_to_screen(champ.pos.sub(champ_future_pos).normalize().add(champ_future_pos))
			game.draw_line(game.world_to_screen(champ.pos), pos, 2, ColorGreen)
			game.draw_circle_world(champ_future_pos.add(champ_dir.scale(t)), 50, 100, 2, ColorGreen)
			game.draw_text(game.world_to_screen(champ_future_pos.add(champ_dir.scale(t))), str(int(t)), ColorRed)

def draw_skillshots(game, player):
	global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
	
	color = Color.WHITE
	for missile in game.missiles:
		if not skillshots_show_ally and missile.is_ally_to(game.player):
			continue
		if not skillshots_show_enemy and missile.is_enemy_to(game.player):
			continue
		
		if not is_skillshot(missile.name) or missile.speed > skillshots_max_speed or missile.start_pos.distance(missile.end_pos) < skillshots_min_range:
			continue

		spell = get_missile_parent_spell(missile.name)
		if not spell:
			continue
		
		end_pos = missile.end_pos.clone()
		start_pos = missile.start_pos.clone()
		curr_pos = missile.pos.clone()
		impact_pos = None
		
		start_pos.y = game.map.height_at(start_pos.x, start_pos.z) + missile.height
		end_pos.y = start_pos.y
		curr_pos.y = start_pos.y
		

		if spell.flags & SFlag.Line:
			draw_rect(game, curr_pos, end_pos, missile.width, color)
			game.draw_circle_world_filled(curr_pos, missile.width, 20, Color.CYAN)
		
		elif spell.flags & SFlag.Area:
			r = game.get_spell_info(spell.name)
			end_pos.y = game.map.height_at(end_pos.x, end_pos.z)
			percent_done = missile.start_pos.distance(curr_pos)/missile.start_pos.distance(end_pos)
			color = Color(1, 1.0 - percent_done, 0, 0.5)
			
			game.draw_circle_world(end_pos, r.cast_radius, 40, 3, color)
			game.draw_circle_world_filled(end_pos, r.cast_radius*percent_done, 40, color)
		else:
			draw_rect(game, curr_pos, end_pos, missile.width, color)
def blitz_update(game, ui):
	global turret_ranges, attack_range, skillshots, minion_last_hit, draw_spell_range, skillshots_predict
	
	player = game.player

	pos_calculator(game, player)
	draw_recall_states(game, player)

	if skillshots_predict:
		draw_predictions(game, player)

	if attack_range:
		draw_atk_range(game, player)
		
	if draw_spell_range:
		draw_spell_ranges(game, player)

	if turret_ranges:
		draw_turret_ranges(game, player)
					
	if enemy_ranges:
		draw_champ_ranges(game, player)
		
	if minion_last_hit:
		draw_minion_last_hit(game, player)

	if skillshots:
		draw_skillshots(game, player)