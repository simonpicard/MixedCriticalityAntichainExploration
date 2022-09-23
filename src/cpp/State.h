#ifndef STATE_H
#define STATE_H
#include "Job.h"
#include <algorithm>
#include <memory>
#include <string>
#include <vector>

#pragma once

class State {
   public:
    State() = default;
    ~State();

    State(const State& other) : crit(other.crit){};

    explicit State(std::vector<Job*> const& jobs_)
        : jobs(std::move(jobs_)), crit(1){};

    std::vector<int> get_actives() const;
    std::vector<int> get_implicitely_dones() const;

    bool is_fail() const;

    void repr() const;
    std::string str() const;
    std::string dot_node(std::string node_id) const;
    std::string get_node_id() const { return std::to_string(get_hash()); };

    virtual void execute(std::vector<int> to_run);
    virtual void terminate(std::vector<int> explicitely_dones);
    virtual void critic();

    uint64_t get_hash() const;

    virtual int get_true_crit();

    int get_crit() const { return crit; };
    void set_crit(int crit_) { crit = crit_; };

    Job* get_job(int i) { return jobs[i]; };

    float get_utilisation_of_level_at_level(int of_level, int at_level) const;
    float get_utilisation_of_level(int of_level) const;

    int get_size() const { return jobs.size(); };

    float get_current_utilisation() const;

    bool is_single_criticality() const;
    bool is_able_to_increase_crit() const;
    bool is_safe() const { return !is_able_to_increase_crit(); };

   protected:
    std::vector<Job*> jobs;
    int crit;
};

#endif