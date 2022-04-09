#include "Graph.h"

Graph::Graph() = default;

Graph::~Graph() { delete initial_state; }

bool Graph::is_fail(std::vector<State*> const& states) {
    for (State* state : states) {
        if (state->is_fail()) return true;
    }
    return false;
}

void Graph::repr(std::vector<State*> states) {
    for (int i = 0; i < states.size(); ++i) {
        std::cout << "S" << i << "-> " << states[i]->str() << std::endl;
    }
    std::cout << std::endl;
}

int64_t* Graph::bfs(std::vector<int> (*schedule)(State*)) {
    int64_t visited_count = 0;
    static int64_t arr[4];

    int step_i = 0;
    std::vector<State*> leaf_states{copy_initial_state()};
    std::vector<State*> neighbors;
    std::unordered_set<int> visited_hash;

    bool res = true;

    visited_hash.insert(leaf_states[0]->get_hash());

    auto start = std::chrono::high_resolution_clock::now();

    while (!leaf_states.empty()) {
        if (is_fail(leaf_states)) {
            res = false;
            break;
        }

        visited_count = visited_count + leaf_states.size();
        // std::cout << step_i << " " << leaf_states.size() << " " <<
        // visited_count
        //           << std::endl;

        neighbors = get_neighbors(leaf_states, schedule);
        step_i++;

        leaf_states.clear();

        for (State* neighbor : neighbors) {
            int state_hash = neighbor->get_hash();
            if (visited_hash.find(state_hash) == visited_hash.end()) {
                visited_hash.insert(state_hash);
                leaf_states.push_back(neighbor);
            } else {
                delete neighbor;
            }
        }
    }
    visited_count = visited_count + leaf_states.size();
    // std::cout << step_i << " " << leaf_states.size() << " " << visited_count
    // << std::endl;

    auto stop = std::chrono::high_resolution_clock::now();
    auto duration =
        std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);

    arr[0] = int64_t(res);
    arr[1] = visited_count;
    arr[2] = duration.count();
    arr[3] = step_i;

    return arr;
}