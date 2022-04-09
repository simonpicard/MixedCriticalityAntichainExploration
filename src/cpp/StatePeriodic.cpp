#include "StatePeriodic.h"
#include <iostream>
#include <sstream>

StatePeriodic::StatePeriodic(const StatePeriodic& other) : State(other) {
    std::vector<Job*> jobs_;
    for (Job* job : other.jobs) {
        Job* clone = new JobPeriodic(static_cast<JobPeriodic*>(job));
        jobs_.push_back(clone);
    }
    jobs = jobs_;
}
