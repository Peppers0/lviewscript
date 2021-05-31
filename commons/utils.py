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