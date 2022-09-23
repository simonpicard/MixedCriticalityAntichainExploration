#ifndef STATESPORADIC_H
#define STATESPORADIC_H
#include "Job.h"
#include "JobSporadic.h"
#include "State.h"
#include <algorithm>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#pragma once

class StateSporadic : public State {
   public:
    StateSporadic() = default;
    explicit StateSporadic(std::vector<Job*> const& jobs_) : State(jobs_){};
    StateSporadic(const StateSporadic& other);

    void submit(std::vector<int> const& requestings);
    void step();

    std::vector<int> get_eligibles();

    uint64_t get_hash_idle() const;
    std::vector<int> get_ordered_idle_nats() const;

    std::string get_node_id_idle() const;
};

#endif