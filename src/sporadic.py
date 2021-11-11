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


def get_execution_transition(ss):
    ss.loc[ss["t_id"] == ss["sched_id"], "rct"] -= 1
    ss.loc[:, "nat"] -= 1
    ss.loc[ss["done"], "nat"] = ss.loc[ss["done"], "nat"].clip(0)
    return ss


def get_implicitely_done_scope(ss):
    scope = ss["rct"] == 0
    scope &= (ss["X"] == ss["crit"]) | (ss[1] == ss[0])
    scope &= ~ss["done"]
    return scope


def get_c_at_k(ss, k):
    return [ss.at[x] for x in list(zip(ss.index, k))]


def get_termination_transition(ss, terminate_scope):

    ss.loc[terminate_scope, "rct"] = 0
    ss.loc[terminate_scope, "done"] = True
    return ss


def get_termination_scope(ss, signal):
    terminate_scope = get_implicitely_done_scope(ss)

    if signal:
        terminate_scope |= ss["t_id"] == ss["sched_id"]

    return terminate_scope


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


def get_active_scope(ss):
    scope = ~ss["done"]
    return scope


def get_crit(ss):
    scope = get_active_scope(ss)
    scope &= ss["rct"] == 0
    ss_scope = ss["ss_id"].isin(ss.loc[scope, "ss_id"].unique())
    new_crit = ss["crit"].copy()
    new_crit.loc[ss_scope] += 1
    return new_crit


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


def get_eligible_scope(ss):
    eligible_scope = ss["rct"] == 0
    eligible_scope &= ss["nat"] <= 0
    eligible_scope &= ss["done"]
    eligible_scope &= ss["X"] >= ss["crit"]
    return eligible_scope


def generate_all_older_requests(ss):

    request_scope = ss["request"]

    nat_ranges = ss.loc[request_scope].apply(
        lambda x: range(int(x["nat"] + x["T"]), int(x["T"] + 1)), axis=1
    )

    new_ss_list = []

    nats = list(itertools.product(*nat_ranges))
    for new_nat in nats:
        new_ss = ss.copy()
        new_ss.loc[request_scope, "nat"] = new_nat
        new_ss_list.append(new_ss)

    return new_ss_list


def get_request_transition_bkp(ss):

    request_scope = ss["request"]

    ss.loc[request_scope, "rct"] = get_c_at_k(
        ss.loc[request_scope], ss.loc[request_scope, "crit"]
    )

    ss.loc[request_scope, "done"] = False

    request_ss_id = ss.loc[request_scope, "ss_id"].unique()
    request_ss_scope = ss["ss_id"].isin(request_ss_id)
    request_ss = ss.loc[request_ss_scope]

    new_ss_lists = request_ss.groupby("ss_id").apply(generate_all_older_requests)

    new_ss_list = list(itertools.chain.from_iterable(new_ss_lists.values))

    ss = ss.loc[~request_ss_scope]

    if ss.shape[0] > 0:
        all_ss_list = [ss] + new_ss_list
    else:
        all_ss_list = new_ss_list

    return concat_graphes(all_ss_list)


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

    nat_sates = nat_ranges.values
    nat_sates = nat_sates.reshape((int(nat_sates.shape[0] / n_tasks), n_tasks))

    def f(x):
        return list(itertools.product(*x))

    nat_sates = np.array(list(map(f, nat_sates)))

    new_ss_list = []

    max_iter = int((1 - ss.loc[ss["request"], "nat"]).max())
    combinations_df = pd.DataFrame(
        index=range(int(ss.shape[0] / n_tasks)), columns=range(max_iter)
    )
    for i in range(len(nat_sates)):
        nat_sate = nat_sates[i]
        combinations_df.iloc[i, : len(nat_sate)] = list(nat_sate)

    for col, combinations_series in combinations_df.iteritems():
        ss_scope = combinations_series.notna()
        if not ss_scope.any():
            break
        task_scope = ss_scope.repeat(n_tasks)
        nat_values = list(itertools.chain.from_iterable(combinations_series.dropna()))

        ss_new = ss.loc[task_scope.values].copy()
        ss_new.loc[:, "nat"] = nat_values
        new_ss_list.append(ss_new)

    return concat_graphes(new_ss_list)


def generate_all_requests(ss):

    new_ss_list = []

    requests = list(itertools.product(*ss["request"]))
    for request in requests:
        new_ss = ss.copy()

        new_ss["request"] = request
        new_ss_list.append(new_ss)

    return new_ss_list


def get_request_transitions_bkp(ss):

    eligible_scope = get_eligible_scope(ss)
    ss["request"] = eligible_scope.apply(lambda x: [True, False] if x else [False])

    new_ss_lists = ss.groupby("ss_id").apply(generate_all_requests)
    new_ss_list = list(itertools.chain.from_iterable(new_ss_lists.values))

    ss = concat_graphes(new_ss_list)

    return get_request_transition(ss)


def get_request_transitions(ss):

    n_tasks = get_n_tasks(ss)

    eligible_scope = get_eligible_scope(ss)
    ss["request"] = eligible_scope.apply(lambda x: [True, False] if x else [False])

    request_sates = ss["request"].values

    def f(x):
        return list(itertools.product(*x))

    request_sates = request_sates.reshape(
        (int(request_sates.shape[0] / n_tasks), n_tasks)
    )

    request_sates = np.array(list(map(f, request_sates)), dtype=object)

    new_ss_list = []

    max_combinations = 2 ** n_tasks
    combinations_df = pd.DataFrame(
        index=range(int(ss.shape[0] / n_tasks)), columns=range(max_combinations)
    )
    for i in range(len(request_sates)):
        request_sate = request_sates[i]
        combinations_df.iloc[i, : len(request_sate)] = list(request_sate)

    for col, combinations_series in combinations_df.iteritems():
        ss_scope = combinations_series.notna()
        if not ss_scope.any():
            break
        task_scope = ss_scope.repeat(n_tasks)
        request_values = list(
            itertools.chain.from_iterable(combinations_series.dropna())
        )

        ss_new = ss.loc[task_scope.values].copy()
        ss_new.loc[:, "request"] = request_values
        new_ss_list.append(ss_new)

    ss = concat_graphes(new_ss_list)

    ss["request"] = ss["request"].astype("bool")

    return get_request_transition(ss)


def unstack_ss(df):
    df = df.drop("ss_id", axis=1)
    df = df.set_index("t_id")
    df = df.unstack()
    return df


def widen_ss(ss):
    ss_core = ss[["ss_id", "t_id", "nat", "rct", "crit"]]
    grouped = ss_core.groupby("ss_id")
    ss_wide = grouped.apply(unstack_ss)
    return ss_wide


def get_n_tasks(ss):
    n_tasks = ss["t_id"].max() + 1
    return n_tasks


def remove_duplicates(ss):

    n_tasks = get_n_tasks(ss)

    ss_hashes = ss.iloc[::n_tasks]["hash"]
    duplicated_scope = ss_hashes.duplicated().repeat(n_tasks)

    return ss.loc[(~duplicated_scope).values]


def get_worst_laxity(ss):
    return (
        ss["nat"]
        - ss["T"]
        + ss["D"]
        - ss["rct"]
        - (ss[1] - get_c_at_k(ss, ss["crit"])) * ((~ss["done"]).astype(int))
    )


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


def set_worst_laxity(ss):
    ss["wl"] = get_worst_laxity(ss)
    return ss


def set_hashes(ss):
    hashes = get_hashes(ss)
    ss = ss.drop("hash", axis=1, errors="ignore")
    ss = ss.merge(hashes, left_on="ss_id", right_index=True)
    return ss


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


def get_hashes(ss):
    ss = get_task_hash(ss)
    ss_hashes = (
        ss.set_index(["ss_id", "t_id"])[["hash_value", "hash_factor"]]
        .groupby(level="ss_id")
        .apply(combine_task_hashes)
    )

    ss_hashes.name = "hash"

    return ss_hashes


def simulate(ss, other, inverted=False):
    if not (
        ss[["crit", "done", "rct"]].values == other[["crit", "done", "rct"]].values
    ).all():
        return False
    if not (
        ss.loc[~ss["done"], "nat"].values == other.loc[~other["done"], "nat"].values
    ).all():
        return False
    if not inverted:
        if not (
            ss.loc[ss["done"], "nat"].values <= other.loc[other["done"], "nat"].values
        ).all():
            return False
    else:
        if not (
            ss.loc[ss["done"], "nat"].values >= other.loc[other["done"], "nat"].values
        ).all():
            return False
    return True


def get_neighbours(ss, simulation=False):
    ss = LWLF(ss)
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


def combine_task_hashes_idle_bkp(ss):
    combine_hash_factor = ss["hash_factor"]
    combine_hash_factor = combine_hash_factor.cumprod()
    nat_order_factor = combine_hash_factor.iloc[-1]
    combine_hash_factor = combine_hash_factor.shift().fillna(1)
    ss_hash = (ss["hash_value"] * combine_hash_factor).sum()

    ss = ss.sort_values("nat")

    nat_order_value = lexicographical_index(ss.index.get_level_values(1))
    ss_hash += nat_order_value * nat_order_factor

    print(
        combine_hash_factor.values,
        nat_order_factor,
        ss["hash_value"].values,
        nat_order_value,
        ss_hash,
    )
    return ss_hash


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
        ss.set_index(["ss_id", "t_id"])[["hash_value", "hash_factor", "nat"]].groupby(
            level="ss_id"
        )
        # .apply(combine_task_hashes_idle_bkp)
        .apply(combine_task_hashes_idle, hash_factor)
    )

    ss_hashes.name = "hash_idle"

    return ss_hashes


def set_hashes_idle(ss):
    hashes = get_hashes_idle(ss)
    ss = ss.drop("hash_idle", axis=1, errors="ignore")
    ss = ss.merge(hashes, left_on="ss_id", right_index=True)
    return ss


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

    simulated = (df_merge["nat_other"] <= df_merge["nat"]).values
    simulated = simulated.reshape((int(simulated.shape[0] / n_tasks), n_tasks))
    simulated = np.logical_and.reduce(simulated, axis=1)

    different_nat = ((df_merge["nat"] != df_merge["nat_other"])).values
    different_nat = different_nat.reshape(
        (int(different_nat.shape[0] / n_tasks), n_tasks)
    )
    different_nat = np.logical_or.reduce(different_nat, axis=1)

    different_id = ((df_merge["ss_id"] > df_merge["ss_id_other"])).values
    different_id = different_id.reshape((int(different_id.shape[0] / n_tasks), n_tasks))
    different_id = np.logical_and.reduce(different_id, axis=1)

    different = different_nat | different_id

    simulated &= different

    ss = remove_simulated_list(ss, df_merge, simulated, n_tasks, id_col="ss_id")

    return ss


def remove_visited_simulation(ss, visited, n_tasks):
    idx_l = ["hash_idle", "t_id"]
    df_merge = ss.set_index(idx_l)
    df_merge = df_merge.join(visited.set_index(idx_l), how="left", rsuffix="_other")
    df_merge = df_merge.reset_index()
    df_merge = df_merge.reset_index()
    df_merge = df_merge.sort_values(["hash_idle", "ss_id", "ss_id_other"])

    simulated_full = df_merge["nat_other"] <= df_merge["nat"]
    simulated = simulated_full.values.reshape(
        (int(simulated_full.shape[0] / n_tasks), n_tasks)
    )
    simulated = np.logical_and.reduce(simulated, axis=1)

    ss = remove_simulated_list(ss, df_merge, simulated, n_tasks, id_col="ss_id")

    never_seen_scope = df_merge["nat_other"].isna()
    never_seen_states = df_merge[never_seen_scope][["hash_idle", "nat", "t_id"]]

    df_merge = df_merge[~never_seen_scope]

    simulator = ((df_merge["nat"] <= df_merge["nat_other"])).values
    simulator = simulator.reshape((int(simulator.shape[0] / n_tasks), n_tasks))
    simulator = np.logical_and.reduce(simulator, axis=1)

    different = ((df_merge["nat"] != df_merge["nat_other"])).values
    different = different.reshape((int(different.shape[0] / n_tasks), n_tasks))
    different = np.logical_or.reduce(different, axis=1)

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


def bfs_simulation(ts):

    ss = get_initial_state(ts.get_df())
    ss = set_hashes_idle(ss)

    n_tasks = len(ts)

    visited = ss[["hash_idle", "nat", "t_id"]].copy()
    visited["ss_id"] = 0

    i = 0

    while ss.shape[0] > 0:

        ss = get_neighbours(ss, True)

        if fail(ss):
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


import TaskSet, Task


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

    pHI = 0.5
    rHI = 2
    Tmax = 30
    CmaxLO = 15
    nbT = 4

    experiment_arg = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for u in range(40, 100, 1):
            for i in range(10):
                experiment_arg.append((pHI, rHI, CmaxLO, Tmax, u / 100.0, nbT))
        results = pd.DataFrame(
            tqdm(executor.map(f_unpack, experiment_arg), total=len(experiment_arg))
        )

    results.to_csv("sporadic_result.csv")

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
