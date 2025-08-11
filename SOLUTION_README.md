# Substitution Cipher Decoder - Solution

## Overview

This project implements a heuristic-based substitution cipher solver that can decode encrypted text by analyzing character frequencies and using hill-climbing optimization to find the most likely plaintext.

## Problem Description

The task was to decode a substitution cipher where:
- Each letter in the alphabet is mapped to another letter
- The encrypted text is 65,535 characters long
- We need to find the best 721-character window that contains readable English text
- The solution should output the first 9 words of the decoded text

## Solution Approach

### 1. Frequency Analysis
- Analyzes character frequencies in each 721-character window
- Uses the provided top-10 letter frequency order: E, A, T, O, I, R, S, N, H, U
- Builds initial substitution mappings based on frequency patterns

### 2. Pattern Recognition
- Recognizes common English patterns like "THE", "AND", "ING", "ION"
- Uses digraph analysis (common letter pairs like "TH", "HE", "AN")
- Implements quadgram scoring for 4-letter sequences

### 3. Hill-Climbing Optimization
- Uses simulated annealing to escape local maxima
- Performs random swaps of letter mappings
- Scores each candidate using multiple criteria:
  - Word recognition (common English words)
  - Pattern matching (common letter sequences)
  - Digraph analysis
  - Quadgram analysis
  - Penalties for impossible letter combinations

### 4. Multi-Window Search
- Evaluates every 721-character window in the signal
- Ranks windows by initial score
- Refines top candidates with hill-climbing
- Returns the best overall result

## Key Features

- **Efficient Search**: Uses step-based window evaluation to reduce computation
- **Robust Scoring**: Multiple scoring criteria for better accuracy
- **Optimization**: Configurable parameters for speed vs. accuracy trade-offs
- **Pattern Recognition**: Leverages English language patterns

## Usage

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Decoder
```bash
python3 src/test.py data/signal.txt
```

### Parameters (configurable in code)
- `WINDOW_LEN = 721`: Length of text window to analyze
- `top_candidates = 20`: Number of windows to refine with hill-climbing
- `max_iters = 1000`: Maximum hill-climbing iterations per restart
- `stagnation_limit = 200`: Iterations without improvement before stopping

## Output

The program outputs:
1. Best window starting index
2. Overall score
3. First 9 words of the decoded text

## Algorithm Details

### Initial Mapping
```python
def build_initial_mapping(freq_order):
    # Map most frequent cipher letters to most frequent plaintext letters
    # Apply common pattern recognition
    # Fill remaining letters
```

### Scoring Function
```python
def score_decoded_text(decoded):
    # Word recognition (40% weight)
    # Digraph analysis (30% weight) 
    # Quadgram analysis (30% weight)
    # Penalties for impossible sequences
```

### Hill-Climbing
```python
def hill_climb_refine(cipher_slice, initial_map):
    # Simulated annealing with temperature cooling
    # Random swaps of letter mappings
    # Early stopping on stagnation
```

## Performance Optimizations

1. **Step-based window evaluation**: Only evaluates every 5th window initially
2. **Early termination**: Stops hill-climbing when no improvement for 200 iterations
3. **Reduced restarts**: Uses 3 restarts instead of 6 for faster execution
4. **Efficient scoring**: Caches quadgram statistics

## Expected Results

The decoder should find a 721-character window that contains readable English text, typically starting with common words like "THE", "AND", or similar patterns.

## Files

- `src/test.py`: Main decoder implementation
- `data/signal.txt`: Encrypted input signal
- `english_quadgrams.pkl`: Cached quadgram statistics (generated automatically)
- `requirements.txt`: Python dependencies

## Troubleshooting

- **Slow execution**: Reduce `top_candidates` or `max_iters` parameters
- **Poor results**: Increase `top_candidates` or `max_iters` for better accuracy
- **Memory issues**: The quadgram file may be large; ensure sufficient disk space

## Algorithm Complexity

- Time: O(n × w × i × r) where:
  - n = number of windows evaluated
  - w = window length (721)
  - i = iterations per hill-climbing run
  - r = number of restarts
- Space: O(w + q) where q = quadgram dictionary size 