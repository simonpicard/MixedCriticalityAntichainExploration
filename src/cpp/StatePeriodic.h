#ifndef STATEPERIODIC_H
#define STATEPERIODIC_H
#include "JobPeriodic.h"
#include "State.h"
#include <algorithm>
#include <string>
#include <vector>

#pragma once

class StatePeriodic : public State {
   public:
    explicit StatePeriodic(std::vector<Job*> const& jobs_) : State(jobs_){};
    StatePeriodic(const StatePeriodic& other);
};

#endif