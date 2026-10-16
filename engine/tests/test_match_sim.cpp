#include <gtest/gtest.h>

#include <numeric>
#include <stdexcept>
#include <string>

#include "subspot/match_sim.hpp"

namespace subspot {
// Lets GoogleTest print MatchRates in failure messages instead of raw bytes.
void PrintTo(const MatchRates& r, std::ostream* os) {
  *os << "{home_xg=" << r.home_xg << ", away_xg=" << r.away_xg << "}";
}
}  // namespace subspot

using subspot::exact_poisson_outcomes;
using subspot::MatchRates;
using subspot::simulate_match;
using subspot::SimulationConfig;

namespace {

SimulationConfig big_run(std::size_t threads = 4) {
  SimulationConfig config;
  config.num_simulations = 200'000;
  config.num_threads = threads;
  config.seed = 7;
  return config;
}

// Readable names for parameterized cases in test output.
std::string case_name(const ::testing::TestParamInfo<subspot::MatchRates>& info) {
  static const char* const kNames[] = {"CloseGame", "HeavyFavourite", "LowScoringDerby"};
  return kNames[info.index];
}

}  // namespace

TEST(ExactPoisson, ProbabilitiesSumToOne) {
  const auto p = exact_poisson_outcomes({1.6, 1.1});
  EXPECT_NEAR(p.home_win + p.draw + p.away_win, 1.0, 1e-9);
}

TEST(ExactPoisson, EqualRatesAreSymmetric) {
  const auto p = exact_poisson_outcomes({1.3, 1.3});
  EXPECT_NEAR(p.home_win, p.away_win, 1e-12);
}

// The core correctness check: with constant rates, the simulator must converge to the
// closed-form Poisson answer. 200k sims gives a standard error under 0.0012.
class ConvergesToPoisson : public ::testing::TestWithParam<MatchRates> {};

TEST_P(ConvergesToPoisson, OutcomesMatchClosedForm) {
  const MatchRates rates = GetParam();
  const auto sim = simulate_match(rates, big_run());
  const auto exact = exact_poisson_outcomes(rates);
  EXPECT_NEAR(sim.outcomes.home_win, exact.home_win, 0.005);
  EXPECT_NEAR(sim.outcomes.draw, exact.draw, 0.005);
  EXPECT_NEAR(sim.outcomes.away_win, exact.away_win, 0.005);
  EXPECT_NEAR(sim.mean_home_goals, rates.home_xg, 0.01);
  EXPECT_NEAR(sim.mean_away_goals, rates.away_xg, 0.01);
}

INSTANTIATE_TEST_SUITE_P(TypicalMatches, ConvergesToPoisson,
                         ::testing::Values(MatchRates{1.5, 1.2},   // close game
                                           MatchRates{2.6, 0.7},   // heavy favourite
                                           MatchRates{0.9, 0.9}),  // low-scoring derby
                         case_name);

TEST(SimulateMatch, ScorelineGridSumsToOne) {
  const auto sim = simulate_match({1.5, 1.2}, big_run());
  const double total = std::accumulate(sim.scoreline_grid.begin(), sim.scoreline_grid.end(), 0.0);
  EXPECT_NEAR(total, 1.0, 1e-9);
}

TEST(SimulateMatch, SameSeedIsDeterministic) {
  const auto a = simulate_match({1.4, 1.0}, big_run());
  const auto b = simulate_match({1.4, 1.0}, big_run());
  EXPECT_DOUBLE_EQ(a.outcomes.home_win, b.outcomes.home_win);
  EXPECT_DOUBLE_EQ(a.outcomes.draw, b.outcomes.draw);
}

TEST(SimulateMatch, ThreadCountDoesNotBiasResults) {
  const auto single = simulate_match({1.4, 1.0}, big_run(1));
  const auto multi = simulate_match({1.4, 1.0}, big_run(8));
  EXPECT_NEAR(single.outcomes.home_win, multi.outcomes.home_win, 0.006);
}

TEST(SimulateMatch, RejectsNonPositiveRates) {
  EXPECT_THROW(simulate_match({0.0, 1.0}, SimulationConfig{}), std::invalid_argument);
  EXPECT_THROW(simulate_match({1.0, -0.5}, SimulationConfig{}), std::invalid_argument);
}
