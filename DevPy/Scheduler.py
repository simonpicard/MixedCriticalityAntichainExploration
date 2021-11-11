EDFVD = 0
LWLF = 1


class Scheduler:
    def __init__(self, taskSet, sched=EDFVD):
        self.ts = taskSet
        self.sched = sched

        if self.getUtilisation(0, 0) + self.getUtilisation(1, 1) <= 1:
            self.relativity = 1
        else:
            self.relativity = self.getRelativity()

    def run(self, systemState):
        if self.sched == EDFVD:
            return self.EDFVD(systemState)
        elif self.sched == LWLF:
            return self.LWLF(systemState)

    def getUtilisation(self, K, l):
        return self.ts.getUtilisationOfLevelAtLevel(K, l)

    def getRelativity(self):
        relativity = self.getUtilisation(1, 0) / (
            1 - self.getUtilisation(0, 0)
        )
        return relativity

    def EDFVD(self, systemState):
        return self.EDF(systemState, self.relativity)

    def EDF(self, systemState, relativity=1):
        active = systemState.getActive()
        toRun = None
        minDL = 9999999999
        for i in active:
            if self.ts.tasks.loc[i, "X"] == 1:
                deadline = systemState.getRelativeDeadline(i, relativity)
            else:
                deadline = systemState.getRelativeDeadline(i)
            if deadline < minDL:
                minDL = deadline
                toRun = i
        if toRun == None:
            return []
        else:
            return [toRun]

    def LWLF(self, systemState):
        active = systemState.getActive()
        if len(active) == 0:
            return []

        WL = systemState.getWorstLaxity(self.ts.getC())
        activeWL = [WL[i] for i in active]
        LWL = min(activeWL)

        return [active[activeWL.index(LWL)]]
