from blitz import *
from evade import checkEvade
from commons.skills import *
from commons.targeting import TargetingConfig
import json, time, math

blitz_script_info = {
    "script": "Mechanic Master",
	"author": "anonm",
	"description": "Mechanic Master",
	"target_champ": "yasuo"
}

harass = False
combo = False
combo_key = 0

use_q_in_combo = True
q_distance = 0
use_q = True

use_e_in_combo = True
e_distance = 0
use_e = True

use_r_in_combo = True
r_distance = 0
use_r = True

last_attacked = 0
toggled = False

q_ready = False
e_ready = False
r_ready = False

draw_q_range = False
draw_e_range = False

targeting = TargetingConfig() 

def blitz_load_cfg(cfg):
    global use_q_in_combo, use_q, use_e_in_combo, use_e, use_r, use_r_in_combo, q_distance, e_distance, r_distance, draw_q_range, draw_e_range, combo_key
    global targeting
    combo_key = cfg.get_int("combo_key", 0)	

    use_q   = cfg.get_bool("use_q", True)
    use_e   = cfg.get_bool("use_e", False)
    use_r   = cfg.get_bool("use_r", True)

    use_q_in_combo   = cfg.get_bool("use_q_in_combo", True)
    use_e_in_combo   = cfg.get_bool("use_e_in_combo", False)
    use_r_in_combo   = cfg.get_bool("use_r_in_combo", True)

    draw_q_range   = cfg.get_bool("draw_q_range", False)
    draw_e_range   = cfg.get_bool("draw_e_range", False)

    q_distance   = cfg.get_float("q_distance", 400)
    e_distance   = cfg.get_float("e_distance", 600)
    r_distance   = cfg.get_float("r_distance", 500)
    targeting.load_from_cfg(cfg)
	
def blitz_save_cfg(cfg):
    global use_q_in_combo, use_q, use_e_in_combo, use_e, use_r, use_r_in_combo, q_distance, e_distance, r_distance, draw_q_range, draw_e_range, combo_key
    global targeting
    cfg.set_int("combo_key", combo_key)

    cfg.set_bool("use_q", use_q)
    cfg.set_bool("use_e", use_e)
    cfg.set_bool("use_r", use_r)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_e_range", draw_e_range)

    cfg.set_float("q_distance", q_distance)
    cfg.set_float("e_distance", e_distance)
    cfg.set_float("r_distance", r_distance)
    targeting.save_to_cfg(cfg)
	
def blitz_draw_settings(game, ui):
    global use_q_in_combo, use_q, use_e_in_combo, use_e, use_r, use_r_in_combo, q_distance, e_distance, r_distance, draw_q_range, draw_e_range, combo_key
    global targeting
    combo_key = ui.keyselect("Combo key", combo_key)

    if ui.treenode("Setting [Q]"):
        ui.text("Setting [Q]")
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        use_q = ui.checkbox("Use Q", use_q)
        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        q_distance = ui.dragfloat("Q Distance", q_distance, 250.0, 400.0, 600.0)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        ui.text("Setting [E]")
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        use_e = ui.checkbox("Use E", use_e)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        e_distance = ui.dragfloat("E Distance", e_distance, 300.0, 450.0, 500.0)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        ui.text("Setting [R]")
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        use_r = ui.checkbox("Use R", use_r)
        r_distance = ui.dragfloat("R Distance", r_distance, 200.0, 400.0, 500.0)
        ui.treepop()

    targeting.draw(ui)

def GetPercentHealth(obj):
    return (obj.health / obj.max_health) * 100

def GetDistanceSqr(p1, p2):
    p2 = p2
    d = p1.sub(p2)
    d.z = (p1.z or p1.y) - (p2.z or p2.y)
    return d.x * d.x + d.z * d.z

def GetDistance(p1, p2):
    squaredDistance = GetDistanceSqr(p1, p2)
    return math.sqrt(squaredDistance)

def isValidTarget(game, target, range):
    return target and target.isVisible and target.is_alive and (not range or GetDistance(target.pos) <= range)
	
def ValidTarget(obj):
    return (obj and obj.is_alive and obj.is_visible and obj.isTargetable)

def RotateAroundPoint(v1 ,v2, angle):
    cos, sin = math.cos(angle), math.sin(angle)
    x = ((v1.x - v2.x) * cos) - ((v2.z - v1.z) * sin) + v2.x
    z = ((v2.z - v1.z) * cos) + ((v1.x - v2.x) * sin) + v2.z
    return Vec3(x, v1.y, z or 0)

def GetWallPosition(target, t_range):
    t_range = t_range or 400
    for i in range(0, 360, 45):
        angle = i * math.pi/180
        targetPosition = target.pos
        targetRotated = Vec3(targetPosition.x + t_range, targetPosition.y, targetPosition.z)
        Wallid = RotateAroundPoint(targetRotated, targetPosition, angle)

        if GetDistance(Wallid, targetRotated) < t_range:
            return Wallid

def GetKitePosition(game, target):
    for i in range(0, 360, 22):
        angle = i * (math.pi/180)
  
        myPos = game.player.pos
        tPos = target.pos
  
        rot = RotateAroundPoint(tPos, myPos, angle)
        pos = myPos.add(myPos.sub(rot))
        if ValidTarget(target):
            for champ in game.champs:
                dist = GetDistance(target.pos, pos) / 2
                if (dist < 340 and dist > 200):
                    return pos
                else:
                    dist = GetDistance(target.pos, pos)
                    if dist > 250 and dist < 380:
                        return pos
    return pos

def IsDangerousPosition(game, target):
    if game.is_point_on_screen(target.pos) and GetDistance(game.player.pos, target.pos) < 300:
        return True
    else: 
        return False

def IsReady(game, skill):
    return skill and skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0

def getSkill(game, slot):
    skill = getattr(game.player, slot)
    if skill:
        return skill
    return None

def castE(game, target):
    skill = getSkill(game, 'E')
    print(IsReady(game, skill))
    if IsReady(game, skill):
        before_pos = game.get_cursor()
        game.move_cursor(game.world_to_screen(target.pos))
        skill.trigger(False, 0)

def castQ(game, target, pos):
    skill = getSkill(game, 'Q')
    print(IsReady(game, skill))
    if IsReady(game, skill):
        before_pos = game.get_cursor()
        if GetKitePosition(game, target).distance(game.player.pos) <= 800:
            game.move_cursor(game.world_to_screen(GetKitePosition(game, target)))
            skill.trigger(False, 0)

def castR(game):
    skill = getSkill(game, 'R')
    print(IsReady(game, skill))
    if IsReady(game, skill):
        skill.trigger(False, 0)

def executeCombo(game, player):
    global use_q_in_combo, use_q, use_e_in_combo, use_e, use_r, use_r_in_combo, q_distance, e_distance, r_distance, combo_key, last_attacked, toggled

    if not game.is_key_down(combo_key):
        return
    for champ in game.champs:
        target = targeting.get_target(game, player.atkRange)
        if target:
            isInDanger = IsDangerousPosition(game, target)
            wallPos = GetWallPosition(target, 435)
            targetToWallDistance = target.pos.distance(wallPos)
            if game.was_key_pressed(combo_key):
                atk_speed = player.base_atk_speed * player.atk_speed_multi
                b_windup_time = (1.0/player.base_atk_speed) * player.basic_atk_windup
                c_atk_time = 1.0/atk_speed
                old_cpos = game.get_cursor()
                if use_q_in_combo:
                    t = game.time
                    if t - last_attacked >= c_atk_time:
                        if use_q_in_combo:
                            castQ(game, target, target.pos)
                        if use_r_in_combo:
                            castR(game)
                        if wallPos and use_e_in_combo or wallPos and use_e:
                            insecPos = target.pos.add(target.pos.sub(wallPos))
                            if insecPos.distance(player.pos) <= 325:
                                castE(game, target)
                                game.draw_line(game.world_to_screen(target.pos), game.world_to_screen(wallPos), 3, Color.RED)
                    else:
                        game.press_right_click()


def blitz_update(game, ui):
    global harass, combo, combo_key, draw_e_range, draw_q_range
    self = game.player

    if draw_q_range:
        game.draw_circle_world(game.player.pos, 300, 40, 3, Color.RED)
    if draw_e_range:
        game.draw_circle_world(game.player.pos, 625, 40, 3, Color.RED)


    if self.is_alive:
        executeCombo(game, self)