from blitz import *
from commons.skills import *
from commons.targeting import TargetingConfig
import json, time
import commons.damage_calculator as damage_calculator

class Lucian:
    targeting = TargetingConfig()
    eq_combo  = False

    def combo(self, game):
        self.castSkill(game, 'Q')
        self.castSkill(game, 'E')
        self.castSkill(game, 'W')

    def harras(self, game):
        self.castSkill(game, 'Q')

    def skPrediction(self, game, skill, slot):
        skill = getattr(game.player, slot)
        b_is_skillshot = is_skillshot(skill.name)
        skill_range = get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
        if slot == "Q":
            skill_range = 600.0
        target = self.targeting.get_target(game, skill_range)
        if target:
            if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
                cast_point = castpoint_for_collision(game, skill, game.player, target)
                if cast_point:
                    if b_is_skillshot:
                        cast_point = castpoint_for_collision(game, skill, game.player, target)
                    else:
                        cast_point = target.pos
                    cast_point = game.world_to_screen(cast_point)
                    return cast_point
                    
    def castSkill(self, game, slot):
        skill = getattr(game.player, slot)
        cast_pos = self.skPrediction(game, skill, slot)
        if cast_pos:
            game.move_cursor(cast_pos)
            game.click_at(True, cast_pos)
            skill.trigger()
            

    def evade(self, game, save_pos):
        game.move_cursor(save_pos)
        castSkill(game, 'W')