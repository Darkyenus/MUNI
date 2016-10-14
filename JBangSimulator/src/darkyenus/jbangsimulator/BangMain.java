package darkyenus.jbangsimulator;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static darkyenus.jbangsimulator.BangSimulator.*;


/**
 *
 */
public class BangMain {
    public static void compare(int runs, boolean log, AbstractBrain...brains) {
        final long startTime = System.currentTimeMillis();
        final Map<AbstractBrain, Integer> scores = new HashMap<>();
        final List<AbstractBrain[]> fightPairs = new ArrayList<>();

        for (int brain1 = 0; brain1 < brains.length; brain1++) {
            for (int brain2 = brain1+1; brain2 < brains.length; brain2++) {
                fightPairs.add(new AbstractBrain[]{brains[brain1], brains[brain2]});
                fightPairs.add(new AbstractBrain[]{brains[brain2], brains[brain1]});
            }
        }

        for (AbstractBrain[] fightPair : fightPairs) {
            for (int run = 0; run < runs; run++) {
                final Player winner = simulateGame(new Game(log, run, fightPair[0], fightPair[1]));
                if(winner != null) {
                    scores.put(winner.brain, scores.getOrDefault(winner.brain, 0) + 1);
                }
            }
        }

        final float elapsedTime = (System.currentTimeMillis() - startTime) /1000f;
        System.out.println("Simulated "+(fightPairs.size() * runs)+" runs in "+(elapsedTime)+" seconds ("+((fightPairs.size() * runs)/elapsedTime)+" runs per second)");

        scores.entrySet().stream()
                .sorted((entry1, entry2) -> entry1.getValue() - entry2.getValue())
                .forEachOrdered(entry -> System.out.println(entry.getKey()+" with "+entry.getValue()+" victories"));
    }

    public static void compareParallel(int runs, boolean log, AbstractBrain...brains) {
        final long startTime = System.currentTimeMillis();
        final Map<AbstractBrain, AtomicInteger> scores = new HashMap<>();
        final List<AbstractBrain[]> fightPairs = new ArrayList<>();

        for (int brain1 = 0; brain1 < brains.length; brain1++) {
            scores.put(brains[brain1], new AtomicInteger(0));
            for (int brain2 = brain1+1; brain2 < brains.length; brain2++) {
                fightPairs.add(new AbstractBrain[]{brains[brain1], brains[brain2]});
                fightPairs.add(new AbstractBrain[]{brains[brain2], brains[brain1]});
            }
        }

        final ForkJoinPool pool = new ForkJoinPool(Runtime.getRuntime().availableProcessors()-1);

        for (AbstractBrain[] fightPair : fightPairs) {
            for (int run = 0; run < runs; run++) {
                final int runSeed = run;
                pool.execute(() -> {
                    final Player winner = simulateGame(new Game(log, runSeed, fightPair[0], fightPair[1]));
                    if(winner != null) {
                        scores.get(winner.brain).incrementAndGet();
                    }
                });

            }
        }
        if (!pool.awaitQuiescence(5, TimeUnit.MINUTES)) {
            System.err.println("Timed out");
        }

        final float elapsedTime = (System.currentTimeMillis() - startTime) /1000f;
        System.out.println("Simulated "+(fightPairs.size() * runs)+" runs in "+(elapsedTime)+" seconds ("+((fightPairs.size() * runs)/elapsedTime)+" runs per second)");

        scores.entrySet().stream()
                .sorted((entry1, entry2) -> entry1.getValue().get() - entry2.getValue().get())
                .forEachOrdered(entry -> System.out.println(entry.getKey()+" with "+entry.getValue().get()+" victories"));
    }

    public static void main(String[] args){
        compareParallel(10_000, false,
                new BangBrains.CustomisablyResponsiveBrain(),
                new BangBrains.CustomisablyResponsiveBrain("HealingLater",
                        BangBrains.CustomisablyResponsiveBrain::actionOpenBoxes,
                        BangBrains.CustomisablyResponsiveBrain::actionGoShopping,
                        BangBrains.CustomisablyResponsiveBrain::actionDoStealing,
                        BangBrains.CustomisablyResponsiveBrain::actionDoDestroying,
                        BangBrains.CustomisablyResponsiveBrain::actionDoHealingSelf,
                        BangBrains.CustomisablyResponsiveBrain::actionIndiani,
                        BangBrains.CustomisablyResponsiveBrain::actionDoHealingAll,
                        BangBrains.CustomisablyResponsiveBrain::actionGatling,
                        BangBrains.CustomisablyResponsiveBrain::actionBang,
                        BangBrains.CustomisablyResponsiveBrain::actionDuel
                        ));
    }
}
