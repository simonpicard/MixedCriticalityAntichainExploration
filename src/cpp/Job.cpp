#include "Job.h"

float Job::get_utilisation_at_level(int at_level) const {
    if (at_level > X) return 0;
    return float(C[at_level - 1]) / float(T);
}