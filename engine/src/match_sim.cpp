#include "subspot/match_sim.hpp"

#include <algorithm>
#include <cmath>
#include <random>
#include <stdexcept>
#include <thread>

namespace subspot {
namespace {

constexpr int kMinutes = 90;

struct Tally {
  std::size_t home_wins = 0;
  std::size_t draws = 0;
  std::size_t away_wins = 0;
  std::uint64_t home_goals = 0;
  std::uint64_t away_goals = 0;
  std::vector<std::size_t> grid;
};

// SplitMix64: turns (seed, thread index) into well-separated RNG seeds.
std::uint64_t split_mix(std::uint64_t x) {
  x += 0x9E3779B97F4A7C15ULL;
  x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL;
  x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL;
  return x ^ (x >> 31);
}

void run_batch(const MatchRates& rates, std::size_t n, std::uint64_t seed, int max_goals,
               Tally& tally) {
  std::mt19937_64 rng(seed);
  std::poisson_distribution<int> home_minute(rates.home_xg / kMinutes);
  std::poisson_distribution<int> away_minute(rates.away_xg / kMinutes);
  const int width = max_goals + 1;
  tally.grid.assign(static_cast<std::size_t>(width * width), 0);

  for (std::size_t i = 0; i < n; ++i) {
    int home = 0;
    int away = 0;
    for (int minute = 0; minute < kMinutes; ++minute) {
      home += home_minute(rng);
      away += away_minute(rng);
    }
    if (home > away) {
      ++tally.home_wins;
    } else if (home == away) {
      ++tally.draws;
    } else {
      ++tally.away_wins;
    }
    tally.home_goals += static_cast<std::uint64_t>(home);
    tally.away_goals += static_cast<std::uint64_t>(away);
    const int h = std::min(home, max_goals);
    const int a = std::min(away, max_goals);
    ++tally.grid[static_cast<std::size_t>(h * width + a)];
  }
}

double poisson_pmf(int k, double lambda) {
  return std::exp(k * std::log(lambda) - lambda - std::lgamma(k + 1.0));
}

void validate(const MatchRates& rates) {
  if (!(rates.home_xg > 0.0) || !(rates.away_xg > 0.0)) {
    throw std::invalid_argument("expected goals must be positive");
  }
}

}  // namespace

SimulationResult simulate_match(const MatchRates& rates, const SimulationConfig& config) {
  validate(rates);
  if (config.num_simulations == 0) {
    throw std::invalid_argument("num_simulations must be positive");
  }
  if (config.max_goals < 1) {
    throw std::invalid_argument("max_goals must be at least 1");
  }

  const std::size_t threads = std::max<std::size_t>(1, config.num_threads);
  std::vector<Tally> tallies(threads);
  std::vector<std::thread> workers;
  workers.reserve(threads);

  const std::size_t base = config.num_simulations / threads;
  const std::size_t remainder = config.num_simulations % threads;
  for (std::size_t t = 0; t < threads; ++t) {
    const std::size_t n = base + (t < remainder ? 1 : 0);
    const std::uint64_t seed = split_mix(config.seed + t);
    workers.emplace_back(run_batch, std::cref(rates), n, seed, config.max_goals,
                         std::ref(tallies[t]));
  }
  for (auto& worker : workers) {
    worker.join();
  }

  const int width = config.max_goals + 1;
  Tally total;
  total.grid.assign(static_cast<std::size_t>(width * width), 0);
  for (const auto& t : tallies) {
    total.home_wins += t.home_wins;
    total.draws += t.draws;
    total.away_wins += t.away_wins;
    total.home_goals += t.home_goals;
    total.away_goals += t.away_goals;
    for (std::size_t i = 0; i < total.grid.size(); ++i) {
      total.grid[i] += t.grid[i];
    }
  }

  const auto n = static_cast<double>(config.num_simulations);
  SimulationResult result;
  result.outcomes = {static_cast<double>(total.home_wins) / n, static_cast<double>(total.draws) / n,
                     static_cast<double>(total.away_wins) / n};
  result.mean_home_goals = static_cast<double>(total.home_goals) / n;
  result.mean_away_goals = static_cast<double>(total.away_goals) / n;
  result.max_goals = config.max_goals;
  result.scoreline_grid.reserve(total.grid.size());
  for (const auto count : total.grid) {
    result.scoreline_grid.push_back(static_cast<double>(count) / n);
  }
  return result;
}

OutcomeProbabilities exact_poisson_outcomes(const MatchRates& rates, int max_goals) {
  validate(rates);
  OutcomeProbabilities p{0.0, 0.0, 0.0};
  for (int h = 0; h <= max_goals; ++h) {
    const double ph = poisson_pmf(h, rates.home_xg);
    for (int a = 0; a <= max_goals; ++a) {
      const double joint = ph * poisson_pmf(a, rates.away_xg);
      if (h > a) {
        p.home_win += joint;
      } else if (h == a) {
        p.draw += joint;
      } else {
        p.away_win += joint;
      }
    }
  }
  return p;
}

}  // namespace subspot
