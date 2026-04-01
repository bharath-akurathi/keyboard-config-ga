"""
Keyboard Configuration using Genetic Algorithm
3Blue1Brown-style Manim Animation

Scenes:
  1. TitleScene          — title card
  2. QwertyProblemScene  — QWERTY keyboard, highlight bad placements
  3. SearchSpaceScene    — 30! visualisation
  4. ChromosomeScene     — what a chromosome is
  5. FitnessScene        — fitness function explained visually
  6. BigramScene         — bigrams sliding window
  7. EvolutionScene      — population evolving over generations
  8. CrossoverScene      — OX1 crossover animated
  9. MutationScene       — swap mutation
  10. ResultScene        — before/after layout comparison

Run individual scenes:
  manim -pql keyboard_ga_animation.py TitleScene
Run all (medium quality):
  manim -pqm keyboard_ga_animation.py
"""

from manim import *
import random
import numpy as np

# ── Colour palette (3b1b-inspired dark theme) ──────────────────────────────
BG       = "#0D1117"
TEAL     = "#0D9488"
TEAL2    = "#14B8A6"
MINT     = "#5EEAD4"
GOLD     = "#F59E0B"
RED      = "#EF4444"
BLUE     = "#1E40AF"
BLUE2    = "#3B82F6"
DIM      = "#64748B"
WHITE    = "#F0F4F8"
NAVY     = "#0F172A"

config.background_color = BG

QWERTY = list("QWERTYUIOPASDFGHJKL;ZXCVBNM,.'")
OPT_EN = list("QJGFV;'KXZBCLNMIADY.PWTSROEHU,")
FREQ_KEYS = set("ETAOINSHRDLUCMFYWGPBVKJXQZ")

def freq_color(ch):
    rank = "ETAOINSHRDLCUMWFGYPBVKJXQZ;,.'".find(ch.upper())
    if rank < 5:   return RED
    if rank < 12:  return GOLD
    if rank < 20:  return BLUE2
    return DIM


# ── Reusable keyboard grid builder ─────────────────────────────────────────
def build_keyboard(layout, scale=0.38, color_fn=None, highlight=None):
    """Return a VGroup of 30 key squares with labels."""
    keys = VGroup()
    rows = [layout[0:10], layout[10:20], layout[20:30]]
    offsets = [0, 0.19, 0.38]          # stagger per row (in units)

    for ri, row in enumerate(rows):
        for ci, ch in enumerate(row):
            fill = color_fn(ch) if color_fn else NAVY
            if highlight and ch in highlight:
                fill = TEAL
            sq = RoundedRectangle(
                corner_radius=0.08, width=0.85, height=0.85,
                fill_color=fill, fill_opacity=0.9,
                stroke_color=TEAL2, stroke_width=1.2
            )
            label = Text(ch, font_size=18, color=WHITE,
                         font="Courier New", weight=BOLD)
            key = VGroup(sq, label)
            key.arrange(IN)
            label.move_to(sq.get_center())
            x = (ci - 4.5) * 0.9 + offsets[ri]
            y = (1 - ri) * 0.92
            key.move_to([x, y, 0])
            keys.add(key)

    keys.scale(scale)
    return keys


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 1 — Title
# ═══════════════════════════════════════════════════════════════════════════
class TitleScene(Scene):
    def construct(self):
        # Background glow
        glow = Circle(radius=3.5, fill_color=TEAL, fill_opacity=0.04,
                      stroke_width=0)
        self.add(glow)

        title1 = Text("Keyboard Configuration", font_size=52,
                      color=WHITE, font="Arial", weight=BOLD)
        title2 = Text("using Genetic Algorithm", font_size=52,
                      color=TEAL2, font="Arial", weight=BOLD)
        subtitle = Text(
            "Bio-Inspired Optimization  ·  Carpalx Biomechanical Model",
            font_size=22, color=DIM, font="Arial"
        )

        title1.move_to(UP * 0.8)
        title2.next_to(title1, DOWN, buff=0.2)
        subtitle.next_to(title2, DOWN, buff=0.55)

        # Stat pill
        pill_bg = RoundedRectangle(
            corner_radius=0.22, width=5.2, height=0.65,
            fill_color=NAVY, fill_opacity=1,
            stroke_color=TEAL, stroke_width=2
        )
        pill_txt = Text("49.4% less effort than QWERTY",
                        font_size=20, color=MINT, font="Arial", weight=BOLD)
        pill = VGroup(pill_bg, pill_txt).arrange(IN)
        pill_txt.move_to(pill_bg.get_center())
        pill.next_to(subtitle, DOWN, buff=0.55)

        # Divider line
        line = Line(LEFT * 3, RIGHT * 3, color=TEAL, stroke_width=2)
        line.next_to(title2, DOWN, buff=0.22)

        self.play(Write(title1), run_time=1.0)
        self.play(Write(title2), run_time=1.0)
        self.play(Create(line), run_time=0.5)
        self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(pill, scale=0.9), run_time=0.8)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 2 — The QWERTY Problem
# ═══════════════════════════════════════════════════════════════════════════
class QwertyProblemScene(Scene):
    def construct(self):
        header = Text("The Problem with QWERTY",
                      font_size=38, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)

        year = Text("Designed in 1873 for typewriters — not human hands.",
                    font_size=22, color=DIM, font="Arial")
        year.next_to(header, DOWN, buff=0.25)

        self.play(Write(header), FadeIn(year, shift=UP * 0.15), run_time=1.0)

        # Draw QWERTY keyboard with frequency colouring
        kbd = build_keyboard(QWERTY, scale=0.42, color_fn=freq_color)
        kbd.move_to(DOWN * 0.3)
        self.play(LaggedStart(*[GrowFromCenter(k) for k in kbd],
                               lag_ratio=0.04), run_time=2.0)
        self.wait(0.5)

        # Legend
        legend_items = [
            (RED,   "Very frequent  (E T A O I)"),
            (GOLD,  "Frequent       (N S H R D)"),
            (BLUE2, "Less frequent  (L C U M F)"),
            (DIM,   "Rare           (Z X Q J)"),
        ]
        legend = VGroup()
        for col, lbl in legend_items:
            dot = Dot(color=col, radius=0.1)
            txt = Text(lbl, font_size=16, color=WHITE, font="Arial")
            row = VGroup(dot, txt).arrange(RIGHT, buff=0.18)
            legend.add(row)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        legend.to_edge(RIGHT, buff=0.35)
        legend.shift(DOWN * 0.3)

        self.play(FadeIn(legend), run_time=0.8)

        # Highlight the issue: E, T, A are NOT on home row
        problem_label = Text(
            "E, T, A are the most used letters\n— but NOT on the home row!",
            font_size=20, color=RED, font="Arial"
        )
        problem_label.to_edge(LEFT, buff=0.4)
        problem_label.shift(DOWN * 1.8)

        # Home row bracket
        home_start = kbd[10].get_left() + LEFT * 0.05
        home_end   = kbd[19].get_right() + RIGHT * 0.05
        brace = Brace(VGroup(kbd[10], kbd[19]), direction=DOWN, color=TEAL2)
        brace_lbl = Text("Home Row", font_size=16, color=TEAL2, font="Arial")
        brace_lbl.next_to(brace, DOWN, buff=0.1)

        self.play(Create(brace), Write(brace_lbl), run_time=0.8)
        self.play(FadeIn(problem_label), run_time=0.8)

        # Flash the E key (index 2 in QWERTY top row)
        e_key = kbd[2]
        self.play(e_key.animate.scale(1.3).set_stroke(RED, width=4),
                  run_time=0.4)
        self.play(e_key.animate.scale(1/1.3).set_stroke(TEAL2, width=1.2),
                  run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 3 — The Search Space
# ═══════════════════════════════════════════════════════════════════════════
class SearchSpaceScene(Scene):
    def construct(self):
        header = Text("The Search Space",
                      font_size=38, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # 30! explanation
        eq = Text(
            "30! = 2.65 x 10^32",
            font_size=56, color=GOLD, font="Courier New", weight=BOLD
        )
        eq.move_to(UP * 0.8)

        sub = Text("possible keyboard arrangements", font_size=26,
                   color=DIM, font="Arial")
        sub.next_to(eq, DOWN, buff=0.3)

        self.play(Write(eq), run_time=1.2)
        self.play(FadeIn(sub), run_time=0.6)

        # Comparison boxes
        comparisons = [
            ("Atoms in the observable\nuniverse", "10^80"),
            ("Seconds since\nthe Big Bang",       "4.3 x 10^17"),
            ("Keyboard layouts",                   "2.65 x 10^32"),
        ]

        boxes = VGroup()
        for label, val in comparisons:
            bg = RoundedRectangle(
                corner_radius=0.15, width=3.4, height=1.5,
                fill_color=NAVY, fill_opacity=1,
                stroke_color=DIM, stroke_width=1.5
            )
            lbl = Text(label, font_size=16, color=DIM, font="Arial")
            num = Text(val, font_size=26,
                       color=WHITE if "Keyboard" not in label else GOLD,
                       font="Courier New", weight=BOLD)
            content = VGroup(lbl, num).arrange(DOWN, buff=0.12)
            content.move_to(bg.get_center())
            boxes.add(VGroup(bg, content))

        boxes.arrange(RIGHT, buff=0.4)
        boxes.move_to(DOWN * 1.4)

        # Highlight keyboard box
        boxes[2][0].set_stroke(TEAL, width=2.5)

        self.play(LaggedStart(*[FadeIn(b, scale=0.9) for b in boxes],
                               lag_ratio=0.2), run_time=1.2)

        conclusion = Text(
            "Exhaustive search is impossible.\nGenetic Algorithm is the solution.",
            font_size=22, color=MINT, font="Arial"
        )
        conclusion.to_edge(DOWN, buff=0.35)
        self.play(Write(conclusion), run_time=1.0)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 4 — Chromosome Representation
# ═══════════════════════════════════════════════════════════════════════════
class ChromosomeScene(Scene):
    def construct(self):
        header = Text("Chromosome = One Keyboard Layout",
                      font_size=36, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # Flat array
        layout = list("QWERTYUIOPASDFGHJKL;ZXCVBNM,.'")
        cells = VGroup()
        for i, ch in enumerate(layout):
            sq = Square(side_length=0.52,
                        fill_color=NAVY, fill_opacity=1,
                        stroke_color=TEAL, stroke_width=1.5)
            lbl = Text(ch, font_size=16, color=WHITE,
                       font="Courier New", weight=BOLD)
            lbl.move_to(sq.get_center())
            cells.add(VGroup(sq, lbl))

        cells.arrange(RIGHT, buff=0.06)
        cells.scale(0.85)
        cells.move_to(UP * 0.9)

        # Index labels below
        indices = VGroup()
        for i in range(30):
            if i % 5 == 0 or i == 29:
                idx_lbl = Text(str(i), font_size=12, color=DIM, font="Courier New")
                idx_lbl.next_to(cells[i], DOWN, buff=0.08)
                indices.add(idx_lbl)

        self.play(LaggedStart(*[GrowFromCenter(c) for c in cells],
                               lag_ratio=0.04), run_time=2.0)
        self.play(FadeIn(indices), run_time=0.5)

        # Row annotations — use string flags to avoid numpy array comparison
        row_labels = [
            (cells[0],  cells[9],  "Top row   (indices 0–9)",   "up"),
            (cells[10], cells[19], "Home row  (indices 10–19)", "down"),
            (cells[20], cells[29], "Bot row   (indices 20–29)", "down"),
        ]

        braces = VGroup()
        for start, end, text, dir_ in row_labels:
            direction = UP if dir_ == "up" else DOWN
            brace = Brace(VGroup(start, end), direction=direction, color=TEAL2)
            blbl = Text(text, font_size=15, color=TEAL2, font="Arial")
            blbl.next_to(brace, direction, buff=0.1)
            braces.add(VGroup(brace, blbl))

        self.play(LaggedStart(*[FadeIn(b) for b in braces],
                               lag_ratio=0.3), run_time=1.2)

        # Now show it as a keyboard
        kbd = build_keyboard(layout, scale=0.42, color_fn=lambda c: NAVY)
        kbd.move_to(DOWN * 1.6)

        arrow = Arrow(
            cells.get_bottom() + DOWN * 0.1,
            kbd.get_top() + UP * 0.1,
            color=TEAL, buff=0.1
        )
        arrow_lbl = Text("same layout, 2D form",
                         font_size=16, color=TEAL, font="Arial")
        arrow_lbl.next_to(arrow, RIGHT, buff=0.15)

        self.play(GrowArrow(arrow), Write(arrow_lbl))
        self.play(LaggedStart(*[GrowFromCenter(k) for k in kbd],
                               lag_ratio=0.03), run_time=1.5)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 5 — Bigrams & Trigrams
# ═══════════════════════════════════════════════════════════════════════════
class BigramScene(Scene):
    def construct(self):
        header = Text("Bigrams & Trigrams — Real Typing Patterns",
                      font_size=34, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # The word "the" as example
        word = "KEYBOARD"
        chars = VGroup()
        for ch in word:
            sq = Square(side_length=0.75,
                        fill_color=NAVY, fill_opacity=1,
                        stroke_color=DIM, stroke_width=1.5)
            lbl = Text(ch, font_size=28, color=WHITE,
                       font="Courier New", weight=BOLD)
            lbl.move_to(sq.get_center())
            chars.add(VGroup(sq, lbl))

        chars.arrange(RIGHT, buff=0.12)
        chars.move_to(UP * 1.0)

        self.play(LaggedStart(*[GrowFromCenter(c) for c in chars],
                               lag_ratio=0.1), run_time=1.2)

        # Sliding bigram window
        bigram_lbl = Text("Bigrams  (window size = 2):",
                          font_size=20, color=TEAL2, font="Arial")
        bigram_lbl.move_to(LEFT * 3.5 + DOWN * 0.2)
        self.play(FadeIn(bigram_lbl))

        bigram_results = VGroup()
        for i in range(len(word) - 1):
            # Highlight window
            rect = SurroundingRectangle(
                VGroup(chars[i], chars[i+1]),
                color=TEAL, buff=0.08, corner_radius=0.1
            )
            pair_text = Text(
                f"({word[i]}, {word[i+1]})",
                font_size=18, color=GOLD, font="Courier New"
            )
            if not bigram_results:
                pair_text.next_to(bigram_lbl, RIGHT, buff=0.3)
            else:
                pair_text.next_to(bigram_results[-1], RIGHT, buff=0.2)
            bigram_results.add(pair_text)

            self.play(Create(rect), run_time=0.3)
            self.play(FadeIn(pair_text), run_time=0.2)
            self.play(FadeOut(rect), run_time=0.2)

        self.wait(0.3)

        # Sliding trigram window
        trigram_lbl = Text("Trigrams  (window size = 3):",
                           font_size=20, color=MINT, font="Arial")
        trigram_lbl.move_to(LEFT * 3.5 + DOWN * 1.4)
        self.play(FadeIn(trigram_lbl))

        trigram_results = VGroup()
        for i in range(len(word) - 2):
            rect = SurroundingRectangle(
                VGroup(chars[i], chars[i+2]),
                color=MINT, buff=0.08, corner_radius=0.1
            )
            triple_text = Text(
                f"({word[i]},{word[i+1]},{word[i+2]})",
                font_size=16, color=MINT, font="Courier New"
            )
            if not trigram_results:
                triple_text.next_to(trigram_lbl, RIGHT, buff=0.3)
            else:
                triple_text.next_to(trigram_results[-1], RIGHT, buff=0.15)
            trigram_results.add(triple_text)

            self.play(Create(rect), run_time=0.3)
            self.play(FadeIn(triple_text), run_time=0.2)
            self.play(FadeOut(rect), run_time=0.2)

        # Corpus stats
        stats = VGroup(
            Text("English corpus:  2,373,664 chars  →  806 bigrams  +  6,978 trigrams",
                 font_size=17, color=DIM, font="Arial"),
        )
        stats.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(stats), run_time=0.8)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 6 — Fitness Function
# ═══════════════════════════════════════════════════════════════════════════
class FitnessScene(Scene):
    def construct(self):
        header = Text("Fitness Function — Scoring a Layout",
                      font_size=36, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # Main formula
        formula = Text(
            "Fitness = 1 / sum((K1*e1 + K2*e2 + K3*e3) * f)",
            font_size=30, color=MINT, font="Courier New", weight=BOLD
        )
        formula.move_to(UP * 1.4)
        self.play(Write(formula), run_time=1.5)

        # K weights with bar chart
        k_labels = ["K₁ = 1.000", "K₂ = 0.367", "K₃ = 0.235"]
        k_colors = [TEAL, TEAL2, MINT]
        k_values = [1.0, 0.367, 0.235]
        k_descs  = ["1st key\n(full effort)", "2nd key\n(hand moving)", "3rd key\n(momentum)"]

        bars = VGroup()
        for j, (lbl, col, val, desc) in enumerate(zip(k_labels, k_colors, k_values, k_descs)):
            bar = Rectangle(
                width=0.7, height=val * 1.6,
                fill_color=col, fill_opacity=0.85,
                stroke_width=0
            )
            bar_lbl = Text(lbl, font_size=16, color=col, font="Courier New")
            bar_desc = Text(desc, font_size=13, color=DIM, font="Arial")
            group = VGroup(bar_lbl, bar, bar_desc)
            group.arrange(DOWN, buff=0.12)
            bars.add(group)

        bars.arrange(RIGHT, buff=0.9)
        bars.move_to(DOWN * 0.4)

        self.play(LaggedStart(*[
            AnimationGroup(GrowFromEdge(b[1], DOWN), FadeIn(b[0]), FadeIn(b[2]))
            for b in bars
        ], lag_ratio=0.3), run_time=1.5)

        # Annotation: finger already moving
        arrow = CurvedArrow(
            bars[0][1].get_top() + UP * 0.05,
            bars[2][1].get_top() + UP * 0.05,
            color=GOLD, angle=-TAU / 6
        )
        arrow_lbl = Text("finger already moving →\ncosts less effort",
                         font_size=15, color=GOLD, font="Arial")
        arrow_lbl.next_to(arrow, UP, buff=0.1)
        self.play(Create(arrow), FadeIn(arrow_lbl), run_time=0.8)

        # Four cost components at bottom
        components = [
            (TEAL,  "Trigram path cost"),
            (RED,   "+1.5× same-finger"),
            (GOLD,  "+0.8 same-hand run"),
            (BLUE2, "±200 hand balance"),
        ]
        comp_group = VGroup()
        for col, txt in components:
            dot = Dot(color=col, radius=0.09)
            lbl = Text(txt, font_size=16, color=WHITE, font="Arial")
            item = VGroup(dot, lbl).arrange(RIGHT, buff=0.15)
            comp_group.add(item)

        comp_group.arrange(RIGHT, buff=0.5)
        comp_group.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(comp_group), run_time=0.8)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 7 — Population & Evolution
# ═══════════════════════════════════════════════════════════════════════════
class EvolutionScene(Scene):
    def construct(self):
        header = Text("Evolution — Population Over Generations",
                      font_size=34, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        random.seed(42)
        alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,;'")

        # Show 6 mini layouts as coloured rectangles (simplified)
        def mini_layout(seed_val, fitness):
            random.seed(seed_val)
            rects = VGroup()
            for i in range(30):
                r = Rectangle(
                    width=0.18, height=0.18,
                    fill_color=random.choice([NAVY, BLUE, TEAL, DIM]),
                    fill_opacity=0.9, stroke_width=0
                )
                rects.add(r)
            rects.arrange_in_grid(3, 10, buff=0.04)

            # Fitness bar
            bar_bg = Rectangle(width=1.8, height=0.18,
                                fill_color=DIM, fill_opacity=0.4, stroke_width=0)
            bar_fg = Rectangle(width=1.8 * fitness, height=0.18,
                                fill_color=TEAL if fitness > 0.7 else GOLD,
                                fill_opacity=1, stroke_width=0)
            bar_fg.align_to(bar_bg, LEFT)
            bar = VGroup(bar_bg, bar_fg)

            fit_label = Text(f"{fitness:.0%}", font_size=12, color=WHITE, font="Arial")
            bar_group = VGroup(bar, fit_label).arrange(RIGHT, buff=0.1)

            card = VGroup(rects, bar_group).arrange(DOWN, buff=0.12)
            bg = RoundedRectangle(
                corner_radius=0.1, width=2.2, height=1.5,
                fill_color=NAVY, fill_opacity=1,
                stroke_color=DIM, stroke_width=1.2
            )
            card.move_to(bg.get_center())
            return VGroup(bg, card)

        fitnesses_gen0 = [0.18, 0.22, 0.31, 0.15, 0.28, 0.20]
        fitnesses_gen5 = [0.55, 0.61, 0.58, 0.72, 0.67, 0.64]

        pop0 = VGroup(*[mini_layout(i, f)
                        for i, f in enumerate(fitnesses_gen0)])
        pop0.arrange(RIGHT, buff=0.25)
        pop0.move_to(DOWN * 0.4)

        gen_label = Text("Generation 0  —  Random Population",
                         font_size=20, color=DIM, font="Arial")
        gen_label.next_to(pop0, UP, buff=0.3)

        self.play(FadeIn(gen_label))
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in pop0],
                               lag_ratio=0.12), run_time=1.2)
        self.wait(0.8)

        # Show "evolving..."
        dots = Text("Evolving . . .", font_size=24, color=TEAL, font="Arial")
        dots.move_to(DOWN * 2.3)
        self.play(FadeIn(dots))
        self.wait(0.6)
        self.play(FadeOut(dots))

        # Generation 5
        pop5 = VGroup(*[mini_layout(i + 10, f)
                        for i, f in enumerate(fitnesses_gen5)])
        pop5.arrange(RIGHT, buff=0.25)
        pop5.move_to(DOWN * 0.4)

        gen_label5 = Text("Generation 500  —  Evolved Population",
                          font_size=20, color=TEAL2, font="Arial")
        gen_label5.next_to(pop5, UP, buff=0.3)

        self.play(
            Transform(pop0, pop5),
            Transform(gen_label, gen_label5),
            run_time=1.2
        )
        self.wait(0.5)

        # Cost convergence curve
        axes = Axes(
            x_range=[0, 1000, 200],
            y_range=[1700, 2700, 200],
            x_length=6, y_length=2.2,
            axis_config={"color": DIM, "stroke_width": 1.5},
            tips=False
        )
        axes.to_edge(DOWN, buff=0.2)
        axes.shift(RIGHT * 0.5)

        x_lbl = Text("Generation", font_size=14, color=DIM, font="Arial")
        y_lbl = Text("Cost", font_size=14, color=DIM, font="Arial").rotate(PI/2)
        x_lbl.next_to(axes, DOWN, buff=0.1)
        y_lbl.next_to(axes, LEFT, buff=0.1)

        # Real convergence data
        points = [
            (0, 2574), (100, 1854), (200, 1808),
            (300, 1796), (400, 1794), (500, 1781),
            (600, 1781), (700, 1781), (800, 1781),
            (900, 1781), (1000, 1781),
        ]
        curve = axes.plot_line_graph(
            x_values=[p[0] for p in points],
            y_values=[p[1] for p in points],
            line_color=TEAL,
            vertex_dot_radius=0.06,
            vertex_dot_style={"fill_color": TEAL2},
            stroke_width=2.5
        )

        converge_line = DashedLine(
            axes.c2p(500, 1700), axes.c2p(500, 1781),
            color=GOLD, stroke_width=1.5
        )
        converge_lbl = Text("Converged\nGen ~500", font_size=13,
                            color=GOLD, font="Arial")
        converge_lbl.next_to(converge_line, DOWN, buff=0.08)

        self.play(Create(axes), FadeIn(x_lbl), FadeIn(y_lbl))
        self.play(Create(curve), run_time=1.5)
        self.play(Create(converge_line), FadeIn(converge_lbl))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 8 — OX1 Crossover
# ═══════════════════════════════════════════════════════════════════════════
class CrossoverScene(Scene):
    def construct(self):
        header = Text("Order Crossover (OX1)",
                      font_size=38, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        sub = Text("How two parents produce a valid child — no duplicate keys",
                   font_size=20, color=DIM, font="Arial")
        sub.next_to(header, DOWN, buff=0.2)
        self.play(Write(header), FadeIn(sub))

        # 10-key example
        p1 = list("ABCDEFGHIJ")
        p2 = list("GIAFBJDECH")

        def make_array(chars, label_str, label_col=WHITE):
            cells = VGroup()
            for ch in chars:
                sq = Square(side_length=0.62,
                            fill_color=NAVY, fill_opacity=1,
                            stroke_color=DIM, stroke_width=1.5)
                lbl = Text(ch, font_size=22, color=WHITE,
                           font="Courier New", weight=BOLD)
                lbl.move_to(sq.get_center())
                cells.add(VGroup(sq, lbl))
            cells.arrange(RIGHT, buff=0.08)

            row_label = Text(label_str, font_size=18, color=label_col,
                             font="Arial", weight=BOLD)
            row_label.next_to(cells, LEFT, buff=0.35)
            return VGroup(row_label, cells)

        row_p1    = make_array(p1, "Parent 1:", TEAL2)
        row_p2    = make_array(p2, "Parent 2:", GOLD)
        row_child = make_array(["?" ] * 10, "Child:   ", MINT)

        rows = VGroup(row_p1, row_p2, row_child)
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rows.move_to(ORIGIN)

        self.play(LaggedStart(
            FadeIn(row_p1), FadeIn(row_p2), FadeIn(row_child),
            lag_ratio=0.3
        ), run_time=1.2)
        self.wait(0.4)

        # Step 1: highlight segment a=2, b=5 from P1
        a, b = 2, 5
        cells_p1    = row_p1[1]
        cells_child = row_child[1]

        segment_rect = SurroundingRectangle(
            VGroup(cells_p1[a], cells_p1[b]),
            color=TEAL, buff=0.06, corner_radius=0.06
        )
        step1_lbl = Text("Step 1: Copy segment [2–5] from Parent 1",
                         font_size=17, color=TEAL, font="Arial")
        step1_lbl.to_edge(DOWN, buff=0.55)

        self.play(Create(segment_rect), Write(step1_lbl))

        # Copy segment into child
        for i in range(a, b + 1):
            ch = p1[i]
            new_sq = Square(side_length=0.62,
                            fill_color=TEAL, fill_opacity=0.85,
                            stroke_color=TEAL2, stroke_width=2)
            new_lbl = Text(ch, font_size=22, color=WHITE,
                           font="Courier New", weight=BOLD)
            new_lbl.move_to(new_sq.get_center())
            new_key = VGroup(new_sq, new_lbl)
            new_key.move_to(cells_child[i].get_center())
            self.play(
                Transform(cells_child[i], new_key),
                run_time=0.3
            )
        self.wait(0.5)

        # Step 2: fill from P2
        step2_lbl = Text("Step 2: Fill remaining slots from Parent 2 (skipping C,D,E,F)",
                         font_size=17, color=GOLD, font="Arial")
        step2_lbl.to_edge(DOWN, buff=0.55)
        self.play(
            FadeOut(step1_lbl), FadeOut(segment_rect),
            Write(step2_lbl)
        )

        # Compute fill order
        segment_chars = set(p1[a:b+1])
        fill = [ch for ch in p2 if ch not in segment_chars]
        fill_idx = 0
        child_indices = [i for i in range(10) if i < a or i > b]

        cells_p2 = row_p2[1]

        for idx in child_indices:
            ch = fill[fill_idx]
            # find ch in p2 and highlight
            p2_pos = p2.index(ch)
            self.play(
                cells_p2[p2_pos].animate.set_stroke(GOLD, width=3),
                run_time=0.2
            )
            new_sq = Square(side_length=0.62,
                            fill_color=BLUE, fill_opacity=0.85,
                            stroke_color=GOLD, stroke_width=1.8)
            new_lbl = Text(ch, font_size=22, color=WHITE,
                           font="Courier New", weight=BOLD)
            new_lbl.move_to(new_sq.get_center())
            new_key = VGroup(new_sq, new_lbl)
            new_key.move_to(cells_child[idx].get_center())
            self.play(
                Transform(cells_child[idx], new_key),
                cells_p2[p2_pos].animate.set_stroke(DIM, width=1.5),
                run_time=0.25
            )
            fill_idx += 1

        result_lbl = Text("✓ Valid permutation — no duplicates, no missing keys",
                          font_size=18, color=MINT, font="Arial")
        result_lbl.to_edge(DOWN, buff=0.25)
        self.play(FadeOut(step2_lbl), Write(result_lbl))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 9 — Mutation
# ═══════════════════════════════════════════════════════════════════════════
class MutationScene(Scene):
    def construct(self):
        header = Text("Swap Mutation",
                      font_size=38, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        sub = Text("8% chance — prevents premature convergence",
                   font_size=22, color=DIM, font="Arial")
        sub.next_to(header, DOWN, buff=0.25)
        self.play(Write(header), FadeIn(sub))

        # Show a layout
        layout = list("BCLNMIADY.PWTSROEHU,QJGFV;'KXZ")
        cells = VGroup()
        for ch in layout:
            sq = Square(side_length=0.55,
                        fill_color=NAVY, fill_opacity=1,
                        stroke_color=DIM, stroke_width=1.5)
            lbl = Text(ch, font_size=18, color=WHITE,
                       font="Courier New", weight=BOLD)
            lbl.move_to(sq.get_center())
            cells.add(VGroup(sq, lbl))

        cells.arrange_in_grid(3, 10, buff=0.08)
        cells.scale(0.88)
        cells.move_to(UP * 0.3)

        self.play(LaggedStart(*[GrowFromCenter(c) for c in cells],
                               lag_ratio=0.03), run_time=1.5)

        # Probability indicator
        prob_bg = Rectangle(width=6, height=0.5,
                            fill_color=NAVY, fill_opacity=1, stroke_width=0)
        prob_bar = Rectangle(width=6 * 0.08, height=0.5,
                             fill_color=TEAL, fill_opacity=1, stroke_width=0)
        prob_bar.align_to(prob_bg, LEFT)
        prob_lbl = Text("8% probability triggers mutation",
                        font_size=16, color=DIM, font="Arial")
        prob_group = VGroup(prob_bg, prob_bar)
        prob_group.next_to(cells, DOWN, buff=0.35)
        prob_lbl.next_to(prob_group, DOWN, buff=0.1)

        self.play(FadeIn(prob_group), FadeIn(prob_lbl))

        # "random.random() < 0.08" coin flip animation
        coin_text = Text("random.random() = 0.042  <  0.08  →  MUTATE!",
                         font_size=17, color=GOLD, font="Courier New")
        coin_text.next_to(prob_lbl, DOWN, buff=0.2)
        self.play(Write(coin_text), run_time=0.8)
        self.wait(0.4)

        # Swap indices 3 and 22 (for example)
        swap_i, swap_j = 3, 22
        ci = cells[swap_i]
        cj = cells[swap_j]

        # Highlight them
        self.play(
            ci.animate.set_stroke(RED, width=4).scale(1.2),
            cj.animate.set_stroke(RED, width=4).scale(1.2),
            run_time=0.4
        )

        swap_lbl = Text(f"Swap position {swap_i} ↔ position {swap_j}",
                        font_size=18, color=RED, font="Arial")
        swap_lbl.to_edge(DOWN, buff=0.25)
        self.play(Write(swap_lbl))

        # Animate the swap
        pos_i = ci.get_center().copy()
        pos_j = cj.get_center().copy()

        self.play(
            ci.animate.move_to(pos_j),
            cj.animate.move_to(pos_i),
            run_time=0.9
        )

        self.play(
            ci.animate.set_stroke(TEAL, width=1.5).scale(1/1.2),
            cj.animate.set_stroke(TEAL, width=1.5).scale(1/1.2),
            run_time=0.4
        )

        result = Text("Layout still valid — two keys swapped, diversity maintained",
                      font_size=17, color=MINT, font="Arial")
        result.to_edge(DOWN, buff=0.25)
        self.play(FadeOut(swap_lbl), Write(result))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# SCENE 10 — Results
# ═══════════════════════════════════════════════════════════════════════════
class ResultScene(Scene):
    def construct(self):
        header = Text("Results — Before vs After",
                      font_size=38, color=WHITE, font="Arial", weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # QWERTY label
        q_lbl = Text("QWERTY (Baseline)", font_size=20,
                     color=DIM, font="Arial", weight=BOLD)
        q_lbl.move_to(LEFT * 3.3 + UP * 1.4)

        # Optimized label
        o_lbl = Text("GA Optimized", font_size=20,
                     color=TEAL2, font="Arial", weight=BOLD)
        o_lbl.move_to(RIGHT * 2.8 + UP * 1.4)

        self.play(FadeIn(q_lbl), FadeIn(o_lbl))

        # Draw both keyboards
        kbd_q = build_keyboard(QWERTY, scale=0.36, color_fn=freq_color)
        kbd_q.move_to(LEFT * 3.3 + DOWN * 0.1)

        kbd_o = build_keyboard(OPT_EN, scale=0.36, color_fn=freq_color)
        kbd_o.move_to(RIGHT * 2.8 + DOWN * 0.1)

        divider = DashedLine(UP * 1.8, DOWN * 2.0, color=DIM, stroke_width=1)

        self.play(
            LaggedStart(*[GrowFromCenter(k) for k in kbd_q], lag_ratio=0.03),
            run_time=1.2
        )
        self.play(Create(divider))
        self.play(
            LaggedStart(*[GrowFromCenter(k) for k in kbd_o], lag_ratio=0.03),
            run_time=1.2
        )

        # Score comparison
        score_q = Text("Cost: 3,521.37", font_size=18,
                       color=RED, font="Courier New")
        score_o = Text("Cost: 1,781.59", font_size=18,
                       color=TEAL2, font="Courier New")
        score_q.next_to(kbd_q, DOWN, buff=0.25)
        score_o.next_to(kbd_o, DOWN, buff=0.25)

        self.play(FadeIn(score_q), FadeIn(score_o))

        # Big reduction stat
        reduction = Text("49.4% reduction", font_size=36,
                         color=GOLD, font="Arial", weight=BOLD)
        reduction.to_edge(DOWN, buff=0.3)
        self.play(Write(reduction), run_time=0.8)

        # Home row annotation for optimized
        home_callout = Text(
            "HOME: B C L N M I A D Y .\n"
            "Vowels I, A + frequent consonants on home row",
            font_size=14, color=MINT, font="Arial"
        )
        home_callout.next_to(score_o, DOWN, buff=0.15)
        self.play(FadeIn(home_callout))
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)

        # End card
        end = Text("Genetic Algorithm — Keyboard Optimization",
                   font_size=32, color=WHITE, font="Arial", weight=BOLD)
        tag = Text("49.4% less effort than QWERTY  ·  Carpalx Biomechanical Model",
                   font_size=18, color=DIM, font="Arial")
        end.move_to(UP * 0.4)
        tag.next_to(end, DOWN, buff=0.3)
        self.play(Write(end), FadeIn(tag))
        self.wait(2)