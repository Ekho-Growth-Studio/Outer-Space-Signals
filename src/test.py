#!/usr/bin/env python3
"""
Dyslexian substitution solver (heuristic)

Reads 'signal.txt' (uppercase letters + spaces), searches every 721-character window,
builds a frequency-based initial substitution mapping using the given top-10 letter order
and then refines the mapping by hill-climbing to maximize recognized English words.

Outputs:
 - Best deciphered candidate
 - First 9 words from the deciphered candidate (as required)
"""

import collections
import random
import math
import sys
import pickle
import os
from typing import Dict, Tuple, List
from collections import defaultdict

WINDOW_LEN = 721
TOP_LETTERS = list("EATOIRSNHU")  # Provided top-10 order (E A T O I R S N H U)
COMMON_WORDS = {
    # small set of common words (uppercase) used for scoring
    "THE","OF","AND","TO","IN","A","IS","IT","YOU","THAT","HE","WAS","FOR",
    "ON","ARE","AS","WITH","HIS","THEY","I","AT","BE","THIS","HAVE","FROM",
    "OR","ONE","HAD","BY","WORD","BUT","NOT","WHAT","ALL","WERE","WE","WHEN",
    "YOUR","CAN","SAID","THERE","USE","AN","EACH","WHICH","SHE","DO","HOW",
    "THEIR","IF","WILL","UP","ABOUT","OUT","WHO","GET","WHICH","GO","ME",
    "MY","NO","SO","MORE","ABOUT","IF","WHAT","JUST","NOW","THEN","LIKE",
    "THEN","THEM","OUR","US","SOON","HOWEVER"
}

ALPHABET = [chr(ord('A') + i) for i in range(26)]
QUADGRAM_FILE = "english_quadgrams.pkl"
QUADGRAM_SCORES = None

def load_signal(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as f:
        s = f.read()
    # normalize: keep only A-Z and spaces (per problem)
    s = s.replace('\r','')
    return s

def letter_freq_order(text: str) -> List[str]:
    cnt = collections.Counter(ch for ch in text if 'A' <= ch <= 'Z')
    ordered = [p for p, _ in cnt.most_common()]
    # append leftover letters (never appearing) to end in arbitrary but stable order
    for a in ALPHABET:
        if a not in ordered:
            ordered.append(a)
    return ordered

def load_quadgrams():
    """Load or generate quadgram statistics from English text"""
    global QUADGRAM_SCORES
    
    if os.path.exists(QUADGRAM_FILE):
        with open(QUADGRAM_FILE, 'rb') as f:
            QUADGRAM_SCORES = pickle.load(f)
    else:
        # Generate from common English words
        QUADGRAM_SCORES = defaultdict(float)
        for word in COMMON_WORDS:
            for i in range(len(word)-3):
                quad = word[i:i+4]
                QUADGRAM_SCORES[quad] += 1
        
        # Save for future use
        with open(QUADGRAM_FILE, 'wb') as f:
            pickle.dump(dict(QUADGRAM_SCORES), f)

def build_initial_mapping(freq_order: List[str]) -> Dict[str, str]:
    """
    Enhanced mapping using both frequency and common patterns
    """
    mapping = {}
    used_plain = set()
    
    # Common English patterns
    patterns = {
        'THE': ['T', 'H', 'E'],
        'AND': ['A', 'N', 'D'],
        'ING': ['I', 'N', 'G'],
        'ION': ['I', 'O', 'N']
    }
    
    # First map based on frequency
    for i, c in enumerate(freq_order):
        if i < len(TOP_LETTERS):
            p = TOP_LETTERS[i]
            mapping[c] = p
            used_plain.add(p)
    
    # Then try to map common patterns
    for pattern in patterns.values():
        for letter in pattern:
            if letter not in used_plain:
                # Find most likely unmapped cipher letter
                for c in freq_order:
                    if c not in mapping:
                        mapping[c] = letter
                        used_plain.add(letter)
                        break
    
    # Fill remaining letters
    remaining_plain = [p for p in ALPHABET if p not in used_plain]
    for c in freq_order:
        if c not in mapping and remaining_plain:
            mapping[c] = remaining_plain.pop(0)
    
    return mapping

def decode_with_mapping(text: str, mapping: Dict[str,str]) -> str:
    out_chars = []
    for ch in text:
        if 'A' <= ch <= 'Z':
            out_chars.append(mapping.get(ch, '?'))
        else:
            out_chars.append(ch)
    return ''.join(out_chars)

def score_decoded_text(decoded: str) -> float:
    """
    Enhanced scoring with better letter pattern recognition
    """
    if QUADGRAM_SCORES is None:
        load_quadgrams()
    
    tokens = decoded.split()
    word_score = 0
    
    # Common English patterns with weights
    patterns = {
        'THE': 10,
        'ING': 8,
        'AND': 8,
        'ION': 7,
        'ENT': 7,
        'ED': 6,
        'TH': 6,
        'AT': 5,
        'ST': 5,
        'ER': 5,
        'ES': 5,
        'ON': 5,
        'IN': 5,
        'COM': 5,
        'PRO': 5
    }
    
    # Common English digraphs with weights
    digraphs = {
        'TH': 8, 'HE': 8, 'AN': 7, 'IN': 7, 'ER': 7,
        'ON': 6, 'RE': 6, 'ED': 6, 'ND': 6, 'HA': 6,
        'AT': 5, 'EN': 5, 'ES': 5, 'OF': 5, 'OR': 5,
        'NT': 5, 'EA': 5, 'TI': 5, 'TO': 5, 'IT': 5
    }
    
    text = ''.join(ch for ch in decoded if 'A' <= ch <= 'Z')
    
    # Word scoring
    for t in tokens:
        t2 = ''.join(ch for ch in t if 'A' <= ch <= 'Z')
        if not t2:
            continue
        if t2 in COMMON_WORDS:
            word_score += 10  # Increased weight for full word matches
        
        # Pattern scoring
        for pattern, score in patterns.items():
            if pattern in t2:
                word_score += score
    
    # Digraph scoring
    digraph_score = 0
    for i in range(len(text)-1):
        digraph = text[i:i+2]
        if digraph in digraphs:
            digraph_score += digraphs[digraph]
    
    # Quadgram scoring
    quad_score = 0
    for i in range(len(text)-3):
        quad = text[i:i+4]
        if quad in QUADGRAM_SCORES:
            quad_score += QUADGRAM_SCORES[quad] * 2.0  # Increased weight
    
    # Penalties
    penalties = 0
    vowels = set('AEIOU')
    
    # Penalize impossible consonant sequences
    for i in range(len(text)-3):
        if text[i:i+4].isalpha() and not any(c in vowels for c in text[i:i+4]):
            penalties += 5
    
    # Penalize impossible vowel sequences
    for i in range(len(text)-3):
        if text[i:i+4].isalpha() and all(c in vowels for c in text[i:i+4]):
            penalties += 5
    
    # Weight the different components
    final_score = (word_score * 0.4 + 
                  digraph_score * 0.3 + 
                  quad_score * 0.3) - penalties
    
    return final_score

def random_swap_mapping(mapping: Dict[str,str]) -> Dict[str,str]:
    """Return a new mapping with two plaintext assignments swapped (randomly)."""
    # create reverse map: plaintext -> cipher for assigned letters only
    p_to_c = {p:c for c,p in mapping.items()}
    # choose from plaintext letters that are in p_to_c
    available_plain = list(p_to_c.keys())
    p1, p2 = random.sample(available_plain, 2)
    c1, c2 = p_to_c[p1], p_to_c[p2]
    new_map = mapping.copy()
    new_map[c1], new_map[c2] = new_map[c2], new_map[c1]
    return new_map


def hill_climb_refine(cipher_slice: str, initial_map: Dict[str,str],
                      max_iters: int = 8000, stagnation_limit: int = 800) -> Tuple[Dict[str,str], int]:
    """
    Enhanced hill-climbing with simulated annealing
    """
    best_map = initial_map.copy()
    current_map = initial_map.copy()
    best_decoded = decode_with_mapping(cipher_slice, best_map)
    best_score = score_decoded_text(best_decoded)
    current_score = best_score
    iters_no_improve = 0
    temperature = 1.0
    cooling_rate = 0.99995
    
    for it in range(max_iters):
        # propose swap
        new_map = random_swap_mapping(current_map)
        new_decoded = decode_with_mapping(cipher_slice, new_map)
        new_score = score_decoded_text(new_decoded)
        
        # Calculate acceptance probability
        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / temperature):
            current_map = new_map
            current_score = new_score
            
            if current_score > best_score:
                best_map = current_map.copy()
                best_score = current_score
                iters_no_improve = 0
            else:
                iters_no_improve += 1
        else:
            iters_no_improve += 1
            
        # Cool down
        temperature *= cooling_rate
        
        if iters_no_improve >= stagnation_limit:
            break
            
    return best_map, best_score

def find_best_candidate(signal: str, top_candidates: int = 20) -> Tuple[str, Dict[str,str], int, int]:
    n = len(signal)
    if n < WINDOW_LEN:
        raise ValueError("Signal shorter than window length.")
    candidate_scores = []
    # Evaluate every window once with frequency-initial mapping and coarse scoring
    for i in range(0, n - WINDOW_LEN + 1):
        window = signal[i:i+WINDOW_LEN]
        freq_order = letter_freq_order(window)
        init_map = build_initial_mapping(freq_order)
        decoded = decode_with_mapping(window, init_map)
        sc = score_decoded_text(decoded)
        candidate_scores.append((sc, i, init_map))
    # Keep best windows
    candidate_scores.sort(reverse=True, key=lambda x: x[0])
    shortlisted = candidate_scores[:top_candidates]
    # refine each shortlisted window with hill-climbing (multiple restarts)
    best_overall = ("", None, -10e9, -1)  # (decoded, mapping, score, start_index)
    for coarse_score, start_idx, init_map in shortlisted:
        window = signal[start_idx:start_idx+WINDOW_LEN]
        # several random restarts to escape local maxima
        best_map_for_win = None
        best_score_for_win = -10**9
        for restart in range(6):
            # shuffle remaining plaintext assignments slightly to diversify start
            # create a randomized initial map variant
            freq_order = letter_freq_order(window)
            base_map = build_initial_mapping(freq_order)
            # randomize by doing a few random swaps
            m = base_map.copy()
            for _ in range(10 + restart*2):
                m = random_swap_mapping(m)
            refined_map, refined_score = hill_climb_refine(
                window, 
                m, 
                max_iters=5000,  # Increased from 2000
                stagnation_limit=500  # Increased from 300
            )
            if refined_score > best_score_for_win:
                best_score_for_win = refined_score
                best_map_for_win = refined_map
        # decode with best_map_for_win
        decoded = decode_with_mapping(window, best_map_for_win)
        if best_score_for_win > best_overall[2]:
            best_overall = (decoded, best_map_for_win, best_score_for_win, start_idx)
    return best_overall  # decoded, mapping, score, start_index

def get_first_n_words(text: str, n: int) -> List[str]:
    toks = text.split()
    return toks[:n]

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "../data/signal.txt"
    print(f"Loading signal from {filename} ...")
    signal = load_signal(filename)
    print(f"Signal length: {len(signal)} chars")
    print("Searching for best 721-char candidate (this can take a minute)...")
    random.seed(0xC0FFEE)
    decoded, mapping, score, start_idx = find_best_candidate(
        signal, 
        top_candidates=100  # Increased from 50
    )
    print("\n=== RESULTS ===")
    print(f"Best window starts at index: {start_idx}")
    print(f"Score: {score}")
    print("\n--- First 9 words (as requested) ---")
    first9 = get_first_n_words(decoded, 9)
    print(" ".join(first9))

if __name__ == "__main__":
    main()