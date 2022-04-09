#include "GraphSporadic.h"
#include "util.cpp"

std::vector<State*> GraphSporadic::get_neighbors(
    std::vector<State*> leaf_states, std::vector<int> (*schedule)(State*)) {
    std::vector<State*> new_states;

    for (State* current_state_uncasted : leaf_states) {
        auto* current_state =
            static_cast<StateSporadic*>(current_state_uncasted);

        // execution transition
        std::vector<int> to_run = schedule(current_state);
        current_state->execute(to_run);

        // termination and critic transition
        std::vector<int> scheduleds = to_run;
        std::vector<int> implicitely_dones =
            current_state->get_implicitely_dones();
        std::vector<int> explicitely_done_candidates;
        for (int scheduled : scheduleds) {
            if (std::find(implicitely_dones.begin(), implicitely_dones.end(),
                          scheduled) == implicitely_dones.end()) {
                explicitely_done_candidates.push_back(scheduled);
            }
        }
        std::vector<std::vector<int>> all_explicitely_dones =
            power_set(explicitely_done_candidates);

        std::vector<StateSporadic*> terminated_states;
        for (std::vector<int> const& current_explicitely_dones :
             all_explicitely_dones) {
            auto* terminate_critic_state = new StateSporadic(*current_state);
            terminate_critic_state->terminate(current_explicitely_dones);
            terminate_critic_state->critic();
            terminated_states.push_back(terminate_critic_state);
        }

        delete current_state;

        // submit transition
        for (StateSporadic* terminated_state : terminated_states) {
            std::vector<int> eligibles_candidates =
                terminated_state->get_eligibles();
            std::vector<std::vector<int>> all_eligibles =
                power_set(eligibles_candidates);
            for (std::vector<int> const& current_eligibles : all_eligibles) {
                auto* submit_state = new StateSporadic(*terminated_state);
                submit_state->submit(current_eligibles);
                new_states.push_back(submit_state);
            }
            delete terminated_state;
        }
    }

    return new_states;
}

struct VectorHash {
    size_t operator()(const std::vector<int>& v) const {
        std::hash<int> hasher;
        size_t seed = 0;
        for (int i : v) {
            seed ^= hasher(i) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        }
        return seed;
    }
};

State* GraphSporadic::copy_initial_state() {
    State* ptr = new StateSporadic(*static_cast<StateSporadic*>(initial_state));
    return ptr;
}

int64_t* GraphSporadic::acbfs(std::vector<int> (*schedule)(State*)) {
    static int64_t arr[4];
    int64_t visited_count = 0;

    int step_i = 0;
    std::vector<State*> leaf_states{copy_initial_state()};
    std::vector<State*> neighbors;
    std::unordered_map<int, std::unordered_set<std::vector<int>, VectorHash>>
        visited_hash;

    int state_hash =
        static_cast<StateSporadic*>(initial_state)->get_hash_idle();
    std::vector<int> ordered_idle_nats =
        static_cast<StateSporadic*>(initial_state)->get_ordered_idle_nats();
    std::unordered_set<std::vector<int>, VectorHash> new_set;
    new_set.insert(ordered_idle_nats);
    visited_hash[state_hash] = new_set;

    auto start = std::chrono::high_resolution_clock::now();

    bool res = true;

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
            int state_hash =
                static_cast<StateSporadic*>(neighbor)->get_hash_idle();
            std::vector<int> ordered_idle_nats =
                static_cast<StateSporadic*>(neighbor)->get_ordered_idle_nats();

            if (visited_hash.find(state_hash) == visited_hash.end()) {
                std::unordered_set<std::vector<int>, VectorHash> new_set;
                new_set.insert(ordered_idle_nats);
                visited_hash[state_hash] = new_set;
                leaf_states.push_back(neighbor);
            } else {
                std::vector<std::vector<int>> to_pop;
                std::unordered_set<std::vector<int>>::iterator itr;
                bool neighbor_is_simulated = false;
                if (visited_hash[state_hash].find(ordered_idle_nats) ==
                    visited_hash[state_hash].end()) {
                    for (const auto& elem : visited_hash[state_hash]) {
                        if (pairwise_smaller_all(elem, ordered_idle_nats)) {
                            neighbor_is_simulated = true;
                        }
                        if (pairwise_smaller_all(ordered_idle_nats, elem)) {
                            to_pop.push_back(elem);
                        }
                    }
                    for (std::vector<int> const& elem : to_pop) {
                        visited_hash[state_hash].erase(elem);
                    }
                    if (!neighbor_is_simulated) {
                        visited_hash[state_hash].insert(ordered_idle_nats);
                        leaf_states.push_back(neighbor);
                    } else {
                        delete neighbor;
                    }
                } else {
                    delete neighbor;
                }
            }
        }
    }
    visited_count = visited_count + leaf_states.size();
    // std::cout << step_i << " " << leaf_states.size() << " " << visited_count
    // << std::endl;

    auto stop = std::chrono::high_resolution_clock::now();
    auto duration =
        std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);

    if (!res)
        for (auto* elem : leaf_states) delete elem;

    arr[0] = int64_t(res);
    arr[1] = visited_count;
    arr[2] = duration.count();
    arr[3] = step_i;

    return arr;
}

bool GraphSporadic::pairwise_smaller_all(std::vector<int> a,
                                         std::vector<int> b) {
    for (unsigned int i = 0; i < a.size(); i++) {
        if (a[i] > b[i]) return false;
    }
    return true;
}