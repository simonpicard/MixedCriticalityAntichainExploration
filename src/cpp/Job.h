#ifndef JOB_H
#define JOB_H
#include <string>
#include <vector>

#pragma once

class Job {
   public:
    Job() = default;
    explicit Job(Job* other)
        : O(other->O),
          T(other->T),
          D(other->D),
          X(other->X),
          C(other->C),
          rct(other->rct),
          p(other->p){};
    Job(Job const& other) = default;
    ~Job() = default;

    Job(int O_, int T_, int D_, int X_, std::vector<int> const& C_)
        : O(O_), T(T_), D(D_), X(X_), C(std::move(C_)), p(0){};

    Job(int O_, int T_, int D_, int X_, std::vector<int> const& C_, int p_)
        : O(O_), T(T_), D(D_), X(X_), C(std::move(C_)), p(p_){};

    int get_rct() const { return rct; };

    virtual int get_laxity() const = 0;
    virtual int get_worst_laxity(int crit) const = 0;
    virtual float get_worst_utilisation(int current_crit,
                                        int target_crit) const = 0;

    virtual bool is_active() const = 0;
    virtual bool is_implicitely_done(int crit) const = 0;

    bool is_fail(int crit) const { return get_worst_laxity(crit) < 0; };

    virtual std::string str() const = 0;
    virtual std::string dot_node() const = 0;
    virtual void repr() const = 0;

    virtual void execute(bool run, int crit) = 0;
    virtual void terminate(int crit) = 0;
    virtual void critic(int crit, int true_crit) = 0;

    float get_utilisation_at_level(int at_level) const;

    int get_X() const { return X; };
    int get_D() const { return D; };
    int get_T() const { return T; };
    int get_p() const { return p; };

    virtual int get_virtual_deadline(float relativity = 1) const = 0;

    virtual uint64_t get_hash() const = 0;
    virtual uint64_t get_hash_factor() const = 0;

    virtual bool is_single_criticality() const = 0;

    int rct;  // move to protected

   protected:
    virtual void initialize() = 0;
    int O;
    int T;
    int D;
    int X;
    std::vector<int> C;
    int p;  // priority
};

#endif