from blitz import *
import commons.damage_calculator as damage_calculator

blitz_script_info = {
	"script": "Execution notifier",
	"author": "orkido",
	"description": "Shows message if a enemy champion can be executed with an ability"
}


def blitz_load_cfg(cfg):
	pass

def blitz_save_cfg(cfg):
	pass

def blitz_draw_settings(game, ui):
	pass

def blitz_update(game, ui):
    damage_spec = damage_calculator.get_damage_specification(game.player)
    if damage_spec is None:
        # Current champion is not supported
        return

    for champ in game.champs:
        if game.is_point_on_screen(champ.pos) and champ.is_alive and champ.is_visible and champ.is_enemy_to(game.player):
            dmg = damage_spec.calculate_damage(game.player, champ)

            if champ.health <= dmg:
                game.draw_circle_world_filled(champ.pos, 40, 3, Color.RED)
    