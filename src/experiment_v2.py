import pandas as pd

import SetGenerator
import Task
import TaskSet
from sufficientCond import EDFVD, LPA, OCBP, PLRS, AMCmax, Greedy, Vestal


def get_sufficient_cond(ts, u):
    occurence = pd.Series()
    occurence["U"] = ts.getAverageUtilisation()
    occurence["target_U"] = u
    occurence["nbt"] = len(ts)

    # print("AMCmax")
    occurence["AMCmax"] = AMCmax.AMCmax(ts).test()
    # print("Greedy")
    # occurence["Greedy"] = Greedy.Greedy(ts).test()
    # print("EDFVD_test")
    occurence["EDFVD_test"] = EDFVD.EDFVD(ts).test()
    # print("LPA")
    # occurence["LPA"] = LPA.LPA(ts).test()
    # print("OCBP")
    # occurence["OCBP"] = OCBP.OCBP(ts).test()
    # print("PLRS")
    # occurence["PLRS"] = PLRS.PLRS(ts).test()
    # print("Vestal")
    occurence["Vestal"] = Vestal.Vestal(ts).test()

    return occurence


def get_ts_str_cpp(ts):
    res = f"{len(ts)}\n"
    for e in ts:
        res += f"{int(e['O'])} {int(e['T'])} {int(e['D'])} {int(e['X'])+1}\n"
        res += f"{int(e[0])} {int(e[1])}\n"
    return res


def generate_for_complex():

    pHI = 0.5
    rHI = 2
    Tmax = 30
    nbTs = [2, 3, 4, 5]

    df_c = pd.DataFrame()

    ts_id = 0

    ts_str_cpp = ""

    for nb_t in nbTs:
        for i in range(500):
            print(nb_t, i)
            sg = SetGenerator.SetGenerator(pHI, rHI, -1, Tmax, 0, nb_t)
            ts = sg.generateSetPerformance(nb_t)
            ts_str_cpp += get_ts_str_cpp(ts)

            res = pd.Series()
            res["ts_id"] = ts_id
            res["U"] = ts.getAverageUtilisation()
            res["nbt"] = len(ts)

            df_c = df_c.append(res, ignore_index=True)

            ts_id += 1

    ts_str_cpp = f"{ts_id}\n" + ts_str_cpp
    print(df_c)
    print(ts_str_cpp)
    df_c.to_csv("task_cplx_header.csv", index=False)
    with open("task_cplx_input.txt", "w") as text_file:
        text_file.write(ts_str_cpp)


if __name__ == "__main__":

    # generate_for_complex()
    # exit()

    pHI = 0.5
    rHI = 2
    Tmax = 30
    CmaxLO = 15
    nbT = 4

    ts_id = 0

    df_sc = pd.DataFrame()
    ts_str_cpp = ""

    generated_tasks = {}

    pct_cnt = 60
    n_t_pct = 1000

    total_t = (pct_cnt) * n_t_pct

    for x in range(pct_cnt):
        u = 0.4 + x / pct_cnt * 0.6
        u = round(u, 2)
        generated_tasks[u] = 0

    sg = SetGenerator.SetGenerator(pHI, rHI, CmaxLO, Tmax, u, nbT)
    current_t = 0
    while current_t < total_t:
        ts = sg.generateAnySetU()
        ts_u = round(ts.getAverageUtilisation(), 2)

        if ts_u >= 0.4 and ts_u < 1 and round(ts_u * 100) % 1 == 0:
            if generated_tasks[ts_u] < n_t_pct:
                generated_tasks[ts_u] += 1
                print(current_t, generated_tasks)
                current_t += 1

                ts_str_cpp += get_ts_str_cpp(ts)
                res = get_sufficient_cond(ts, ts_u)

                res["ts_id"] = ts_id
                df_sc = df_sc.append(res, ignore_index=True)
                ts_id += 1

    ts_str_cpp = f"{ts_id}\n" + ts_str_cpp
    print(df_sc)
    print(ts_str_cpp)

    df_sc.to_csv("task_sched_header.csv", index=False)
    with open("task_sched_input.txt", "w") as text_file:
        text_file.write(ts_str_cpp)

    #     u = round(u, 3)
    #     for i in range(2000):
    #         print(u, i)

    #         # print(pHI, rHI, CmaxLO, Tmax, u, nbT)

    #         sg = SetGenerator.SetGenerator(pHI, rHI, CmaxLO, Tmax, u, nbT)
    #         ts = sg.generateSetU()

    #         ts_str_cpp += get_ts_str_cpp(ts)

    #         res = get_sufficient_cond(ts, u)
    #         res["ts_id"] = ts_id

    #         df_sc = df_sc.append(res, ignore_index=True)

    #         ts_id += 1
