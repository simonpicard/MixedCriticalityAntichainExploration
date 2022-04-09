#ifndef GRAPH_H
#define GRAPH_H
#include "Job.h"
#include "State.h"
#include <bits/stdc++.h>
#include <algorithm>
#include <chrono>
#include <iostream>

#pragma once

class Graph {
   public:
    Graph();
    ~Graph();

    explicit Graph(State* initial_state_) : initial_state(initial_state_){};

    static bool is_fail(std::vector<State*> const& states);

    virtual std::vector<State*> get_neighbors(
        std::vector<State*> leaf_states,
        std::vector<int> (*schedule)(State*)) = 0;

    int64_t* bfs(std::vector<int> (*schedule)(State*));

    static void repr(std::vector<State*> states);

    virtual State* copy_initial_state() = 0;

   protected:
    State* initial_state;
};

#endif