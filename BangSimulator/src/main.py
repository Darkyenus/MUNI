from game_bang_brains import *
from game_plot import *
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

# BECAUSE PYTHON SUCKS, ENJOY A SMALL LOAN OF ONE MILLION OCTOTHORPES
# compare(10000, False,
#         CustomisablyResponsiveBrain(),
#         CustomisablyResponsiveBrain(name="HealingLater", action_queue=[
#             BrainActions.action_open_boxes,
#             BrainActions.action_go_shopping,
#             BrainActions.action_do_stealing,
#             BrainActions.action_do_destroying,
#             BrainActions.action_do_healing_self,
#             BrainActions.action_do_healing_all,
#             BrainActions.action_indiani,
#             BrainActions.action_gatling,
#             BrainActions.action_bang,
#             BrainActions.action_duel,
#         ])
#         )

def compare_brains(iterations_per_side, log, max_turns_per_fight, brain1, brain2):
    seed = (hash(brain1) * hash(brain2)) & 0xFFFFFFF
    brain1_score = 0
    brain2_score = 0

    for _ in range(iterations_per_side):
        seed += 1
        _, winner = simulate_game(Game(log, seed, brain1, brain2), max_turns_per_fight)
        if winner is not None:
            if winner.brain is brain1:
                brain1_score += 1
            elif winner.brain is brain2:
                brain2_score += 1

        seed += 1
        _, winner = simulate_game(Game(log, seed, brain2, brain1), max_turns_per_fight)
        if winner is not None:
            if winner.brain is brain1:
                brain1_score += 1
            elif winner.brain is brain2:
                brain2_score += 1

    win_ratio = brain1_score / (iterations_per_side * 2)

    if brain1_score == brain2_score == 0:
        # Both are incapable of doing anything
        return None, 0
    elif brain1_score >= brain2_score:
        return brain1, win_ratio
    else:
        return brain2, win_ratio

def start_genetic_breeding(fights_per_match=10, iterations=1000, max_turns_per_fight=1000, log=False):
    start_time = time.process_time()

    brain_pool_size = 5  # Hardcoded for now, see mutations part

    # Strategy:
    # brains = [brain_pool_size random brains]
    # for iterations {
    #   for each possible pair of two brains {
    #       Fight them together fights_per_match times.
    #       Winner gets a point.
    #       If the fight takes more than max_turns_per_fight turns, fight terminates and nobody gets a point
    #   }
    #   Take 30% of best, use it, break it, fix it, trash it, change it, mail, upgrade it, charge it, point it, zoom it, press it, snap it, work it, quick, erase it
    # }

    brain_pool = [genetic_mutant_create(None, 10) for _ in range(brain_pool_size)]
    for iteration in range(iterations):
        # Do mutations (won't be exactly right for first iteration, but that does not matter. It will make more sense for last iteration)
        # Mix first three with each o

        new_brain_pool = [
            brain_pool[0],
            brain_pool[1],
            genetic_mutant_create(brain_pool[0]),
            genetic_mutant_create(brain_pool[1]),
            genetic_mutant_merge(brain_pool[0], brain_pool[1])
        ]
        brain_pool = new_brain_pool

        # Reset scores because python whould freak out later
        for brain in brain_pool:
            brain.score = 0
        # Do fighting
        for brain_1_index in range(brain_pool_size):
            for brain_2_index in range(brain_1_index + 1, brain_pool_size):
                better_brain, _ = compare_brains(fights_per_match, log, max_turns_per_fight, brain_pool[brain_1_index], brain_pool[brain_2_index])
                if better_brain is not None:
                    better_brain.score += 1
        # Do post-fight sorting
        brain_pool = sorted(brain_pool, key=attrgetter('score'), reverse=True)
        # Log and plot
        plot_add_value("Winner generation", brain_pool[0].generation)
        plot_add_value("Winner gene count", len(brain_pool[0].genes))
        plot_add_value("Winner score", brain_pool[0].score)
        _, win_ratio = compare_brains(100, False, 10000, brain_pool[0], CustomisablyResponsiveBrain())
        plot_add_value("Winner baseline %", win_ratio, 1)
        print("{:.2%} complete, winner is in {} generation and has {} genes ({:%} win ratio against baseline)".format(iteration / iterations, brain_pool[0].generation, len(brain_pool[0].genes), win_ratio))

    elapsed_time = time.process_time() - start_time
    import math
    print("Simulated "+str(iterations)+" iterations in "+str(elapsed_time)+" seconds ("+str((iterations * math.factorial(brain_pool_size) * 2 * fights_per_match)/elapsed_time)+" runs per second)")

    # Print winners
    for brain in brain_pool:
        winner, win_ratio = compare_brains(100, False, 10000, brain, CustomisablyResponsiveBrain())
        print("Brain: {!r} {} (win rate {:%})".format(brain, "better than default" if winner == brain else "worse than default", win_ratio))
    plot_display()

quick = False
#quick = True
if quick:
    start_genetic_breeding(fights_per_match=20, iterations=10)
else:
    start_genetic_breeding(fights_per_match=100, iterations=100)