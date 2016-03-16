


class Scheduler:
    def __init__(self, taskSet):
        self.taskSet = taskSet


    def run(self, systemState):
        return self.EDFVD(systemState)

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
        if self.getUtilisation(1,1) + self.getUtilisation(2,2) <= 1:
            relativity = 1
        else:
            relativity = self.getRelativity()
        return self.EDF(systemState, relativity)


    def EDF(self, systemState, relativity=1):
        active = systemState.getActive()
        toRun = None
        minDL = 9999999999
        for it in active:
            if self.taskSet.getX()[it] == 2:
                deadline = systemState.at[it] + self.taskSet.getTask(it).D*relativity
            else: 
                deadline = systemState.at[it] + self.taskSet.getTask(it).D
            if deadline < minDL:
                minDL = deadline
                toRun = it
        if toRun == None:
            return []
        else:
            return [toRun]


