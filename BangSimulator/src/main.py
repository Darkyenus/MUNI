from game_bang import *
from game_bang_brains import *

game = Game(True, HumanBrain(), ResponsiveBrain())
game_simulate(game)