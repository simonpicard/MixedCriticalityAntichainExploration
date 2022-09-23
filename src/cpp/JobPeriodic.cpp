#include "JobPeriodic.h"
#include <iostream>
#include <sstream>

JobPeriodic::JobPeriodic(const JobPeriodic& other) : Job(other) {
    at = other.at;
    rct = other.rct;
}

void JobPeriodic::discard() {
    at = 0;
    rct = 0;
}

void JobPeriodic::initialize() {
    at = O;
    rct = C[0];
}

void JobPeriodic::execute(bool run, int crit) {
    if (run) {
        rct--;
    }
    if (X < crit) {
        at = 0;
    } else {
        at--;
    }
}

void JobPeriodic::terminate(int crit) {
    rct = C[crit - 1];
    at = at + T;
}

void JobPeriodic::critic(int crit, int true_crit) {
    if (X >= true_crit) {
        rct = rct + C[true_crit - 1] - C[crit - 1];
    } else {
        discard();
    }
}

void JobPeriodic::repr() const { std::cout << str() << std::endl; }

std::string JobPeriodic::str() const {
    std::stringstream ss;
    ss << "(" << at << ", " << rct << ")";
    return ss.str();
}

std::string JobPeriodic::dot_node() const {
    std::stringstream ss;
    ss << "(" << at << ", " << rct << ")";
    return ss.str();
}

int JobPeriodic::get_laxity() const { return at + D - rct; }

int JobPeriodic::get_worst_laxity(int crit) const {
    return at + D - (rct + C[X - 1] - C[crit - 1]);
}

float JobPeriodic::get_worst_utilisation(int current_crit,
                                         int target_crit) const {
    return (rct + C[X - 1] - C[current_crit - 1]) / (D + at);  // TODO
}

uint64_t JobPeriodic::get_hash() const {
    uint64_t hash = rct;
    uint64_t factor = C[1] + 1;

    hash = hash + (at + 1) * factor;
    factor = factor * (T + 2);

    return hash;
}

uint64_t JobPeriodic::get_hash_factor() const {
    uint64_t factor = C[1] + 1;

    factor = factor * (T + 2);

    return factor;
}