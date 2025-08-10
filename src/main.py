# -*- coding: utf-8 -*-
"""
Created on Sun Aug 10 23:21:16 2025

@author: Hamza.Javaid1
"""

# write your code here

from collections import Counter
from heapq import nlargest
from pathlib import Path
import random

WINDOW = 721                    # length of hidden message
TOP_K = 5                       # keep top K windows for safety (we solve #1)
FILE_PATH = "D:\\python scripts\\technical_assessment\\signal.txt"        # keep in same folder as this file

# English letter frequencies (%) – for chi-square
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
    'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
    'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
    'P': 1.93, 'B': 1.49, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
    'Q': 0.10, 'Z': 0.07
}
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Small English trigram model (log-probs); unseen gets FLOOR_TRI
TRI = {
    'THE': -2.1, 'AND': -2.9, 'ING': -3.0, 'ENT': -3.4, 'ION': -3.5, 'TIO': -3.6,
    'FOR': -3.6, 'NTH': -3.7, 'ATI': -3.7, 'ERA': -3.7, 'HAT': -3.8, 'ATE': -3.9,
    'ALL': -3.9, 'ETH': -3.9, 'HES': -4.0, 'VER': -4.0, 'HIS': -4.0, 'ERE': -4.2,
    'ERS': -4.2, 'TED': -4.2, 'NOT': -4.5, 'YOU': -4.5, 'THA': -3.8, 'WAS': -4.2,
    'WIT': -4.2, 'OFT': -4.2
}
FLOOR_TRI = -8.5
COMMON_SHORT = {"THE","AND","OF","TO","IN","IS","IT","AS","ON","BY","AN","AT","OR","BE","THAT","THIS"}
TARGET_ORDER = "EATOIRSNHULDCMWFGYPBVKJXQ"   # rank order for seeding key

# --------------------------- utilities ---------------------------

def load_text(path: str) -> str:
    s = Path(path).read_text(encoding="utf-8", errors="ignore")
    # keep only A–Z and space, uppercase
    return "".join(ch for ch in s.upper() if ch == " " or ("A" <= ch <= "Z"))

def chi_square_against_english(s: str) -> float:
    s = s.replace(" ", "")
    n = len(s)
    if n == 0:
        return float("inf")
    counts = Counter(s)
    chi2 = 0.0
    for L in LETTERS:
        obs = counts.get(L, 0)
        exp = ENGLISH_FREQ[L] * n / 100.0
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp
    return chi2

def index_of_coincidence(s: str) -> float:
    s = s.replace(" ", "")
    n = len(s)
    if n <= 1:
        return 0.0
    counts = Counter(s)
    num = sum(c * (c - 1) for c in counts.values())
    den = n * (n - 1)
    return num / den

def english_likeness(window: str) -> float:
    """Higher is better."""
    sp = window.count(" ") / len(window)
    # soft bonus for plausible space rate
    space_score = 1.0 if 0.13 <= sp <= 0.20 else (0.4 if 0.08 <= sp <= 0.26 else 0.0)
    chi2 = chi_square_against_english(window)       # lower better
    ic  = index_of_coincidence(window)              # close to 0.066 better
    ic_score = 1.0 - abs(ic - 0.066) / 0.066
    return (-chi2) + 50.0*space_score + 200.0*ic_score

def find_top_windows(text: str, window: int, top_k: int):
    scores = ((english_likeness(text[i:i+window]), i) for i in range(len(text)-window+1))
    return nlargest(top_k, scores, key=lambda x: x[0])  # [(score, start), ...]

# --------------------- substitution solver ----------------------

def score_text(plain: str) -> float:
    s2 = plain.replace(" ", "")
    sc = 0.0
    for i in range(len(s2) - 2):
        tri = s2[i:i+3]
        sc += TRI.get(tri, FLOOR_TRI)
    # small bonus for common words
    sc += sum(0.6 for w in plain.split() if w in COMMON_SHORT)
    return sc

def seed_key_from_freq(cipher: str) -> str:
    counts = Counter(ch for ch in cipher if ch != " ")
    ranked = [kv[0] for kv in sorted(counts.items(), key=lambda x: x[1], reverse=True)]
    m = {}
    for i, c in enumerate(ranked):
        if i < len(TARGET_ORDER):
            m[c] = TARGET_ORDER[i]
    used = set(m.values())
    remaining = [L for L in LETTERS if L not in used]
    for c in LETTERS:
        if c not in m:
            m[c] = remaining.pop(0)
    return "".join(m.get(c, c) for c in LETTERS)  # 26-char table

def decrypt_with_key(cipher: str, key26: str) -> str:
    out = []
    for ch in cipher:
        if ch == " ":
            out.append(" ")
        else:
            out.append(key26[ord(ch) - 65])
    return "".join(out)

def random_swap(key: str) -> str:
    a, b = random.sample(range(26), 2)
    k = list(key); k[a], k[b] = k[b], k[a]
    return "".join(k)

def hill_climb(cipher: str, starts=60, iters=50000, patience=2000):
    best_plain, best_score, best_key = None, -1e18, None
    for s in range(starts):
        key = seed_key_from_freq(cipher)
        for _ in range(30):  # diversify
            key = random_swap(key)
        plain = decrypt_with_key(cipher, key)
        cur_score = score_text(plain)
        no_improve = 0

        for i in range(iters):
            cand_key = random_swap(key)
            cand_plain = decrypt_with_key(cipher, cand_key)
            cand_score = score_text(cand_plain)
            if cand_score > cur_score:
                key, plain, cur_score = cand_key, cand_plain, cand_score
                no_improve = 0
            else:
                no_improve += 1
                # small shake if stuck
                if no_improve % 800 == 0:
                    for _ in range(3):
                        key = random_swap(key)
                    plain = decrypt_with_key(cipher, key)
                    cur_score = score_text(plain)
            if no_improve > patience:
                break

        if cur_score > best_score:
            best_plain, best_score, best_key = plain, cur_score, key
    return best_plain, best_key, best_score





def main():
    """Main function to run the program."""
    print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    
    # Your code logic goes here -- feel free to add functions or classes as needed
    print("Analyzing 64KB of alien signals...")
    print("Searching for 721-character encrypted message...")
    
    
    random.seed(42)

    text = load_text(FILE_PATH)
    if len(text) < WINDOW:
        raise ValueError("signal.txt is shorter than the required window size.")
    print(f"Loaded {len(text):,} characters.")

    # 1) Find best candidate window
    top = find_top_windows(text, WINDOW, TOP_K)
    best_score, best_start = top[0]
    cipher_seg = text[best_start:best_start + WINDOW]
    spc = cipher_seg.count(" ") / len(cipher_seg) * 100
    chi2 = chi_square_against_english(cipher_seg)
    ic  = index_of_coincidence(cipher_seg)

    print(f"Top window start index: {best_start}")
    print(f"Space%: {spc:.2f}   Chi²: {chi2:.2f}   IC: {ic:.4f}")
    print("Running substitution solver...\n")

    # 2) Solve substitution
    plain, key, score = hill_climb(cipher_seg, starts=120, iters=50000, patience=3000)

    # 3) Output
    print("Best language score:", round(score, 2))
    print("Key (cipher A..Z -> plain):", key)
    print("\nPLAINTEXT (first 400 chars):")
    print(plain[:400])

    words = plain.split()
    first9 = " ".join(words[:9])
    print("\nFirst 9 words:")
    print(first9)

if __name__ == "__main__":
    main()

