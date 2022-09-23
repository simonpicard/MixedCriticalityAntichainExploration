#include "GraphSporadic.h"
#include "util.cpp"
#include <fstream>  //deleteme

std::vector<State*> GraphSporadic::get_neighbors(
    std::vector<State*> leaf_states, std::vector<int> (*schedule)(State*)) {
    std::vector<State*> new_states;

    for (State* current_state_uncasted : leaf_states) {
        auto* current_state =
            static_cast<StateSporadic*>(current_state_uncasted);

        auto* current_state_bkp = new StateSporadic(*current_state);

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

                if (plot_graph) {
                    connect_neighbor_graphviz(current_state_bkp, submit_state);
                }
            }
            delete terminated_state;
        }

        delete current_state;
        delete current_state_bkp;
    }

    return new_states;
}

std::vector<State*> GraphSporadic::get_neighbors_graphviz(
    std::vector<State*> leaf_states, std::vector<int> (*schedule)(State*),
    int depth) {
    std::vector<State*> new_states;

    std::ofstream o_file;  // deleteme
    o_file.open("test_graph.txt",
                std::ios::in | std::ios::out | std::ios::ate);  // deleteme

    for (State* current_state_uncasted : leaf_states) {
        auto* current_state =
            static_cast<StateSporadic*>(current_state_uncasted);

        std::string from_state_node =
            current_state->dot_node("bla");                    // deleteme
        uint64_t from_state_hash = current_state->get_hash();  // deleteme

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

                o_file << from_state_node;                // deleteme
                o_file << submit_state->dot_node("bla");  // deleteme

                o_file << from_state_hash << " -> "  // deleteme
                       << submit_state->get_hash()   // deleteme
                       << std::endl;                 // deleteme
            }
            delete terminated_state;
        }

        delete current_state;
    }

    o_file.close();

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

int64_t* GraphSporadic::acbfs(std::vector<int> (*schedule)(State*),
                              bool use_pruning) {
    static int64_t arr[4];
    int64_t visited_count = 0;

    this->ac_hash = true;

    if (plot_graph) {
        graphiz_setup(graph_output_path);
    }

    int step_i = 0;
    std::vector<State*> leaf_states{copy_initial_state()};
    std::vector<State*> neighbors;
    std::unordered_map<uint64_t,
                       std::unordered_set<std::vector<int>, VectorHash>>
        visited_hash;

    uint64_t state_hash =
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
            if (use_pruning && neighbor->is_safe()) {
                delete neighbor;
                continue;
            }
            uint64_t state_hash =
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

                            if (plot_graph) {
                                std::stringstream simulator_hash;
                                simulator_hash << "n_";
                                simulator_hash << state_hash;
                                for (int nat : elem) {
                                    simulator_hash << "_" << nat;
                                }

                                std::stringstream ss;
                                ss << static_cast<StateSporadic*>(neighbor)
                                          ->get_node_id_idle()
                                   << " -> " << simulator_hash.str()
                                   << " [style=\"dashed\"] //neighbor is "
                                      "simulated "
                                   << std::endl;
                                append_to_file(graph_output_path, ss.str());
                            }
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

    if (plot_graph) graphiz_teardown(graph_output_path);

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

int64_t* GraphSporadic::acbfs_graphviz(std::vector<int> (*schedule)(State*)) {
    static int64_t arr[4];
    int64_t visited_count = 0;

    std::string path = "test_graph.txt";  // deleteme

    std::ofstream o_file;  // deleteme
    o_file.open(path);     // deleteme
    o_file << "digraph G "
              "{\n"
              "node[shape=\"box\",style=\"rounded,filled\"]"
              "\n";
    o_file.close();  // deleteme

    int step_i = 0;
    std::vector<State*> leaf_states{copy_initial_state()};
    std::vector<State*> neighbors;
    std::unordered_map<uint64_t,
                       std::unordered_set<std::vector<int>, VectorHash>>
        visited_hash;
    std::unordered_map<
        uint64_t, std::unordered_map<std::vector<int>, uint64_t, VectorHash>>
        visited_dot_node;  // delete me

    uint64_t state_hash =
        static_cast<StateSporadic*>(initial_state)->get_hash_idle();
    std::vector<int> ordered_idle_nats =
        static_cast<StateSporadic*>(initial_state)->get_ordered_idle_nats();
    std::unordered_set<std::vector<int>, VectorHash> new_set;
    new_set.insert(ordered_idle_nats);
    visited_hash[state_hash] = new_set;

    std::unordered_map<std::vector<int>, uint64_t, VectorHash>
        new_umap;                                             // delete me
    new_umap[ordered_idle_nats] = initial_state->get_hash();  // delete me
    visited_dot_node[state_hash] = new_umap;                  // delete me

    auto start = std::chrono::high_resolution_clock::now();

    bool res = true;

    while (!leaf_states.empty()) {
        if (is_fail(leaf_states)) {
            res = false;
            break;
        }

        visited_count = visited_count + leaf_states.size();
        neighbors = get_neighbors_graphviz(leaf_states, schedule, step_i);
        step_i++;

        leaf_states.clear();

        for (State* neighbor : neighbors) {
            uint64_t state_hash =
                static_cast<StateSporadic*>(neighbor)->get_hash_idle();
            std::vector<int> ordered_idle_nats =
                static_cast<StateSporadic*>(neighbor)->get_ordered_idle_nats();

            if (visited_hash.find(state_hash) == visited_hash.end()) {
                std::unordered_set<std::vector<int>, VectorHash> new_set;
                new_set.insert(ordered_idle_nats);
                visited_hash[state_hash] = new_set;
                leaf_states.push_back(neighbor);

                std::unordered_map<std::vector<int>, uint64_t, VectorHash>
                    new_umap;  // delete me
                new_umap[ordered_idle_nats] =
                    neighbor->get_hash();                 // delete me
                visited_dot_node[state_hash] = new_umap;  // delete me

            } else {
                std::vector<std::vector<int>> to_pop;
                std::unordered_set<std::vector<int>>::iterator itr;
                bool neighbor_is_simulated = false;
                if (visited_hash[state_hash].find(ordered_idle_nats) ==
                    visited_hash[state_hash].end()) {
                    for (const auto& elem : visited_hash[state_hash]) {
                        if (pairwise_smaller_all(elem, ordered_idle_nats)) {
                            neighbor_is_simulated = true;

                            uint64_t simulator_hash =
                                visited_dot_node[state_hash]
                                                [elem];  // Delete me

                            std::stringstream ss;
                            ss << neighbor->get_hash() << " -> "
                               << simulator_hash
                               << " [style=\"dashed\"] //neighbor is simulated "
                               << std::endl;
                            append_to_file(path, ss.str());
                        }
                        if (pairwise_smaller_all(ordered_idle_nats, elem)) {
                            to_pop.push_back(elem);

                            uint64_t simulated_hash =
                                visited_dot_node[state_hash]
                                                [elem];  // Delete me

                            // std::stringstream ss;
                            // ss << simulated_hash << " -> "
                            //    << neighbor->get_hash()
                            //    << " [style=\"dashed\"] //neighbor simulates"
                            //    << std::endl;
                            // append_to_file(path, ss.str());
                        }
                    }
                    for (std::vector<int> const& elem : to_pop) {
                        visited_hash[state_hash].erase(elem);
                    }
                    if (!neighbor_is_simulated) {
                        visited_hash[state_hash].insert(ordered_idle_nats);
                        leaf_states.push_back(neighbor);

                        visited_dot_node[state_hash][ordered_idle_nats] =
                            neighbor->get_hash();  // Delete me

                    } else {
                        delete neighbor;
                    }
                } else {
                    delete neighbor;
                }
            }
        }
    }

    append_to_file(path, "\n}");

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
    if (a.size() != b.size()) {
        std::cout << "a" << std::endl;
        for (int i : a) {
            std::cout << i << std::endl;
        }
        std::cout << "b" << std::endl;
        for (int i : b) {
            std::cout << i << std::endl;
        }
    }
    for (unsigned int i = 0; i < a.size(); i++) {
        if (a[i] > b[i]) return false;
    }
    return true;
}

void GraphSporadic::connect_neighbor_graphviz(StateSporadic* from,
                                              StateSporadic* to) const {
    std::string from_node_id;
    std::string to_node_id;

    if (ac_hash) {
        from_node_id = from->get_node_id_idle();
        to_node_id = to->get_node_id_idle();
    } else {
        from_node_id = from->get_node_id();
        to_node_id = to->get_node_id();
    }

    std::string from_node_desc = from->dot_node(from_node_id);
    std::string to_node_desc = to->dot_node(to_node_id);

    std::stringstream edge_desc;

    edge_desc << from_node_id << " -> " << to_node_id << std::endl;

    append_to_file(graph_output_path, from_node_desc);
    append_to_file(graph_output_path, to_node_desc);
    append_to_file(graph_output_path, edge_desc.str());
};
