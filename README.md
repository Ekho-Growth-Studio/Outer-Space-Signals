# Dyslexian Substitution Cipher Solver - Algorithm Analysis

## Overview
This code implements a heuristic-based solver for substitution ciphers that uses a combination of frequency analysis, pattern matching, and optimization algorithms to decrypt encrypted text.

## Algorithms Used

### 1. **Frequency Analysis**
- **Purpose**: Creates initial cipher-to-plaintext mappings based on letter frequency
- **Method**: Counts occurrence of each letter in the cipher text and maps most frequent cipher letters to most frequent English letters
- **Implementation**: Uses the provided top-10 English letter frequency order: "EATOIRSTNU"

### 2. **Pattern-Based Mapping Enhancement**
- **Purpose**: Improves initial mappings using common English patterns
- **Patterns Used**: 
  - Common words: "THE", "AND", "ING", "ION"
  - Digraphs (2-letter combinations): "TH", "HE", "AN", "IN", "ER", etc.
  - Trigrams and quadgrams for more sophisticated pattern recognition

### 3. **Hill Climbing Optimization**
- **Purpose**: Refines the initial mapping by iteratively improving it
- **Method**: Makes small random changes (swapping two letter mappings) and keeps changes that improve the score
- **Enhancement**: Includes simulated annealing to escape local optima

### 4. **Simulated Annealing**
- **Purpose**: Prevents the hill climbing from getting stuck in local maxima
- **Method**: Occasionally accepts worse solutions with decreasing probability as "temperature" cools
- **Parameters**: Starting temperature = 1.0, cooling rate = 0.99995

### 5. **Multi-Restart Strategy**
- **Purpose**: Increases chances of finding global optimum
- **Method**: Runs multiple hill climbing attempts with different starting points for each promising window

### 6. **Sliding Window Search**
- **Purpose**: Finds the best 721-character segment within the larger signal
- **Method**: Evaluates every possible 721-character window in the input text

## Step-by-Step Process

### Phase 1: Initialization and Data Loading
1. **Load Signal**: Read the encrypted text from file, normalize to uppercase letters and spaces only
2. **Load Quadgrams**: Load or generate 4-letter sequence statistics for English text scoring
3. **Set Parameters**: Initialize window length (721 chars), common words list, and algorithm parameters

### Phase 2: Candidate Window Identification
4. **Sliding Window Analysis**: 
   - Extract every possible 721-character window from the signal
   - For each window, perform frequency analysis to get letter occurrence order
   - Create initial substitution mapping using frequency matching
   - Score each window using basic pattern recognition
   - Keep top candidates (default: 100 windows) for detailed analysis

### Phase 3: Initial Mapping Creation
5. **Frequency-Based Mapping**: 
   - Count letter frequencies in the cipher window
   - Map most frequent cipher letters to most frequent English letters ("EATOIRSTNU")
6. **Pattern Enhancement**:
   - Try to identify common English patterns like "THE", "AND", "ING"
   - Adjust mappings to favor these common patterns
   - Fill remaining unmapped letters

### Phase 4: Iterative Refinement (Hill Climbing + Simulated Annealing)
7. **Multiple Restart Optimization**:
   - For each promising window, perform 6 independent optimization runs
   - Each run starts with a slightly randomized version of the initial mapping
8. **Hill Climbing Process**:
   - Randomly swap two letter mappings in the current solution
   - Decode the text with the new mapping
   - Calculate fitness score using multiple criteria
   - Accept or reject the change based on score improvement and temperature
9. **Scoring Function**:
   - **Word Recognition**: Bonus points for identifying common English words
   - **Pattern Recognition**: Points for common English letter patterns and digraphs
   - **Quadgram Analysis**: Statistical analysis of 4-letter sequences
   - **Penalties**: Deductions for impossible letter combinations

### Phase 5: Solution Selection and Output
10. **Best Solution Selection**: Choose the window and mapping combination with highest score
11. **Final Decoding**: Apply the best mapping to decode the 721-character window
12. **Output Generation**: 
    - Extract first 9 words as requested
    - Save full decoded text to file
    - Display mapping and statistics

## Key Features

### Scoring Mechanism
The fitness function combines multiple English language characteristics:
- **Word Matching** (40% weight): Recognition of common English words
- **Digraph Scoring** (30% weight): Common 2-letter combinations
- **Quadgram Scoring** (30% weight): 4-letter sequence patterns
- **Penalty System**: Reduces score for impossible letter combinations

### Optimization Enhancements
- **Simulated Annealing**: Prevents getting trapped in local optima
- **Multiple Restarts**: Increases probability of finding global optimum
- **Stagnation Detection**: Stops optimization when no improvement occurs
- **Adaptive Parameters**: Temperature cooling and iteration limits

### Robustness Features
- **Window Search**: Handles cases where only part of the signal contains the target text
- **Normalization**: Handles different input formats by normalizing to uppercase
- **Error Handling**: Graceful handling of short inputs and missing files

## Computational Complexity
- **Time Complexity**: O(n × w × r × i) where:
  - n = signal length
  - w = number of top candidate windows
  - r = number of restarts per window
  - i = hill climbing iterations
- **Space Complexity**: O(1) relative to input size (fixed-size data structures)

This solver represents a sophisticated approach to cryptanalysis, combining classical frequency analysis with modern optimization techniques to achieve robust decryption of substitution ciphers.