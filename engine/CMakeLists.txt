cmake_minimum_required(VERSION 3.20)
project(subspot_engine VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(SUBSPOT_BUILD_TESTS "Build unit tests" ON)
option(SUBSPOT_BUILD_PYTHON "Build pybind11 module for the ML pipeline" OFF)
option(SUBSPOT_SANITIZE "Build with AddressSanitizer and UBSan" OFF)

find_package(Threads REQUIRED)

add_library(subspot_engine src/match_sim.cpp)
add_library(subspot::engine ALIAS subspot_engine)
target_include_directories(subspot_engine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(subspot_engine PUBLIC Threads::Threads)
set_target_properties(subspot_engine PROPERTIES POSITION_INDEPENDENT_CODE ON)

if(MSVC)
  target_compile_options(subspot_engine PRIVATE /W4 /WX)
else()
  target_compile_options(subspot_engine PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Werror)
endif()

if(SUBSPOT_SANITIZE AND NOT MSVC)
  add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
  add_link_options(-fsanitize=address,undefined)
  target_compile_options(subspot_engine PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
  target_link_options(subspot_engine PUBLIC -fsanitize=address,undefined)
endif()

if(SUBSPOT_BUILD_TESTS)
  include(FetchContent)
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.15.2
    GIT_SHALLOW TRUE)
  set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
  set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(googletest)

  enable_testing()
  add_executable(subspot_tests tests/test_match_sim.cpp)
  target_link_libraries(subspot_tests PRIVATE subspot::engine GTest::gtest_main)
  include(GoogleTest)
  gtest_discover_tests(subspot_tests)
endif()

if(SUBSPOT_BUILD_PYTHON)
  find_package(pybind11 CONFIG REQUIRED)
  pybind11_add_module(subspot_engine_py bindings/python.cpp)
  set_target_properties(subspot_engine_py PROPERTIES OUTPUT_NAME _engine)
  target_link_libraries(subspot_engine_py PRIVATE subspot::engine)
endif()
