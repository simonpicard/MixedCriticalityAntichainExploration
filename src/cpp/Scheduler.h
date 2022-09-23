#ifndef SCHEDULER_H
#define SCHEDULER_H
#include "State.h"
#include "StatePeriodic.h"
#include "StateSporadic.h"
#include <iostream>
#include <vector>

#pragma once

class Scheduler {
   public:
    static std::vector<int> dummy_scheduler(State* state);
    static std::vector<int> mwuf(State* state);
    static std::vector<int> lwlf(State* state);
    static std::vector<int> edfvd(State* state);
    static std::vector<int> fp(State* state);

   private:
};

#endif