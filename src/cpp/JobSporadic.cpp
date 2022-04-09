#include "JobSporadic.h"

JobSporadic::JobSporadic(const JobSporadic& other) : Job(other) {
    nat = other.nat;
    rct = other.rct;
    done = other.done;
}

void JobSporadic::initialize() {
    nat = O;
    rct = 0;
    done = true;
}

int JobSporadic::get_laxity() const { return nat - T + D - rct; }

int JobSporadic::get_worst_laxity(int crit) const {
    if (done) {
        return 0;
    }
    return nat - T + D - (rct + C[X - 1] - C[crit - 1]);
}

void JobSporadic::execute(bool run, int crit) {
    if (run) {
        rct--;
    }
    if (is_active()) {
        nat--;
    } else {
        nat = std::max(nat - 1, 0);
    }
}

void JobSporadic::terminate(int crit) {
    rct = 0;
    done = true;
}

void JobSporadic::critic(int crit, int true_crit) {
    if (X >= true_crit) {
        if (is_active()) {
            rct = rct + C[true_crit - 1] - C[crit - 1];
        }
    } else {
        rct = 0;
        nat = 0;
        done = true;
    }
}

std::vector<int> JobSporadic::get_possible_ats() const {
    std::vector<int> possible_ats;
    for (int i = nat; i <= 0; ++i) {
        possible_ats.push_back(i);
    }
    return possible_ats;
}

void JobSporadic::submit(int true_at, int crit) {
    rct = C[crit - 1];
    done = false;
    nat = true_at + T;
}

void JobSporadic::repr() const { std::cout << str() << std::endl; }

std::string JobSporadic::str() const {
    std::string done_str = (done) ? "I" : "A";
    std::stringstream ss;
    ss << "(" << nat << ", " << rct << ", " << done_str << ")";
    return ss.str();
}

bool JobSporadic::operator==(const JobSporadic& other) const {
    return (rct == other.rct && nat == other.nat && done == other.done);
}

int JobSporadic::get_hash() const {
    int hash = rct;
    int factor = C[1] + 1;

    hash = hash + (nat + 1) * factor;
    factor = factor * (T + 2);

    if (done) hash = hash + factor;
    factor = factor * 2;

    return hash;
}

int JobSporadic::get_hash_factor() const {
    int factor = C[1] + 1;

    factor = factor * (T + 2);

    factor = factor * 2;

    return factor;
}

int JobSporadic::get_hash_idle() const {
    int hash = rct;
    int factor = C[1] + 1;

    if (not done) hash = hash + (nat + 1) * factor;
    factor = factor * (T + 2);

    if (done) hash = hash + factor;
    factor = factor * 2;

    return hash;
}
