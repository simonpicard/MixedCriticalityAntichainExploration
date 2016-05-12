from Task import *


class TaskSet:
    def __init__(self, tasks=[]):
        self.tasks = tasks

    def addTask(self, task):
        self.tasks.append(task)

    def clear(self):
        self.tasks = list()

    def getMaxO(self):
        res = 0
        for task in self.tasks:
            if task.O > res:
                res = task.O
        return res

    def getMaxT(self):
        res = 0
        for task in self.tasks:
            if task.T > res:
                res = task.T
        return res

    def getMaxC(self):
        res = 0
        for task in self.tasks:
            currentMax =  max(task.C)
            if currentMax > res:
                res = currentMax
        return res

    def getK(self):
        res = 0
        for task in self.tasks:
            if task.X > res:
                res = task.X
        return res

    def getSize(self):
        return len(self.tasks)

    def getTask(self, i):
        return self.tasks[i]

    def getT(self):
        res = []
        for t in self.tasks:
            res.append(t.T)
        return res

    def getO(self):
        res = []
        for t in self.tasks:
            res.append(t.O)
        return res

    def getD(self):
        res = []
        for t in self.tasks:
            res.append(t.D)
        return res

    def getX(self):
        res = []
        for t in self.tasks:
            res.append(t.X)
        return res

    def getC(self):
        res = []
        for t in self.tasks:
            res.append(t.C)
        return res

    def getMaxCs(self):
        res = []
        for task in self.tasks:
            res.append(max(task.C))
        return res


    def getUtilisationOfLevelAtLevel(self, K, l):
        ut = 0.0
        for i in range(self.getSize()):
            if self.getTask(i).X == K:
                ut += self.getTask(i).getUtilisation(l)
        return ut

    def getUtilisationOfLevel(self, K):
        ut = 0.0
        for i in range(self.getSize()):
            if self.getTask(i).X >= K:
                ut += self.getTask(i).getUtilisation(K)
        return ut

    def getAverageUtilisation(self):
        if self.getSize() == 0:
            return 0
        res = 0.0
        for i in range(1,self.getK()+1):
            res += self.getUtilisationOfLevel(i)
        return res/self.getK()

    def __repr__(self):
        return "TaskSet("+str(self.tasks)+")"

    def __getitem__(self,index):
        return self.getTask(index)

    def __hash__(self):
        return hash(tuple(self.tasks))

    def copy(self):
        return TaskSet(self.tasks)

    def __eq__(self, other):
        return self.tasks == other.tasks

