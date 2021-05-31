from blitz import *
from commons.skills import *
from commons.targeting import TargetingConfig
import json, time
import commons.damage_calculator as damage_calculator

class Zed:
    cast_keys = {
        'W': 0,
        'Q': 0,
        'E': 0,
        'R': 0
    }

    targeting = TargetingConfig()

    def combo(self, game):
        for slot, key in self.cast_keys.items():
            skill = getattr(game.player, slot)
            b_is_skillshot = is_skillshot(skill.name)
            skill_range = get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
            target = self.targeting.get_target(game, skill_range)
            if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
                if target:
                    champ_hp = target.health
                    if b_is_skillshot:
                        cast_point = castpoint_for_collision(game, skill, game.player, target)
                    else:
                        cast_point = target.pos
                    if cast_point:
                        damage_spec = damage_calculator.get_damage_specification(game.player)
                        if damage_spec is None:
                            return
                        dmg = damage_spec.calculate_damage(game.player, target)
                        cast_point = game.world_to_screen(cast_point)
                        game.draw_line(cast_point, game.world_to_screen(game.player.pos), 1.0, Color.WHITE)
                        game.move_cursor(cast_point)
                        game.click_at(True, cast_point)
                        if target.health <= dmg and slot == "R":
                            skill.trigger()
                        else:
                            skill.trigger()

    def isDead(self, game, champ):
        champ_hp = int(champ.health)
        for slot, key in self.cast_keys.items():
            skill = getattr(game.player, slot)
            print(skill.value)
            champ_hp = int(champ.health) - int(skill.value)
            print(champ_hp)
            if int(champ_hp) < 0 or int(champ_hp) == 0:
                return True
            else:
                return False
