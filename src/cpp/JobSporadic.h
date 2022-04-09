#ifndef JOBSPORADIC_H
#define JOBSPORADIC_H
#include "Job.h"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#pragma once

class JobSporadic : public Job {
   public:
    JobSporadic(int O_, int T_, int D_, int X_, std::vector<int> const& C_)
        : Job(O_, T_, D_, X_, C_) {
        initialize();
    };
    JobSporadic(const JobSporadic& other);
    explicit JobSporadic(JobSporadic* other)
        : Job(other), nat(other->nat), done(other->done){};
    ~JobSporadic() = default;

    int get_nat() const { return nat; };
    int get_rct() const { return rct; };
    bool get_done() const { return done; };

    void initialize() override;
    int get_laxity() const override;
    int get_worst_laxity(int crit) const override;

    bool is_discarded(int crit) const { return X < crit; };
    bool is_active() const override { return not done; };
    bool is_implicitely_done(int crit) const override {
        return rct == 0 and is_active() and C[crit - 1] == C[X - 1];
    };
    bool is_fail(int crit) const { return get_worst_laxity(crit) < 0; };
    bool is_idle(int crit) const {
        return is_active() and not is_discarded(crit);
    }
    bool is_eligible(int crit) {
        return rct == 0 and nat <= 0 and done and X >= crit;
    };

    std::vector<int> get_possible_ats() const;

    void repr() const override;
    std::string str() const override;

    void execute(bool run, int crit) override;
    void terminate(int crit) override;
    void critic(int crit, int true_crit) override;
    void submit(int true_at, int crit);

    bool operator==(const JobSporadic& other) const;
    int get_hash() const override;
    int get_hash_factor() const override;
    int get_hash_idle() const;

    int get_deadline() const override { return get_nat() + get_D(); };

   private:
    int nat;
    bool done;
};

#endif