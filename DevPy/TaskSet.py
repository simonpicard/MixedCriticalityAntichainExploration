from Task import *


class TaskSet:
    def __init__(self, tasks=[]):
        self.tasks = tasks

    def addTask(self, task):
        self.tasks.append(task)

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