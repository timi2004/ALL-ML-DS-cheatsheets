# Quant interview practice

Double-click **Start practice desk.cmd** for the browser interface, or run `python desk.py`. Set a difficulty, format and topic. Select **Review** to retry the exact prompts you missed. A correct retry clears the prompt from the queue and preserves earlier attempts in your accuracy. Open responses use a two-point self-grade. The desk runs on localhost and shares a SQLite tracker with the terminal. On Windows the database lives in `%LOCALAPPDATA%/QuantPractice/progress.sqlite3`. Keeping this file preserves your progress across restarts. Close the server window to stop the desk.

For the terminal, double-click **Start practice.cmd** for a six-question mixed round. The trainer runs offline with Python 3.9 or newer. Enter a letter for a multiple-choice question or type your reasoning for an open question. After an open answer, compare it with the two rubric points and score yourself. Each round ends with separate scores and topics to revisit.

From this directory:

```powershell
python practice.py --mode mixed --count 8
python practice.py --mode mcq --topic execution --count 3
python practice.py --mode open --level advanced --count 4
python practice.py --review --count 10
```

Each of the 22 topics has a calculation or decision question and an open interview prompt. Several calculations draw fresh numbers each round. Use `--seed 17` to replay a session, `hint` during a multiple-choice question, or `quit` to finish early.

## Concepts

Open **Concepts** in the browser desk for nine lessons across the three difficulty levels. Choose a scenario to recalculate each worked example, expand the follow-up to check your reasoning, or select **Practice this concept** to answer a scored question on the same topic.

## Worked notebooks

1. [Probability and edge](01_probability_and_edge.ipynb) asks when a detector's alert is worth trading. Change the jump rate and watch both precision and expected profit change. [Run in Colab](https://colab.research.google.com/github/timi2004/ALL-ML-DS-cheatsheets/blob/quant-practice/quant/01_probability_and_edge.ipynb)
2. [Execution and backtests](02_execution_and_backtests.ipynb) follows a forecast through the spread, fees and execution clock. Change a signal and identify which day's P&L it affects. [Run in Colab](https://colab.research.google.com/github/timi2004/ALL-ML-DS-cheatsheets/blob/quant-practice/quant/02_execution_and_backtests.ipynb)

Both notebooks include saved outputs and run in Jupyter or Colab with a Python 3 kernel. The exercises are original. For related material in the repository, see [Probability cheatsheet](../Probability%20cheatsheet.pdf), [Fifty Challenging Problems in Probability](../Fifty_Challenging_Problems_in_Probability.pdf), and [time series analysis in python](../time%20series%20analysis%20in%20python.pdf).
