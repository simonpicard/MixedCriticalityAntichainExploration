import time

import pandas as pd

import SetGenerator, TaskSet, Task
from sufficientCond import AMCmax, Greedy, EDFVD, LPA, OCBP, PLRS, Vestal
from sporadic_ref import bfs_simulation

from tqdm import tqdm


import concurrent.futures


def experiment(pHI, rHI, CmaxLO, Tmax, u, nbT):
    sg = SetGenerator.SetGenerator(pHI, rHI, CmaxLO, Tmax, u, nbT)
    ts = sg.generateSetU()
    occurence = pd.Series()
    occurence["U"] = ts.getAverageUtilisation()
    occurence["target_U"] = u
    occurence["nbt"] = nbT

    occurence["AMCmax"] = AMCmax.AMCmax(ts).test()
    occurence["Greedy"] = Greedy.Greedy(ts).test()
    occurence["EDFVD_test"] = EDFVD.EDFVD(ts).test()
    occurence["LPA"] = LPA.LPA(ts).test()
    occurence["OCBP"] = OCBP.OCBP(ts).test()
    occurence["PLRS"] = PLRS.PLRS(ts).test()
    occurence["Vestal"] = Vestal.Vestal(ts).test()

    s = time.time()
    res, n = bfs_simulation(ts, "LWLF")
    occurence["LWLF"] = res
    occurence["LWLF_t"] = time.time() - s
    occurence["LWLF_n_states"] = n
    s = time.time()
    res, n = bfs_simulation(ts, "EDFVD")
    occurence["EDFVD"] = res
    occurence["EDFVD_t"] = time.time() - s
    occurence["EDFVD_n_states"] = n

    return occurence


def f_unpack(arg):
    return experiment(*arg)


if __name__ == "__main__":

    pHI = 0.5
    rHI = 2
    Tmax = 30
    CmaxLO = 15
    nbT = 4

    experiment_arg = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for u in range(40, 101, 1):
            for i in range(10):
                experiment_arg.append((pHI, rHI, CmaxLO, Tmax, u / 100.0, nbT))
        results = pd.DataFrame(
            tqdm(executor.map(f_unpack, experiment_arg), total=len(experiment_arg))
        )

    results.to_csv("sporadic_result.csv")
