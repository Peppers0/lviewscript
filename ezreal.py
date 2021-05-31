from blitz import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import TargetingConfig
import json, time, math

blitz_script_info = {
    "script": "Ezreal",
	"author": "anonm",
	"description": "For Ezreal",
	"target_champ": "ezreal"
}

combo_key = 0
harass_key = 0
laneclear_key = 0
killsteal_key = 0

use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

steal_kill_with_q = False
steal_kill_with_e = False
steal_kill_with_r = False

lane_clear_with_q = False
lasthit_with_q = False

toggled = False

draw_q_range = False
draw_e_range = False
draw_r_range = False

q = { 'Range': 1150 }
w = { 'Range': 1150 }
e = { 'Range': 475 }
r = { 'Range': 25000 }

spell_priority = {
	'Q': 0,
    'W': 0,
	'E': 0,
	'R': 0
}

targeting = TargetingConfig() 

def blitz_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global targeting, spell_priority, combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q
    combo_key = cfg.get_int("combo_key", 0)	
    harass_key = cfg.get_int("harass_key", 0)
    laneclear_key = cfg.get_int("laneclear_key", 0)
    killsteal_key = cfg.get_int("killsteal_key", 0)

    use_q_in_combo   = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo   = cfg.get_bool("use_w_in_combo", True)
    use_r_in_combo   = cfg.get_bool("use_r_in_combo", True)

    draw_q_range   = cfg.get_bool("draw_q_range", False)
    draw_e_range   = cfg.get_bool("draw_e_range", False)
    draw_r_range   = cfg.get_bool("draw_r_range", False)

    steal_kill_with_q   = cfg.get_bool("steal_kill_with_q", False)
    steal_kill_with_e   = cfg.get_bool("steal_kill_with_e", False)
    steal_kill_with_r   = cfg.get_bool("steal_kill_with_r", False)

    lane_clear_with_q   = cfg.get_bool("lane_clear_with_q", False)
    lasthit_with_q   = cfg.get_bool("lasthit_with_q", False)

    spell_priority = json.loads(cfg.get_str('spell_priority', json.dumps(spell_priority)))
    targeting.load_from_cfg(cfg)
	
def blitz_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_r_range, draw_e_range
    global targeting, spell_priority, combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("killsteal_key", killsteal_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_bool("steal_kill_with_q", steal_kill_with_q)
    cfg.set_bool("steal_kill_with_e", steal_kill_with_e)
    cfg.set_bool("steal_kill_with_r", steal_kill_with_r)

    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)
    cfg.set_bool("lasthit_with_q", lasthit_with_q)

    cfg.set_str('spell_priority', json.dumps(spell_priority))
    targeting.save_to_cfg(cfg)
	
def blitz_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global targeting, spell_priority, combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q

    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    killsteal_key = ui.keyselect("Killsteal key", killsteal_key)

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        steal_kill_with_q = ui.checkbox("Steal kill with Q", steal_kill_with_q)
        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_w_in_combo)
        steal_kill_with_e = ui.checkbox("Steal kill with E", steal_kill_with_e)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        steal_kill_with_r = ui.checkbox("Steal kill with R", steal_kill_with_r)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lasthit_with_q = ui.checkbox("Lasthit with Q", lasthit_with_q)
        lane_clear_with_q = ui.checkbox("Laneclear with Q", lane_clear_with_q)
        ui.treepop()

    if ui.treenode("Utils"):
        for slot, key in spell_priority.items():
            spell_priority[slot] = ui.dragfloat(f'{slot}', 1.0, 2.0, 3.0, 4.0)
        ui.treepop()

    targeting.draw(ui)

def TargetSelection(target, dist, range):
    global q
    if dist <= range:
        return True
    return False

def QDamage(game, target):
    damage = 0
    if game.player.Q.level > 0:
        damage = 20 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level > 2:
        damage = 45 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level > 3:
        damage = 70 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level > 4:
        damage = 95 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level > 5:
        damage = 120 + (get_onhit_physical(game.player, target))
    return damage

def RDamage(game, target):
    damage = 0
    if game.player.R.level == 1:
        damage = 350 + (get_onhit_physical(game.player, target))
    elif game.player.R.level == 2:
        damage = 500 + (get_onhit_physical(game.player, target))
    elif game.player.R.level == 3:
        damage = 650 + (get_onhit_physical(game.player, target))
    return damage

def find_minion_target(game, min_range):
	target = None
	for minion in game.minions:
		if minion.is_enemy_to(game.player) and minion.is_alive and game.distance(game.player, minion) < min_range and game.is_point_on_screen(minion.pos):
			target = minion
		
	return target

def Combo(game):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_r_range, draw_e_range
    global targeting, combo_key, harass_key, laneclear_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q
    global q, w, e, r
    q_spell = getSkill(game, 'Q')
    w_spell = getSkill(game, 'W')
    e_spell = getSkill(game, 'E')
    r_spell = getSkill(game, 'R')
    before_cpos = game.get_cursor()
    if use_w_in_combo and IsReady(game, w_spell):
        target = targeting.get_target(game, w['Range'])
        if ValidTarget(target) and target:
            if game.player.pos.distance(target.pos) <= w['Range']:
                game.move_cursor(game.world_to_screen(castpoint_for_collision(game, w_spell, game.player, target)))
                game.press_right_click()
                w_spell.trigger(False)
                time.sleep(0.02)
                game.move_cursor(before_cpos)
    if use_q_in_combo and IsReady(game, q_spell):
        target = targeting.get_target(game, q['Range'])
        if ValidTarget(target) and target and not IsCollisioned(game, target):
            if game.player.pos.distance(target.pos) <= q['Range']:
                game.move_cursor(game.world_to_screen(castpoint_for_collision(game, q_spell, game.player, target)))
                game.press_right_click()
                q_spell.trigger(False)
                time.sleep(0.02)
                game.move_cursor(before_cpos)
    # if use_e_in_combo and IsReady(game, e_spell):
    #     target = targeting.get_target(game, e['Range'])
    #     if ValidTarget(target) and target and not IsCollisioned(game, target):
    #         if target.pos.distance(game.player.pos) <= e['Range']:
    #             game.move_cursor(game.world_to_screen(target.pos))
    #             game.press_right_click()
    #             e_spell.trigger(False)
    #             time.sleep(0.02)
    #             game.move_cursor(before_cpos)
    if use_r_in_combo and IsReady(game, r_spell):
        target = targeting.get_target(game, r['Range'])
        if ValidTarget(target) and target:
            if target.pos.distance(game.player.pos) <= r['Range']:
                if RDamage(game, target) >= target.health:
                    game.move_cursor(game.world_to_screen(castpoint_for_collision(game, r_spell, game.player, target)))
                    game.press_right_click()
                    r_spell.trigger(False)
                    time.sleep(0.02)
                    game.move_cursor(before_cpos)

def LaneClear(game):
    q_spell = getSkill(game, 'Q')
    before_cpos = game.get_cursor()
    num = 10000
    if q_spell and IsReady(game, q_spell):
        enemyMinion = find_minion_target(game, game.player.atkRange)
        if enemyMinion and is_last_hitable(game, game.player, enemyMinion):
            game.move_cursor(game.world_to_screen(enemyMinion.pos))
            game.press_right_click()
            q_spell.trigger(False)
            time.sleep(0.02)
            return game.move_cursor(before_cpos)
        elif enemyMinion and enemyMinion.health < num:
            num = enemyMinion.health
            game.move_cursor(game.world_to_screen(enemyMinion.pos))
            game.press_right_click()
            q_spell.trigger(False)
            time.sleep(0.02)
            return game.move_cursor(before_cpos)
        else:
            game.move_cursor(game.world_to_screen(enemyMinion.pos))
            game.press_right_click()
            time.sleep(0.02)
            return game.move_cursor(before_cpos)
            

def killStealQ(game):
    q_spell = getSkill(game, 'Q')
    target = targeting.get_target(game, q['Range'])
    before_cpos = game.get_cursor()
    if ValidTarget(target) and target and not IsCollisioned(game, target) and IsReady(game, q_spell):
        if game.player.pos.distance(target.pos) <= q['Range']:
            delay = q_spell.delay + game.player.pos.distance(target.pos) / 3000
            if (QDamage(game, target) >= target.health + delay / 2):
                game.move_cursor(game.world_to_screen(castpoint_for_collision(game, q_spell, game.player, target)))
                game.press_right_click()
                q_spell.trigger(False)
                time.sleep(0.02)
                game.move_cursor(before_cpos)

def killStealE(game):
    e_spell = getSkill(game, 'E')
    target = targeting.get_target(game, e['Range'])
    before_cpos = game.get_cursor()
    if ValidTarget(target) and target and not IsCollisioned(game, target) and IsReady(game, e_spell):
        if game.player.pos.distance(target.pos) <= e['Range']:
            if is_last_hitable(game, game.player, target):
                game.move_cursor(game.world_to_screen(castpoint_for_collision(game, e_spell, game.player, target)))
                game.press_right_click()
                e_spell.trigger(False)
                time.sleep(0.02)
                game.move_cursor(before_cpos)

def killStealR(game):
    q_spell = getSkill(game, 'Q')
    r_spell = getSkill(game, 'R')
    target = targeting.get_target(game, r['Range'])
    before_cpos = game.get_cursor()
    if ValidTarget(target) and target and IsReady(game, r_spell):
        if game.player.pos.distance(target.pos) <= r['Range']:
            delay = r_spell.delay + game.player.pos.distance(target.pos) / 3000
            if (RDamage(game, target) >= target.health):
                game.move_cursor(game.world_to_screen(castpoint_for_collision(game, r_spell, game.player, target)))
                game.press_right_click()
                r_spell.trigger(False)
                time.sleep(0.02)
                game.move_cursor(before_cpos)

def Harass(game):
    target = targeting.get_target(game, q['Range'])
    w_spell = getSkill(game, 'W')
    q_spell = getSkill(game, 'Q')
    before_cpos = game.get_cursor()
    if ValidTarget(target) and target and target.is_enemy_to(game.player) and game.is_point_on_screen(target.pos) and IsReady(game, w_spell):
        if game.player.pos.distance(target.pos) <= w['Range']:
            game.move_cursor(game.world_to_screen(target.pos))
            game.press_right_click()
            w_spell.trigger(False)
            time.sleep(0.02)
            game.move_cursor(before_cpos)
            game.press_right_click()
    if ValidTarget(target) and target and target.is_enemy_to(game.player) and game.is_point_on_screen(target.pos) and IsReady(game, q_spell) and not IsCollisioned(game, target):
        if game.player.pos.distance(target.pos) <= q['Range']:
            game.move_cursor(game.world_to_screen(target.pos))
            game.press_right_click()
            q_spell.trigger(False)
            time.sleep(0.02)
            game.move_cursor(before_cpos)
            game.press_right_click()
            
def blitz_update(game, ui):
    global use_q_in_combo, use_w_in_combo, use_w_in_combo, use_r_in_combo
    global draw_q_range, draw_r_range, draw_e_range
    global q, e, r
    global targeting, combo_key, laneclear_key, harass_key, laneclear_key
    self = game.player

    if draw_q_range:
        game.draw_circle_world(game.player.pos, q["Range"], 100, 5, Color.RED)
        game.draw_circle_world(game.player.pos, w["Range"], 100, 5, Color.RED)
    if draw_e_range:
        game.draw_circle_world(game.player.pos, e["Range"], 100, 5, Color.RED)
    if draw_r_range:
        game.draw_circle_world(game.player.pos, r["Range"], 100, 5, Color.RED)

    if self.is_alive and self.is_visible:
        if game.was_key_pressed(combo_key):
            Combo(game)
        if game.was_key_pressed(laneclear_key):
            LaneClear(game)
        if game.was_key_pressed(harass_key):
            Harass(game)
        if game.was_key_pressed(killsteal_key):
            if steal_kill_with_q:
                killStealQ(game)
            if steal_kill_with_e:
                killStealQ(game)
            if steal_kill_with_r:
                killStealQ(game)