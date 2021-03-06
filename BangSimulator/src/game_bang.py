
import random as random_package_not_thread_safe

class Card:
    """Represents a card. Only one instance per card type, see Cards class."""
    def __init__(self, name, deck_amount, needs_target=False):
        self.name = name
        self.deck_amount = deck_amount
        self.needs_target = needs_target
        self.threat_response = []

    def __str__(self):
        return self.name


class Cards:
    """All implemented cards"""
    BANG = Card("Bang!", 25, needs_target=True)
    MANCATO = Card("Mancato!", 12)
    BIRRA = Card("Birra", 6)
    PANICO = Card("Panico!", 4, needs_target=True)
    CAT_BALOU = Card("Cat Balou", 4, needs_target=True)
    DUELLO = Card("Duello", 3, needs_target=True)
    DILIGENZA = Card("Diligenza", 2)
    EMPORIO = Card("Emporio", 2)
    INDIANI = Card("Indiani!", 2)
    WELLS_FARGO = Card("Wells Fargo", 1)
    GATLING = Card("Gatling", 1)
    SALOON = Card("Saloon", 1)

    ALL = [BANG, MANCATO, BIRRA, PANICO, CAT_BALOU, DUELLO, DILIGENZA, EMPORIO, INDIANI, WELLS_FARGO, GATLING, SALOON]

    BANG.threat_response = [MANCATO]
    GATLING.threat_response = [MANCATO]
    INDIANI.threat_response = [BANG, GATLING]
    DUELLO.threat_response = [BANG, GATLING]

class AbstractBrain:
    """Basis for all brains. Brains are controllers of players and can be implemented in any way.
    Brains should not retain any state about the current game, as they can be used in more games at the same time.
    For such storage, Player can be used. Implementations should be thread safe."""

    # Call play_card in this to simulate player's turn.
    # Returns nothing
    def simulate_turn(self, player):
        pass

    # Called when player is in danger and needs to respond.
    # Returns which type of card should be used or None if no response is generated. Card should be in inventory.
    # (If the card is not in inventory, it is assumed that None was returned)
    def handle_threat(self, player, from_player, threat_card):
        return None

    # Called when emporio is open and player must pick one card.
    # Must not modify `selection`, but should return one of the cards in selection.
    # If returned card is not in selection or None is returned, random card is picked.
    def emporio_pick(self, player, selection):
        return None

    def __str__(self, *args, **kwargs):
        return type(self).__name__


class Player:
    """Single player which enters the Game. New instance will be often created for each match."""

    def __init__(self, game, random, player_id, health, brain):
        self.game = game
        self.random = random
        self.player_id = player_id
        self.max_health = health
        self.health = health
        self.brain = brain
        self.cards = []
        self.played_bang_this_turn = False

    @property
    def has_cards(self):
        return len(self.cards) > 0

    @property
    def count_cards(self):
        return len(self.cards)

    def __str__(self, *args, **kwargs):
        return "Player "+str(self.player_id)+" "+str(self.health)+"/"+str(self.max_health)

def card_draw_return(game):
    """Draw a card and return it. Caller must ensure that the card does not get lost from the game."""
    if len(game.fresh_cards) == 0:
        game.fresh_cards.extend(game.used_cards)
        game.used_cards.clear()
        game.random.shuffle(game.fresh_cards)
    return game.fresh_cards.pop()

def card_draw(player):
    """Draw a card and add it to player's hand."""
    card = card_draw_return(player.game)
    player.game.log("draw card {} {}", player, card)
    player.cards.append(card)

def card_discard(player, card):
    """Discard a single card of given type from player's hand.
    Returns true if succeeded, false if no such card exists."""
    if card in player.cards:
        player.cards.remove(card)
        player.game.used_cards.append(card)
        player.game.log("discard card {} {}", player, card)
        return True
    return False

class GameEndedException(Exception):
    """Exception which may be thrown anywhere during the game turn logic, to indicate that the game has ended."""
    pass

def card_play(player, card, target=None):
    """Play given card type from player's hand. If the card is targeted, target must be also specified.
    Return's true iff the card has been found in hand, played (and thus discarded).
    Contains the logic of cards."""
    log = player.game.log
    if card not in player.cards:
        log("{} can't play {} because it is not in their inventory", player, card)
        return False
    if (card.needs_target == (target is None)) or (target == player) or (target is not None and target.health <= 0):
        log("{} can't play {} because needs_target = {} and target is {}", player, card, card.needs_target, target)
        return False

    def consume_card(p, c):
        p.cards.remove(c)
        p.game.used_cards.append(c)

    def cause_damage(by_player, to_player):
        if to_player.health <= 0:
            log("Can't cause damage to {}, already dead", to_player)
            return
        to_player.health -= 1
        if to_player.health == 0:
            log("{} killed {}", by_player, to_player)
            by_player.cards.extend(to_player.cards)
            to_player.cards.clear()
        else:
            log("{} damaged {}", by_player, to_player)
        if len(by_player.game.players_in_game) <= 1:
            raise GameEndedException


    if card == Cards.BANG:
        if player.played_bang_this_turn:
            log("{} can't play {} because they already played bang this turn", player, card)
            return False
        log("{} shot after {}", player, target)
        consume_card(player, card)
        player.played_bang_this_turn = True
        response = target.brain.handle_threat(target, player, card)
        if response in target.cards and response in card.threat_response:
            # Missed
            log(" ... and missed")
            consume_card(target, response)
        else:
            # Hit
            log(" ... and hit")
            cause_damage(player, target)
        return True
    elif card == Cards.MANCATO:
        log("{} tried to dodge without reason", player)
        return False
    elif card == Cards.BIRRA:
        if player.health < player.max_health:
            player.health += 1
            consume_card(player, card)
            log("{} drank a beer", player)
            return True
        log("{} tried to drink a beer, but at full health", player)
        return False
    elif card == Cards.PANICO:
        if len(target.cards) != 0:
            consume_card(player, card)
            stolen = player.random.choice(target.cards)
            target.cards.remove(stolen)
            player.cards.append(stolen)
            log("{} has stolen {} from {}", player, stolen, target)
            return True
        log("{} tried to steal a card, but {} has no cards", player, target)
        return False
    elif card == Cards.CAT_BALOU:
        if len(target.cards) != 0:
            consume_card(player, card)
            stolen = player.random.choice(target.cards)
            target.cards.remove(stolen)
            player.game.used_cards.append(stolen)
            log("{} has discarded {} from {}", player, stolen, target)
            return True
        log("{} tried to discard a card, but {} has no cards", player, target)
        return False
    elif card == Cards.DUELLO:
        log("{} entered a duel with {}", player, target)
        consume_card(player, card)
        while True:
            # Target needs to shoot
            response = target.brain.handle_threat(player=target, from_player=player, threat_card=card)
            if response in target.cards and response in card.threat_response:
                # Did shoot
                consume_card(target, response)
                # Duel continues
            else:
                # Did not shoot, takes damage, duel ends
                log("{} has won the duel", player)
                cause_damage(player, target)
                return True
            # Initiator needs to shoot
            response = player.brain.handle_threat(player=player, from_player=target, threat_card=card)
            if response in player.cards and response in card.threat_response:
                # Did shoot
                consume_card(player, response)
                # Duel continues
            else:
                # Did not shoot, takes damage, duel ends
                log("{} has won the duel", target)
                cause_damage(by_player=target, to_player=player)
                return True
            # Both shot, duel loop repeats
    elif card == Cards.DILIGENZA:
        consume_card(player, card)
        card_draw(player)
        card_draw(player)
        log("{} got two cards from {}", player, card)
        return True
    elif card == Cards.EMPORIO:
        log("{} opened {}", player, card)
        consume_card(player, card)
        players = player.game.players_in_game
        emporio_cards = [card_draw_return(player.game) for _ in players]

        me_index = players.index(player)
        for index in range(len(players)):
            choosing_player = players[(index + me_index) % len(players)]
            selected = choosing_player.brain.emporio_pick(choosing_player, emporio_cards)
            if selected not in emporio_cards:
                selected = player.random.choice(emporio_cards)
            emporio_cards.remove(selected)
            choosing_player.cards.append(selected)
            log(" ... {} got {}", choosing_player, selected)
        return True
    elif card == Cards.INDIANI:
        log("{} called Indiani!", player)
        consume_card(player, card)
        for target in player.game.players_in_game_except(player):
            response = target.brain.handle_threat(target, player, card)
            if response in target.cards and response in card.threat_response:
                # Missed
                consume_card(target, response)
                log(" ... which missed {}", target)
            else:
                # Hit
                log(" ... which hit {}", target)
                cause_damage(player, target)
        return True
    elif card == Cards.WELLS_FARGO:
        consume_card(player, card)
        card_draw(player)
        card_draw(player)
        card_draw(player)
        log("{} got three cards from {}", player, card)
        return True
    elif card == Cards.GATLING:
        log("{} shot after all", player)
        consume_card(player, card)
        for target in player.game.players_in_game_except(player):
            response = target.brain.handle_threat(target, player, card)
            if response in target.cards and response in card.threat_response:
                # Missed
                consume_card(target, response)
                log(" ... and missed {}", target)
            else:
                # Hit
                log(" ... and hit {}",target)
                cause_damage(player, target)
        return True
    elif card == Cards.SALOON:
        consume_card(player, card)
        healed_count = 0
        for healed in player.game.players_in_game:
            if healed.health < healed.max_health:
                healed_count += 1
                healed.health += 1
        log(str(player)+" used saloon and healed {} players", healed_count)
        return True
    else:
        log(str(player)+" tried to use unknown card {}", card)
        return False
    raise NotImplementedError("Should never happen: {} played {} at {}", player, card, target)
pass

def simulate_game_round(game):
    """Simulate single round of running game"""
    try:
        for player in game.players:
            if player.health <= 0:
                continue
            game.log("Turn of "+str(player))
            player.played_bang_this_turn = False
            # Give two cards
            card_draw(player)
            card_draw(player)
            player.brain.simulate_turn(player)
            # Discard over limit cards
            over_limit = len(player.cards) - player.health
            if over_limit > 0:
                game.log("Player {} ended turn with too much cards, discarding randomly", player)
                for _ in range(over_limit):
                    card_discard(player, player.random.choice(player.cards))
    except GameEndedException:
        game.log("Game ended mid-turn")
        pass

def simulate_game(game, max_rounds=0):
    """Simulate whole game, from current state (start?) to finish, quitting early if the game takes longer than max_turns
    and max_turns is a meaningful value.
    Returns "rounds, winner", where rounds is the amount of rounds that was simulated and winner is the winning player
    (winner may be None)"""
    rounds = 0
    while len(game.players_in_game) >= 2:
        rounds += 1
        if 0 < max_rounds < rounds:
            game.log("Game completed: Too many turns")
            return rounds, None
        simulate_game_round(game)
    survivors = game.players_in_game
    if len(survivors) == 0:
        game.log("Game completed: No survivors")
        return rounds, None
    else:
        game.log("Game completed: {} won", survivors[0])
        return rounds, survivors[0]

class Game:
    """Instance represents a single match of simplified bang"""

    def __init__(self, logging, seed=None, *brains):
        """bool logging = enable logging to console?
        seed = seed for random number generator for this match, None for random seed
        brains = variable amount of brains, each representing one player which will be created"""
        self.fresh_cards = []
        self.used_cards = []
        self.logging = logging
        if seed is None:
            seed = 1
        self.random = random_package_not_thread_safe.Random(seed)
        for card in Cards.ALL:
            for i in range(card.deck_amount):
                self.fresh_cards.append(card)
        self.random.shuffle(self.fresh_cards)

        self.players = [Player(self, random_package_not_thread_safe.Random(seed + player_id), player_id, 4, brain) for brain, player_id in zip(brains, range(len(brains)))]
        for player in self.players:
            for _ in range(player.health):
                card_draw(player)

    def log(self, message_format, *args):
        """Log message with the same syntax as string.format has, only if game logging is enabled"""
        if self.logging:
            print(message_format.format(*args))

    @property
    def players_in_game(self):
        result = []
        for p in self.players:
            if p.health != 0:
                result.append(p)
        return result

    def players_in_game_except(self, except_player):
        result = []
        for p in self.players:
            if p.health != 0 and p != except_player:
                result.append(p)
        return result

