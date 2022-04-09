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

int StateSporadic::get_hash_idle() const {
    int hash = crit - 1;
    int factor = 2;

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