#include "StateSporadic.h"

StateSporadic::StateSporadic(const StateSporadic& other) : State(other) {
    std::vector<Job*> jobs_;
    for (int i = 0; i < other.jobs.size(); ++i) {
        Job* clone = new JobSporadic(static_cast<JobSporadic*>(other.jobs[i]));
        jobs_.push_back(clone);
    }
    jobs = jobs_;
}

void StateSporadic::submit(std::vector<int> const& requestings) {
    for (int i : requestings) {
        std::vector<int> possible_ats =
            static_cast<JobSporadic*>(jobs[i])->get_possible_ats();
        for (int j : possible_ats) {
            static_cast<JobSporadic*>(jobs[i])->submit(j, crit);
        }
    }
}

std::vector<int> StateSporadic::get_eligibles() {
    std::vector<int> vect;
    for (int i = 0; i < jobs.size(); ++i) {
        if (static_cast<JobSporadic*>(jobs[i])->is_eligible(crit)) {
            vect.push_back(i);
        }
    }
    return vect;
}

uint64_t StateSporadic::get_hash_idle() const {
    uint64_t hash = crit - 1;
    uint64_t factor = 2;

    for (Job* job : jobs) {
        hash = hash + static_cast<JobSporadic*>(job)->get_hash_idle() * factor;
        factor = factor * static_cast<JobSporadic*>(job)->get_hash_factor();
    }

    return hash;
}

std::vector<int> StateSporadic::get_ordered_idle_nats() const {
    std::vector<int> nats;

    for (Job* job : jobs) {
        if (static_cast<JobSporadic*>(job)->get_done())
            nats.push_back(static_cast<JobSporadic*>(job)->get_nat());
    }

    return nats;
}

std::string StateSporadic::get_node_id_idle() const {
    std::stringstream ss;
    ss << "n_" << this->get_hash_idle();
    for (int nat : this->get_ordered_idle_nats()) {
        ss << "_" << nat;
    }
    return ss.str();
}