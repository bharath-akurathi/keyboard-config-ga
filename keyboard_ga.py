"""
=============================================================================
  ERGONOMIC KEYBOARD LAYOUT OPTIMIZER
  Powered by the Carpalx Corpus & Biomechanical Model
=============================================================================
  Corpus   : carpalx/corpus/books.short.txt
             (~3MB of classic literature: Alice, Dracula, Moby Dick, etc.)
  Model    : Authentic Carpalx effort formula
             - Row penalties      (from etc/effort/weight/01.conf)
             - Finger penalties   (from etc/effort/weight/01.conf)
             - Weight scalars     (kb, kp, ks, k1, k2, k3 from k/01.conf)
             - Trigram awareness  (k1/k2/k3 multi-stroke path cost)
  GA       : Elitism + Tournament Selection + Order Crossover (OX1)
=============================================================================
"""

import random
# import math
import collections
# import os
import time

# ─────────────────────────────────────────────────────────────────────────────
# 0.  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

CORPUS_PATH     = "/corpus/books_short.txt"  # 2.97 MB carpalx literature corpus #or /corpus/java.txt 
POPULATION_SIZE = 200
GENERATIONS     = 1000
MUTATION_RATE   = 0.08
ELITE_FRACTION  = 0.10
TOURNAMENT_SIZE = 5

# ─────────────────────────────────────────────────────────────────────────────
# 1.  CARPALX EFFORT MODEL  (values taken directly from config files)
# ─────────────────────────────────────────────────────────────────────────────

# --- k/01.conf weights ---
KB = 0.3555   # base effort weight
KP = 0.6423   # penalty effort weight
KS = 0.4268   # stroke path weight
K1 = 1.000    # first  key in trigram
K2 = 0.367    # second key in trigram
K3 = 0.235    # third  key in trigram

# --- effort/weight/01.conf ---
W_ROW    = 1.3088   # row    penalty multiplier
W_FINGER = 2.5948   # finger penalty multiplier
W_HAND   = 1.0      # hand   penalty multiplier

# Row penalties (carpalx row 0=top, 1=upper-mid, 2=home, 3=lower)
ROW_PENALTY = {0: 1.5, 1: 0.5, 2: 0.0, 3: 1.0}

# Finger penalties (index 0=left pinky … 9=right pinky)
# left  = [1, 0.5, 0, 0, 0]   (pinky, ring, mid, index-outer, index-inner)
# right = [0, 0, 0, 0.5, 1]
FINGER_PENALTY = [1.0, 0.5, 0.0, 0.0, 0.0,   # left  hand fingers
                  0.0, 0.0, 0.0, 0.5, 1.0]    # right hand fingers

# Base effort per key position (row 1 = number row, row 2 = top alpha, etc.)
# Approximated from effort/base/02.conf for a standard staggered keyboard.
# Rows 0–2 map to our top / home / bottom rows.
BASE_EFFORT_GRID = [
    # col: 0    1    2    3    4    5    6    7    8    9
    [4.0, 2.5, 1.8, 1.8, 2.5, 2.5, 1.8, 1.8, 2.5, 4.0],  # row 0  top
    [1.5, 1.0, 0.8, 0.5, 1.0, 1.0, 0.5, 0.8, 1.0, 1.5],  # row 1  home row ← best
    [2.5, 1.8, 1.5, 1.3, 2.0, 2.0, 1.3, 1.5, 1.8, 2.5],  # row 2  bottom
]

# Map column index → finger index (0–9)
COL_TO_FINGER_IDX = [0, 1, 2, 3, 3, 6, 6, 7, 8, 9]

# Map column index → hand ('L' or 'R')
COL_TO_HAND = ['L','L','L','L','L','R','R','R','R','R']

# ─────────────────────────────────────────────────────────────────────────────
# 2.  30-KEY LAYOUT DEFINITION
# ─────────────────────────────────────────────────────────────────────────────

ALPHABET = list("abcdefghijklmnopqrstuvwxyz.,;'")   # 30 chars → 3 × 10 grid

QWERTY_30 = list("qwertyuiop"
                 "asdfghjkl;"
                 "zxcvbnm,.'")

def layout_info(layout):
    """Return dicts: char→row, char→col, char→finger_idx, char→hand."""
    row_map, col_map, finger_map, hand_map = {}, {}, {}, {}
    for idx, ch in enumerate(layout):
        r, c = divmod(idx, 10)
        row_map[ch]    = r
        col_map[ch]    = c
        finger_map[ch] = COL_TO_FINGER_IDX[c]
        hand_map[ch]   = COL_TO_HAND[c]
    return row_map, col_map, finger_map, hand_map

# ─────────────────────────────────────────────────────────────────────────────
# 3.  CORPUS LOADING — real bigrams + trigrams from carpalx books
# ─────────────────────────────────────────────────────────────────────────────

def load_corpus(path):
    """
    Read the carpalx books corpus and extract:
      - bigram  frequency dict  {(a,b): count}
      - trigram frequency dict  {(a,b,c): count}
    Returns normalised float frequencies.
    """
    print(f"[Corpus] Reading {path} …", end=" ", flush=True)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read().lower()

    valid = set(ALPHABET)
    chars = [ch for ch in text if ch in valid]

    bigrams  = collections.Counter()
    trigrams = collections.Counter()
    for i in range(len(chars) - 2):
        a, b, c = chars[i], chars[i+1], chars[i+2]
        bigrams[(a, b)]    += 1
        trigrams[(a, b, c)] += 1

    total_bi  = sum(bigrams.values())  or 1
    total_tri = sum(trigrams.values()) or 1

    bigrams  = {k: v / total_bi  * 1000 for k, v in bigrams.items()}
    trigrams = {k: v / total_tri * 1000 for k, v in trigrams.items()
                if v / total_tri * 1000 > 0.005}   # prune rare trigrams

    print(f"{len(chars):,} chars → {len(bigrams):,} bigrams, "
          f"{len(trigrams):,} trigrams")
    return bigrams, trigrams

# ─────────────────────────────────────────────────────────────────────────────
# 4.  CARPALX FITNESS FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def key_base_effort(row, col):
    return BASE_EFFORT_GRID[row][col]

def key_penalty(row, col):
    """Row + finger component of carpalx penalty."""
    rp = ROW_PENALTY[row] * W_ROW
    fp = FINGER_PENALTY[COL_TO_FINGER_IDX[col]] * W_FINGER
    return rp + fp

def stroke_effort(row, col):
    """Total effort for a single keystroke = KB*base + KP*penalty."""
    b = key_base_effort(row, col)
    p = key_penalty(row, col)
    return KB * b + KP * p

def same_hand(h1, h2):
    return h1 == h2

def same_finger(f1, f2):
    return f1 == f2

def hand_alternation_penalty(h1, h2, h3):
    """Penalise runs of 3 on same hand."""
    if h1 == h2 == h3:
        return 1.0
    return 0.0

def calculate_fitness(layout, bigrams, trigrams):
    """
    Carpalx-faithful effort = sum over trigrams of:
      (K1*e1 + K2*e2 + K3*e3) * freq
    plus same-finger bigram penalty and hand-balance penalty.
    Returns 1/cost (higher = better).
    """
    row_map, col_map, finger_map, hand_map = layout_info(layout)

    total_effort = 0.0

    # ── Trigram path effort (K1/K2/K3 weighted) ─────────────────────────────
    for (a, b, c), freq in trigrams.items():
        if a not in row_map or b not in row_map or c not in row_map:
            continue
        e1 = stroke_effort(row_map[a], col_map[a])
        e2 = stroke_effort(row_map[b], col_map[b])
        e3 = stroke_effort(row_map[c], col_map[c])

        path_cost = K1*e1 + K2*e2 + K3*e3

        # Extra: penalise same-finger transitions within the trigram
        sf_pen = 0.0
        if same_finger(finger_map[a], finger_map[b]):
            sf_pen += 1.5 * e2
        if same_finger(finger_map[b], finger_map[c]):
            sf_pen += 1.5 * e3

        # Extra: penalise all-same-hand trigrams
        sh_pen = hand_alternation_penalty(hand_map[a], hand_map[b], hand_map[c]) * 0.8

        total_effort += (path_cost + sf_pen + sh_pen) * freq

    # ── Bigram same-finger penalty (catches pairs not in trigrams) ──────────
    for (a, b), freq in bigrams.items():
        if a not in row_map or b not in row_map:
            continue
        if same_finger(finger_map[a], finger_map[b]) and a != b:
            penalty = stroke_effort(row_map[b], col_map[b]) * 2.0 * KS
            total_effort += penalty * freq

    # ── Hand balance penalty ─────────────────────────────────────────────────
    left_load = sum(f for (a, _), f in bigrams.items()
                    if a in hand_map and hand_map[a] == 'L')
    right_load = sum(f for (a, _), f in bigrams.items()
                     if a in hand_map and hand_map[a] == 'R')
    denom = left_load + right_load or 1
    imbalance = abs(left_load - right_load) / denom
    total_effort += imbalance * 200

    return 1.0 / (total_effort + 1e-9)

# ─────────────────────────────────────────────────────────────────────────────
# 5.  GENETIC OPERATORS
# ─────────────────────────────────────────────────────────────────────────────

def ordered_crossover(p1, p2):
    n    = len(p1)
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
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(layout)), 2)
        layout[i], layout[j] = layout[j], layout[i]
    return layout

def tournament_select(population, scores):
    contestants = random.sample(list(zip(population, scores)), TOURNAMENT_SIZE)
    return max(contestants, key=lambda x: x[1])[0]

# ─────────────────────────────────────────────────────────────────────────────
# 6.  MAIN GA LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_ga(bigrams, trigrams):
    n        = len(ALPHABET)
    n_elite  = max(1, int(POPULATION_SIZE * ELITE_FRACTION))
    population = [random.sample(ALPHABET, n) for _ in range(POPULATION_SIZE)]

    best_layout  = None
    best_fitness = 0.0
    history      = []
    start        = time.time()

    print(f"\n{'='*62}")
    print(f"  Carpalx GA  |  pop={POPULATION_SIZE}  gen={GENERATIONS}")
    print(f"{'='*62}")

    for gen in range(GENERATIONS):
        scored = [(lay, calculate_fitness(lay, bigrams, trigrams))
                  for lay in population]
        scored.sort(key=lambda x: x[1], reverse=True)

        if scored[0][1] > best_fitness:
            best_fitness = scored[0][1]
            best_layout  = scored[0][0][:]

        history.append(1.0 / best_fitness)

        if gen % 100 == 0 or gen == GENERATIONS - 1:
            print(f"  Gen {gen:>5} | Cost: {1/best_fitness:>10.2f} | "
                  f"Elapsed: {time.time()-start:>5.1f}s")

        elites     = [lay for lay, _ in scored[:n_elite]]
        score_vals = [sc  for _,   sc in scored]
        next_gen   = elites[:]
        while len(next_gen) < POPULATION_SIZE:
            p1    = tournament_select(population, score_vals)
            p2    = tournament_select(population, score_vals)
            child = ordered_crossover(p1, p2)
            child = mutate(child)
            next_gen.append(child)
        population = next_gen

    print(f"\n  Done in {time.time()-start:.1f}s  |  Best cost: {1/best_fitness:.2f}")
    return best_layout, best_fitness, history

# ─────────────────────────────────────────────────────────────────────────────
# 7.  OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

def display_layout(layout, label="Layout"):
    print(f"\n{'─'*50}")
    print(f"  {label}")
    print(f"{'─'*50}")
    labels  = ["TOP ", "HOME", "BOT "]
    staggers = ["", " ", "  "]
    for i in range(3):
        row    = layout[i*10:(i+1)*10]
        keys   = "  ".join(f"[{k.upper()}]" for k in row)
        print(f"  {labels[i]} {staggers[i]}{keys}")
    print(f"{'─'*50}")

def display_comparison(qwerty, optimized, bigrams, trigrams):
    qc  = 1.0 / calculate_fitness(qwerty,    bigrams, trigrams)
    oc  = 1.0 / calculate_fitness(optimized, bigrams, trigrams)
    pct = (qc - oc) / qc * 100
    print(f"\n{'='*50}")
    print("  RESULTS")
    print(f"{'='*50}")
    print(f"  QWERTY effort score   : {qc:>10.2f}")
    print(f"  Optimized effort score: {oc:>10.2f}")
    print(f"  Reduction             : {pct:>9.1f}%")
    print(f"{'='*50}")

    # Home-row analysis
    home_chars = optimized[10:20]
    print(f"\n  Home row: {' '.join(k.upper() for k in home_chars)}")
    print(f"  (vowels on home row: "
          f"{[k.upper() for k in home_chars if k in 'aeiou']})")

def save_results(layout, history, bigrams, trigrams, path="keyboard_results_carpalx.txt"):
    with open(path, "w") as f:
        f.write("CARPALX-POWERED KEYBOARD OPTIMIZER — RESULTS\n")
        f.write("=" * 50 + "\n\n")
        labels = ["Top Row : ", "Home Row: ", "Bot Row : "]
        for i, label in enumerate(labels):
            row = layout[i*10:(i+1)*10]
            f.write(label + "  ".join(k.upper() for k in row) + "\n")
        f.write("\nFlat array:\n" + str(layout) + "\n\n")
        qc = 1.0 / calculate_fitness(QWERTY_30, bigrams, trigrams)
        oc = 1.0 / calculate_fitness(layout,    bigrams, trigrams)
        f.write(f"QWERTY effort score   : {qc:.2f}\n")
        f.write(f"Optimized effort score: {oc:.2f}\n")
        f.write(f"Reduction             : {(qc-oc)/qc*100:.1f}%\n\n")
        f.write("Cost per 100 generations:\n")
        for i, cost in enumerate(history):
            if i % 100 == 0:
                f.write(f"  Gen {i:>5}: {cost:.2f}\n")
    print(f"  Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# 8.  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bigrams, trigrams = load_corpus(CORPUS_PATH)

    display_layout(QWERTY_30, label="BASELINE: QWERTY")

    best_layout, best_fitness, history = run_ga(bigrams, trigrams)

    display_layout(best_layout, label="OPTIMIZED: Carpalx GA Result")
    display_comparison(QWERTY_30, best_layout, bigrams, trigrams)
    save_results(best_layout, history, bigrams, trigrams)

    print("\n  Tip: swap CORPUS_PATH to 'java.txt' or 'ruby.txt' from")
    print("  the carpalx corpus to optimise for programming layouts.\n")
