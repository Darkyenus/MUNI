from game_bang_brains import *
from operator import attrgetter

def compare(runs, log, *brains):
    for b in brains:
        b.score = 0

    for brain_1_index in range(len(brains)):
        for brain_2_index in range(brain_1_index + 1, len(brains)):
            for i in range(runs):
                # Shuffle starting positions, as it gives significant edge
                if i % 2 == 0:
                    game = Game(log, brains[brain_1_index], brains[brain_2_index])
                else:
                    game = Game(log, brains[brain_2_index], brains[brain_1_index])
                rounds, winner = simulate_game(game)
                if winner is not None:
                    winner.brain.score += 1

    result = sorted(brains, key=attrgetter('score'), reverse=True)
    for b in result:
        print(str(b)+" with "+str(b.score)+" victories")
    return result

compare(100000, False,
        CustomisablyResponsiveBrain(),
        CustomisablyResponsiveBrain(name="HealingLater", action_queue=[
            CustomisablyResponsiveBrain.action_open_boxes,
            CustomisablyResponsiveBrain.action_go_shopping,
            CustomisablyResponsiveBrain.action_do_stealing,
            CustomisablyResponsiveBrain.action_do_destroying,
            CustomisablyResponsiveBrain.action_do_healing_self,
            CustomisablyResponsiveBrain.action_indiani,
            CustomisablyResponsiveBrain.action_gatling,
            CustomisablyResponsiveBrain.action_bang,
            CustomisablyResponsiveBrain.action_do_healing_all,
            CustomisablyResponsiveBrain.action_duel,
        ])
        )