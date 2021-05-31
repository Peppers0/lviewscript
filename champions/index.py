from . import ashe
from . import brand
from . import draven
from . import jinx
from . import rengar
from . import yasuo
from . import zed
from . import malphite
from . import ryze
from . import lucian
from . import vayne

def useComboToChampion(game):
    if game.player.name == "ashe":
        return ashe.Ashe().combo(game)
    elif game.player.name == "brand":
        return brand.Brand().combo(game)
    elif game.player.name == "draven":
        return draven.Draven().combo(game)
    elif game.player.name == "jinx":
        return jinx.Jinx().combo(game)
    elif game.player.name == "rengar":
        return rengar.Rengar().combo(game)
    elif game.player.name == "yasuo":
        return yasuo.Yasuo().combo(game)
    elif game.player.name == "zed":
        return zed.Zed().combo(game)
    elif game.player.name == "malphite":
        return malphite.Malphite().combo(game)
    elif game.player.name == "ryze":
        return ryze.Ryze().combo(game)
    elif game.player.name == "lucian":
        return lucian.Lucian().combo(game)
        
def useHarrasMode(game):
    if game.player.name == "ashe":
        return ashe.Ashe().harras(game)
    elif game.player.name == "brand":
        return brand.Brand().harras(game)
    elif game.player.name == "draven":
        return draven.Draven().harras(game)
    elif game.player.name == "jinx":
        return jinx.Jinx().harras(game)
    elif game.player.name == "rengar":
        return rengar.Rengar().harras(game)
    elif game.player.name == "yasuo":
        return yasuo.Yasuo().harras(game)
    elif game.player.name == "zed":
        return zed.Zed().harras(game)

def useEvadeToChampion(game, save_pos):
    if game.player.name == "yasuo":
        return yasuo.Yasuo().evade(game, save_pos)
    elif game.player.name == "vayne":
        return vayne.Vayne().evade(game, save_pos)

def useLaneClear(game):
    if game.player.name == "yasuo":
        return yasuo.Yasuo().laneClear(game)
# class Legend:
#     def __init__(self, game):
#         self.game = game
        
#     def useComboToChampion(self):
#         self.game()
        
# class Yasuo(Legend):
#     def __init__(self):
#         super().__init__("Yasuo", yasuo.Yasuo().combo(self.game), yasuo.Yasuo().harras(self.game))

# yasuo = Yasuo()
# yasuo.useComboToChampion()