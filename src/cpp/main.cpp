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

void experiment_graph(std::vector<Job*> jobs_sporadic, int t_id) {
    int64_t* res;

    State* ss = new StateSporadic(jobs_sporadic);
    std::string graph_output_path = "./graphviz/test_refactor.txt";
    GraphSporadic gs(ss, graph_output_path);

    res = gs.acbfs(&Scheduler::edfvd);
    // res = gs.acbfs_graphviz(&Scheduler::fp);
    std::cout << t_id << ",SPO,ACBF,MWUF," << res[0] << "," << res[1] << ","
              << res[2] << "," << res[3] << std::endl;
}

void experiment_graph_per(std::vector<Job*> jobs, int t_id) {
    int64_t* res;

    State* ss = new StatePeriodic(jobs);
    std::string graph_output_path = "./graphviz/periodic_entry.dot";
    GraphPeriodic gs(ss, graph_output_path);

    res = gs.bfs(&Scheduler::edfvd);
    std::cout << t_id << ",PER,BF,MWUF," << res[0] << "," << res[1] << ","
              << res[2] << "," << res[3] << std::endl;
}

void experiment_sched(std::vector<Job*> jobs_sporadic, int t_id,
                      std::string o_file_path) {
    std::ofstream o_file;
    o_file.open(o_file_path, std::ios::in | std::ios::out | std::ios::ate);
    int64_t* res;

    State* ss = new StateSporadic(jobs_sporadic);
    GraphSporadic gs(ss);

    res = gs.acbfs(&Scheduler::fp);
    std::cout << t_id << ",SPO,ACBF,FP," << res[0] << "," << res[1] << ","
              << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,ACBF,FP," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    o_file.close();
}

void experiment_sched_bkp(std::vector<Job*> jobs_sporadic, int t_id,
                          std::string o_file_path) {
    std::ofstream o_file;
    o_file.open(o_file_path, std::ios::in | std::ios::out | std::ios::ate);
    int64_t* res;

    State* ss = new StateSporadic(jobs_sporadic);
    GraphSporadic gs(ss);

    res = gs.acbfs(&Scheduler::lwlf);
    std::cout << t_id << ",SPO,ACBF,LWLF," << res[0] << "," << res[1] << ","
              << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,ACBF,LWLF," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    res = gs.acbfs(&Scheduler::edfvd);
    std::cout << t_id << ",SPO,ACBF,EDF-VD," << res[0] << "," << res[1] << ","
              << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,ACBF,EDF-VD," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    o_file.close();
}

void experiment_cplx(std::vector<Job*> jobs_sporadic,
                     std::vector<Job*> jobs_periodic, int t_id,
                     std::string o_file_path) {
    std::ofstream o_file;
    o_file.open(o_file_path, std::ios::in | std::ios::out | std::ios::ate);

    int64_t* res;

    State* ss = new StateSporadic(jobs_sporadic);
    GraphSporadic gs(ss);

    State* sp = new StatePeriodic(jobs_periodic);
    GraphPeriodic gp(sp);

    res = gp.bfs(&Scheduler::edfvd);
    std::cout << t_id << ",PER,BF,EDF-VD,false," << res[0] << "," << res[1]
              << "," << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",PER,BF,EDF-VD,false," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    res = gs.acbfs(&Scheduler::edfvd);
    std::cout << t_id << ",SPO,ACBF,EDF-VD,false," << res[0] << "," << res[1]
              << "," << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,ACBF,EDF-VD,false," << res[0] << "," << res[1]
           << "," << res[2] << "," << res[3] << std::endl;

    res = gs.bfs(&Scheduler::edfvd);
    std::cout << t_id << ",SPO,BF,EDF-VD,false," << res[0] << "," << res[1]
              << "," << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,BF,EDF-VD,false," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    res = gp.bfs(&Scheduler::edfvd, true);
    std::cout << t_id << ",PER,BF,EDF-VD,true," << res[0] << "," << res[1]
              << "," << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",PER,BF,EDF-VD,true," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    res = gs.acbfs(&Scheduler::edfvd, true);
    std::cout << t_id << ",SPO,ACBF,EDF-VD,true," << res[0] << "," << res[1]
              << "," << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,ACBF,EDF-VD,true," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    res = gs.bfs(&Scheduler::edfvd, true);
    std::cout << t_id << ",SPO,BF,EDF-VD,true," << res[0] << "," << res[1]
              << "," << res[2] << "," << res[3] << std::endl;
    o_file << t_id << ",SPO,BF,EDF-VD,true," << res[0] << "," << res[1] << ","
           << res[2] << "," << res[3] << std::endl;

    o_file.close();
}

int main(int argc, char** argv) {
    std::string xp_type = argv[1];

    std::ifstream infile(argv[2]);
    std::string o_file_path = argv[3];

    int start_input = 0;
    int step_input = 0;
    int end_input = 0;

    if (argc >= 6) {
        start_input = std::atoi(argv[4]);
        step_input = std::atoi(argv[5]);
        end_input = start_input + step_input;
    }

    std::ofstream o_file;
    o_file.open(o_file_path);

    o_file << "tid,task_type,search_type,scheduler,safe_pruning,schedulable,n_"
              "visited,"
              "duration,depth"
           << std::endl;

    o_file.close();

    int t, n, O, T, D, X, c1, c2;
    infile >> t;

    if (end_input == 0) end_input = t;

    if (xp_type == "cplx") {
        std::vector<Job*> jobs_sporadic;
        std::vector<Job*> jobs_periodic;

        for (int i = 0; i < end_input; i++) {
            jobs_sporadic.clear();
            jobs_periodic.clear();

            infile >> n;
            for (int j = 0; j < n; j++) {
                infile >> O >> T >> D >> X;
                infile >> c1 >> c2;
                if (i >= start_input) {
                    Job* job_spo = new JobSporadic(O, T, D, X,
                                                   std::vector<int>{c1, c2}, j);
                    jobs_sporadic.push_back(job_spo);
                    Job* job_per = new JobPeriodic(O, T, D, X,
                                                   std::vector<int>{c1, c2}, j);
                    jobs_periodic.push_back(job_per);
                }
            }
            if (i >= start_input) {
                experiment_cplx(jobs_sporadic, jobs_periodic, i, o_file_path);
            }
        }
    } else if (xp_type == "sched") {
        std::vector<Job*> jobs_sporadic;

        for (int i = 0; i < end_input; i++) {
            jobs_sporadic.clear();
            infile >> n;
            for (int j = 0; j < n; j++) {
                infile >> O >> T >> D >> X;
                infile >> c1 >> c2;
                if (i >= start_input) {
                    Job* job_spo = new JobSporadic(O, T, D, X,
                                                   std::vector<int>{c1, c2}, j);
                    jobs_sporadic.push_back(job_spo);
                }
            }
            if (i >= start_input) {
                experiment_sched(jobs_sporadic, i, o_file_path);
            }
        }
    } else if (xp_type == "graph") {
        std::vector<Job*> jobs_sporadic;

        for (int i = 0; i < end_input; i++) {
            jobs_sporadic.clear();
            infile >> n;
            for (int j = 0; j < n; j++) {
                infile >> O >> T >> D >> X;
                infile >> c1 >> c2;
                if (i >= start_input) {
                    Job* job_spo = new JobSporadic(O, T, D, X,
                                                   std::vector<int>{c1, c2}, j);
                    jobs_sporadic.push_back(job_spo);
                }
            }
            if (i >= start_input) {
                experiment_graph(jobs_sporadic, i);
            }
        }
    } else if (xp_type == "graph_per") {
        std::vector<Job*> jobs;

        for (int i = 0; i < end_input; i++) {
            jobs.clear();
            infile >> n;
            for (int j = 0; j < n; j++) {
                infile >> O >> T >> D >> X;
                infile >> c1 >> c2;
                if (i >= start_input) {
                    Job* job_spo = new JobPeriodic(O, T, D, X,
                                                   std::vector<int>{c1, c2}, j);
                    jobs.push_back(job_spo);
                }
            }
            if (i >= start_input) {
                experiment_graph_per(jobs, i);
            }
        }
    }
    return 0;
}