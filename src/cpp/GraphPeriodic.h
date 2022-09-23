#ifndef GRAPHPERIODIC_H
#define GRAPHPERIODIC_H
#include "Graph.h"
#include "StatePeriodic.h"
#include <string>
#include <vector>

#pragma once

class GraphPeriodic : public Graph {
   public:
    explicit GraphPeriodic(State* initial_state_) : Graph(initial_state_){};
    explicit GraphPeriodic(State* initial_state_,
                           std::string graph_output_path_)
        : Graph(initial_state_, graph_output_path_){};

   private:
    std::vector<State*> get_neighbors(
        std::vector<State*> leaf_states,
        std::vector<int> (*schedule)(State*)) override;

    State* copy_initial_state() override;

    void connect_neighbor_graphviz(StatePeriodic* from,
                                   StatePeriodic* to) const;
};

#endif