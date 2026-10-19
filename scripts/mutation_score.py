"""Fail when the mutmut score drops below the threshold.

Run after `mutmut run`: python scripts/mutation_score.py [threshold]
Score = killed / (killed + survived + no_tests), from mutants/mutmut-cicd-stats.json.
The threshold is a ratchet: only ever raise it (#70).
"""
import json
import subprocess
import sys

THRESHOLD = 85.0


def main(argv):
    threshold = float(argv[1]) if len(argv) > 1 else THRESHOLD
    subprocess.run(["mutmut", "export-cicd-stats"], check=True)
    with open("mutants/mutmut-cicd-stats.json") as f:
        stats = json.load(f)
    # Mutants no test reaches count against the score, like survivors.
    survived = stats["survived"] + stats["no_tests"]
    decided = stats["killed"] + survived
    if not decided:
        print("no mutants were run")
        return 1
    score = 100.0 * stats["killed"] / decided
    print(f"mutation score {score:.1f}% "
          f"({stats['killed']} killed, {survived} survived, "
          f"threshold {threshold}%)")
    return 0 if score >= threshold else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
