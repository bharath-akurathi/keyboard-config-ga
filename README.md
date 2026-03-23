# ⌨️ Keyboard Configuration using Genetic Algorithm

> Evolving an ergonomic keyboard layout that reduces typing effort by **47.1%** compared to QWERTY — powered by the Carpalx biomechanical model and real literary corpus data.

---

## 📌 Overview

The standard **QWERTY keyboard** was designed in 1873 for mechanical typewriters — not for human hands. It forces excessive finger travel, overloads weak pinky and ring fingers, and contributes to Repetitive Strain Injuries (RSI) such as Carpal Tunnel Syndrome and Tendonitis.

This project uses a **Genetic Algorithm (GA)** to discover a keyboard layout that minimizes biomechanical typing effort. The fitness function is grounded in the authentic **Carpalx effort model** — calibrated using real constants from published research — and trained on **2,373,664 characters** of classic English literature.

---

## 📊 Results

| Metric | QWERTY | GA Optimized |
|--------|--------|--------------|
| Carpalx effort score | 3,521.4 | 1,863.1 |
| **Effort reduction** | — | **47.1%** |
| Finger travel | High | Significantly reduced |
| Home row usage | Low | High |
| Pinky / ring load | Heavy | Minimized |
| Same-finger bigrams | Common | Avoided |
| Hand balance | Uneven | ~50 / 50 |

### Optimized Layout (300 generations)

```
TOP : Q   X   ,   V   '   ;   Y   M   J   Z
HOME: K   G   O   H   L   F   I   N   C   P
BOT : .   D   A   S   R   U   E   T   W   B
```

Vowels **O** and **I** alongside high-frequency consonants **H, L, F, N** all land on the home row — exactly what ergonomics research recommends.

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
│   │   ├── books_short.txt        # Collection of English Text
│   │   └── java.txt               # Collection of java code
│   ├── keyboard_results_carpalx.txt
│   ├── keyboard_results.txt
│   ├── keyboard_for_books.txt
│   ├── keyboard_for_java.txt
│   ├── assignment_keyboard_ga*.docx
│   └── keyboard_ga_presentation.pptx
├── .gitignore
└── README.md
```

Note: `.gitignore` excludes `carpalx.zip`, `carpalx-master/`, and `Application_of_a_genetic_algorithm_to_the_keyboard.pdf` from new tracking. If these are already tracked in your clone, they still appear in your working tree.

---

## ⚙️ Setup & Usage

### 1. Clone the repo

```bash
git clone https://github.com/bharath-akurathi/keyboard-config-ga.git
cd keyboard-config-ga
```

### 2. Install dependencies

```bash
python --version
```

> Python 3.8+ required. No third-party packages are needed for the Python GA scripts.

### 3. Verify corpus files

This repository already includes corpus files in:

```bash
results/corpus/books_short.txt
results/corpus/java.txt
# full upstream corpus is under carpalx-master/corpus/
```

You can also point to your own `.txt` file by changing `CORPUS_PATH`.

### 4. Run the optimizer

```bash
# Optimize for English prose (books corpus)
python results/keyboard_ga.py

# Run alternate implementation
python results/generated_data_ga.py

# To optimize for Java code, change CORPUS_PATH in the script:
# CORPUS_PATH = "results/corpus/java.txt"
```

### 5. Expected output

```
[Corpus] Reading results/corpus/books_short.txt ...

==============================================================
  Carpalx GA  |  pop=200  gen=1000
==============================================================
  Gen     0 | Cost:    2849.04 | Elapsed:   0.0s
  Gen   100 | Cost:    1981.22 | Elapsed:  85.3s
  Gen   200 | Cost:    1901.45 | Elapsed: 170.1s
  ...

Optimized Layout:
TOP : Q   X   ,   V   '   ;   Y   M   J   Z
HOME: K   G   O   H   L   F   I   N   C   P
BOT : .   D   A   S   R   U   E   T   W   B

QWERTY: 3521.4  |  Optimized: 1863.1  |  Reduction: 47.1%
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

```
Gen    0  →  2849.04   (random start)
Gen  100  →  1981.22   (fast early gains)
Gen  200  →  1901.45
Gen  300  →  1863.14   (47.1% below QWERTY)
Gen  400  →  1851.77
...
Gen 1000  →  ~1820     (further improvement with full run)
```

---

## 🏥 Why This Matters — Medical Context

Typing-related conditions affect millions of keyboard users:

- **Carpal Tunnel Syndrome** — median nerve compression from inflamed tendons
- **Tendonitis / Tenosynovitis** — tendon inflammation from repetitive movement
- **Osteoarthritis aggravation** — keypress micro-impacts worsen joint cartilage
- **Trigger Finger** — narrowed tendon sheath causes finger to lock

A layout that reduces effort by 47.1% means significantly fewer micro-strain events per day — across millions of keystrokes per year, this makes a meaningful ergonomic difference.

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
  <sub>Built as part of an Machine Learning assignment on Bio-Inspired Computing</sub>
</div>