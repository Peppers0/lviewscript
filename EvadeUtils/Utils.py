from blitz import *

def FixPos(game, pos, y = None):
    return Vec3(pos.x, y or game.player.pos.y, pos.y)

def DrawArrow(game, startPos, endPos, color):
    direction = startPos.sub(endPos)
    p1 = endPos.sub(direction).normalize().scale(30).add(direction.normalize().scale(30))
    p2 = endPos.sub(direction).normalize().scale(-30).add(direction.normalize().scale(-30))
    startPos = FixPos(game, startPos)
    endPos = FixPos(game, endPos) 
    p1 = FixPos(game, p1)
    p2 = FixPos(game, p2)
    game.draw_line(game.world_to_screen(startPos), game.world_to_screen(endPos), 1, color)
    game.draw_line(game.world_to_screen(p1), game.world_to_screen(endPos), 1, color)
    game.draw_line(game.world_to_screen(p2), game.world_to_screen(endPos), 1, color)

def ClosestPointOnSegment(s1, s2, pt):
    ab = s2.sub(s1)
    t = ((pt.x - s1.x) * ab.x + (pt.y - s1.y) * ab.y) / (ab.x * ab.x + ab.y * ab.y)
    return t < 0 and s1 or (t > 1 and s2 or s1 + t * ab)

def AppendVector(pos1, pos2, dist):
    return pos2.add(pos2.sub(pos1)).normalize().scale(dist)

