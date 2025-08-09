#!/usr/bin/env python3
"""
NASA Signal Decoder - Deciphering Messages from Planet Dyslexia
Class-based monoalphabetic substitution solver for the given alien signal.
"""

import sys
import random
from collections import Counter
from typing import Dict, List, Tuple

# --------------------
# CONFIGURATION
# --------------------
WINDOW_LEN = 721
PREFILTER_TOP = 400
HILLCLIMB_RESTARTS = 40
HILLCLIMB_ITERS = 4000
RANDOM_SEED = 42
TOP10_PLAINTEXT = list("E A T O I R S N H U".split())
COMMON_WORDS = [
    "THE","BE","TO","OF","AND","A","IN","THAT","IS","IT","FOR","AS","WITH","HE","SHE",
    "ON","WAS","BY","AT","FROM","ARE","THIS","AN","OR","HAVE","NOT","BUT","YOU","I","WE",
    "THEY","HAVE","HAS"
]
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class SubstitutionCipherSolver:
    """Solver for monoalphabetic substitution with known top-10 plaintext frequency letters."""
    
    def __init__(self, filepath: str):
        random.seed(RANDOM_SEED)
        self.filepath = filepath
        self.clean_text = self._load_and_clean(filepath)
        if len(self.clean_text) < WINDOW_LEN:
            raise ValueError("Signal file shorter than required window length.")
        self.best_result = None

    @staticmethod
    def _load_and_clean(path: str) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
        data = data.upper()
        return ''.join(ch for ch in data if ch == ' ' or 'A' <= ch <= 'Z')

    def _find_candidate_windows(self) -> List[Tuple[int, str, float]]:
        text = self.clean_text
        n = len(text)
        scores = []
        window = text[0:WINDOW_LEN]
        freq = Counter(ch for ch in window if ch != ' ')

        def quick_score(freq_counter):
            most = [c for c,_ in freq_counter.most_common(10)]
            return len(set(most))

        scores.append((0, window, quick_score(freq)))
        for i in range(1, n - WINDOW_LEN + 1):
            left = text[i-1]
            new = text[i + WINDOW_LEN - 1]
            if left != ' ':
                freq[left] -= 1
                if freq[left] == 0:
                    del freq[left]
            if new != ' ':
                freq[new] += 1
            scores.append((i, text[i:i+WINDOW_LEN], quick_score(freq)))

        scores.sort(key=lambda t: (t[2], len(set(t[1]))), reverse=True)
        return scores[:PREFILTER_TOP]

    @staticmethod
    def _initial_key(window: str) -> Dict[str, str]:
        freq = Counter(ch for ch in window if ch != ' ')
        most = [c for c,_ in freq.most_common()]
        key = {}
        used_plain = set()
        for i, ct in enumerate(most):
            if i < len(TOP10_PLAINTEXT):
                pt = TOP10_PLAINTEXT[i]
            else:
                pt = next(p for p in ALPHABET if p not in used_plain)
            key[ct] = pt
            used_plain.add(pt)
        for letter in ALPHABET:
            if letter not in key:
                pt = next(p for p in ALPHABET if p not in used_plain)
                key[letter] = pt
                used_plain.add(pt)
        return key

    @staticmethod
    def _decrypt(window: str, key: Dict[str, str]) -> str:
        return ''.join(key.get(ch, ch) if ch != ' ' else ' ' for ch in window)

    @staticmethod
    def _score_plaintext(pt: str) -> float:
        up = pt.upper()
        score = 0.0
        for w in COMMON_WORDS:
            hits = up.count(" " + w + " ") + up.startswith(w + " ") + up.endswith(" " + w)
            score += hits * (len(w) + 2)
        words = up.split()
        single_letters = sum(1 for w in words if len(w) == 1 and w not in ("A","I"))
        score -= single_letters * 1.5
        alpha_words = sum(1 for w in words if w.isalpha() and len(w) > 1)
        score += 0.5 * alpha_words
        bad_bigrams = sum(up.count(bg) for bg in ["QX","XZ","ZX","QZ","JQ","QQ"])
        score -= 0.3 * bad_bigrams
        return score

    @staticmethod
    def _swap_key(key: Dict[str, str]) -> Dict[str, str]:
        k = key.copy()
        a, b = random.sample(ALPHABET, 2)
        k[a], k[b] = k[b], k[a]
        return k

    def _hill_climb(self, window: str, key: Dict[str, str], iters: int) -> Tuple[float, Dict[str, str], str]:
        best_key = key.copy()
        best_plain = self._decrypt(window, best_key)
        best_score = self._score_plaintext(best_plain)
        current_key = best_key
        current_score = best_score
        for _ in range(iters):
            cand_key = self._swap_key(current_key)
            cand_plain = self._decrypt(window, cand_key)
            cand_score = self._score_plaintext(cand_plain)
            if cand_score >= current_score or random.random() < 0.001:
                current_key, current_score = cand_key, cand_score
                if cand_score > best_score:
                    best_key, best_score, best_plain = cand_key, cand_score, cand_plain
        return best_score, best_key, best_plain

    def solve(self):
        print("Scanning for candidate windows...")
        candidates = self._find_candidate_windows()
        print(f"Prefiltered to {len(candidates)} promising windows.")

        global_best = (-1e9, None, None, None)
        for start_idx, window_str, _ in candidates:
            init_key = self._initial_key(window_str)
            for _ in range(HILLCLIMB_RESTARTS):
                perturbed = init_key.copy()
                for _ in range(random.randint(0, 6)):
                    a, b = random.sample(ALPHABET, 2)
                    perturbed[a], perturbed[b] = perturbed[b], perturbed[a]
                score, key, plain = self._hill_climb(window_str, perturbed, iters=HILLCLIMB_ITERS//10)
                if score > global_best[0]:
                    global_best = (score, plain, key, start_idx)

        self.best_result = global_best
        return global_best


def main():
    """Main function to run the program."""
    print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    print("Analyzing 64KB of alien signals...")
    print("Searching for 721-character encrypted message...")

    if len(sys.argv) < 2:
        print("Usage: python3 main.py /path/to/signal.txt")
        sys.exit(1)

    solver = SubstitutionCipherSolver(sys.argv[1])
    score, plaintext, key, start = solver.solve()

    if plaintext:
        words = plaintext.split()
        first9 = " ".join(words[:9])
        print("\n=== DECRYPTION COMPLETE ===")
        print(f"Start index: {start}, Score: {score:.2f}")
        print(f"First 9 words: {first9}")
        print("\nFull plaintext:")
        print(plaintext)
        print("\nSubstitution Key (cipher -> plain):")
        for c in sorted(key.keys()):
            print(f"{c} -> {key[c]}", end="; ")
        print()
        with open("best_candidate.txt", "w", encoding="utf-8") as f:
            f.write(plaintext)
        print("\nSaved plaintext to best_candidate.txt")
    else:
        print("No viable decryption found.")


if __name__ == "__main__":
    main()



# # write your code here

# def main():
#     """Main function to run the program."""
#     print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    
#     # Your code logic goes here -- feel free to add functions or classes as needed
#     print("Analyzing 64KB of alien signals...")
#     print("Searching for 721-character encrypted message...")


# if __name__ == "__main__":
#     main() 
