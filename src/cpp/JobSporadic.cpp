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

float JobSporadic::get_worst_utilisation(int current_crit,
                                         int target_crit) const {
    if (X < target_crit) {
        return 0;
    } else {
        if (done) {
            return C[target_crit - 1] / (float(D) + nat - 1);
        } else {
            return (float(rct) + C[target_crit - 1] - C[current_crit - 1]) /
                   (nat - T + D);
        }
    }
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

std::string JobSporadic::dot_node() const {
    std::stringstream ss;

    if (!done) ss << "<u>";
    ss << "(" << nat << ", " << rct << ")";
    if (!done) ss << "</u>";
    return ss.str();
}

bool JobSporadic::operator==(const JobSporadic& other) const {
    return (rct == other.rct && nat == other.nat && done == other.done);
}

uint64_t JobSporadic::get_hash() const {
    uint64_t hash = rct;
    uint64_t factor = C[1] + 1;

    hash = hash + (nat + 1) * factor;
    factor = factor * (T + 2);

    if (done) hash = hash + factor;
    factor = factor * 2;

    return hash;
}

uint64_t JobSporadic::get_hash_factor() const {
    uint64_t factor = C[1] + 1;

    factor = factor * (T + 2);

    factor = factor * 2;

    return factor;
}

uint64_t JobSporadic::get_hash_idle() const {
    uint64_t hash = rct;
    uint64_t factor = C[1] + 1;

    if (not done) hash = hash + (nat + 1) * factor;
    factor = factor * (T + 2);

    // T-(D+1)+(C[1]-C[0]) <= nat <= T
    // T-D-1+C[1]-C[0] <= nat <= T
    // C[1]-C[0]-1 <= nat <= T
    // 0 <= nat-(C[1]-C[0]-1) <= T-(C[1]-C[0]-1)
    // 0 <= nat+1-(C[1]-C[0]) <= T+1-(C[1]-C[0])

    if (done) hash = hash + factor;
    factor = factor * 2;

    return hash;
}
