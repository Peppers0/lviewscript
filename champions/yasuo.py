from blitz import *
from commons.skills import *
from commons import skills
from commons.targeting import TargetingConfig
import json, time
import commons.damage_calculator as damage_calculator

class Yasuo:
    targeting = TargetingConfig()
    eq_combo  = False

    def combo(self, game):
        self.castSkill(game, 'E', True)
        skill = getattr(game.player, 'Q', True)
        if skill.name == "yasuoq3wrapper":
            self.castSkill(game, 'Q', True)
        flash = game.player.get_summoner_spell(SummonerSpellType.Flash)
        if flash == None:
            return
        ignite = game.player.get_summoner_spell(SummonerSpellType.Ignite)
        if ignite == None:
            return    
        if flash.get_current_cooldown(game.time) == 0.0 and ignite.get_current_cooldown(game.time) == 0.0:
            self.castSkill(game, 'F', True)
            self.castSkill(game, 'D', True)
        
        
    def harras(self, game):
        self.castSkill(game, 'Q')

    def skPrediction(self, game, skill, slot, low):
        skill = getattr(game.player, slot)
        b_is_skillshot = is_skillshot(skill.name)
        skill_range = get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
        if slot == "Q":
            skill_range = 400.0
        if slot == "Q" and skill.name == "yasuoq3wrapper":
            skill_range = 900.0
        target = self.targeting.get_target(game, skill_range)
        if target:
            hp = int(target.health / target.max_health * 100)
            if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
                cast_point = target.pos
                cast_point = game.world_to_screen(cast_point)
                if low and hp < 20:
                    return cast_point
                elif not low:
                    return cast_point

    def castSkill(self, game, slot, low = False):
        skill = getattr(game.player, slot)
        cast_pos = self.skPrediction(game, skill, slot, low)
        before_pos = game.get_cursor()
        if cast_pos:
            game.move_cursor(cast_pos)
            game.click_at(True, cast_pos)
            skill.trigger()
            game.move_cursor(before_pos)

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
        skill = getattr(game.player, 'E')
        skillQ = getattr(game.player, 'Q')
        target = self.find_minion_target(game)
        cursor = game.get_cursor()
        if target:
            if game.world_to_screen(target.pos).distance(cursor) < 30:
                game.move_cursor(game.world_to_screen(target.pos))
                game.press_right_click()
                if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0 or skillQ.get_current_cooldown(game.time) == 0.0 and skillQ.level > 0:
                    skill.trigger()
                else:
                    skillQ.trigger()


    def evade(self, game, save_pos):
        game.move_cursor(save_pos)
        self.castSkill(game, 'W')