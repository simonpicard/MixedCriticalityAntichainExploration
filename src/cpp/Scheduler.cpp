#include "Scheduler.h"

std::vector<int> Scheduler::dummy_scheduler(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();
    if (!actives.empty()) {
        to_run.push_back(actives[0]);
    }
    return to_run;
}

std::vector<int> Scheduler::lwlf(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();
    int min_wl = 1316134911;
    int wl;
    int j_id;
    for (int i : actives) {
        wl = state->get_job(i)->get_worst_laxity(state->get_crit());
        if (wl < min_wl) {
            min_wl = wl;
            j_id = i;
        }
    }
    if (!actives.empty()) {
        to_run.push_back(j_id);
    }
    return to_run;
}

std::vector<int> Scheduler::edfvd(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();

    float relativity = 1;

    int simple_crit_test = state->get_utilisation_of_level_at_level(1, 1);
    simple_crit_test =
        simple_crit_test + state->get_utilisation_of_level_at_level(2, 2);

    if (simple_crit_test > 1) {
        relativity = state->get_utilisation_of_level_at_level(2, 1);
        relativity =
            relativity / (1 - state->get_utilisation_of_level_at_level(1, 1));
    }

    float min_dl = 1316134911;
    float dl;
    int j_id;
    for (int i : actives) {
        dl = state->get_job(i)->get_deadline();

        if (state->get_job(i)->get_X() == 2) {
            dl = dl * relativity;
        }
        if (dl < min_dl) {
            min_dl = dl;
            j_id = i;
        }
    }
    if (!actives.empty()) {
        to_run.push_back(j_id);
    }
    return to_run;
}