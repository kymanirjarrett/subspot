// Python bindings so backtests in ml/ run the exact same simulator the iOS app ships.
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "subspot/match_sim.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_engine, m) {
  m.doc() = "Subspot C++ match simulation engine";

  py::class_<subspot::OutcomeProbabilities>(m, "OutcomeProbabilities")
      .def_readonly("home_win", &subspot::OutcomeProbabilities::home_win)
      .def_readonly("draw", &subspot::OutcomeProbabilities::draw)
      .def_readonly("away_win", &subspot::OutcomeProbabilities::away_win);

  py::class_<subspot::SimulationResult>(m, "SimulationResult")
      .def_readonly("outcomes", &subspot::SimulationResult::outcomes)
      .def_readonly("mean_home_goals", &subspot::SimulationResult::mean_home_goals)
      .def_readonly("mean_away_goals", &subspot::SimulationResult::mean_away_goals)
      .def_readonly("scoreline_grid", &subspot::SimulationResult::scoreline_grid)
      .def_readonly("max_goals", &subspot::SimulationResult::max_goals);

  m.def(
      "simulate_match",
      [](double home_xg, double away_xg, std::size_t num_simulations, std::size_t num_threads,
         std::uint64_t seed, int max_goals) {
        subspot::SimulationConfig config{num_simulations, num_threads, seed, max_goals};
        py::gil_scoped_release release;
        return subspot::simulate_match({home_xg, away_xg}, config);
      },
      py::arg("home_xg"), py::arg("away_xg"), py::arg("num_simulations") = 10'000,
      py::arg("num_threads") = 1, py::arg("seed") = 42, py::arg("max_goals") = 10);

  m.def(
      "exact_poisson_outcomes",
      [](double home_xg, double away_xg) {
        return subspot::exact_poisson_outcomes({home_xg, away_xg});
      },
      py::arg("home_xg"), py::arg("away_xg"));
}
