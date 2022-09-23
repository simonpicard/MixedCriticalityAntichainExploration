#include "Scheduler.h"

std::vector<int> Scheduler::dummy_scheduler(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();
    if (!actives.empty()) {
        to_run.push_back(actives[0]);
    }
    return to_run;
}

std::vector<int> Scheduler::mwuf(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();

    if (actives.empty()) {
        return to_run;
    }

    int current_crit = state->get_crit();

    bool active_lo = false;
    bool active_hi = false;

    for (int i : actives) {
        if (state->get_job(i)->get_X() == 1) active_lo = true;
        if (state->get_job(i)->get_X() == 2) active_hi = true;
    }

    float u1 = 0;
    float u2 = 0;
    for (int i = 0; i < state->get_size(); i++) {
        u1 = u1 + state->get_job(i)->get_worst_utilisation(current_crit, 1);
        u2 = u2 + state->get_job(i)->get_worst_utilisation(current_crit, 2);
    }

    int crit_to_sched;
    if (active_lo and !active_hi)
        crit_to_sched = 1;
    else if (!active_lo and active_hi)
        crit_to_sched = 2;
    else if (active_lo and active_hi) {
        if (u1 <= u2)
            crit_to_sched = 2;
        else
            crit_to_sched = 1;
    }

    bool first_set = false;
    float max_u, u;
    int j_id;
    for (int i : actives) {
        if (state->get_job(i)->get_X() >= crit_to_sched) {
            u = state->get_job(i)->get_worst_utilisation(current_crit,
                                                         crit_to_sched);
            if (!first_set) {
                first_set = true;
                max_u = u;
                j_id = i;
            } else if (u > max_u) {
                max_u = u;
                j_id = i;
            }
        }
    }

    // bool first_set = false;
    // int min_wl, wl;
    // int j_id;
    // for (int i : actives) {
    //     if (state->get_job(i)->get_X() >= crit_to_sched) {
    //         wl = state->get_job(i)->get_worst_laxity(current_crit);
    //         if (!first_set) {
    //             first_set = true;
    //             min_wl = wl;
    //             j_id = i;
    //         } else if (wl < min_wl) {
    //             min_wl = wl;
    //             j_id = i;
    //         }
    //     }
    // }

    if (!actives.empty()) {
        to_run.push_back(j_id);
    }
    return to_run;
}

// std::vector<int> Scheduler::mwuf(State* state) {
//     std::vector<int> to_run;
//     std::vector<int> actives = state->get_actives();

//     int current_crit = state->get_crit();

//     float u1, u2 = 0;
//     for (int i : actives) {
//         u1 = u1 + state->get_job(i)->get_worst_utilisation(current_crit, 1);
//         u2 = u2 + state->get_job(i)->get_worst_utilisation(current_crit, 2);
//     }

//     int crit_to_sched;
//     if (u1 > u2)
//         crit_to_sched = 1;
//     else
//         crit_to_sched = 2;

//     // bool first_set = false;
//     // float max_u, u;
//     // int j_id;
//     // for (int i : actives) {
//     //     if (state->get_job(i)->get_X() == crit_to_sched) {
//     //         u = state->get_job(i)->get_worst_utilisation(current_crit,
//     //                                                      crit_to_sched);
//     //         if (!first_set) {
//     //             first_set = true;
//     //             max_u = u;
//     //             j_id = i;
//     //         } else if (u > max_u) {
//     //             max_u = u;
//     //             j_id = i;
//     //         }
//     //     }
//     // }

//     bool first_set = false;
//     int min_wl, wl;
//     int j_id;
//     for (int i : actives) {
//         if (state->get_job(i)->get_X() >= crit_to_sched) {
//             wl = state->get_job(i)->get_worst_laxity(current_crit);
//             if (!first_set) {
//                 first_set = true;
//                 min_wl = wl;
//                 j_id = i;
//             } else if (wl < min_wl) {
//                 min_wl = wl;
//                 j_id = i;
//             }
//         }
//     }

//     if (!actives.empty()) {
//         to_run.push_back(j_id);
//     }
//     return to_run;
// }

std::vector<int> Scheduler::lwlf(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();

    bool first_set = false;
    int max_x, x;
    int min_wl, wl;
    int min_dl, dl;
    int j_id;
    for (int i : actives) {
        wl = state->get_job(i)->get_worst_laxity(state->get_crit());
        x = state->get_job(i)->get_X();
        dl = state->get_job(i)->get_virtual_deadline();
        if (!first_set) {
            first_set = true;
            min_wl = wl;
            j_id = i;
            max_x = x;
            min_dl = dl;
        } else if (wl < min_wl) {
            min_wl = wl;
            j_id = i;
            max_x = x;
            min_dl = dl;
        }
        // else if (wl == min_wl and x < max_x) {
        //     min_wl = wl;
        //     j_id = i;
        //     max_x = x;
        // } else if (wl == min_wl and x == max_x and dl < min_dl) {
        //     min_wl = wl;
        //     j_id = i;
        //     max_x = x;
        //     min_dl = dl;
        // }
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

    bool first_set = false;
    float min_dl;
    float dl;
    int j_id;
    for (int i : actives) {
        if (state->get_job(i)->get_X() == 2) {
            dl = state->get_job(i)->get_virtual_deadline(relativity);
        } else {
            dl = state->get_job(i)->get_virtual_deadline();
        }
        if (!first_set or dl < min_dl) {
            min_dl = dl;
            j_id = i;
            first_set = true;
        }
    }
    if (!actives.empty()) {
        to_run.push_back(j_id);
    }
    return to_run;
}

std::vector<int> Scheduler::fp(State* state) {
    std::vector<int> to_run;
    std::vector<int> actives = state->get_actives();

    bool first_set = false;
    int min_p, p;
    int j_id;
    for (int i : actives) {
        p = state->get_job(i)->get_p();
        if (!first_set) {
            first_set = true;
            min_p = p;
            j_id = i;
        } else if (p < min_p) {
            min_p = p;
            j_id = i;
        }
    }
    if (!actives.empty()) {
        to_run.push_back(j_id);
    }
    return to_run;
}