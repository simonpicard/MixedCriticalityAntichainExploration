import pandas as pd


class Task:
    def __init__(self, O, T, D, X, C):

        self.task = pd.Series(
            [O, T, D, X] + list(C), ["O", "T", "D", "X"] + list(range(len(C)))
        )
        U = pd.Series(
            (self.task[range(len(C))] / self.task["T"]).values,
            index=["U" + str(i) for i in range(len(C))],
        )
        if X == 0:
            U["U1"] = 0
        self.task = self.task.append(U)

    def getUtilisation(self, l):
        return self.execution_time.loc[l, "U"]

    def getWorstC(self):
        return self.execution_time["C"].min()

    def __repr__(self):
        return str(self.task)

    def generateJobForItv(self, itv):
        nb = 0
        while itv >= 0:
            itv -= self.T
            nb += 1
        return nb

    def __hash__(self):
        return hash(self.task)

    def __eq__(self, other):
        return self.get_settings() == other.get_settings()
