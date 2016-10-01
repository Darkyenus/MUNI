from game_bang_brains import *
from operator import attrgetter
import time

def compare(runs, log, *brains):
    start_time = time.process_time()
    for b in brains:
        b.score = 0

    fight_index_pairs = []

    for brain_1_index in range(len(brains)):
        for brain_2_index in range(brain_1_index + 1, len(brains)):
            fight_index_pairs.append((brain_1_index, brain_2_index))
            fight_index_pairs.append((brain_2_index, brain_1_index))

    def simulate_match(seed, brain_1_index, brain_2_index):
        rounds, winner = simulate_game(Game(log, seed, brains[brain_1_index], brains[brain_2_index]))
        if winner is not None:
            winner.brain.score += 1
        return winner

    for b1, b2 in fight_index_pairs:
        for i in range(runs):
            simulate_match(i, b1, b2)

    elapsed_time = time.process_time() - start_time
    print("Simulated "+str(len(fight_index_pairs) * runs)+" runs in "+str(elapsed_time)+" seconds ("+str((len(fight_index_pairs) * runs)/elapsed_time)+" runs per second)")

    result = sorted(brains, key=attrgetter('score'), reverse=True)
    for b in result:
        print(str(b)+" with "+str(b.score)+" victories")
    return result

compare(10000, False,
        CustomisablyResponsiveBrain(),
        CustomisablyResponsiveBrain(name="HealingLater", action_queue=[
            CustomisablyResponsiveBrain.action_open_boxes,
            CustomisablyResponsiveBrain.action_go_shopping,
            CustomisablyResponsiveBrain.action_do_stealing,
            CustomisablyResponsiveBrain.action_do_destroying,
            CustomisablyResponsiveBrain.action_do_healing_self,
            CustomisablyResponsiveBrain.action_do_healing_all,
            CustomisablyResponsiveBrain.action_indiani,
            CustomisablyResponsiveBrain.action_gatling,
            CustomisablyResponsiveBrain.action_bang,
            CustomisablyResponsiveBrain.action_duel,
        ])
        )