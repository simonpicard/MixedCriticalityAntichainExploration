#include "GraphPeriodic.h"
#include "util.cpp"

std::vector<State*> GraphPeriodic::get_neighbors(
    std::vector<State*> leaf_states, std::vector<int> (*schedule)(State*)) {
    std::vector<State*> new_states;

    for (State* current_state_uncasted : leaf_states) {
        auto* current_state =
            static_cast<StatePeriodic*>(current_state_uncasted);

        auto* current_state_bkp = new StatePeriodic(*current_state);

        std::vector<int> to_run = schedule(current_state);
        current_state->execute(to_run);

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

        for (std::vector<int> const& current_explicitely_dones :
             all_explicitely_dones) {
            auto* terminate_critic_state = new StatePeriodic(*current_state);

            terminate_critic_state->terminate(current_explicitely_dones);
            terminate_critic_state->critic();
            new_states.push_back(terminate_critic_state);

            if (plot_graph) {
                connect_neighbor_graphviz(current_state_bkp,
                                          terminate_critic_state);
            }
        }

        delete current_state;
        delete current_state_bkp;
    }

    return new_states;
}

State* GraphPeriodic::copy_initial_state() {
    State* ptr = new StatePeriodic(*static_cast<StatePeriodic*>(initial_state));
    return ptr;
}

void GraphPeriodic::connect_neighbor_graphviz(StatePeriodic* from,
                                              StatePeriodic* to) const {
    std::string from_node_id;
    std::string to_node_id;

    from_node_id = from->get_node_id();
    to_node_id = to->get_node_id();

    std::string from_node_desc = from->dot_node(from_node_id);
    std::string to_node_desc = to->dot_node(to_node_id);

    std::stringstream edge_desc;

    edge_desc << from_node_id << " -> " << to_node_id << std::endl;

    append_to_file(graph_output_path, from_node_desc);
    append_to_file(graph_output_path, to_node_desc);
    append_to_file(graph_output_path, edge_desc.str());
};