from blitz import *
from time import time

show_healable = False
enabled_autoadc = True

blitz_script_info = {
	"script": "Auto heal",
	"author": "leryss",
	"description": "Auto heals for adc"
}

def blitz_load_cfg(cfg):
	global show_healable
	show_healable = cfg.get_bool("show_healable", True)
	
def blitz_save_cfg(cfg):
	global show_healable
	cfg.set_bool("show_healable", show_healable)
	
def blitz_draw_settings(game, ui):
	global show_healable
	show_healable = ui.checkbox("Show when to heal", show_healable)
	
def blitz_update(game, ui):
	global enabled_autoadc, show_healable
	
	self = game.player

	if self.is_alive and self.is_visible and game.is_point_on_screen(self.pos):
		heal = game.player.get_summoner_spell(SummonerSpellType.Heal)
		if heal == None: 
			return
		
		hp = int(self.health / self.max_health * 100)

		hovered = game.hovered_obj
		if enabled_autoadc:
			p = game.world_to_screen(game.player.pos)
			p.y -= 70
			
			if hp < 30 and self.is_alive and heal.get_current_cooldown(game.time) == 0.0:
				heal.trigger(False)