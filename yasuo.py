from blitz import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import TargetingConfig
import json, time, math

blitz_script_info = {
    "script": "Yasuo",
	"author": "anonm",
	"description": "For Yasuo",
	"target_champ": "yasuo"
}

combo_key = 0
harass_key = 0
laneclear_key = 0

use_q_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

use_q_tornado_in_laneclear = False

toggled = False

draw_q_range = False
draw_e_range = False
draw_r_range = False

q = { 'Range': 400 }
w = { 'Range': 1000 }
e = { 'Range': 475 }
r = { 'Range': 1800 }

spell_priority = {
	'Q': 0,
	'E': 0,
	'R': 0
}

targeting = TargetingConfig() 

def blitz_load_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global targeting, spell_priority, combo_key, harass_key, laneclear_key
    global use_q_tornado_in_laneclear
    combo_key = cfg.get_int("combo_key", 0)	
    harass_key = cfg.get_int("harras_key", 0)
    laneclear_key = cfg.get_int("laneclear_key", 0)

    use_q_in_combo   = cfg.get_bool("use_q_in_combo", True)
    use_e_in_combo   = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo   = cfg.get_bool("use_r_in_combo", True)

    use_q_tornado_in_laneclear   = cfg.get_bool("use_q_tornado_in_laneclear", False)

    draw_q_range   = cfg.get_bool("draw_q_range", False)
    draw_e_range   = cfg.get_bool("draw_e_range", False)
    draw_r_range   = cfg.get_bool("draw_r_range", False)

    spell_priority = json.loads(cfg.get_str('spell_priority', json.dumps(spell_priority)))
    targeting.load_from_cfg(cfg)
	
def blitz_save_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_r_range, draw_e_range
    global targeting, spell_priority, combo_key, harass_key, laneclear_key
    global use_q_tornado_in_laneclear
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("use_q_tornado_in_laneclear", use_q_tornado_in_laneclear)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_str('spell_priority', json.dumps(spell_priority))
    targeting.save_to_cfg(cfg)
	
def blitz_draw_settings(game, ui):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global targeting, spell_priority, combo_key, harass_key, laneclear_key
    global use_q_tornado_in_laneclear
    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        ui.treepop()

    if ui.treenode("Laneclear"):
        use_q_tornado_in_laneclear = ui.checkbox("Use Q Tornado in Lane Clear", use_q_tornado_in_laneclear)
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

def GetClosestMobToEnemyForGap(game):
    global e
    closestMinionDistance = 9999
    for enemy in game.champs:
        if enemy and ValidTarget(enemy) and enemy.is_enemy_to(game.player) and game.is_point_on_screen(enemy.pos):
            for minion in game.minions:
                if minion and minion.is_visible and minion.movement_speed > 0 and minion.isTargetable and minion.is_alive and minion.pos.distance(game.player.pos) < e['Range'] and minion.is_enemy_to(game.player) and game.is_point_on_screen(minion.pos):
                    if minion.pos.distance(enemy.pos) < e['Range']:
                        minionDistanceToMouse = minion.pos.distance(enemy.pos)
                        if minionDistanceToMouse < closestMinionDistance:
                            return minion

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
    if game.player.Q.level == 1:
        damage = 200 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level == 2:
        damage = 350 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level == 3:
        damage = 500 + (get_onhit_physical(game.player, target))
    return damage

def find_minion_target(game, min_range):
	target = None
	for minion in game.minions:
		if minion.is_enemy_to(game.player) and minion.is_alive and game.distance(game.player, minion) < min_range:
			target = minion
		
	return target

def ultIsKillable(game, target):
    for missile in game.missiles:
        if missile.name != "yasuowmis":
            continue
        if not is_skillshot(missile.name):
            continue
        spell = get_missile_parent_spell(missile.name)
        if not spell:
            continue
        end_pos = missile.end_pos.clone()
        start_pos = missile.start_pos.clone()
        curr_pos = missile.pos.clone()
        if game.point_on_line(game.world_to_screen(target.pos), game.world_to_screen(end_pos), game.world_to_screen(curr_pos), target.gameplay_radius * 2):
            return True
    return False

def Combo(game):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_r_range, draw_e_range
    global targeting, combo_key, harass_key, laneclear_key
    global q, w, e, r
    q_spell = getSkill(game, 'Q')
    e_spell = getSkill(game, 'E')
    r_spell = getSkill(game, 'R')
    before_cpos = game.get_cursor()
    if use_q_in_combo and IsReady(game, q_spell):
        target = targeting.get_target(game, q['Range'])
        if ValidTarget(target) and target and q_spell.name != "YasuowWrapper":
            if game.player.pos.distance(target.pos) <= q['Range']:
                game.move_cursor(game.world_to_screen(target.pos))
                game.press_right_click()
                q_spell.trigger(False)
                # time.sleep(0.02)
                # game.move_cursor(before_cpos)
    if use_q_in_combo and IsReady(game, q_spell):
        target = targeting.get_target(game, w['Range'])
        if ValidTarget(target) and target and q_spell.name == "YasuowWrapper":
            if game.player.pos.distance(target.pos) <= w['Range']:
                game.move_cursor(game.world_to_screen(target.pos))
                game.press_right_click()
                q_spell.trigger(False)
                # time.sleep(0.02)
                # game.move_cursor(before_cpos)
    if use_e_in_combo and IsReady(game, e_spell):
        target = targeting.get_target(game, e['Range'])
        if ValidTarget(target) and target:
            if target.pos.distance(game.player.pos) <= e['Range']:
                game.move_cursor(game.world_to_screen(target.pos))
                game.press_right_click()
                e_spell.trigger(False)
                # time.sleep(0.02)
                # game.move_cursor(before_cpos)
    if use_e_in_combo and IsReady(game, e_spell):
        for target in game.champs:
            enemy = target
            if ValidTarget(target) and target and enemy.is_enemy_to(game.player) and game.is_point_on_screen(enemy.pos):
                if target.pos.distance(game.player.pos) > q['Range']:
                    minion = GetClosestMobToEnemyForGap(game)
                    if minion and game.distance(game.player, minion) <= e['Range']:
                        game.move_cursor(game.world_to_screen(minion.pos))
                        game.press_right_click()
                        e_spell.trigger(False)
                        # time.sleep(0.02)
                        # game.move_cursor(before_cpos)
    if use_r_in_combo and IsReady(game, r_spell):
        target = targeting.get_target(game, r['Range'])
        if ValidTarget(target) and target:
            if target.pos.distance(game.player.pos) <= r['Range']:
                if ultIsKillable(game, target) and RDamage(game, target) >= target.health:
                    r_spell.trigger(False)

def LaneClear(game):
    q_spell = getSkill(game, 'Q')
    before_cpos = game.get_cursor()
    if q_spell and q_spell.name != "YasuowWrapper":
        enemyMinion = find_minion_target(game, q["Range"])
        if enemyMinion and IsReady(game, q_spell):
            game.move_cursor(game.world_to_screen(enemyMinion.pos))
            game.press_right_click()
            q_spell.trigger(False)
            # time.sleep(0.02)
            # game.move_cursor(before_cpos)
        if enemyMinion and IsReady(game, q_spell):
            delay = 0.25 + game.player.pos.distance(enemyMinion.pos) / 3000
            if (QDamage(game, enemyMinion) >= enemyMinion.health + delay / 2 - 150):
                return
            if (QDamage(game, enemyMinion) >= enemyMinion.health + delay / 2):
                game.move_cursor(game.world_to_screen(enemyMinion.pos))
                game.press_right_click()
                q_spell.trigger(False)
    if q_spell and q_spell.name == "YasuowWrapper" and use_q_tornado_in_laneclear:
        enemyMinion = find_minion_target(game, w["Range"])
        if enemyMinion and IsReady(game, q_spell):
            game.move_cursor(game.world_to_screen(enemyMinion.pos))
            game.press_right_click()
            q_spell.trigger(False)
            # time.sleep(0.02)
            # game.move_cursor(before_cpos)

def Harass(game):
    target = targeting.get_target(game, q['Range'])
    q_spell = getSkill(game, 'Q')
    e_spell = getSkill(game, 'E')
    r_spell = getSkill(game, 'R')
    before_cpos = game.get_cursor()
    if ValidTarget(target) and target and target.is_enemy_to(game.player) and game.is_point_on_screen(target.pos) and q_spell.name != "YasuowWrapper":
        if game.player.pos.distance(target.pos) <= q['Range']:
            game.move_cursor(game.world_to_screen(target.pos))
            game.press_right_click()
            q_spell.trigger(False)
            time.sleep(0.02)
            game.move_cursor(before_cpos)
    if ValidTarget(target) and target and target.is_enemy_to(game.player) and game.is_point_on_screen(target.pos) and q_spell.name == "YasuowWrapper":
        if game.player.pos.distance(target.pos) <= w['Range']:
            game.move_cursor(game.world_to_screen(target.pos))
            game.press_right_click()
            q_spell.trigger(False)
            time.sleep(0.02)
            game.move_cursor(before_cpos)
            
def blitz_update(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_r_range, draw_e_range
    global q, e, r
    global targeting, combo_key
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