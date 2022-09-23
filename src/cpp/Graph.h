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

    Graph(State* initial_state_)
        : initial_state(initial_state_),
          graph_output_path(""),
          plot_graph(false){};

    Graph(State* initial_state_, std::string graph_output_path_)
        : initial_state(initial_state_),
          graph_output_path(graph_output_path_),
          plot_graph(true){};

    static bool is_fail(std::vector<State*> const& states);

    virtual std::vector<State*> get_neighbors(
        std::vector<State*> leaf_states,
        std::vector<int> (*schedule)(State*)) = 0;

    int64_t* bfs(std::vector<int> (*schedule)(State*),
                 bool use_pruning = false);

    static void repr(std::vector<State*> states);

    virtual State* copy_initial_state() = 0;

    void graphiz_setup(std::string path);
    void graphiz_teardown(std::string path);

   protected:
    State* initial_state;
    std::string graph_output_path;
    bool plot_graph;
    bool ac_hash = false;
};

#endif