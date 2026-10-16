#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace subspot {

// Expected goals for each side over 90 minutes. Produced upstream by the ML model.
struct MatchRates {
  double home_xg;
  double away_xg;
};

// Win / draw / loss probabilities from the home side's perspective.
struct OutcomeProbabilities {
  double home_win;
  double draw;
  double away_win;
};

struct SimulationConfig {
  std::size_t num_simulations = 10'000;
  std::size_t num_threads = 1;
  std::uint64_t seed = 42;
  // Scorelines above this are folded into the last bucket of the grid.
  int max_goals = 10;
};

struct SimulationResult {
  OutcomeProbabilities outcomes;
  double mean_home_goals;
  double mean_away_goals;
  // scoreline_grid[h * (max_goals + 1) + a] = P(home scores h, away scores a)
  std::vector<double> scoreline_grid;
  int max_goals;
};

// Monte Carlo simulation, minute by minute. Deterministic for a given seed and thread count.
// Today the scoring rate is constant across the match; game-state effects (a leading side
// sitting deeper) will hook into the per-minute rate later.
SimulationResult simulate_match(const MatchRates& rates, const SimulationConfig& config);

// Closed-form answer for independent Poisson goals. The simulator must converge to this
// when rates are constant, which is how the engine is tested.
OutcomeProbabilities exact_poisson_outcomes(const MatchRates& rates, int max_goals = 20);

}  // namespace subspot
