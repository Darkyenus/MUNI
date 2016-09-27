from game_bang import *
import random

class HumanBrain(AbstractBrain):

    def show_list(self, cards):
        i = 1
        for c in cards:
            print(str(i) + ") " + str(c))
            i += 1

    def input_pick(self, selection, noun):
        self.show_list(selection)
        while True:
            response = input("Pick "+noun+" number? > ")
            try:
                pick = int(response)
                if pick < 1 or pick > len(selection):
                    print("Must pick a valid number from 1 to "+str(len(selection)))
                else:
                    return selection[pick-1]
            except ValueError:
                print("No "+noun+" picked")
                return None

    def simulate_turn(self, player):
        print("\nYour turn, human playing as "+str(player)+"!")
        while True:
            print("What will you play?")
            picked = self.input_pick(player.cards, "card")
            if picked is None:
                break
            else:
                target = None
                if picked.needs_target:
                    target = self.input_pick(player.game.players_in_game_except(player), "target")
                    if target is None:
                        continue
                card_play(player, picked, target)
        while len(player.cards) > player.health:
            print("Too many cards in inventory. Which one do you want to discard?")
            picked = self.input_pick(player.cards, "card")
            if picked is None:
                break
            else:
                card_discard(player, picked)
        print("Turn complete")

    def handle_threat(self, player, from_player, threat_card):
        possible_responses = []
        for res in threat_card.threat_response:
            if res in player.cards:
                possible_responses.append(res)

        if len(possible_responses) == 0:
            print(str(player)+"! You are threatened by "+str(threat_card)+" played by "+str(from_player)+"! But you don't have a response...")
            return None
        else:
            print(str(player)+"! You are threatened by "+str(threat_card)+" played by "+str(from_player)+"! Select a response!")
            return self.input_pick(possible_responses, "response")

    def emporio_pick(self, player, selection):
        if len(selection) == 1:
            print(str(player)+"! You picked up "+selection[0]+" from emporio sale as it was the last item")
            return selection[0]
        else:
            print(str(player)+"! Emporio sale is in town! Select a ware!")
            return self.input_pick(selection, "emporio pick")

class SittingDuck(AbstractBrain):
    pass

class ResponsiveBrain(AbstractBrain):

    def handle_threat(self, player, from_player, threat_card):
        for possible_response in threat_card.threat_response:
            if possible_response in player.cards:
                return possible_response
        return None

    def emporio_pick(self, player, selection):
        if player.health < player.max_health and Cards.BIRRA in selection:
            return Cards.BIRRA
        if Cards.MANCATO not in player.cards and Cards.MANCATO in selection:
            return Cards.MANCATO
        if player.health <= 2:
            for maybe_card in [Cards.WELLS_FARGO, Cards.DILIGENZA, Cards.SALOON, Cards.MANCATO]:
                if maybe_card in selection:
                    return maybe_card
        if player.cards.count(Cards.BANG) > 2 and Cards.DUELLO in selection and Cards.DUELLO not in player.cards:
            return Cards.DUELLO
        for maybe_card in [Cards.WELLS_FARGO, Cards.GATLING, Cards.DILIGENZA, Cards.PANICO, Cards.BIRRA,Cards.CAT_BALOU, Cards.MANCATO, Cards.BANG]:
            if maybe_card in selection:
                return maybe_card
        return None

class RandomResponsiveBrain(ResponsiveBrain):
    def simulate_turn(self, player):
        for _ in range(random.randint(1, int(len(player.cards) * 1.5))):
            if len(player.cards) == 0:
                break
            card = random.choice(player.cards)
            target = None
            if card.needs_target:
                target = random.choice(player.game.players_in_game_except(player))
            card_play(player, card, target)

class MildlyCompetentResponsiveBrain(ResponsiveBrain):

    def pick_player_to_steal_from(self, player):
        players = list(player.game.players_in_game_except(player))
        random.shuffle(players)
        for p in players:
            if p.has_cards:
                return p
        return None

    def simulate_turn(self, player):
        # Open boxes
        while Cards.WELLS_FARGO in player.cards or Cards.DILIGENZA in player.cards:
            if Cards.WELLS_FARGO in player.cards:
                card_play(player, Cards.WELLS_FARGO)
            else:
                card_play(player, Cards.DILIGENZA)

        # Go shopping
        while Cards.EMPORIO in player.cards:
            card_play(player, Cards.EMPORIO)

        # Steal what you can...
        while Cards.PANICO in player.cards:
            to_steal_from = self.pick_player_to_steal_from(player)
            if to_steal_from is None:
                break
            card_play(player, Cards.PANICO, to_steal_from)
        # ...discard what you can't
        while Cards.CAT_BALOU in player.cards:
            to_steal_from = self.pick_player_to_steal_from(player)
            if to_steal_from is None:
                break
            card_play(player, Cards.CAT_BALOU, to_steal_from)

        # Take care of health
        while player.health < player.max_health and Cards.BIRRA in player.cards:
            card_play(player, Cards.BIRRA)
        if player.health <= 2 and Cards.SALOON in player.cards:
            card_play(player, Cards.SALOON)

        # Unleash beasts!
        while Cards.INDIANI in player.cards:
            card_play(player, Cards.INDIANI)
        while Cards.GATLING in player.cards:
            card_play(player, Cards.GATLING)

        # Bang!
        if Cards.BANG in player.cards:
            targets = sorted(player.game.players_in_game_except(player), key=lambda p: p.health)
            card_play(player, Cards.BANG, targets[0])

        # Duel time!
        while Cards.DUELLO in player.cards:
            my_bangs = player.cards.count(Cards.BANG) + player.cards.count(Cards.GATLING)
            targets = sorted(player.game.players_in_game_except(player), key=lambda p: p.health)
            for target in targets:
                if target.count_cards - 1 <= my_bangs:
                    card_play(player, Cards.DUELLO, target)
                    continue
            break
