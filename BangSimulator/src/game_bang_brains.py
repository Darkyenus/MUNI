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
        for maybe_card in [Cards.WELLS_FARGO, Cards.GATLING, Cards.DILIGENZA, Cards.PANICO, Cards.BIRRA, Cards.CAT_BALOU, Cards.MANCATO, Cards.BANG]:
            if maybe_card in selection:
                return maybe_card
        return None

class RandomResponsiveBrain(ResponsiveBrain):
    def simulate_turn(self, player):
        for _ in range(player.random.randint(1, int(len(player.cards) * 1.5))):
            if len(player.cards) == 0:
                break
            card = player.random.choice(player.cards)
            target = None
            if card.needs_target:
                target = player.random.choice(player.game.players_in_game_except(player))
            card_play(player, card, target)

class BrainActions:
    @staticmethod
    def _pick_player_to_steal_from(player):
        players = list(player.game.players_in_game_except(player))
        player.random.shuffle(players)
        for p in players:
            if p.has_cards:
                return p
        return None

    @staticmethod
    def action_open_boxes(player):
        if Cards.WELLS_FARGO in player.cards or Cards.DILIGENZA in player.cards:
            if Cards.WELLS_FARGO in player.cards:
                return card_play(player, Cards.WELLS_FARGO)
            else:
                return card_play(player, Cards.DILIGENZA)
        return False

    @staticmethod
    def action_go_shopping(player):
        if Cards.EMPORIO in player.cards:
            return card_play(player, Cards.EMPORIO)
        return False

    @staticmethod
    def action_do_stealing(player):
        if Cards.PANICO in player.cards:
            to_steal_from = BrainActions._pick_player_to_steal_from(player)
            if to_steal_from is None:
                return False
            return card_play(player, Cards.PANICO, to_steal_from)
        return False

    @staticmethod
    def action_do_destroying(player):
        if Cards.CAT_BALOU in player.cards:
            to_steal_from = BrainActions._pick_player_to_steal_from(player)
            if to_steal_from is None:
                return False
            return card_play(player, Cards.CAT_BALOU, to_steal_from)
        return False

    @staticmethod
    def action_do_healing_self(player):
        if player.health < player.max_health and Cards.BIRRA in player.cards:
            return card_play(player, Cards.BIRRA)
        return False

    @staticmethod
    def action_do_healing_all(player):
        if player.health <= 2 and Cards.SALOON in player.cards:
            return card_play(player, Cards.SALOON)
        return False

    @staticmethod
    def action_indiani(player):
        if Cards.INDIANI in player.cards:
            return card_play(player, Cards.INDIANI)
        return False

    @staticmethod
    def action_gatling(player):
        if Cards.GATLING in player.cards:
            return card_play(player, Cards.GATLING)
        return False

    @staticmethod
    def action_bang(player):
        if Cards.BANG in player.cards:
            targets = sorted(player.game.players_in_game_except(player), key=lambda p: p.health)
            return card_play(player, Cards.BANG, targets[0])
        return False

    @staticmethod
    def action_duel(player):
        if Cards.DUELLO in player.cards:
            my_bangs = player.cards.count(Cards.BANG) + player.cards.count(Cards.GATLING)
            targets = sorted(player.game.players_in_game_except(player), key=lambda p: p.health)
            for target in targets:
                if target.count_cards - 1 <= my_bangs:
                    return card_play(player, Cards.DUELLO, target)
        return False

class CustomisablyResponsiveBrain(ResponsiveBrain):

    def __init__(self, name=None, action_queue=None):
        self.name = name
        if action_queue is None:
            self.action_queue = [
                BrainActions.action_open_boxes,
                BrainActions.action_go_shopping,
                BrainActions.action_do_stealing,
                BrainActions.action_do_destroying,
                BrainActions.action_do_healing_self,
                BrainActions.action_do_healing_all,
                BrainActions.action_indiani,
                BrainActions.action_gatling,
                BrainActions.action_bang,
                BrainActions.action_duel,
            ]
        else:
            self.action_queue = action_queue

    def __str__(self):
        if self.name is None:
            return super().__str__()
        else:
            return self.name

    def simulate_turn(self, player):
        while True:
            did_something = False
            for action in self.action_queue:
                while action(player):
                    did_something = True
            if not did_something:
                break

class GeneticBrain(ResponsiveBrain):

    gene_selection = [
        BrainActions.action_open_boxes,
        BrainActions.action_go_shopping,
        BrainActions.action_do_stealing,
        BrainActions.action_do_destroying,
        BrainActions.action_do_healing_self,
        BrainActions.action_do_healing_all,
        BrainActions.action_indiani,
        BrainActions.action_gatling,
        BrainActions.action_bang,
        BrainActions.action_duel,
    ]

    mutation_functions = []
    add_probability = 3
    remove_probability = 2
    swap_probability = 4

    def add(self):
        self.genes.insert(self.random.randint(0, len(self.genes) + 1), self.random.choice(GeneticBrain.gene_selection))


    def remove(self):
        if len(self.genes) != 0:
            self.genes.remove(self.random.choice(self.genes))

    def swap(self):
        if len(self.genes) == 0:
            return
        s1 = self.random.randint(0, len(self.genes) - 1)
        s2 = self.random.randint(0, len(self.genes) - 1)
        s1v = self.genes[s1]
        s2v = self.genes[s2]
        self.genes[s1] = s2v
        self.genes[s2] = s1v

    for _ in range(add_probability):
        mutation_functions.append(add)
    for _ in range(remove_probability):
        mutation_functions.append(remove)
    for _ in range(swap_probability):
        mutation_functions.append(swap)

    def __init__(self):
        self.generation = 0
        # Contains genome of this brain
        self.genes = []
        # Contains booleans determining if the corresponding gene has ever be used or can be forgotten
        self.gene_usages = []
        self.random = random.Random()

    def simplify_genome(self):
        new_action_queue = []
        for action in self.genes:
            if len(new_action_queue) > 0 and new_action_queue[-1] == action:
                pass
            else:
                new_action_queue.append(action)
        self.genes = new_action_queue

    def refresh_gene_blocks(self):
        self.gene_usages = [False for _ in self.genes]

    @property
    def blocked_genes(self):
        result = []
        for i in range(len(self.genes)):
            if self.gene_usages[i]:
                result.append(self.genes[i])
        return result

    def __repr__(self):
        result = "Genetic Brain of "+str(self.generation) + ". generation\n"
        for action in self.genes:
            result += "\t{}\n".format(action.__name__)
        return result

    def simulate_turn(self, player):
        for action_i in range(len(self.genes)):
            if self.genes[action_i](player):
                self.gene_usages[action_i] = True

def genetic_mutant_create(from_brain, mutations=1):
    new_mutant = GeneticBrain()
    if from_brain is not None:
        new_mutant.parent_brains = [from_brain]
        new_mutant.genes = from_brain.blocked_genes
        new_mutant.generation = from_brain.generation + 1

        for _ in range(mutations):
            new_mutant.random.choice(new_mutant.mutation_functions)(new_mutant)
    else:
        new_mutant.parent_brains = []
        # Only add mutations for new brains
        for _ in range(mutations):
            GeneticBrain.add(new_mutant)

    new_mutant.simplify_genome()
    new_mutant.refresh_gene_blocks()
    return new_mutant

def genetic_mutant_merge(brain1, brain2, mutations=1):
    merged_mutant = GeneticBrain()
    merged_mutant.parent_brains = [brain1, brain2]
    merged_mutant.generation = max(brain1.generation, brain2.generation) + 1
    brain1_genes = brain1.blocked_genes
    brain2_genes = brain2.blocked_genes
    while len(brain1_genes) > 0 or len(brain2_genes) > 0:
        if len(brain1_genes) == 0:
            merged_mutant.genes.append(brain2_genes.pop(0))
        elif len(brain2_genes) == 0:
            merged_mutant.genes.append(brain1_genes.pop(0))
        else:
            if merged_mutant.random.getrandbits(1):
                gene = brain2_genes.pop(0)
            else:
                gene = brain1_genes.pop(0)
            if merged_mutant.random.getrandbits(2) != 0:
                # 1/4 of merged genes will get lost
                merged_mutant.genes.append(gene)
    for _ in range(mutations):
        merged_mutant.random.choice(merged_mutant.mutation_functions)(merged_mutant)
    merged_mutant.simplify_genome()
    merged_mutant.refresh_gene_blocks()
    return merged_mutant
