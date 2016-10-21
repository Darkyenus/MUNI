from game_comparison_and_breeding import start_genetic_breeding
from game_comparison_and_breeding import compare_brains
from game_bang_brains import *

MODE_MANUAL_FIGHT = 1
MODE_DEBUG_BREEDING = 2
MODE_QUICK_BREEDING = 3
MODE_FULL_BREEDING = 4

bred_brain = None

def start(mode):
    global bred_brain
    if mode == MODE_MANUAL_FIGHT:
        compare_brains(1, True, 0, HumanBrain(), bred_brain if bred_brain is not None else CustomisablyResponsiveBrain(name="DefaultOpponent"))
    elif mode == MODE_DEBUG_BREEDING:
        bred_brain = start_genetic_breeding(fights_per_match=20, iterations=10)
    elif mode == MODE_QUICK_BREEDING:
        bred_brain = start_genetic_breeding(fights_per_match=100, iterations=100)
    elif mode == MODE_FULL_BREEDING:
        bred_brain = start_genetic_breeding(fights_per_match=100, iterations=1000)
    else:
        print("Invalid mode")

#start(MODE_QUICK_BREEDING)
start(MODE_QUICK_BREEDING)
start(MODE_MANUAL_FIGHT)