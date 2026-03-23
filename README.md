# ⌨️ Keyboard Configuration using Genetic Algorithm

> Evolving an ergonomic keyboard layout that reduces typing effort by **49.4%** (English) and **49.6%** (Java) compared to QWERTY — powered by the Carpalx biomechanical model and real corpus data.

---

## 📌 Overview

The standard **QWERTY keyboard** was designed in 1873 for mechanical typewriters — not for human hands. It forces excessive finger travel, overloads weak pinky and ring fingers, and contributes to Repetitive Strain Injuries (RSI) such as Carpal Tunnel Syndrome and Tendonitis.

This project uses a **Genetic Algorithm (GA)** to discover a keyboard layout that minimizes biomechanical typing effort. The fitness function is grounded in the authentic **Carpalx effort model** — calibrated using real constants from published research — and trained on real corpus data for two use cases: English prose and Java code.

---

## 📊 Results

### English Prose (books_short.txt — 2,373,664 characters)

| Metric | QWERTY | GA Optimized |
|--------|--------|--------------|
| Carpalx effort score | 3,521.37 | 1,781.59 |
| **Effort reduction** | — | **49.4%** |
| Bigrams extracted | — | 806 |
| Trigrams used | — | 6,978 |
| Time to converge | — | ~1,071s (1000 gen) |

### Optimized Layout — English

```
TOP : Q   J   G   F   V   ;   '   K   X   Z
HOME: B   C   L   N   M   I   A   D   Y   .
BOT : P   W   T   S   R   O   E   H   U   ,
```

Vowels **I** and **A** on the home row alongside high-frequency consonants **L, N, M** — with common letters T, S, R, O, E, H accessible on the bottom row.

---

### Java Code (java.txt — 1,467,254 characters)

| Metric | QWERTY | GA Optimized |
|--------|--------|--------------|
| Carpalx effort score | 3,745.99 | 1,886.61 |
| **Effort reduction** | — | **49.6%** |
| Bigrams extracted | — | 861 |
| Trigrams used | — | 6,861 |
| Time to converge | — | ~1,128s (1000 gen) |

### Optimized Layout — Java

```
TOP : '   Q   J   B   X   ,   K   M   W   Z
HOME: Y   G   I   N   P   U   A   L   ;   V
BOT : H   D   E   R   C   O   S   T   .   F
```

Vowels **I, U, A** all on the home row. The semicolon `;` pulled to home row (terminates every Java statement). Common Java keywords use E, R, C, S, T — all on the bottom row.

---

## 🧬 How It Works

The keyboard layout problem has **30! ≈ 2.65 × 10³²** possible arrangements — far too large for exhaustive search. A Genetic Algorithm solves this by simulating natural evolution:

```
Random population (200 layouts)
        ↓
Evaluate fitness (Carpalx effort formula)
        ↓
Tournament selection (best of 5)
        ↓
OX1 Crossover (combine two parents)
        ↓
Swap mutation (8% chance)
        ↓
Repeat for 1,000 generations
        ↓
Best layout found
```

### GA Concepts Mapped

| GA Concept | Keyboard Mapping |
|------------|-----------------|
| Chromosome | One complete 30-key layout (Python list) |
| Gene | A single character at a key position |
| Population | 200 randomly generated layouts |
| Fitness | `1 / Carpalx effort score` |
| Selection | Tournament — best of 5 random candidates |
| Crossover | Order Crossover OX1 — always valid permutation |
| Mutation | Swap two random keys (8% probability) |
| Elitism | Top 10% survive unchanged each generation |

---

## 📐 Fitness Function

The fitness function uses the authentic **Carpalx biomechanical effort model**:

```
Fitness = 1 ÷ Σ ( K1·e₁ + K2·e₂ + K3·e₃ ) × freq(trigram)
```

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `KB` | 0.3555 | Base effort weight |
| `KP` | 0.6423 | Penalty effort weight |
| `KS` | 0.4268 | Stroke path weight |
| `K1 / K2 / K3` | 1.000 / 0.367 / 0.235 | Trigram position decay |
| `W_ROW` | 1.3088 | Row penalty multiplier |
| `W_FINGER` | 2.5948 | Finger penalty multiplier |

Four components contribute to total cost:
1. **Trigram path cost** — K1/K2/K3 weighted stroke effort per 3-char sequence
2. **Same-finger penalty** — +1.5× when consecutive keys use the same finger
3. **Same-hand penalty** — +0.8 when all 3 trigram keys land on one hand
4. **Hand balance penalty** — scaled up to 200 for fully one-sided layouts

---

## 📚 Dataset — Carpalx Corpus

Trained on **14 classic English novels** (~2.97 MB) from the [Carpalx project](https://mk.bcgsc.ca/carpalx/):

| | | |
|--|--|--|
| Alice's Adventures in Wonderland | Dracula | Great Expectations |
| The Picture of Dorian Gray | Huckleberry Finn | Jane Eyre |
| Moby-Dick | The Count of Monte Cristo | Pride and Prejudice |
| Sense and Sensibility | Sherlock Holmes | Tom Sawyer |
| Ulysses | Walden | |

After processing: **2,373,664 characters → 806 bigrams → 6,978 trigrams**

Java corpus: **1,467,254 characters → 861 bigrams → 6,861 trigrams**

---

## 🗂️ Project Structure

```
keyboard-config-ga/
├── Application_of_a_genetic_algorithm_to_the_keyboard.pdf (currently ignored by .gitignore)
├── keyboard_results_carpalx.txt
├── carpalx-master/                    # Local Carpalx copy (currently ignored by .gitignore)
├── carpalx.zip                        # Carpalx archive (currently ignored by .gitignore)
├── results/
│   ├── keyboard_ga.py             # Main Python GA implementation
│   ├── generated_data_ga.py       # Alternate/simplified GA
│   ├── corpus/                    # From Carpalx
│   │   ├── books_short.txt        # Collection of English text
│   │   └── java.txt               # Collection of Java code
│   ├── keyboard_results_carpalx.txt
│   ├── keyboard_results.txt
│   ├── keyboard_for_books.txt     # Full output — English run
│   ├── keyboard_for_java.txt      # Full output — Java run
│   ├── assignment_keyboard_ga*.docx
│   └── keyboard_ga_presentation.pptx
├── .gitignore
└── README.md
```

> `.gitignore` excludes `carpalx.zip`, `carpalx-master/`, and `Application_of_a_genetic_algorithm_to_the_keyboard.pdf` from tracking.

---

## ⚙️ Setup & Usage

### 1. Clone the repo

```bash
git clone https://github.com/bharath-akurathi/keyboard-config-ga.git
cd keyboard-config-ga
```

### 2. Check Python version

```bash
python --version
```

> Python 3.8+ required. No third-party packages needed — only `random`, `math`, `collections`, `time` from the standard library.

### 3. Verify corpus files

```bash
results/corpus/books_short.txt   # English prose corpus
results/corpus/java.txt          # Java code corpus
```

### 4. Run the optimizer

```bash
# Optimize for English prose
python results/keyboard_ga.py

# To optimize for Java code, change CORPUS_PATH in the script:
# CORPUS_PATH = "results/corpus/java.txt"

# Run alternate simplified implementation
python results/generated_data_ga.py
```

### 5. Expected output

```
[Corpus] Reading results/corpus/books_short.txt … 2,373,664 chars → 806 bigrams, 6,978 trigrams

==============================================================
  Carpalx GA  |  pop=200  gen=1000
==============================================================
  Gen     0 | Cost:    2574.76 | Elapsed:   1.1s
  Gen   100 | Cost:    1854.29 | Elapsed:  98.9s
  Gen   200 | Cost:    1808.35 | Elapsed: 212.7s
  Gen   300 | Cost:    1796.89 | Elapsed: 332.2s
  Gen   400 | Cost:    1794.06 | Elapsed: 446.8s
  Gen   500 | Cost:    1781.59 | Elapsed: 559.9s
  ...
  Gen   999 | Cost:    1781.59 | Elapsed: 1071.0s

Optimized Layout:
TOP : Q   J   G   F   V   ;   '   K   X   Z
HOME: B   C   L   N   M   I   A   D   Y   .
BOT : P   W   T   S   R   O   E   H   U   ,

QWERTY: 3521.37  |  Optimized: 1781.59  |  Reduction: 49.4%
```

---

## 🔧 Configuration

All parameters are at the top of `results/keyboard_ga.py`:

```python
CORPUS_PATH     = "results/corpus/books_short.txt"  # swap to java.txt for code layout
POPULATION_SIZE = 200                # more = richer gene pool, slower
GENERATIONS     = 1000               # more = better result
MUTATION_RATE   = 0.08               # 8% — swap two keys per child
ELITE_FRACTION  = 0.10               # top 10% survive unchanged
TOURNAMENT_SIZE = 5                  # candidates per selection round
```

---

## 📈 Cost Over Generations

### English corpus

```
Gen    0  →  2574.76   (random start)
Gen  100  →  1854.29   (fast early improvement)
Gen  200  →  1808.35
Gen  300  →  1796.89
Gen  400  →  1794.06
Gen  500  →  1781.59   (converged — 49.4% below QWERTY)
Gen 1000  →  1781.59   (held steady)
```

### Java corpus

```
Gen    0  →  2609.25   (random start)
Gen  100  →  1953.64   (fast early improvement)
Gen  200  →  1911.04
Gen  300  →  1889.10
Gen  400  →  1886.61   (converged — 49.6% below QWERTY)
Gen 1000  →  1886.61   (held steady)
```

> Both runs converged around generation 400–500 and held steady — a healthy sign the GA found a strong local optimum.

---

## 🏥 Why This Matters — Medical Context

Typing-related conditions affect millions of keyboard users:

- **Carpal Tunnel Syndrome** — median nerve compression from inflamed tendons
- **Tendonitis / Tenosynovitis** — tendon inflammation from repetitive movement
- **Osteoarthritis aggravation** — keypress micro-impacts worsen joint cartilage
- **Trigger Finger** — narrowed tendon sheath causes finger to lock

A layout that reduces effort by ~49% means significantly fewer micro-strain events per day — across millions of keystrokes per year, this makes a meaningful ergonomic difference.

---

## 📖 References

1. **Krzywinski, M.** (2007). *Carpalx — Keyboard Layout Optimizer*. Genome Sciences Centre.
   → http://mkweb.bcgsc.ca/carpalx/

2. **Eggers, J., De Brock, B., & Land, R.** (2020). *Application of a Genetic Algorithm to the Keyboard Layout Problem*. University of Groningen.
   → https://www.researchgate.net/publication/338443852

3. **Norvig, P.** (2012). *English Letter Frequency Counts: Mayzner Revisited*. Google Research.
   → http://norvig.com/mayzner.html

4. **Goldberg, D. E.** (1989). *Genetic Algorithms in Search, Optimization and Machine Learning*. Addison-Wesley.

5. **adumb** (2023). *Using AI to Create the Perfect Keyboard* [YouTube].
   → https://youtu.be/EOaPb9wrgDY

---

## 📄 License

This project (code, assignment, and presentation) is released under the **MIT License** — free to use, modify, and distribute with attribution.

The Carpalx corpus (books) consists of public domain texts from [Project Gutenberg](https://www.gutenberg.org/).
The Carpalx configuration files are the work of Martin Krzywinski. A local copy may be present in this working tree, but `.gitignore` is configured to exclude Carpalx archive/folder paths from new tracking.

---

<div align="center">
  <sub>Built as part of a Machine Learning assignment on Bio-Inspired Computing</sub>
</div>