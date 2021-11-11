import pandas as pd


class SystemState:
    def __init__(self, ss, crit, tasks):
        self.tasks = tasks
        self.ss = ss
        self.crit = crit

    def getActive(self):
        scope = self.ss["at"] < 0
        scope |= (self.ss["at"] == 0) & (self.ss["rct"] > 0)
        return scope.loc[scope].index.values

    def get_active_scope(self):
        scope = self.ss["at"] < 0
        scope |= (self.ss["at"] == 0) & (self.ss["rct"] > 0)
        return scope.loc[scope].index.values

    def getCrit(self):
        if (self.ss.loc[self.get_active_scope(), "rct"] == 0).any():
            return self.crit + 1
        return self.crit

    def getLaxity(self):
        return self.ss["at"] - self.ss["rct"] + self.tasks["D"]

    def getWorstLaxity(self, C):
        return (
            self.ss["at"]
            - (
                self.ss["rct"]
                + (self.tasks[self.tasks["X"].max()] - self.tasks[self.crit])
            )
            + self.tasks["D"]
        )

    def isFail(self):
        return (self.getLaxity() < 0).any()

    def getImplicitelyDone(self):
        scope = self.ss["rct"] == 0
        scope &= self.tasks["X"] == self.crit
        return scope.loc[scope].index.values

    def getExecutionTransition(self, run):
        critP = self.crit
        ssP = self.ss.copy()
        ssP.loc[run, "rct"] -= 1
        ssP.loc[self.tasks["X"] >= self.crit, "at"] -= 1
        ssP.loc[self.tasks["X"] < self.crit, "at"] = 0  # useless?

        return SystemState(ssP, critP, self.tasks)

    def getTerminationTransition(self, toTerminate):
        critP = self.crit
        toTerminate = list(toTerminate.union(self.getImplicitelyDone()))
        ssP = self.ss.copy()
        ssP.loc[toTerminate, "rct"] = self.tasks[self.crit]
        ssP.loc[toTerminate, "at"] += self.tasks["T"]
        return SystemState(ssP, critP, self.tasks)

    def getCriticalTransition(self):
        critP = self.getCrit()

        ssP = self.ss.copy()

        ssP.loc[self.tasks["X"] >= critP, "rct"] += (
            self.tasks[critP] - self.tasks[self.crit]
        )
        ssP.loc[self.tasks["X"] < critP, "rct"] = 0
        ssP.loc[self.tasks["X"] < critP, "at"] = 0

        return SystemState(ssP, critP, self.tasks)

    def getRelativeDeadline(self, i, relativity=1):
        return self.ss.loc[i, "at"] + self.tasks.loc[i, "D"] * relativity

    def isWCSimulation(self, other):
        if self.crit != other.crit or self.ss["at"] != other.ss["at"]:
            return False

        if ((self.ss["rct"] == 0) & (other.ss["rct"] != 0)).any():
            return False

        if (self.ss.loc[(self.ss["rct"] > 0), "rct"] < other.ss["rct"]).any():
            return False

        return True

    def __repr__(self):
        return f"{self.ss}\ncrit={self.crit}"

    def __eq__(self, other):
        # print("eq")
        return True
        # return (self.at == other.at and self.rct == other.rct and self.crit == other.crit)
        # return self.isWCSimulation(other)

    def compute_max_nodes(self):
        at_poss = self.tasks["T"] + self.tasks[1] - 1
        rct_poss = self.tasks[1] - 1
        c_poss = 2
        return int((at_poss * rct_poss * c_poss).product())

    def __hash__(self):
        return hash(self.ss.values.data.tobytes()) + self.crit

        # hashinfo = D, T, Cmax, K
        D = self.tasks["D"].apply(int)
        T = self.tasks["T"].apply(int)
        K = int(self.tasks["X"].max())
        Cmax = self.tasks[K].apply(int)
        # -D-1 <= at <= T
        # 0 <= at+D+1 <= T+D+1
        # 0 <= rct <= Cmax
        # 0 <= crit <= K
        h = 0

        h = self.crit + 1
        factor = K + 1
        for i in range(self.ss.shape[0]):
            print(h)
            h += int(self.ss.loc[i, "rct"]) * factor
            print(h)
            factor *= Cmax[i] + 1
            h += (int(self.ss.loc[i, "at"]) + D[i] + 1) * factor
            print(h)
            factor *= T[i] + D[i] + 1

        print(h)
        return h
