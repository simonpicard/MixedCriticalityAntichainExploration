#include "State.h"
#include <iostream>
#include <sstream>

State::~State() {
    for (Job* p : jobs) {
        delete p;
    }
    jobs.clear();
}

std::vector<int> State::get_actives() const {
    std::vector<int> vect;
    for (int i = 0; i < jobs.size(); ++i) {
        if (jobs[i]->is_active()) {
            vect.push_back(i);
        }
    }
    return vect;
}

std::vector<int> State::get_implicitely_dones() const {
    std::vector<int> vect;
    for (int i = 0; i < jobs.size(); ++i) {
        if (jobs[i]->is_implicitely_done(crit)) {
            vect.push_back(i);
        }
    }
    return vect;
}

bool State::is_fail() const {
    for (Job* job : jobs) {
        if (job->is_fail(crit)) return true;
    }
    return false;
}

void State::repr() const { std::cout << str() << std::endl; }

std::string State::str() const {
    std::stringstream ss;
    ss << crit;
    for (Job* job : jobs) {
        ss << " ";
        ss << job->str();
    }
    return ss.str();
}

float State::get_utilisation_of_level_at_level(int of_level,
                                               int at_level) const {
    float res = 0;
    for (Job* job : jobs) {
        if (job->get_X() == of_level)
            res = res + job->get_utilisation_at_level(at_level);
    }
    return res;
}

int State::get_hash() const {
    int hash = crit - 1;
    int factor = 2;

    for (Job* job : jobs) {
        hash = hash + job->get_hash() * factor;
        factor = factor * job->get_hash_factor();
    }

    return hash;
}

void State::execute(std::vector<int> to_run) {
    for (int i = 0; i < jobs.size(); ++i) {
        if (std::find(to_run.begin(), to_run.end(), i) != to_run.end()) {
            jobs[i]->execute(true, crit);
        } else {
            jobs[i]->execute(false, crit);
        }
    }
}

void State::terminate(std::vector<int> explicitely_dones) {
    std::vector<int> implicitely_dones = get_implicitely_dones();
    for (int i = 0; i < jobs.size(); ++i) {
        if (std::find(implicitely_dones.begin(), implicitely_dones.end(), i) !=
                implicitely_dones.end() or
            std::find(explicitely_dones.begin(), explicitely_dones.end(), i) !=
                explicitely_dones.end()) {
            jobs[i]->terminate(crit);
        }
    }
}

int State::get_true_crit() {
    std::vector<int> actives = get_actives();
    for (int i : actives) {
        if (jobs[i]->get_rct() == 0) {
            return crit + 1;
        }
    }
    return crit;
}

void State::critic() {
    int true_crit = get_true_crit();
    for (Job* job : jobs) {
        job->critic(crit, true_crit);
    }
    crit = true_crit;
}