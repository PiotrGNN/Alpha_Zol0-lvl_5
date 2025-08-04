# analyze_log.py – Analiza skuteczności decyzji AI na podstawie decision_log.csv
import csv
from collections import Counter
from datetime import datetime


def analyze_decision_log(log_path="autopsy/decision_log.csv"):
    decisions = []
    with open(log_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                timestamp, decision = row[0], row[1]
                decisions.append((timestamp, decision))
    total = len(decisions)
    counter = Counter([d[1] for d in decisions])
    print(f"Liczba decyzji AI: {total}")
    for k, v in counter.items():
        print(f"{k}: {v} ({v/total:.2%})")
    # Analiza trendu decyzji w czasie
    if total > 1:
        first = datetime.fromisoformat(decisions[0][0])
        last = datetime.fromisoformat(decisions[-1][0])
        print(f"Zakres logów: {first} – {last}")


if __name__ == "__main__":
    analyze_decision_log()
