#include "GraphPeriodic.h"
#include "GraphSporadic.h"
#include "Job.h"
#include "JobPeriodic.h"
#include "JobSporadic.h"
#include "Scheduler.h"
#include "StatePeriodic.h"
#include "StateSporadic.h"
#include <fstream>
#include <iostream>
#include <vector>

void experiment_sched(std::vector<Job*> jobs_sporadic) {
    int64_t* res;

    State* ss = new StateSporadic(jobs_sporadic);
    GraphSporadic gs(ss);

    res = gs.acbfs(&Scheduler::lwlf);
    std::cout << "SPO AC LW " << res[0] << " " << res[1] << " " << res[2] << " "
              << res[3] << std::endl;

    res = gs.acbfs(&Scheduler::edfvd);
    std::cout << "SPO AC ED " << res[0] << " " << res[1] << " " << res[2] << " "
              << res[3] << std::endl;
}

void experiment(std::vector<Job*> jobs_sporadic,
                std::vector<Job*> jobs_periodic) {
    int64_t* res;

    State* ss = new StateSporadic(jobs_sporadic);
    GraphSporadic gs(ss);

    State* sp = new StatePeriodic(jobs_periodic);
    GraphPeriodic gp(sp);

    res = gp.bfs(&Scheduler::lwlf);
    std::cout << "PER BF LW " << res[0] << " " << res[1] << " " << res[2] << " "
              << res[3] << std::endl;

    res = gs.acbfs(&Scheduler::lwlf);
    std::cout << "SPO AC LW " << res[0] << " " << res[1] << " " << res[2] << " "
              << res[3] << std::endl;

    res = gs.bfs(&Scheduler::lwlf);
    std::cout << "SPO BF LW " << res[0] << " " << res[1] << " " << res[2] << " "
              << res[3] << std::endl;
}

int main(int argc, char** argv) {
    std::ifstream infile(argv[1]);

    int t, n, O, T, D, X, c1, c2;
    std::vector<Job*> jobs_sporadic;
    std::vector<Job*> jobs_periodic;
    infile >> t;

    for (int i = 0; i < t; i++) {
        jobs_sporadic.clear();
        jobs_periodic.clear();

        infile >> n;
        for (int j = 0; j < n; j++) {
            infile >> O >> T >> D >> X;
            infile >> c1 >> c2;
            Job* job_spo =
                new JobSporadic(O, T, D, X, std::vector<int>{c1, c2});
            // Job* job_per =
            //     new JobPeriodic(O, T, D, X, std::vector<int>{c1, c2});

            jobs_sporadic.push_back(job_spo);
            // jobs_periodic.push_back(job_per);
        }
        // experiment(jobs_sporadic, jobs_periodic);

        experiment_sched(jobs_sporadic);

        // for (auto elem : jobs_sporadic) delete elem;

        // for (auto elem : jobs_periodic) delete elem;
    }

    return 0;

    // Job *j1 = new JobSporadic(0, 3, 3, 2, {2, 3});
    // Job *j2 = new JobSporadic(0, 1, 1, 1, {2, 2});

    Job* ja1 = new JobSporadic(0, 25, 25, 2, std::vector<int>{2, 22});
    Job* ja2 = new JobSporadic(0, 26, 26, 1, std::vector<int>{2, 2});
    Job* ja3 = new JobSporadic(0, 27, 27, 2, std::vector<int>{1, 2});
    Job* ja4 = new JobSporadic(0, 34, 34, 2, std::vector<int>{1, 3});

    // Job *jb1 = new JobSporadic(0, 6, 6, 2, std::vector<int>{2, 2});
    // Job *jb2 = new JobSporadic(0, 3, 3, 2, std::vector<int>{1, 1});
    // Job *jb3 = new JobSporadic(0, 5, 5, 2, std::vector<int>{1, 1});
    // Job *jb4 = new JobSporadic(0, 15, 15, 2, std::vector<int>{1, 2});

    // StateSporadic sa(vector<Job *>{ja1, ja2, ja3, ja4});
    //  StateSporadic sa1(vector<Job *>{ja1});
    //  StateSporadic sa2 = sa1;

    // StateSporadic sb(vector<Job *>{ja1, ja2});

    // vector<Job*> jobs{ja1, ja2, ja3, ja4};

    // vector<Job *> jobs{j1};

    return 0;
}