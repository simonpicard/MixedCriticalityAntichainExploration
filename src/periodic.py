import pandas as pd
import PeriodicGraph
import Task
import TaskSet


def get_execution_transition(ss):
    ss.loc[ss["t_id"] == ss["sched_id"], "rct"] -= 1
    ss.loc[ss["X"] >= ss["crit"], "at"] -= 1
    return ss


def get_done_scope(ss):
    scope = ss["rct"] == 0
    scope &= ss["X"] == ss["crit"]
    return scope


def get_c_at_k(ss, k):
    return [ss.at[x] for x in list(zip(ss.index, k))]


def get_termination_transition(ss, terminate_scope):

    new_rct = get_c_at_k(ss.loc[terminate_scope], ss.loc[terminate_scope, "crit"])

    ss.loc[terminate_scope, "rct"] = new_rct
    ss.loc[terminate_scope, "at"] += ss.loc[terminate_scope, "T"]
    return ss


def get_termination_scope(ss, signal):
    terminate_scope = get_done_scope(ss)

    if signal:
        terminate_scope |= ss["t_id"] == ss["sched_id"]

    return terminate_scope


def get_termination_transitions(ss):
    implicit_scope = get_termination_scope(ss, True)
    explicit_scope = get_termination_scope(ss, False)

    if (implicit_scope == explicit_scope).all():
        ss_done = get_termination_transition(ss, implicit_scope)
    else:
        ss_done_0 = get_termination_transition(ss.copy(), implicit_scope)
        ss_done_1 = get_termination_transition(ss, explicit_scope)
        max_id = ss_done_0["ss_id"].max()
        n_tasks = ss_done_0["t_id"].max() + 1
        ss_done_1["ss_id"] = [
            i
            for i in range(max_id + 1, max_id + 1 + int(ss_done_1.shape[0] / n_tasks))
            for _ in range(n_tasks)
        ]
        ss_done = pd.concat([ss_done_0, ss_done_1], ignore_index=True)
    return ss_done


def get_active_scope(ss):
    scope = ss["at"] < 0
    scope |= (ss["at"] == 0) & (ss["rct"] > 0)
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

    still_active = (ss["X"] >= new_crit) & (new_crit != ss["crit"])

    if still_active.any():

        current_rct = get_c_at_k(ss.loc[still_active], ss.loc[still_active, "crit"])
        next_rct = get_c_at_k(ss.loc[still_active], new_crit.loc[still_active])

        ss.loc[still_active, "rct"] += next_rct
        ss.loc[still_active, "rct"] -= current_rct

    not_active = ss["X"] < new_crit
    ss.loc[not_active, "rct"] = 0
    ss.loc[not_active, "at"] = 0
    ss.loc[:, "crit"] = new_crit

    return ss


def unstack_ss(df):
    df = df.drop("ss_id", axis=1)
    df = df.set_index("t_id")
    df = df.unstack()
    return df


def widen_ss(ss):
    ss_core = ss[["ss_id", "t_id", "at", "rct", "crit"]]
    grouped = ss_core.groupby("ss_id")
    ss_wide = grouped.apply(unstack_ss)
    return ss_wide


def remove_duplicates(ss):

    ss_hashes = get_hashes(ss)
    duplicated_scope = ss_hashes.duplicated()
    duplicated_ssid = ss_hashes.loc[duplicated_scope].index
    return ss.loc[~ss["ss_id"].isin(duplicated_ssid)]


def get_worst_laxity(ss):
    return (
        ss["at"] - (ss["rct"] + ss[1] - ss.apply(lambda row: row[1], axis=1)) + ss["D"]
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
    assert scope.all(), ss.loc[~scope]

    scope = ((ss["X"] < ss["crit"]) & (ss["rct"] == 0) & (ss["at"] == 0)) | (
        ss["X"] >= ss["crit"]
    )
    assert scope.all(), ss.loc[~scope]

    scope = ss["crit"] >= 0
    assert scope.all(), ss.loc[~scope]

    scope = ss["at"] <= ss["T"]
    assert scope.all(), ss.loc[~scope]

    scope = ss["rct"] >= 0
    assert scope.all(), ss.loc[~scope]

    scope = ss["rct"] <= ss[1]
    assert scope.all(), ss.loc[~scope]


def get_laxity(ss):
    return ss["at"] - ss["rct"] + ss["D"]


def fail(ss):
    ss["l"] = get_laxity(ss)
    return (ss["l"] < 0).any()


def get_hashes(ss):
    ss_hashes = (
        ss.set_index(["ss_id", "t_id"])[["at", "rct", "crit"]]
        .groupby(level="ss_id")
        .apply(hash_ss)
    )

    return ss_hashes


def hash_ss(df):
    return hash(df.droplevel(0).reset_index().values.data.tobytes())


def get_neighbours(ss):
    ss = LWLF(ss)
    ss = get_execution_transition(ss)
    ss = get_termination_transitions(ss)
    ss = get_critical_transition(ss)
    ss = remove_duplicates(ss)
    check(ss)
    return ss


def get_initial_state(tasks):
    ss = tasks[["O", 0]].rename(columns={0: "rct", "O": "at"})
    ss["crit"] = 0
    ss = ss.join(tasks)
    ss["t_id"] = ss.index
    ss["ss_id"] = 0
    ss["sched_id"] = -1
    ss["wl"] = get_worst_laxity(ss)
    return ss


if __name__ == "__main__":
    g = TaskSet.TaskSet(
        [
            Task.Task(O=0, T=29, D=29, X=0, C=(5, 5)),
            Task.Task(O=0, T=30, D=30, X=1, C=(6, 7)),
            # Task.Task(O=0, T=28, D=28, X=0, C=(5, 5)),
            # Task.Task(O=0, T=30, D=30, X=1, C=(6, 7)),
        ]
    )

    pg = PeriodicGraph.PeriodicGraph(g)

    ss = pg.getInitialVertex()
    df = ss.ss
    df["crit"] = ss.crit
    ss = df.join(g.tasks)
    ss["t_id"] = ss.index
    ss["ss_id"] = 0
    ss["sched_id"] = -1
    ss["wl"] = get_worst_laxity(ss)

    visited = set()

    ss_hashes = get_hashes(ss)

    i = 0

    while ss.shape[0] > 0:
        visited.update(ss_hashes)

        ss = get_neighbours(ss)

        if fail(ss):
            print("fail")
            break

        ss_hashes = get_hashes(ss)

        ss_visited = ss_hashes.isin(visited)
        ss_visited.name = "visited"

        ss = ss.merge(ss_visited, left_on="ss_id", right_index=True)
        ss = ss.loc[~ss["visited"]]
        ss = ss.drop("visited", axis=1)

        print(i, ss.shape[0] / len(g), ss_visited.sum(), len(visited))
        i += 1
