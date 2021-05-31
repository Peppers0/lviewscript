from blitz import *
from evade import checkEvade
from commons.skills import *
from commons.targeting import TargetingConfig
import json, time, math

blitz_script_info = {
    "script": "Xerath God",
	"author": "anonm",
	"description": "For Vayne",
	"target_champ": "xerath"
}

harass = False
combo = False
combo_key = 0

use_q_in_combo = True
q_distance = 0
use_q = True

use_w_in_combo = True
w_distance = 0
use_w = True

use_e_in_combo = True
e_distance = 0
use_e = True

use_r_in_combo = True
r_distance = 0
use_r = True

toggled = False

draw_q_range = False
draw_w_range = False
draw_e_range = False

q = { 'MaxRange': 1440, 'MinRange': 750, 'QCharge': False, 'TimeQ': 0 }
w = { 'Range': 1100 }
e = { 'Range': 1000 }
r = { 'Range': 0, 'RCharge': False, 'RStacks': 0 }

spell_priority = {
	'Q': 0,
	'W': 0,
	'E': 0,
	'R': 0
}

targeting = TargetingConfig() 

last_charge_time = 0
last_moved = 0

def blitz_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q, use_w, use_e, use_r
    global draw_q_range, draw_w_range, draw_e_range
    global q_distance, w_distance, e_distance
    global targeting, spell_priority, combo_key
    combo_key = cfg.get_int("combo_key", 0)	

    use_q   = cfg.get_bool("use_q", True)
    use_w   = cfg.get_bool("use_w", True)
    use_e   = cfg.get_bool("use_e", False)
    use_r   = cfg.get_bool("use_r", True)

    use_q_in_combo   = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo   = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo   = cfg.get_bool("use_e_in_combo", False)
    use_r_in_combo   = cfg.get_bool("use_r_in_combo", True)

    draw_q_range   = cfg.get_bool("draw_q_range", False)
    draw_w_range   = cfg.get_bool("draw_w_range", False)
    draw_e_range   = cfg.get_bool("draw_e_range", False)

    q_distance   = cfg.get_float("q_distance", 900)
    w_distance   = cfg.get_float("w_distance", 800)
    e_distance   = cfg.get_float("e_distance", 800)
    r_distance   = cfg.get_float("r_distance", 5000)

    spell_priority = json.loads(cfg.get_str('spell_priority', json.dumps(spell_priority)))
    targeting.load_from_cfg(cfg)
	
def blitz_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q, use_w, use_e, use_r
    global draw_q_range, draw_w_range, draw_e_range
    global q_distance, w_distance, e_distance
    global targeting, spell_priority, combo_key
    cfg.set_int("combo_key", combo_key)

    cfg.set_bool("use_q", use_q)
    cfg.set_bool("use_w", use_w)
    cfg.set_bool("use_e", use_e)
    cfg.set_bool("use_r", use_r)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_w_range", draw_w_range)
    cfg.set_bool("draw_e_range", draw_e_range)

    cfg.set_float("q_distance", q_distance)
    cfg.set_float("w_distance", w_distance)
    cfg.set_float("e_distance", e_distance)
    cfg.set_float("r_distance", r_distance)

    cfg.set_str('spell_priority', json.dumps(spell_priority))
    targeting.save_to_cfg(cfg)
	
def blitz_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q, use_w, use_e, use_r
    global draw_q_range, draw_w_range, draw_e_range
    global q_distance, w_distance, e_distance, r_distance
    global targeting, spell_priority, combo_key
    combo_key = ui.keyselect("Combo key", combo_key)

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        use_q = ui.checkbox("Use Q", use_q)
        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        q_distance = ui.dragfloat("Q Distance", q_distance, 800, 1300, 1500)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        use_w = ui.checkbox("Use W", use_w)
        draw_w_range = ui.checkbox("Draw W Range", draw_w_range)
        w_distance = ui.dragfloat("W Distance", e_distance, 600.0, 850.0, 1050.0)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        use_e = ui.checkbox("Use E", use_e)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        e_distance = ui.dragfloat("E Distance", e_distance, 600.0, 850.0, 1050.0)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        use_r = ui.checkbox("Use R", use_r)
        r_distance = ui.dragfloat("R Distance", r_distance, 1000.0, 1500.0, 5000.0)
        ui.treepop()

    if ui.treenode("Utils"):
        for slot, key in spell_priority.items():
            spell_priority[slot] = ui.dragfloat(f'{slot}', 1.0, 2.0, 3.0, 4.0)
        ui.treepop()

    targeting.draw(ui)

def GetDistanceSqr(p1, p2):
    p2 = p2
    d = p1.sub(p2)
    d.z = (p1.z or p1.y) - (p2.z or p2.y)
    return d.x * d.x + d.z * d.z

def GetDistance(p1, p2):
    squaredDistance = GetDistanceSqr(p1, p2)
    return math.sqrt(squaredDistance)

def isValidTarget(game, target, range):
    return target and target.is_visible and target.is_alive and (not range or GetDistance(target.pos, game.player.pos) <= range)
	
def ValidTarget(obj):
    return (obj and obj.is_alive and obj.is_visible and obj.isTargetable)

def getSkill(game, slot):
    skill = getattr(game.player, slot)
    if skill:
        return skill
    return None


def IsReady(game, skill):
    return skill and skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0

def QRange(time):
    global q
    RangeQ = q['MaxRange'] - q['MinRange']
    MinRangeSpell = q['MinRange']
    AlcanceLocal = RangeQ / 1.4 * time + MinRangeSpell
    if AlcanceLocal > q['MaxRange']:
        AlcanceLocal = q['MaxRange'] 
    return AlcanceLocal

def IsCombo(game):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q, use_w, use_e, use_r
    global draw_q_range, draw_w_range, draw_e_range
    global q_distance, w_distance, e_distance
    global targeting, combo_key
    global last_charge_time, last_moved
    q_spell = getSkill(game, 'Q')
    w_spell = getSkill(game, 'W')
    e_spell = getSkill(game, 'E')
    before_cpos = game.get_cursor()
    if IsReady(game, q_spell) and use_q:
        TempoCang = game.time - 1
        s_range = QRange(TempoCang)
        target = targeting.get_target(game, s_range)
        charge_time = (1.0/game.player.base_atk_speed) * game.player.basic_atk_windup
        t = game.time * 1000
        if isValidTarget(game, target, s_range - 150) and not IsCollisioned(game, target) and isValidTarget(game, target, q_distance):
            game.move_cursor(game.world_to_screen(target.pos))
            q_spell.trigger(True)
            charge_time = 2.25 * 1000 + 10
            if game.time * 1000 >= (charge_time + last_charge_time):
                last_charge_time = game.time * 1000
                q_spell.trigger(False)
            # time.sleep(0.02)
            # game.move_cursor(before_cpos)
    target = targeting.get_target(game, w["Range"])
    if IsReady(game, w_spell) and use_w:
        if target and not IsCollisioned(game, target) and isValidTarget(game, target, w["Range"]) and isValidTarget(game, target, w_distance):
            # predPos = fast_prediction(game, w_spell, game.player, target, w["Range"])
            game.move_cursor(game.world_to_screen(target.pos))
            w_spell.trigger(False)
            time.sleep(0.02)
            game.move_cursor(before_cpos)
    if IsReady(game, e_spell) and use_e:
        if target and not IsCollisioned(game, target) and isValidTarget(game, target, e["Range"]) and isValidTarget(game, target, e_distance):
            # predPos = fast_prediction(game, e_spell, game.player, target, e["Range"])
            game.move_cursor(game.world_to_screen(target.pos))
            e_spell.trigger(False)
            time.sleep(0.02)
            game.move_cursor(before_cpos)

def blitz_update(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q, use_w, use_e, use_r
    global draw_q_range, draw_w_range, draw_e_range
    global q_distance, w_distance, e_distance
    global targeting, combo_key
    self = game.player

    if draw_q_range:
        game.draw_circle_world(game.player.pos, q["MaxRange"], 40, 3, Color.RED)
    if draw_e_range:
        game.draw_circle_world(game.player.pos, e["Range"], 40, 3, Color.RED)


    if self.is_alive:
        if game.was_key_pressed(combo_key):
            IsCombo(game)