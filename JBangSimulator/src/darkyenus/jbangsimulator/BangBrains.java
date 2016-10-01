package darkyenus.jbangsimulator;

import darkyenus.jbangsimulator.BangSimulator.*;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static darkyenus.jbangsimulator.BangSimulator.Card.*;
import static darkyenus.jbangsimulator.BangSimulator.*;

/**
 *
 */
public class BangBrains {
    public static class HumanBrain extends AbstractBrain {

        private void showList(List<?> items) {
            for (int i = 0; i < items.size(); i++) {
                System.out.println(i+") "+items.get(i));
            }
        }

        private <T> T inputPick(List<T> selection, String noun) {
            showList(selection);
            while(true) {
                final String response = System.console().readLine("Pick %s number? > ", noun);
                try {
                    final int pick = Integer.parseInt(response);
                    if(pick < 1 || pick > selection.size()) {
                        System.out.println("Must pick a valid number from 1 to "+selection.size());
                    } else {
                        return selection.get(pick - 1);
                    }
                } catch (NumberFormatException ex) {
                    System.out.println("No "+noun+" picked");
                    return null;
                }
            }
        }

        @Override
        public void simulateTurn(Player player) {
            System.out.println("\nYour turn, human playing as "+ player +"!");
            while(true) {
                System.out.println("What will you play?");
                final Card picked = inputPick(player.cards, "card");
                if(picked == null) break;
                Player target = null;
                if(picked.needsTarget) {
                    target = inputPick(player.game.playersInGameExcept(player), "target");
                    if(target == null) {
                        continue;
                    }
                }
                cardPlay(player, picked, target);
            }
            while(player.cards.size() > player.health) {
                System.out.println("Too many cards in inventory. Which one do you want to discard?");
                final Card picked = inputPick(player.cards, "card");
                if(picked == null) {
                    break;
                } else {
                    cardDiscard(player, picked);
                }
            }
            System.out.println("Turn complete");
        }

        @Override
        public Card handleThreat(Player player, Player fromPlayer, Card threatCard) {
            final List<Card> possibleResponses = new ArrayList<>();
            for (Card card : threatCard.threatResponse) {
                if(player.cards.contains(card)) {
                    possibleResponses.add(card);
                }
            }
            if(possibleResponses.isEmpty()) {
                System.out.println((player)+"! You are threatened by "+(threatCard)+" played by "+(fromPlayer)+"! But you don't have a response...");
                return null;
            } else {
                System.out.println((player)+"! You are threatened by "+(threatCard)+" played by "+(fromPlayer)+"! Select a response!");
                return inputPick(possibleResponses, "response");
            }
        }

        @Override
        public Card emporioPick(Player player, List<Card> selection) {
            if(selection.size() == 1) {
                System.out.println((player)+"! You picked up "+selection.get(0)+" from emporio sale as it was the last item");
                return selection.get(0);
            } else {
                System.out.println((player)+"! Emporio sale is in town! Select a ware!");
                return inputPick(selection, "emporio pick");
            }
        }
    }

    public static final class SittingDuckBrain extends AbstractBrain {

        @Override
        public void simulateTurn(Player player) {
        }

        @Override
        public Card handleThreat(Player player, Player fromPlayer, Card threatCard) {
            return null;
        }

        @Override
        public Card emporioPick(Player player, List<Card> selection) {
            return null;
        }
    }

    public static abstract class ResponsiveBrain extends AbstractBrain {
        @Override
        public Card handleThreat(Player player, Player fromPlayer, Card threatCard) {
            for (Card possibleResponse : threatCard.threatResponse) {
                if(player.cards.contains(possibleResponse)) {
                    return possibleResponse;
                }
            }
            return null;
        }

        @Override
        public Card emporioPick(Player player, List<Card> selection) {
            if(player.health < player.maxHealth && selection.contains(BIRRA)) {
                return BIRRA;
            }
            if(!player.cards.contains(MANCATO) && selection.contains(MANCATO)) {
                return MANCATO;
            }
            if(player.health <= 2) {
                for (Card maybeCard : new Card[]{WELLS_FARGO, DILIGENZA, SALOON, MANCATO}) {
                    if(selection.contains(maybeCard)) {
                        return maybeCard;
                    }
                }
            }
            if(Collections.frequency(player.cards, BANG) > 2 && selection.contains(DUELLO) && !player.cards.contains(DUELLO)) {
                return DUELLO;
            }
            for (Card maybeCard : new Card[]{WELLS_FARGO, GATLING, DILIGENZA, PANICO, BIRRA, CAT_BALOU, MANCATO, BANG}) {
                if(selection.contains(maybeCard)) {
                    return maybeCard;
                }
            }
            return null;
        }
    }

    public static class RandomResponsiveBrain extends ResponsiveBrain {

        @Override
        public void simulateTurn(Player player) {
            final int cardsToPlay = player.random.nextInt((int) (player.cards.size() * 1.5f)) + 1;
            for (int i = 0; i < cardsToPlay; i++) {
                if(player.cards.isEmpty()) break;
                final Card card = randomChoice(player.cards, player.random);
                Player target = null;
                if(card.needsTarget) {
                    target = randomChoice(player.game.playersInGameExcept(player), player.random);
                }
                cardPlay(player, card, target);
            }
        }
    }

    public static class CustomisablyResponsiveBrain extends ResponsiveBrain {

        public final String name;
        public final BrainAction[] actionQueue;

        public CustomisablyResponsiveBrain(String name, BrainAction...actionQueue) {
            this.name = name;
            this.actionQueue = actionQueue;
        }

        public CustomisablyResponsiveBrain() {
            this("MildlyResponsiveBrain",
                    CustomisablyResponsiveBrain::actionOpenBoxes,
                    CustomisablyResponsiveBrain::actionGoShopping,
                    CustomisablyResponsiveBrain::actionDoStealing,
                    CustomisablyResponsiveBrain::actionDoDestroying,
                    CustomisablyResponsiveBrain::actionDoHealingSelf,
                    CustomisablyResponsiveBrain::actionDoHealingAll,
                    CustomisablyResponsiveBrain::actionIndiani,
                    CustomisablyResponsiveBrain::actionGatling,
                    CustomisablyResponsiveBrain::actionBang,
                    CustomisablyResponsiveBrain::actionDuel);
        }

        private static Player pickPlayerToStealFrom(Player player) {
            final List<Player> players = player.game.playersInGameExcept(player);
            Collections.shuffle(players, player.random);
            for (Player p : players) {
                if(p.hasCards()) {
                    return p;
                }
            }
            return null;
        }

        public static boolean actionOpenBoxes(Player player) {
            if(player.cards.contains(WELLS_FARGO)) {
                return cardPlay(player, WELLS_FARGO);
            }
            if(player.cards.contains(DILIGENZA)) {
                return cardPlay(player, DILIGENZA);
            }
            return false;
        }

        public static boolean actionGoShopping(Player player) {
            if(player.cards.contains(EMPORIO)) {
                return cardPlay(player, EMPORIO);
            }
            return false;
        }

        public static boolean actionDoStealing(Player player) {
            if(player.cards.contains(PANICO)) {
                final Player toStealFrom = pickPlayerToStealFrom(player);
                if(toStealFrom != null) {
                    return cardPlay(player, PANICO, toStealFrom);
                }
            }
            return false;
        }

        public static boolean actionDoDestroying(Player player) {
            if(player.cards.contains(CAT_BALOU)) {
                final Player toStealFrom = pickPlayerToStealFrom(player);
                if(toStealFrom != null) {
                    return cardPlay(player, CAT_BALOU, toStealFrom);
                }
            }
            return false;
        }

        public static boolean actionDoHealingSelf(Player player) {
            if(player.health < player.maxHealth && player.cards.contains(BIRRA)) {
                return cardPlay(player, BIRRA);
            }
            return false;
        }

        public static boolean actionDoHealingAll(Player player) {
            if(player.health < 2 && player.cards.contains(SALOON)) {
                return cardPlay(player, SALOON);
            }
            return false;
        }

        public static boolean actionIndiani(Player player) {
            if(player.cards.contains(INDIANI)) {
                return cardPlay(player, INDIANI);
            }
            return false;
        }

        public static boolean actionGatling(Player player) {
            if(player.cards.contains(GATLING)) {
                return cardPlay(player, GATLING);
            }
            return false;
        }

        public static boolean actionBang(Player player) {
            if(player.cards.contains(BANG)) {
                final List<Player> targets = player.game.playersInGameExcept(player);
                targets.sort((o1, o2) -> o1.health - o2.health);//TODO Check if correct order
                return cardPlay(player, BANG, targets.get(0));
            }
            return false;
        }

        public static boolean actionDuel(Player player) {
            if(player.cards.contains(DUELLO)) {
                final int myBangs = Collections.frequency(player.cards, BANG) + Collections.frequency(player.cards, GATLING);
                final List<Player> targets = player.game.playersInGameExcept(player);
                targets.sort((o1, o2) -> o1.health - o2.health);//TODO Check if correct order
                for (Player target : targets) {
                    if(target.countCards() - 1 < myBangs) {
                        return cardPlay(player, DUELLO, target);
                    }
                }
            }
            return false;
        }


        @Override
        public void simulateTurn(Player player) {
            while(true) {
                boolean didSomething = false;
                for (BrainAction action : actionQueue) {
                    while(action.act(player)) {
                        didSomething = true;
                    }
                }
                if(!didSomething) {
                    break;
                }
            }
        }

        @Override
        public String toString() {
            return super.toString()+": "+name;
        }

        @FunctionalInterface
        public interface BrainAction {
            boolean act(Player me);
        }
    }
}
