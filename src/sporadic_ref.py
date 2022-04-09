import pandas as pd
import itertools
import numpy as np


from math import factorial
from functools import reduce

import SetGenerator

import time
import concurrent.futures
from tqdm import tqdm
import pandas as pd


import TaskSet, Task


### SCOPES ###


def get_implicitely_done_scope(ss):
    scope = ss["rct"] == 0
    scope &= (ss["X"] == ss["crit"]) | (ss[1] == ss[0])
    scope &= ~ss["done"]
    return scope


def get_active_scope(ss):
    scope = ~ss["done"]
    return scope


def get_termination_scope(ss, signal):
    terminate_scope = get_implicitely_done_scope(ss)
    if signal:
        terminate_scope |= ss["t_id"] == ss["sched_id"]
    return terminate_scope


def get_eligible_scope(ss):
    eligible_scope = ss["rct"] == 0
    eligible_scope &= ss["nat"] <= 0
    eligible_scope &= ss["done"]
    eligible_scope &= ss["X"] >= ss["crit"]
    return eligible_scope


### HELPER FUNC ###


def concat_graphes(graphes):
    ss_main = graphes[0]
    n_tasks = get_n_tasks(ss_main)

    for i in range(1, len(graphes)):
        ss_other = graphes[i]

        max_id = ss_main["ss_id"].max()

        ss_other["ss_id"] = [
            i
            for i in range(max_id + 1, max_id + 1 + int(ss_other.shape[0] / n_tasks))
            for _ in range(n_tasks)
        ]
        ss_main = pd.concat([ss_main, ss_other], ignore_index=True)

    return ss_main


def get_system_state_wise_operation(bool_series, n_tasks, operation):

    bool_series = bool_series.values

    bool_series = bool_series.reshape((int(bool_series.shape[0] / n_tasks), n_tasks))
    if operation == "and":
        bool_series = np.logical_and.reduce(bool_series, axis=1)
    elif operation == "or":
        bool_series = np.logical_or.reduce(bool_series, axis=1)
    else:
        print("operation must be `and` or `or`")
        raise

    return bool_series


def get_c_at_k(ss, k):
    return [ss.at[x] for x in list(zip(ss.index, k))]


def get_n_tasks(ss):
    n_tasks = ss["t_id"].max() + 1
    return n_tasks


def get_worst_laxity(ss):
    return (
        ss["nat"]
        - ss["T"]
        + ss["D"]
        - ss["rct"]
        - (ss[1] - get_c_at_k(ss, ss["crit"])) * ((~ss["done"]).astype(int))
    )


def set_worst_laxity(ss):
    ss["wl"] = get_worst_laxity(ss)
    return ss


def get_crit(ss):
    scope = get_active_scope(ss)
    scope &= ss["rct"] == 0
    ss_scope = ss["ss_id"].isin(ss.loc[scope, "ss_id"].unique())
    new_crit = ss["crit"].copy()
    new_crit.loc[ss_scope] += 1
    return new_crit


### TRANSITIONS ###


def get_execution_transition(ss):
    ss.loc[ss["t_id"] == ss["sched_id"], "rct"] -= 1
    ss.loc[:, "nat"] -= 1
    ss.loc[ss["done"], "nat"] = ss.loc[ss["done"], "nat"].clip(0)
    return ss


def get_termination_transition(ss, terminate_scope):
    ss.loc[terminate_scope, "rct"] = 0
    ss.loc[terminate_scope, "done"] = True
    return ss


def get_termination_transitions(ss):
    implicit_scope = get_termination_scope(ss, False)
    explicit_scope = get_termination_scope(ss, True)

    if (implicit_scope == explicit_scope).all():
        ss_done = get_termination_transition(ss, implicit_scope)
    else:
        ss_done_0 = get_termination_transition(ss.copy(), implicit_scope)
        ss_done_1 = get_termination_transition(ss, explicit_scope)
        ss_done = concat_graphes([ss_done_0, ss_done_1])
    return ss_done


def get_critical_transition(ss):
    new_crit = get_crit(ss)

    if (new_crit == ss["X"]).all():
        return ss

    active_scope = get_active_scope(ss)
    enabled_scope = ss["X"] >= new_crit
    disaled_scope = ~enabled_scope

    increase_rct_scope = (active_scope) & (enabled_scope)

    if increase_rct_scope.any():

        current_rct = get_c_at_k(
            ss.loc[increase_rct_scope], ss.loc[increase_rct_scope, "crit"]
        )
        next_rct = get_c_at_k(
            ss.loc[increase_rct_scope], new_crit.loc[increase_rct_scope]
        )

        ss.loc[increase_rct_scope, "rct"] += next_rct
        ss.loc[increase_rct_scope, "rct"] -= current_rct

    ss.loc[disaled_scope, "rct"] = 0
    ss.loc[disaled_scope, "nat"] = 0
    ss.loc[disaled_scope, "done"] = True

    ss.loc[:, "crit"] = new_crit

    return ss


def get_combinations_per_system_state(possible_values_per_task, n_tasks):
    """
    [[0, 1, 2], [A, B], [0], [A, B, C]] with n_tasks=2
    >
    [
        [[0, A], [1, A], [2, A], [0, B], [1, B], [2, B]],
        [[0, A], [0, B], [0, C]]
    ]
    """

    possible_values_per_task = possible_values_per_task.values
    possible_values_per_task = possible_values_per_task.reshape(
        (int(possible_values_per_task.shape[0] / n_tasks), n_tasks)
    )

    def f(x):
        return list(itertools.product(*x))

    combinations_per_system_state = np.array(list(map(f, possible_values_per_task)))

    return combinations_per_system_state


def pivot_combinations(combination_series, max_combination_per_sate, n_ss):
    """
    Given an iterable of iterable of different len, will create a dataframe where
    nested iterables become rows filled with the iterable values and then NaNs if needed
    """

    combinations_df = pd.DataFrame(
        index=range(n_ss), columns=range(max_combination_per_sate)
    )
    for i in range(len(combination_series)):
        combination = combination_series[i]
        combinations_df.iloc[i, : len(combination)] = list(combination)

    return combinations_df


def generate_all_combinations(ss, combinations_df, n_tasks, variable):

    new_ss_list = []

    for col, combinations_series in combinations_df.iteritems():
        ss_scope = combinations_series.notna()
        if not ss_scope.any():
            break
        task_scope = ss_scope.repeat(n_tasks)
        variable_values = list(
            itertools.chain.from_iterable(combinations_series.dropna())
        )

        ss_new = ss.loc[task_scope.values].copy()
        ss_new.loc[:, variable] = variable_values
        new_ss_list.append(ss_new)

    ss = concat_graphes(new_ss_list)

    return ss


def get_request_transition(ss):

    if not ss["request"].any():
        return ss

    n_tasks = get_n_tasks(ss)

    request_scope = ss["request"]

    ss.loc[request_scope, "rct"] = get_c_at_k(
        ss.loc[request_scope], ss.loc[request_scope, "crit"]
    )

    ss.loc[request_scope, "done"] = False

    nat_ranges = ss.apply(
        lambda x: list(range(int(x["nat"] + x["T"]), int(x["T"] + 1)))
        if x["request"]
        else [x["nat"]],
        axis=1,
    )

    nat_sates = get_combinations_per_system_state(nat_ranges, n_tasks)

    max_iter = int((1 - ss.loc[ss["request"], "nat"]).max())

    combinations_df = pivot_combinations(
        nat_sates, max_iter, int(ss.shape[0] / n_tasks)
    )

    ss = generate_all_combinations(ss, combinations_df, n_tasks, "nat")

    return ss


def generate_all_requests(ss):

    new_ss_list = []

    requests = list(itertools.product(*ss["request"]))
    for request in requests:
        new_ss = ss.copy()

        new_ss["request"] = request
        new_ss_list.append(new_ss)

    return new_ss_list


def get_request_transitions(ss):

    n_tasks = get_n_tasks(ss)

    eligible_scope = get_eligible_scope(ss)
    ss["request"] = eligible_scope.apply(lambda x: [True, False] if x else [False])

    request_sates = get_combinations_per_system_state(ss["request"], n_tasks)

    max_combinations = 2 ** n_tasks

    combinations_df = pivot_combinations(
        request_sates, max_combinations, int(ss.shape[0] / n_tasks)
    )

    ss = generate_all_combinations(ss, combinations_df, n_tasks, "request")

    ss["request"] = ss["request"].astype("bool")

    return get_request_transition(ss)


def remove_duplicates(ss):

    n_tasks = get_n_tasks(ss)

    ss_hashes = ss.iloc[::n_tasks]["hash"]
    duplicated_scope = ss_hashes.duplicated().repeat(n_tasks)

    return ss.loc[(~duplicated_scope).values]


### SCHEDULER ###


def LWLF(ss):

    ss["wl"] = get_worst_laxity(ss)

    active_scope = get_active_scope(ss)

    sched_loc = ss.loc[active_scope].groupby("ss_id")["wl"].idxmin()
    sched_ids = ss.loc[sched_loc, ["ss_id", "t_id"]].rename(
        columns={"t_id": "sched_id"}
    )
    ss = ss.drop("sched_id", axis=1).merge(sched_ids, on="ss_id", how="left")

    ss["sched_id"] = ss["sched_id"].fillna(-1)

    return ss


def get_relativity(ts):
    if (
        ts.getUtilisationOfLevelAtLevel(0, 0) + ts.getUtilisationOfLevelAtLevel(1, 1)
        > 1
    ):
        relativity = ts.getUtilisationOfLevelAtLevel(1, 0) / (
            1 - ts.getUtilisationOfLevelAtLevel(0, 0)
        )
    else:
        relativity = 0
    return relativity


def get_virtual_deadline(ss, relativity):
    vdl = ss["nat"] - ss["T"] + ss["D"]
    vdl += (
        (ss["crit"] == 0).apply(int) * (ss["X"] == 1).apply(int) * ss["T"] * relativity
    )
    return vdl


def EDFVD(ss, relativity=1):
    ss["vdl"] = get_virtual_deadline(ss, relativity)

    active_scope = get_active_scope(ss)

    sched_loc = ss.loc[active_scope].groupby("ss_id")["vdl"].idxmin()
    sched_ids = ss.loc[sched_loc, ["ss_id", "t_id"]].rename(
        columns={"t_id": "sched_id"}
    )
    ss = ss.drop("sched_id", axis=1).merge(sched_ids, on="ss_id", how="left")

    ss["sched_id"] = ss["sched_id"].fillna(-1)
    return ss


### HASHING ###


def set_hashes(ss):
    hashes = get_hashes(ss)
    ss = ss.drop("hash", axis=1, errors="ignore")
    ss = ss.merge(hashes, left_on="ss_id", right_index=True)
    return ss


def get_hashes(ss):
    ss = get_task_hash(ss)
    ss_hashes = (
        ss.set_index(["ss_id", "t_id"])[["hash_value", "hash_factor"]]
        .groupby(level="ss_id")
        .apply(combine_task_hashes)
    )

    ss_hashes.name = "hash"

    return ss_hashes


def get_task_hash(ss):
    value = ss["crit"]
    factor = 2

    value += ss["rct"] * factor
    factor *= ss[1] + 1

    value += (ss["done"]).astype(int) * factor
    factor *= 2

    value += (ss["nat"] + 1) * factor
    factor *= ss["T"] + 2

    ss["hash_value"] = value
    ss["hash_factor"] = factor

    return ss


def combine_task_hashes(ss):
    combine_hash_factor = ss["hash_factor"].shift().fillna(1)
    combine_hash_factor = combine_hash_factor.cumprod()
    return (ss["hash_value"] * combine_hash_factor).sum()


def get_task_hash_idle(ss):
    value = ss["crit"]
    factor = 2

    value += ss["rct"] * factor
    factor *= ss[1] + 1

    value += (ss["done"]).astype(int) * factor
    factor *= 2

    value += ((ss["nat"] + 1) * (~ss["done"]).astype(int)) * factor
    factor *= ss["T"] + 2

    ss["hash_value"] = value
    ss["hash_factor"] = factor

    return ss


def lexicographical_index(idx):
    rank = 0
    l = len(idx)
    freqs = [1] * l

    for n in range(l):
        fsum = sum([freqs[j] for j in range(idx[n])])
        freqs[idx[n]] -= 1
        rank += fsum * factorial(l - n - 1)
    return rank


def combine_task_hashes_idle(ss, hash_factor):
    hash_value = ss["hash_value"].values
    nat_order = ss["nat"].sort_values().index.get_level_values(1)
    nat_order_value = lexicographical_index(nat_order)
    hash_value = np.append(hash_value, nat_order_value)
    ss_hash = hash_value * hash_factor
    ss_hash = np.sum(ss_hash)

    return ss_hash


def get_hash_idle_factor(ss):
    ss_single = ss.loc[ss["ss_id"] == ss["ss_id"].iloc[0]]
    hash_factor = ss_single["hash_factor"]
    hash_factor = hash_factor.cumprod()
    hash_factor = hash_factor.values
    hash_factor = np.insert(hash_factor, 0, 1)

    return hash_factor


def get_hashes_idle(ss):
    ss = get_task_hash_idle(ss)
    hash_factor = get_hash_idle_factor(ss)
    ss_hashes = (
        ss.set_index(["ss_id", "t_id"])[["hash_value", "hash_factor", "nat"]]
        .groupby(level="ss_id")
        .apply(combine_task_hashes_idle, hash_factor)
    )

    ss_hashes.name = "hash_idle"

    return ss_hashes


def set_hashes_idle(ss):
    hashes = get_hashes_idle(ss)
    ss = ss.drop("hash_idle", axis=1, errors="ignore")
    ss = ss.merge(hashes, left_on="ss_id", right_index=True)
    return ss


### MAIN LOOP ###


def get_initial_state(tasks):
    ss = tasks[["O"]].rename(columns={"O": "nat"})
    ss["rct"] = 0
    ss["crit"] = 0
    ss = ss.join(tasks)
    ss["t_id"] = ss.index
    ss["ss_id"] = 0
    ss["done"] = True
    ss = set_worst_laxity(ss)
    ss["sched_id"] = -1
    ss["request"] = False
    return ss


def get_neighbours(ss, sched, simulation=False, relativity=None):
    if sched == "LWLF":
        ss = LWLF(ss)
    elif sched == "EDFVD":
        ss = EDFVD(ss, relativity)
    ss = get_execution_transition(ss)
    ss = get_termination_transitions(ss)
    ss = get_critical_transition(ss)
    ss = get_request_transitions(ss)
    if simulation:
        ss = set_hashes_idle(ss)
    else:
        ss = set_hashes(ss)
        ss = remove_duplicates(ss)
    ss = set_worst_laxity(ss)
    check(ss)
    return ss


def check(ss):
    scope = ss["crit"] <= 1
    assert scope.all(), "\n" + str(ss.loc[~scope])

    scope = ((ss["X"] < ss["crit"]) & (ss["rct"] == 0) & (ss["nat"] == 0)) | (
        ss["X"] >= ss["crit"]
    )
    assert scope.all(), "\n" + str(ss.loc[~scope])

    scope = ss["crit"] >= 0
    assert scope.all(), "\n" + str(ss.loc[~scope])

    scope = ss["nat"] <= ss["T"]
    assert scope.all(), "\n" + str(ss.loc[~scope])

    scope = ss["rct"] >= 0
    assert scope.all(), "\n" + str(ss.loc[~scope])

    scope = ss["rct"] <= ss[1]
    assert scope.all(), "\n" + str(ss.loc[~scope])

    scope = ss["nat"] >= ss["T"] - (ss["D"] + 1) + (ss[1] - get_c_at_k(ss, ss["crit"]))
    scope |= ss["done"]
    scope |= fail(ss)
    assert scope.all(), "\n" + str(ss.loc[~scope])


def fail(ss):
    return (ss["wl"] < 0).any()


### SIMULATION ###


def remove_simulated_list(ss, df_merge, simulated, n_tasks, id_col):
    simulated_ss_id = df_merge.loc[::n_tasks].loc[simulated, id_col]
    simulated_ss_id = simulated_ss_id.drop_duplicates()
    simulated_ss_id.name = "ss_id_simulated"

    ss = ss.merge(
        simulated_ss_id, left_on="ss_id", right_on="ss_id_simulated", how="left"
    )
    ss = ss.loc[ss["ss_id_simulated"].isna()]
    ss = ss.drop("ss_id_simulated", axis=1)

    return ss


def append_visited_states(visited, other, n_tasks):
    ss_id_start = int(visited["ss_id"].max() + 1)
    other["ss_id"] = np.array(
        range(ss_id_start, int(other.shape[0] / n_tasks) + ss_id_start)
    ).repeat(n_tasks)
    visited = visited.append(other, ignore_index=True)
    return visited


def remove_self_simulated(ss, n_tasks):
    df_merge = ss.merge(
        ss, on=["hash_idle", "t_id"], how="left", suffixes=("", "_other")
    )
    df_merge = df_merge.sort_values(["hash_idle", "ss_id", "ss_id_other"])

    simulated = df_merge["nat_other"] <= df_merge["nat"]
    simulated = get_system_state_wise_operation(simulated, n_tasks, "and")

    different_nat = df_merge["nat"] != df_merge["nat_other"]
    different_nat = get_system_state_wise_operation(different_nat, n_tasks, "or")

    different_id = df_merge["ss_id"] > df_merge["ss_id_other"]
    different_id = get_system_state_wise_operation(different_id, n_tasks, "and")

    different = different_nat | different_id

    simulated &= different

    ss = remove_simulated_list(ss, df_merge, simulated, n_tasks, id_col="ss_id")

    return ss


def remove_visited_simulation(ss, visited, n_tasks):
    idx_l = ["hash_idle", "t_id"]
    df_merge = ss.set_index(idx_l)
    df_merge = df_merge.join(visited.set_index(idx_l), how="left", rsuffix="_other")
    df_merge = df_merge.reset_index()
    df_merge = df_merge.sort_values(["hash_idle", "ss_id", "ss_id_other"])

    simulated = df_merge["nat_other"] <= df_merge["nat"]
    simulated = get_system_state_wise_operation(simulated, n_tasks, "and")

    ss = remove_simulated_list(ss, df_merge, simulated, n_tasks, id_col="ss_id")

    never_seen_scope = df_merge["nat_other"].isna()
    never_seen_states = df_merge[never_seen_scope][["hash_idle", "nat", "t_id"]]

    df_merge = df_merge[~never_seen_scope]

    simulator = df_merge["nat"] <= df_merge["nat_other"]
    simulator = get_system_state_wise_operation(simulator, n_tasks, "and")

    different = df_merge["nat"] != df_merge["nat_other"]
    different = get_system_state_wise_operation(different, n_tasks, "or")

    simulator &= different

    visited = remove_simulated_list(
        visited, df_merge, simulator, n_tasks, id_col="ss_id_other"
    )

    simulator_states = df_merge.loc[simulator.repeat(n_tasks)][
        ["hash_idle", "nat", "t_id"]
    ]

    visited = append_visited_states(visited, simulator_states, n_tasks)
    visited = append_visited_states(visited, never_seen_states, n_tasks)

    return ss, visited


### SEARCH ###


def bfs_simulation(ts, sched):

    ss = get_initial_state(ts.get_df())
    ss = set_hashes_idle(ss)

    relativity = get_relativity(ts)

    n_tasks = len(ts)

    visited = ss[["hash_idle", "nat", "t_id"]].copy()
    visited["ss_id"] = 0

    i = 0

    while ss.shape[0] > 0:

        ss = get_neighbours(ss, sched, simulation=True, relativity=relativity)

        if fail(ss):
            print("fail")
            return False, len(visited)
            break

        ss = remove_self_simulated(ss, n_tasks)
        ss, visited = remove_visited_simulation(ss, visited, n_tasks)

        # print(
        #     i,
        #     len(ss) / n_tasks,
        #     len(visited) / n_tasks,
        #     visited.groupby("hash_idle").count().max().max(),
        # )
        i += 1
    return True, len(visited)


def experiment(pHI, rHI, CmaxLO, Tmax, u, nbT):
    sg = SetGenerator.SetGenerator(pHI, rHI, CmaxLO, Tmax, u, nbT)
    ts = sg.generateSetU()
    s = time.time()
    res, n = bfs_simulation(ts)
    occurence = pd.Series([u, res, n], ["u", "res", "n"])
    occurence["time"] = time.time() - s
    occurence["nbt"] = nbT
    occurence["u"] = u
    return occurence


def f_unpack(arg):
    return experiment(*arg)


if __name__ == "__main__":

    ts = TaskSet.TaskSet(
        [
            Task.Task(O=0, T=25, D=25, X=1, C=(2, 21)),
            Task.Task(O=0, T=26, D=26, X=0, C=(2, 2)),
            Task.Task(O=0, T=27, D=27, X=1, C=(1, 2)),
            Task.Task(O=0, T=34, D=34, X=1, C=(1, 3)),
        ]
    )

    bfs_simulation(ts)

    # pHI = 0.5
    # rHI = 2
    # Tmax = 30
    # CmaxLO = 15
    # nbT = 4

    # experiment_arg = []
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     for u in range(40, 100, 1):
    #         for i in range(10):
    #             experiment_arg.append((pHI, rHI, CmaxLO, Tmax, u / 100.0, nbT))
    #     results = pd.DataFrame(
    #         tqdm(executor.map(f_unpack, experiment_arg), total=len(experiment_arg))
    #     )

    # results.to_csv("sporadic_result.csv")

    # pHI = 0.5
    # rHI = 2
    # Tmax = 30
    # CmaxLO = 15
    # nbT = 4
    # u = 99

    # experiment_arg = []
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     for i in range(10):
    #         experiment_arg.append((pHI, rHI, CmaxLO, Tmax, u / 100.0, nbT))
    #     results = pd.DataFrame(
    #         tqdm(executor.map(f_unpack, experiment_arg), total=len(experiment_arg))
    #     )

    # results.to_csv("sporadic_result.csv")
