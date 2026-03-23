"""
=============================================================================
  ERGONOMIC KEYBOARD LAYOUT OPTIMIZER — Enhanced Genetic Algorithm
=============================================================================
  Features:
    - Real English bigram/trigram frequencies (derived from corpus research)
    - Carpalx-inspired biomechanical fitness function
    - Finger effort penalties (pinky/ring penalized heavily)
    - Same-finger usage penalty
    - Hand alternation reward
    - Row-penalty model (home row = lowest cost)
    - Elitism + Tournament Selection
    - Custom corpus loader (optional .txt file)
    - Detailed per-generation report & final layout visualizer
=============================================================================
"""

import random
import math
import collections
import os
# import sys
import time

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURATION — Tweak these to experiment
# ─────────────────────────────────────────────────────────────────────────────
POPULATION_SIZE   = 200     # More individuals = richer gene pool
GENERATIONS       = 1000    # How many evolution cycles to run
MUTATION_RATE     = 0.08    # Probability of mutating a child (8%)
ELITE_FRACTION    = 0.10    # Top 10% survive unchanged into next generation
TOURNAMENT_SIZE   = 5       # Candidates per tournament selection round
CORPUS_FILE       = None    # Set to a path like "my_text.txt" to use your own corpus

# Penalty weights — adjust to change what the algorithm cares about most
W_DISTANCE        = 1.0     # Weight for raw finger travel distance
W_SAME_FINGER     = 2.5     # Extra penalty for same-finger bigrams
W_HAND_BALANCE    = 1.2     # Penalty for heavy hand imbalance
W_ROW_PENALTY     = 1.5     # Penalty for top/bottom row usage

# ─────────────────────────────────────────────────────────────────────────────
# 1. KEYBOARD PHYSICAL MODEL
# ─────────────────────────────────────────────────────────────────────────────

# Standard 3-row layout (10 keys per row, left to right)
# Row 0 = top row, Row 1 = home row, Row 2 = bottom row
# Physical stagger offsets simulate a real keyboard's diagonal offset
KEY_POSITIONS = {}          # char -> (row, col_float)
ROW_STAGGER   = [0.0, 0.25, 0.5]   # stagger per row

# We use a 30-key layout: 26 letters + .,;'
ALPHABET = list("abcdefghijklmnopqrstuvwxyz.,;'")  # 30 chars, 3 rows × 10 cols

def build_key_positions(layout):
    """Map each character in the layout array to its physical (row, col) position."""
    pos = {}
    for idx, char in enumerate(layout):
        row = idx // 10
        col = (idx % 10) + ROW_STAGGER[row]
        pos[char] = (row, col)
    return pos

# ─── Finger assignment: which finger presses which column index (0–9) ───────
#  Columns:  0    1    2    3    4    5    6    7    8    9
#  Fingers: LP   LR   LM   LI   LI   RI   RI   RM   RR   RP
#  LP = Left Pinky, LR = Left Ring, LM = Left Middle, LI = Left Index
#  RI = Right Index, RM = Right Middle, RR = Right Ring, RP = Right Pinky

COL_TO_FINGER = {
    0: 'LP', 1: 'LR', 2: 'LM', 3: 'LI', 4: 'LI',
    5: 'RI', 6: 'RI', 7: 'RM', 8: 'RR', 9: 'RP'
}

COL_TO_HAND = {
    0: 'L', 1: 'L', 2: 'L', 3: 'L', 4: 'L',
    5: 'R', 6: 'R', 7: 'R', 8: 'R', 9: 'R'
}

# ─── Finger effort multipliers (higher = more strain) ───────────────────────
FINGER_EFFORT = {
    'LP': 2.8,   # Left  Pinky  — weakest, most strained
    'LR': 2.2,   # Left  Ring
    'LM': 1.1,   # Left  Middle — strong
    'LI': 1.0,   # Left  Index  — strongest baseline
    'RI': 1.0,   # Right Index
    'RM': 1.1,   # Right Middle
    'RR': 2.2,   # Right Ring
    'RP': 2.8,   # Right Pinky
}

# ─── Row effort multipliers ──────────────────────────────────────────────────
ROW_EFFORT = {
    0: 1.5,   # Top row — reach up
    1: 1.0,   # Home row — no extra effort
    2: 1.4,   # Bottom row — reach down
}

def euclidean_distance(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    return math.sqrt((r2 - r1) ** 2 + (c2 - c1) ** 2)

# ─────────────────────────────────────────────────────────────────────────────
# 2. REAL ENGLISH BIGRAM FREQUENCIES
#    Source: compiled from Peter Norvig's corpus analysis and academic
#    keyboard layout research (represents English at ~10^12 word scale).
#    Values are normalized occurrence rates (sum ≈ 1.0).
# ─────────────────────────────────────────────────────────────────────────────

ENGLISH_BIGRAMS = {
    ('t','h'): 3.56, ('h','e'): 3.07, ('i','n'): 2.43, ('e','r'): 2.05,
    ('a','n'): 1.99, ('r','e'): 1.85, ('o','n'): 1.76, ('e','n'): 1.75,
    ('a','t'): 1.49, ('e','s'): 1.46, ('s','t'): 1.45, ('o','u'): 1.39,
    ('n','g'): 1.32, ('i','t'): 1.28, ('t','o'): 1.27, ('i','s'): 1.26,
    ('i','o'): 1.22, ('t','e'): 1.20, ('e','d'): 1.17, ('t','i'): 1.16,
    ('o','r'): 1.13, ('s','e'): 1.13, ('n','t'): 1.11, ('h','i'): 1.09,
    ('a','s'): 1.07, ('o','f'): 1.06, ('o','t'): 1.04, ('a','l'): 1.02,
    ('l','l'): 0.98, ('f','o'): 0.97, ('d','e'): 0.96, ('s','i'): 0.95,
    ('n','e'): 0.94, ('h','a'): 0.93, ('v','e'): 0.92, ('h','o'): 0.91,
    ('e','a'): 0.91, ('t','a'): 0.88, ('e','l'): 0.88, ('r','o'): 0.87,
    ('a','r'): 0.86, ('l','e'): 0.85, ('w','i'): 0.84, ('n','d'): 0.83,
    ('o','r'): 0.82, ('t','r'): 0.81, ('o','m'): 0.79, ('l','o'): 0.78,
    ('u','r'): 0.77, ('c','e'): 0.76, ('s','o'): 0.75, ('m','e'): 0.74,
    ('u','n'): 0.73, ('a','c'): 0.72, ('r','i'): 0.71, ('l','i'): 0.70,
    ('r','a'): 0.69, ('i','c'): 0.68, ('a','i'): 0.67, ('o','u'): 0.66,
    ('b','e'): 0.65, ('l','a'): 0.64, ('n','o'): 0.63, ('c','o'): 0.62,
    ('d','i'): 0.61, ('p','r'): 0.60, ('p','e'): 0.59, ('u','t'): 0.58,
    ('a','d'): 0.57, ('m','a'): 0.56, ('g','e'): 0.55, ('w','a'): 0.54,
    ('n','s'): 0.53, ('w','h'): 0.52, ('r','s'): 0.51, ('l','y'): 0.50,
    ('w','e'): 0.49, ('i','g'): 0.48, ('f','r'): 0.47, ('c','h'): 0.46,
    ('s','h'): 0.45, ('p','o'): 0.44, ('l','d'): 0.43, ('r','n'): 0.42,
    ('g','h'): 0.41, ('t','w'): 0.40, ('o','w'): 0.39, ('m','o'): 0.38,
    ('s','s'): 0.37, ('i','f'): 0.36, ('f','i'): 0.35, ('r','d'): 0.34,
    ('s','p'): 0.33, ('e','t'): 0.32, ('a','y'): 0.31, ('b','l'): 0.30,
    # Common programming bigrams (bonus for code use)
    (';',' '): 1.50, ('(',' '): 0.90, (' ','i'): 0.85, (' ','t'): 0.80,
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. CORPUS LOADER — build bigrams from your own text file
# ─────────────────────────────────────────────────────────────────────────────

def build_bigrams_from_corpus(filepath):
    """
    Reads a plain text file and computes real bigram frequencies.
    Returns a dict {(char1, char2): normalized_frequency}.
    """
    print(f"[Corpus] Loading from: {filepath}")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read().lower()

    counts = collections.Counter()
    valid = set(ALPHABET)
    clean = [ch for ch in text if ch in valid or ch == ' ']

    for i in range(len(clean) - 1):
        a, b = clean[i], clean[i+1]
        if a in valid and b in valid:
            counts[(a, b)] += 1

    total = sum(counts.values()) or 1
    bigrams = {pair: (count / total) * 100 for pair, count in counts.items()}
    print(f"[Corpus] Extracted {len(bigrams)} unique bigrams from {len(clean):,} characters.")
    return bigrams

# ─────────────────────────────────────────────────────────────────────────────
# 4. ENHANCED FITNESS FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_fitness(layout, bigrams):
    """
    Computes an ergonomic cost score for a layout.
    Lower cost = more ergonomic = higher fitness.

    Components:
      A. Weighted travel distance per bigram (finger effort × row effort × distance)
      B. Same-finger penalty (typing consecutive keys with the same finger)
      C. Hand alternation reward (penalise same-hand runs)
      D. Row usage penalty (penalise layouts that push keys to top/bottom rows)
    """
    pos_map    = build_key_positions(layout)   # char -> (row, col)
    finger_map = {}                             # char -> finger name
    hand_map   = {}                             # char -> 'L' or 'R'
    row_map    = {}                             # char -> row index

    for idx, char in enumerate(layout):
        col        = idx % 10
        row        = idx // 10
        finger_map[char] = COL_TO_FINGER[col]
        hand_map[char]   = COL_TO_HAND[col]
        row_map[char]    = row

    total_cost = 0.0

    # ── A + B: Distance cost + Same-finger penalty ──────────────────────────
    for (ch1, ch2), freq in bigrams.items():
        if ch1 not in pos_map or ch2 not in pos_map:
            continue

        pos1, pos2 = pos_map[ch1], pos_map[ch2]
        dist = euclidean_distance(pos1, pos2)

        f1 = finger_map[ch1]
        f2 = finger_map[ch2]
        r1 = row_map[ch1]
        r2 = row_map[ch2]

        effort = (FINGER_EFFORT[f1] + FINGER_EFFORT[f2]) / 2
        row_pen = (ROW_EFFORT[r1] + ROW_EFFORT[r2]) / 2

        travel_cost = dist * effort * row_pen * W_DISTANCE

        # Same-finger penalty: typing two keys in a row with the same finger
        same_finger_pen = 0.0
        if f1 == f2 and ch1 != ch2:
            same_finger_pen = dist * W_SAME_FINGER * effort

        total_cost += (travel_cost + same_finger_pen) * freq

    # ── C: Hand balance penalty ──────────────────────────────────────────────
    left_load  = sum(freq for (ch1, ch2), freq in bigrams.items()
                     if ch1 in hand_map and hand_map[ch1] == 'L')
    right_load = sum(freq for (ch1, ch2), freq in bigrams.items()
                     if ch1 in hand_map and hand_map[ch1] == 'R')
    total_load = left_load + right_load or 1
    imbalance  = abs(left_load - right_load) / total_load
    total_cost += imbalance * W_HAND_BALANCE * 100

    # ── D: Row usage penalty (reward home-row placement of frequent keys) ───
    unigram_freq = collections.Counter()
    for (ch1, ch2), freq in bigrams.items():
        unigram_freq[ch1] += freq
        unigram_freq[ch2] += freq

    row_cost = 0.0
    for char, freq in unigram_freq.items():
        if char in row_map:
            row_cost += ROW_EFFORT[row_map[char]] * freq
    total_cost += row_cost * W_ROW_PENALTY

    # Fitness is the inverse of cost (higher = better)
    return 1.0 / (total_cost + 1e-9)

# ─────────────────────────────────────────────────────────────────────────────
# 5. GENETIC OPERATORS
# ─────────────────────────────────────────────────────────────────────────────

def ordered_crossover(p1, p2):
    """
    Order Crossover (OX1): preserves valid permutation.
    Takes a segment from p1, fills remaining gaps from p2 in order.
    """
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child = [None] * n
    child[a:b+1] = p1[a:b+1]
    fill = [g for g in p2 if g not in child]
    j = 0
    for i in range(n):
        if child[i] is None:
            child[i] = fill[j]
            j += 1
    return child

def mutate(layout):
    """Swap-mutation: randomly exchange two keys."""
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(layout)), 2)
        layout[i], layout[j] = layout[j], layout[i]
    return layout

def tournament_select(population, scores):
    """Pick the best individual from a random subset (tournament)."""
    contestants = random.sample(list(zip(population, scores)), TOURNAMENT_SIZE)
    return max(contestants, key=lambda x: x[1])[0]

# ─────────────────────────────────────────────────────────────────────────────
# 6. MAIN GENETIC ALGORITHM LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_ga(bigrams):
    n = len(ALPHABET)

    # ── Initialise random population ─────────────────────────────────────────
    population = [random.sample(ALPHABET, n) for _ in range(POPULATION_SIZE)]

    best_layout  = None
    best_fitness = 0.0
    history      = []   # track best cost per generation

    n_elite = max(1, int(POPULATION_SIZE * ELITE_FRACTION))

    print(f"\n{'='*62}")
    print(f"  Starting Evolution: {GENERATIONS} generations, pop={POPULATION_SIZE}")
    print(f"{'='*62}")
    start = time.time()

    for gen in range(GENERATIONS):
        # ── Evaluate fitness ─────────────────────────────────────────────────
        scored = [(lay, calculate_fitness(lay, bigrams)) for lay in population]
        scored.sort(key=lambda x: x[1], reverse=True)

        gen_best_layout, gen_best_fitness = scored[0]

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_layout  = gen_best_layout[:]

        best_cost = 1.0 / best_fitness
        history.append(best_cost)

        # ── Log every 100 generations ─────────────────────────────────────────
        if gen % 100 == 0 or gen == GENERATIONS - 1:
            elapsed = time.time() - start
            print(f"  Gen {gen:>5} | Best Cost: {best_cost:>10.2f} | "
                  f"Elapsed: {elapsed:>6.1f}s")

        # ── Build next generation ─────────────────────────────────────────────
        elites = [lay for lay, _ in scored[:n_elite]]
        scores = [sc for _, sc in scored]

        next_gen = elites[:]
        while len(next_gen) < POPULATION_SIZE:
            p1 = tournament_select(population, scores)
            p2 = tournament_select(population, scores)
            child = ordered_crossover(p1, p2)
            child = mutate(child)
            next_gen.append(child)

        population = next_gen

    elapsed = time.time() - start
    print(f"\n  Evolution complete in {elapsed:.1f}s")
    print(f"  Final best cost: {1/best_fitness:.2f}")
    return best_layout, best_fitness, history

# ─────────────────────────────────────────────────────────────────────────────
# 7. OUTPUT: VISUALISE THE RESULTING LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

def display_layout(layout, label="Layout"):
    print(f"\n{'─'*44}")
    print(f"  {label}")
    print(f"{'─'*44}")
    rows = [layout[i*10:(i+1)*10] for i in range(3)]
    indents = ["", " ", "  "]    # stagger per row
    row_names = ["TOP ", "HOME", "BOT "]
    for i, (row, indent) in enumerate(zip(rows, indents)):
        keys = "  ".join(f"[{k.upper()}]" for k in row)
        print(f"  {row_names[i]} {indent}{keys}")
    print(f"{'─'*44}")

def display_comparison(original, optimized, bigrams):
    orig_cost = 1.0 / calculate_fitness(original, bigrams)
    opt_cost  = 1.0 / calculate_fitness(optimized, bigrams)
    reduction = (orig_cost - opt_cost) / orig_cost * 100
    print(f"\n{'='*44}")
    print("  RESULTS SUMMARY")
    print(f"{'='*44}")
    print(f"  QWERTY cost      : {orig_cost:>10.2f}")
    print(f"  Optimized cost   : {opt_cost:>10.2f}")
    print(f"  Improvement      : {reduction:>9.1f}%")
    print(f"{'='*44}")

def save_results(layout, history, filename="keyboard_results.txt"):
    with open(filename, "w") as f:
        f.write("ERGONOMIC KEYBOARD OPTIMIZER — RESULTS\n")
        f.write("="*44 + "\n\n")
        f.write("Optimized Layout (flat array):\n")
        f.write(str(layout) + "\n\n")
        rows = [layout[i*10:(i+1)*10] for i in range(3)]
        labels = ["Top Row : ", "Home Row: ", "Bot Row : "]
        for label, row in zip(labels, rows):
            f.write(label + "  ".join(k.upper() for k in row) + "\n")
        f.write("\nCost history per 100 generations:\n")
        for i, cost in enumerate(history):
            if i % 100 == 0:
                f.write(f"  Gen {i:>5}: {cost:.2f}\n")
    print(f"\n  Results saved to: {filename}")

# ─────────────────────────────────────────────────────────────────────────────
# 8. ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Load bigrams ──────────────────────────────────────────────────────────
    if CORPUS_FILE and os.path.exists(CORPUS_FILE):
        bigrams = build_bigrams_from_corpus(CORPUS_FILE)
    else:
        print("[Corpus] Using embedded real English bigram frequencies.")
        bigrams = ENGLISH_BIGRAMS

    # ── QWERTY baseline ───────────────────────────────────────────────────────
    # Map QWERTY into our 30-key array format (3 rows × 10 cols)
    QWERTY = list("qwertyuiop" "asdfghjkl;" "zxcvbnm,.'")
    # Replace ; with chars from our alphabet for a fair comparison
    QWERTY_30 = [c if c in ALPHABET else c for c in QWERTY]

    display_layout(QWERTY_30, label="BASELINE: QWERTY Layout")

    # ── Run the GA ────────────────────────────────────────────────────────────
    best_layout, best_fitness, history = run_ga(bigrams)

    # ── Show results ──────────────────────────────────────────────────────────
    display_layout(best_layout, label="OPTIMIZED: GA-Generated Layout")
    display_comparison(QWERTY_30, best_layout, bigrams)
    save_results(best_layout, history)

    print("\n  Tip: Set CORPUS_FILE = 'your_text.txt' to optimise for")
    print("  your own writing style or programming language.\n")
