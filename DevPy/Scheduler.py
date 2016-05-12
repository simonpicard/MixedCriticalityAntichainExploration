
EDFVD = 0
LWLF = 1

class Scheduler:
    def __init__(self, taskSet, sched=EDFVD):
        self.taskSet = taskSet
        self.sched = sched

        if self.getUtilisation(1,1) + self.getUtilisation(2,2) <= 1:
            self.relativity = 1
        else:
            self.relativity = self.getRelativity()


    def run(self, systemState):
        if self.sched == EDFVD :
            return self.EDFVD(systemState)
        elif self.sched == LWLF:
            return self.LWLF(systemState)

    def getUtilisation(self, K, l):
        ut = 0.0
        for i in range(self.taskSet.getSize()):
            if self.taskSet.getTask(i).X == K:
                ut += self.taskSet.getTask(i).getUtilisation(l)
        return ut

    def getRelativity(self):
        relativity = (self.getUtilisation(2,1)/(1-self.getUtilisation(1,1)))
        return relativity


    def EDFVD(self, systemState):
        return self.EDF(systemState, self.relativity)


    def EDF(self, systemState, relativity=1):
        active = systemState.getActive()
        toRun = None
        minDL = 9999999999
        for it in active:
            if self.taskSet.getX()[it] == 2:
                deadline = systemState.getRelativeDeadline(self.taskSet.getTask(it).D*relativity, self.taskSet.getTask(it).T, it)
            else: 
                deadline = systemState.getRelativeDeadline(self.taskSet.getTask(it).D, self.taskSet.getTask(it).T, it)
            if deadline < minDL:
                minDL = deadline
                toRun = it
        if toRun == None:
            return []
        else:
            return [toRun]

    def LWLF(self, systemState):
        active = systemState.getActive()
        if len(active) == 0:
            return []

        WL = systemState.getWorstLaxity(self.taskSet.getC())
        activeWL = [WL[i] for i in active]
        LWL = min(activeWL)

        return [active[activeWL.index(LWL)]]


