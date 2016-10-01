package darkyenus.jbangsimulator;

import java.util.*;
import java.util.function.Consumer;

/**
 *
 */
public class BangSimulator {
    public enum Card {
        BANG("Bang!", 25, true),
        MANCATO("Mancato!", 12),
        BIRRA("Birra", 6),
        PANICO("Panico!", 4, true),
        CAT_BALOU("Cat Balou", 4, true),
        DUELLO("Duello", 3, true),
        DILIGENZA("Diligenza", 2),
        EMPORIO("Emporio", 2),
        INDIANI("Indiani!", 2),
        WELLS_FARGO("Wells Fargo", 1),
        GATLING("Gatling", 1),
        SALOON("Saloon", 1)
        ;

        public final String name;
        public final int deckAmount;
        public final boolean needsTarget;
        public final List<Card> threatResponse = new ArrayList<>(2);

        Card(String name, int deckAmount, boolean needsTarget) {
            this.name = name;
            this.deckAmount = deckAmount;
            this.needsTarget = needsTarget;
        }

        Card(String name, int deckAmount) {
            this(name, deckAmount, false);
        }

        @Override
        public String toString() {
            return name;
        }

        public static final Card[] ALL = values();

        static {
            BANG.threatResponse.add(MANCATO);
            GATLING.threatResponse.add(MANCATO);
            INDIANI.threatResponse.add(BANG);
            INDIANI.threatResponse.add(GATLING);
            DUELLO.threatResponse.add(BANG);
            DUELLO.threatResponse.add(GATLING);
        }
    }

    public static abstract class AbstractBrain {

        /**
         * Call playCard in this method to simulate player's turn.
         */
        public abstract void simulateTurn(Player player);

        /**
         * Called when player is in danger and needs to respond.
         * @param fromPlayer which player is threatening this player
         * @param threatCard card threatening with
         * @return which type of card should be used to respond or null to not respond
         */
        public abstract Card handleThreat(Player player, Player fromPlayer, Card threatCard);

        /**
         * Called when emporio is open and player must pick one card.
         # Must not modify `selection`, but should return one of the cards in selection.
         # If returned card is not in selection or null is returned, random card is picked.
         */
        public abstract Card emporioPick(Player player, List<Card> selection);

        @Override
        public String toString() {
            return getClass().getSimpleName();
        }
    }

    public static final class Player {

        public final Game game;
        public final Random random;
        public final int playerId;
        public final int maxHealth;
        public final AbstractBrain brain;

        public int health;
        public final List<Card> cards = new ArrayList<>();
        public boolean playedBangThisTurn = false;

        public Player(Game game, Random random, int playerId, int health, AbstractBrain brain) {
            this.game = game;
            this.random = random;
            this.playerId = playerId;
            this.maxHealth = health;
            this.brain = brain;

            this.health = health;
        }

        public boolean hasCards() {
            return !cards.isEmpty();
        }

        public int countCards() {
            return cards.size();
        }

        @Override
        public String toString() {
            return "Player "+playerId+" "+health+"/"+maxHealth;
        }
    }

    public static Card cardDrawReturn(Game game) {
        if(game.freshCards.isEmpty()) {
            game.freshCards.addAll(game.usedCards);
            game.usedCards.clear();
            Collections.shuffle(game.freshCards, game.random);
        }
        return game.freshCards.remove(game.freshCards.size()-1);
    }

    public static void cardDraw(Player player) {
        final Card card = cardDrawReturn(player.game);
        player.game.log("draw card "+player+" "+card);
        player.cards.add(card);
    }

    public static boolean cardDiscard(Player player, Card card) {
        if(player.cards.remove(card)) {
            player.game.usedCards.add(card);
            player.game.log("discard card "+player+" "+card);
            return true;
        } else return false;
    }

    public static final class GameEndedException extends RuntimeException {
        protected GameEndedException(String message) {
            super(message, null, false, true);
        }
    }

    public static final class Game {
        public final List<Card> freshCards = new ArrayList<>();
        public final List<Card> usedCards = new ArrayList<>();
        public final List<Player> players = new ArrayList<>();
        public final boolean logging;
        public final Random random;

        public Game(boolean logging, long seed, AbstractBrain...brains) {
            this.logging = logging;
            this.random = new Random(seed);
            for (Card card : Card.ALL) {
                for (int i = 0; i < card.deckAmount; i++) {
                    freshCards.add(card);
                }
            }
            Collections.shuffle(freshCards, random);
            for (int playerId = 0; playerId < brains.length; playerId++) {
                final Player player = new Player(this, new Random(seed + playerId), playerId, 4, brains[playerId]);
                players.add(player);
                for (int i = 0; i < player.health; i++) {
                    cardDraw(player);
                }
            }
        }

        public void log(CharSequence message) {
            if(logging) {
                System.out.println(message);
            }
        }

        public List<Player> playersInGame() {
            final List<Player> result = new ArrayList<>();
            for (Player player : players) {
                if(player.health > 0) {
                    result.add(player);
                }
            }
            return result;
        }

        public List<Player> playersInGameExcept(Player except) {
            final List<Player> result = new ArrayList<>();
            for (Player player : players) {
                if(player.health > 0 && !player.equals(except)) {
                    result.add(player);
                }
            }
            return result;
        }
    }

    public static boolean cardPlay(Player player, Card card) {
        return cardPlay(player, card, null);
    }

    private static void cardPlay_consumeCard(Player player, Card card) {
        player.cards.remove(card);
        player.game.usedCards.add(card);
    }

    private static void cardPlay_causeDamage(Player byPlayer, Player toPlayer) {
        if(toPlayer.health <= 0) {
            byPlayer.game.log("Can't cause damage to "+toPlayer+", already dead");
            return;
        }
        toPlayer.health -= 1;
        if(toPlayer.health == 0) {
            byPlayer.game.log(byPlayer+" killed "+toPlayer);
            byPlayer.cards.addAll(toPlayer.cards);
            toPlayer.cards.clear();
            if (byPlayer.game.playersInGame().size() <= 1){
                throw new GameEndedException("All opponents are dead");
            }
        } else {
            byPlayer.game.log(byPlayer+" damaged "+toPlayer);
        }
    }

    public static boolean cardPlay(Player player, Card card, Player target) {
        final Consumer<CharSequence> log = player.game::log;
        if(!player.cards.contains(card)) {
            log.accept(player+" can't play "+card+" because it is not in their inventory");
            return false;
        }
        if((card.needsTarget == (target == null)) || (target == player) || (target != null && target.health <= 0)) {
            log.accept(player+" can't play "+card+" because needs_target = "+card.needsTarget+" and target is "+target);
            return false;
        }

        switch (card) {
            case BANG:{
                if(player.playedBangThisTurn) {
                    log.accept(player+" can't play "+card+" because they already played bang this turn");
                    return false;
                }
                log.accept(player+" shot after "+target);
                cardPlay_consumeCard(player, card);
                player.playedBangThisTurn = true;
                final Card response = target.brain.handleThreat(target, player, card);
                if(target.cards.contains(response) && card.threatResponse.contains(card)) {
                    //Missed
                    log.accept(" ... and missed");
                    cardPlay_consumeCard(target, response);
                } else {
                    //Hit
                    log.accept(" ... and hit");
                    cardPlay_causeDamage(player, target);
                }
                return true;
            }
            case MANCATO:{
                log.accept(player+" tried to dodge without reason");
                return false;
            }
            case BIRRA:{
                if(player.health < player.maxHealth) {
                    player.health += 1;
                    cardPlay_consumeCard(player, card);
                    log.accept(player+" drank a beer");
                    return true;
                } else {
                    log.accept(player+" tried to drink a beer, but at full health");
                    return false;
                }
            }
            case PANICO:{
                if(!target.cards.isEmpty()) {
                    cardPlay_consumeCard(player, card);
                    final Card stolen = randomChoice(target.cards, player.random);
                    target.cards.remove(stolen);
                    player.cards.add(stolen);
                    log.accept(player+" has stolen "+stolen+" from "+target);
                    return true;
                } else {
                    log.accept(player+" tried to steal a card, but "+target+" has no cards");
                    return false;
                }
            }
            case CAT_BALOU:{
                if(!target.cards.isEmpty()) {
                    cardPlay_consumeCard(player, card);
                    final Card stolen = randomChoice(target.cards, player.random);
                    target.cards.remove(stolen);
                    player.game.usedCards.add(stolen);
                    log.accept(player+" has discarded "+stolen+" from "+target);
                    return true;
                } else {
                    log.accept(player+" tried to discard a card, but "+target+" has no cards");
                    return false;
                }
            }
            case DUELLO:{
                log.accept(player+" entered a duel with "+target);
                cardPlay_consumeCard(player, card);
                while(true){
                    //Target needs to shoot
                    {
                        final Card response = target.brain.handleThreat(target, player, card);
                        if(target.cards.contains(response) && card.threatResponse.contains(response)) {
                            //Did shoot
                            cardPlay_consumeCard(target, response);
                            //Duel continues
                        } else {
                            //Did not shoot, takes damage, duel ends
                            log.accept(player+" has won the duel");
                            cardPlay_causeDamage(player, target);
                            return true;
                        }
                    }
                    //Initiator needs to shoot
                    {
                        final Card response = player.brain.handleThreat(player, target, card);
                        if(player.cards.contains(response) && card.threatResponse.contains(response)) {
                            //Did shoot
                            cardPlay_consumeCard(player, response);
                            //Duel continues
                        } else {
                            //Did not shoot, takes damage, duel ends
                            log.accept(target+" has won the duel");
                            cardPlay_causeDamage(target, player);
                            return true;
                        }
                    }
                    //Both shot, duel loop repeats
                }
            }
            case DILIGENZA:{
                cardPlay_consumeCard(player, card);
                cardDraw(player);
                cardDraw(player);
                log.accept(player+" got two cards from "+card);
                return true;
            }
            case EMPORIO:{
                log.accept(player+" opened "+card);
                cardPlay_consumeCard(player, card);
                final List<Player> players = player.game.playersInGame();
                final List<Card> emporioCards = new ArrayList<>(players.size());
                for (int i = 0; i < players.size(); i++) {
                    emporioCards.add(cardDrawReturn(player.game));
                }
                final int meIndex = players.indexOf(player);
                for (int i = 0; i < players.size(); i++) {
                    final Player choosingPlayer = players.get((i + meIndex) % players.size());
                    Card selected = choosingPlayer.brain.emporioPick(choosingPlayer, emporioCards);
                    if(!emporioCards.contains(selected)) {
                        selected = randomChoice(emporioCards, choosingPlayer.random);
                    }
                    emporioCards.remove(selected);
                    choosingPlayer.cards.add(selected);
                    log.accept(" ... "+choosingPlayer+" got "+selected);
                }
                return true;
            }
            case INDIANI:{
                log.accept(player+" called Indiani!");
                cardPlay_consumeCard(player, card);
                for (Player iTarget : player.game.playersInGameExcept(player)) {
                    final Card response = iTarget.brain.handleThreat(iTarget, player, card);
                    if(iTarget.cards.contains(response) && card.threatResponse.contains(response)) {
                        //Missed
                        cardPlay_consumeCard(iTarget, response);
                        log.accept(" ... which missed "+iTarget);
                    } else {
                        //Hit
                        log.accept(" ... which hit "+iTarget);
                        cardPlay_causeDamage(player, iTarget);
                    }
                }
                return true;
            }
            case WELLS_FARGO:{
                cardPlay_consumeCard(player, card);
                cardDraw(player);
                cardDraw(player);
                cardDraw(player);
                log.accept(player+" got three cards from "+card);
                return true;
            }
            case GATLING:{
                log.accept(player+" shot after all");
                cardPlay_consumeCard(player, card);
                for (Player iTarget : player.game.playersInGameExcept(player)) {
                    final Card response = iTarget.brain.handleThreat(iTarget, player, card);
                    if(iTarget.cards.contains(response) && card.threatResponse.contains(response)) {
                        //Missed
                        cardPlay_consumeCard(iTarget, response);
                        log.accept(" ... and missed "+iTarget);
                    } else {
                        //Hit
                        log.accept(" ... and hit "+iTarget);
                        cardPlay_causeDamage(player, iTarget);
                    }
                }
                return true;
            }
            case SALOON:{
                cardPlay_consumeCard(player, card);
                int healedCount = 0;
                for (Player healed : player.game.playersInGame()) {
                    if(healed.health < healed.maxHealth) {
                        healed.health += 1;
                        healedCount++;
                    }
                }
                log.accept(player+" used saloon and healed "+healedCount+" players");
                return true;
            }
            default: {
                throw new IllegalArgumentException(player+" tried to use unknown card "+card);
            }
        }
    }

    public static void simulateGameRound(Game game) {
        try {
            for (Player player : game.players) {
                if(player.health <= 0){
                    continue;
                }
                game.log("Turn of "+player);
                player.playedBangThisTurn = false;
                //Give two cards
                cardDraw(player);
                cardDraw(player);
                //Simulate
                player.brain.simulateTurn(player);
                //Discard over limit cards
                final int overLimit = player.cards.size() - player.health;
                if(overLimit > 0){
                    game.log("Player "+player+" ended turn with too much cards, discarding randomly");
                    for (int i = 0; i < overLimit; i++) {
                        cardDiscard(player, randomChoice(player.cards, player.random));
                    }
                }
            }
        } catch (GameEndedException ex) {
            game.log("Game ended mid-turn ("+ex.getMessage()+")");
        }
    }

    public static Player simulateGame(Game game) {
        int rounds = 0;
        while(game.playersInGame().size() >= 2) {
            rounds++;
            simulateGameRound(game);
        }
        final List<Player> survivors = game.playersInGame();
        if(survivors.size() == 0) {
            game.log("Game completed ("+rounds+" rounds): No survivors");
            return null;
        } else {
            game.log("Game completed ("+rounds+" rounds): "+survivors.get(0)+" won");
            return survivors.get(0);
        }
    }

    public static <T> T randomChoice(List<T> from, Random random) {
        if(from.isEmpty()) return null;
        return from.get(random.nextInt(from.size()));
    }
}