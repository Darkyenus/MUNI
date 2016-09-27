from game_bang_brains import *
from operator import attrgetter

def compare(runs, log, *brains):
    for b in brains:
        b.score = 0

    for brain_1_index in range(len(brains)):
        for brain_2_index in range(brain_1_index + 1, len(brains)):
            for _ in range(runs):
                game = Game(log, brains[brain_1_index], brains[brain_2_index])
                rounds, winner = simulate_game(game)
                if winner is not None:
                    winner.brain.score += 1

    result = sorted(brains, key=attrgetter('score'), reverse=True)
    for b in result:
        print(str(b)+" with "+str(b.score)+" victories")
    return result

compare(1000, False, RandomResponsiveBrain(), MildlyCompetentResponsiveBrain())