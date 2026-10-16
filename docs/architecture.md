# Architecture

## Components

| Component | Responsibility |
| --- | --- |
| Ingestion (Lambda) | Pull each matchweek's results, xG and odds into S3 as raw files |
| Features (Glue + Athena) | Build point-in-time features: only what was knowable before kickoff |
| Model (PyTorch) | Predict each side's expected goals from team embeddings, form, rest and home advantage |
| Engine (C++) | Turn expected goals into full distributions by simulating each match many times |
| Evaluation (Python) | Walk-forward backtests scored with log loss and Brier score vs Pinnacle closing odds |
| App (SwiftUI) | Show forecasts, scoreline heatmaps, live re-simulation and the model's report card |

## Design decisions

### One simulation engine, two hosts

The engine is written once in C++ and exposed to Python with pybind11 and to Swift with C++
interoperability. Backtests and the app therefore run identical code, so the accuracy numbers
published in the app describe the code that produces its forecasts.

### Why simulate instead of using closed-form Poisson

With constant scoring rates, the scoreline distribution has a closed form, and the engine's tests
check that it converges to it. The simulator exists for what closed form can't express: scoring
rates that change with game state (a leading side sitting deeper, a trailing side pushing, a red
card), and in-match re-simulation from the current minute and score.

### Point-in-time correctness

Every feature is computed from data available before kickoff. Leakage, such as season averages
that include future matches, inflates backtest scores and is the most common failure in sports
models. Features carry an `as_of` timestamp and backtests only train on matches before the one
being predicted.

### Canonical team IDs

Sources spell clubs differently ("Man United" vs "Manchester United"). Every name is mapped to one
canonical ID, and unknown names raise an error instead of silently dropping rows from joins.

### The benchmark is the closing line

Pinnacle's closing odds, with the margin removed, are the strongest public forecast available.
Subspot reports how close it gets to them rather than claiming betting returns.
