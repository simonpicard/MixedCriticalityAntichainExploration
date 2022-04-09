#ifndef JOBPERIODIC_H
#define JOBPERIODIC_H
#include "Job.h"
#include <string>
#include <vector>

class JobPeriodic : public Job {
   public:
    JobPeriodic(int O_, int T_, int D_, int X_, std::vector<int> const& C_)
        : Job(O_, T_, D_, X_, C_) {
        initialize();
    };
    JobPeriodic(const JobPeriodic& other);
    explicit JobPeriodic(JobPeriodic* other) : Job(other), at(other->at){};
    ~JobPeriodic() = default;

    int get_at() const { return at; };

    void initialize() override;
    int get_laxity() const override;
    int get_worst_laxity(int crit) const override;

    bool is_discarded() const { return at == 0 and rct == 0; };
    bool is_active() const override { return at < 0 or (at == 0 and rct > 0); };
    bool is_implicitely_done(int crit) const override {
        return rct == 0 and at < 0 and C[crit - 1] == C[X - 1];
    };
    bool is_fail(int crit) const { return get_worst_laxity(crit) < 0; };

    void repr() const override;
    std::string str() const override;

    void execute(bool run, int crit) override;
    void terminate(int crit) override;
    void critic(int crit, int true_crit) override;

    int get_deadline() const override { return get_at() + get_D(); };

    int get_hash() const override;
    int get_hash_factor() const override;

   private:
    void discard();

    int at;
};

#endif