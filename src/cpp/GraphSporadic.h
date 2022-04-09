#ifndef GRAPHSPORADIC_H
#define GRAPHSPORADIC_H
#include "Graph.h"
#include "JobSporadic.h"
#include "Scheduler.h"
#include "StateSporadic.h"
#include <bits/stdc++.h>
#include <chrono>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

#pragma once

class GraphSporadic : public Graph {
   public:
    explicit GraphSporadic(State* initial_state_) : Graph(initial_state_){};

    std::vector<State*> get_neighbors(
        std::vector<State*> leaf_states,
        std::vector<int> (*schedule)(State*)) override;

    int64_t* acbfs(std::vector<int> (*schedule)(State*));

    bool pairwise_smaller_all(std::vector<int> a, std::vector<int> b);

    State* copy_initial_state() override;
};

#endif