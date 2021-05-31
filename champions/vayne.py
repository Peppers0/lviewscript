from blitz import *
from commons.skills import *
from commons import skills
from commons.targeting import TargetingConfig
import json, time
import commons.damage_calculator as damage_calculator

class Vayne:
    targeting = TargetingConfig()
    eq_combo  = False

    def skPrediction(self, game, skill, slot):
        skill = getattr(game.player, slot)
        b_is_skillshot = is_skillshot(skill.name)
        skill_range = get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
        target = self.targeting.get_target(game, skill_range)
        if target:
            if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
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
            
    def find_minion_target(self, game):
        atk_range = game.player.base_atk_range + game.player.gameplay_radius
        min_health = 9999999999
        target = None
        for minion in game.minions:
            if minion.is_enemy_to(game.player) and minion.is_alive and minion.health < min_health and game.distance(game.player, minion) < atk_range and skills.is_last_hitable(game, game.player, minion):
                target = minion
                min_health = minion.health
            
        return target

    def laneClear(self, game):
        target = self.find_minion_target(game)
        if target:
            game.move_cursor(game.world_to_screen(target.pos))
            self.castSkill(game, 'Q')


    def evade(self, game, save_pos):
        game.move_cursor(save_pos)
        skill = getattr(game.player, 'Q')
        if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
            skill.trigger()
