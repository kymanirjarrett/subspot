#!/usr/bin/env bash
# Creates the roadmap as GitHub issues. Run once after the first push.
# Requires the GitHub CLI (https://cli.github.com) and `gh auth login`.
set -euo pipefail

for label in engine ml ios infra; do
  gh label create "$label" --force >/dev/null
done

issue() { gh issue create --title "$1" --label "$2" --body "$3"; }

issue "Dixon-Coles baseline with time-decay weighting" "ml" \
"Extend the Poisson baseline with the Dixon-Coles low-score correction and exponential time decay.

- [ ] Fit rho and the decay rate by maximum likelihood
- [ ] Tests showing the low-score correction changes 0-0/1-0/0-1/1-1 probabilities only"

issue "Walk-forward backtest against Pinnacle closing odds" "ml" \
"Refit before each matchweek using only earlier matches and score predictions against devigged closing odds.

- [ ] Log loss and Brier score per season for model vs market
- [ ] Calibration plot output
- [ ] Test that no fold trains on a match on or after its prediction date"

issue "Load Understat xG and join on canonical team IDs" "ml" \
"- [ ] Loader for match-level xG
- [ ] Every Understat team name maps through subspot_ml.data.teams
- [ ] Join coverage check: fail if any match is missing xG"

issue "Game-state scoring rates in the simulator" "engine" \
"Let each side's per-minute scoring rate depend on the score and minute.

- [ ] Configurable game-state multipliers
- [ ] With all multipliers at 1.0, results still match closed-form Poisson
- [ ] Benchmark sims/second before and after"

issue "Season simulator for title, top-four and relegation odds" "engine" \
"- [ ] Simulate all remaining fixtures N times and aggregate final table positions
- [ ] Benchmark with Google Benchmark and record results in the README"

issue "PyTorch expected-goals model with team embeddings" "ml" \
"- [ ] Learned team embeddings plus form, rest days and home advantage
- [ ] Promoted-team cold start strategy documented
- [ ] Beats the Dixon-Coles baseline on walk-forward log loss
- [ ] Experiment tracking and a model card"

issue "Create SwiftUI app target and fixtures list screen" "ios" \
"- [ ] Xcode app target depending on SubspotKit
- [ ] Fixture list with win/draw/loss bars
- [ ] Scoreline heatmap with Swift Charts"

issue "Link the C++ engine into the iOS app with Swift C++ interop" "ios" \
"- [ ] Engine builds for iOS
- [ ] On-device what-if: change score and minute, re-simulate"

issue "Ingestion Lambda and Glue catalog via CloudFormation" "infra" \
"- [ ] Scheduled Lambda lands football-data.co.uk files in the raw bucket
- [ ] Glue table and Athena workgroup
- [ ] AWS Budgets alarm"

echo "Roadmap issues created."
