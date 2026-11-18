"""Offline quant interview practice. Run python practice.py --help for options."""
import argparse
import random
from dataclasses import dataclass
from uuid import uuid4

from bank import ROWS
from progress import history, record


@dataclass
class Drill:
    topic: str
    question: str
    choices: list[str]  # Correct answer first, shuffled at display time.
    hint: str
    solution: str
    discussion: str
    rubric: list[str]
    level: str = 'foundation'


def build_deck(rng):
    p = rng.choice([0.2, 0.3, 0.4])
    win = rng.choice([8, 10, 12])
    spread = rng.choice([4, 6, 8])
    premium = rng.choice([2, 3, 4])
    move = rng.choice([5, 7, 9])
    sigma = rng.choice([10, 14, 18])
    days = rng.choice([25, 100, 400])
    bounce = rng.choice([10, 20, 30])
    cards = [
        Drill("fills", f"Two orders each have an independent {p:.0%} chance of filling. What is the chance at least one fills?",
              [f"{x:.0%}" for x in (1-(1-p)**2, p*p, 2*p, (1-p)**2)],
              "Count the outcome where neither order fills.",
              f"Both miss with probability {1-p:.1f} squared. Subtract that from 1 to get {1-(1-p)**2:.0%}.",
              "Both orders sit on the same venue during a burst of buying. Can you still infer the chance of any fill from the two individual fill rates?",
              ["Use P(A or B) = P(A) + P(B) - P(A and B).",
               "A common flow shock can make the fills dependent. Estimate their joint rate or specify a dependence model."]),
        Drill("edge", f"A trade gains ${win} with probability 60% and loses $4 otherwise. The round-trip fee is $1. What is expected net profit?",
              [f"${x:.2f}" for x in (0.6*win-2.6, 0.6*win-1.6, 0.6*win-1, win-5)],
              "Write down both signed cash flows. The fee applies to either outcome.",
              f"Net expectation = 0.6 x {win} - 0.4 x 4 - 1 = ${0.6*win-2.6:.2f}.",
              "A strategy wins on 80% of trades. What else do you need to estimate its edge?",
              ["Estimate average gain on winners and average loss on losers; weight by their frequencies.",
               "Deduct fees, spread and slippage using realistic fills."]),
        Drill("execution", f"The bid and ask are {spread} cents apart. You buy at the ask with a stable midpoint. What is the one-way cost versus midpoint per share?",
              [f"{x:g} cents" for x in (spread/2, spread, 2*spread, 0)],
              "Place the midpoint halfway between the quotes.",
              f"The ask sits {spread}/2 = {spread/2:g} cents above the midpoint. Crossing back at the bid would cost another half-spread.",
              "A limit buy captures the spread on paper. Why might its realized result be worse?",
              ["A passive order can miss a favorable move because it never fills.",
               "Adverse selection can move fair value below the fill price. Measure post-fill markouts."]),
        Drill("options", f"You pay ${premium} per share for a call struck at $100. It expires with stock at ${100+move}. Ignoring costs, what is profit per share?",
              [f"${x}" for x in (move-premium, move, move+premium, -premium)],
              "First compute the exercise value, then account for the premium.",
              f"Exercise value is max({100+move} - 100, 0) = {move}. Subtract {premium} to get ${move-premium}.",
              "A long call expires in the money and the buyer loses money. Explain how both can hold.",
              ["The terminal stock price exceeds the strike, so exercise has positive value.",
               "If that value is smaller than the premium, net profit is negative. Break-even equals strike plus premium, ignoring financing and fees."]),
        Drill("inference", f"Daily P&L has standard deviation ${sigma}. Across {days} independent days, what is the standard error of average daily P&L?",
              [f"${x:.3g}" for x in (sigma/days**0.5, sigma, sigma/days, sigma*days**0.5)],
              "The variance of the average of n independent observations with equal variance is variance divided by n.",
              f"Take the square root to obtain {sigma}/sqrt({days}) = ${sigma/days**0.5:.3g}.",
              "Daily profits are positively autocorrelated. What goes wrong with the usual standard error of the mean?",
              ["Positive serial covariance adds to the variance of the sample mean. The independent-days formula can understate uncertainty.",
               "Use a dependence-aware estimate, such as a block bootstrap with an appropriate block length."]),
        Drill("returns", f"An account falls {bounce}% and then rises {bounce}%. What is the two-period return?",
              [f"{x:g}%" for x in (-bounce**2/100, 0, bounce, -bounce)],
              "Start with 100 dollars and apply the moves sequentially.",
              f"The final balance per 100 is 100 x {1-bounce/100:g} x {1+bounce/100:g} = {100-bounce**2/100:g}.",
              "Why does a 20% drawdown require a gain larger than 20% to recover?",
              ["After a fall from 100 to 80, returns are measured on the smaller base of 80.",
               "Recovering 20 dollars requires a gain of 20/80 = 25%."]),
        Drill("signals", "Of 1,000 sessions, 100 had a jump. A detector flagged 80 jump sessions and 180 quiet sessions. Given a flag, how likely was a jump?",
              ["30.8%", "80%", "10%", "18%"], "Restrict the sample to all flagged sessions.",
              "There were 260 flags, of which 80 were jumps. Precision is 80/260, about 30.8%.",
              "A detector catches most jumps, yet most alerts are false. How can that happen?",
              ["Recall measures the share of jumps detected. Precision measures the share of alerts that correspond to jumps.",
               "When jumps are rare, even a modest false-positive rate on quiet days can dominate the alert count."]),
        Drill("backtesting", "You compute a signal after Monday's closing auction using its final price. Which proposed fill is defensible?",
              ["Tuesday's executable quote after routing", "Monday's opening price", "Monday's auction price using the completed signal", "The best price seen on Monday"],
              "Order the information, decision and execution timestamps.",
              "The signal exists only after the auction. Tuesday's quote can support a fill if size, latency and execution costs are modeled.",
              "How would you test whether choosing the best of 200 parameter sets produced a misleading Sharpe ratio?",
              ["Select parameters using training or validation data in chronological order.",
               "Freeze the choice before evaluating on an untouched later period. Repeated tuning on that period turns it into validation data."])
    ]


    for card in cards:
        if card.topic in ("inference", "signals", "backtesting"):
            card.level = "intermediate"
    cards.extend(Drill(topic, *fields, level=level) for level, topic, *fields in ROWS)
    return cards


def get_card(topic, seed):
    return next(card for card in build_deck(random.Random(seed)) if card.topic == topic)


def ask(card, mode, rng):
    print(f"\n[{card.topic}]")
    if mode == "open":
        print(card.discussion)
        while True:
            response = input("Your reasoning (or quit)> ").strip()
            if response.lower() == "quit":
                return None
            if response:
                break
        print("\nCompare your reasoning:")
        for point in card.rubric:
            print(" -", point)
        while True:
            rating = input("Did you cover both points? [y/n/quit] ").strip().lower()
            if rating in ("y", "n", "quit"):
                return None if rating == "quit" else rating == "y"
    print(card.question)
    options = rng.sample(card.choices, len(card.choices))
    for letter, option in zip("ABCD", options):
        print(f"  {letter}. {option}")
    while True:
        reply = input("Answer [A-D / hint / quit]> ").strip().upper()
        if reply == "QUIT":
            return None
        if reply == "HINT":
            print(card.hint)
        elif reply in ("A", "B", "C", "D"):
            correct = options[ord(reply)-ord("A")] == card.choices[0]
            print("Correct." if correct else f"Answer: {card.choices[0]}.", card.solution)
            return correct
        else:
            print("Enter one of the displayed letters, hint or quit.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["mixed", "mcq", "open"], default="mixed")
    parser.add_argument("--topic", choices=[c.topic for c in build_deck(random.Random(0))])
    parser.add_argument("--level", choices=["foundation", "intermediate", "advanced"])
    parser.add_argument("--review", action="store_true", help="retry currently missed prompts")
    parser.add_argument("--count", type=int, default=6)
    parser.add_argument("--seed", type=int, help="replay a session")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("count must be positive")
    rng = random.Random(args.seed)
    results = []
    deck = []
    print("Quant interview practice | Type quit to end a round.")
    try:
        missed = [(topic, mode, row["seed"]) for (topic, mode), row in history().items()
                  if not row["correct"] and (args.mode == "mixed" or args.mode == mode)
                  and (not args.topic or args.topic == topic)
                  and (not args.level or get_card(topic, row["seed"]).level == args.level)]
        rng.shuffle(missed)
        for i in range(args.count):
            if args.review:
                if not missed:
                    print("No more missed questions matching these filters.")
                    break
                topic, mode, seed = missed.pop()
                card = get_card(topic, seed)
            else:
                if not deck:
                    seed = rng.randrange(2**32)
                    deck = [c for c in build_deck(random.Random(seed))
                            if (not args.topic or c.topic == args.topic)
                            and (not args.level or c.level == args.level)]
                    rng.shuffle(deck)
                if not deck:
                    print("No questions match these filters.")
                    break
                card = deck.pop()
                mode = ("mcq", "open")[i % 2] if args.mode == "mixed" else args.mode
            result = ask(card, mode, rng)
            if result is None:
                break
            record(uuid4().hex, card.topic, mode, seed, result)
            results.append((mode, card.topic, result))
    except (EOFError, KeyboardInterrupt):
        pass
    for mode, label in [("mcq", "Multiple choice"), ("open", "Self-graded reasoning")]:
        scores = [score for kind, _, score in results if kind == mode]
        if scores:
            print(f"{label}: {sum(scores)}/{len(scores)}")
    missed = sorted({topic for _, topic, score in results if not score})
    if missed:
        print("Revisit with --topic:", ", ".join(missed))


if __name__ == "__main__":
    main()
