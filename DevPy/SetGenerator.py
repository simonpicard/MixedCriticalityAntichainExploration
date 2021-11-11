import Task
import TaskSet
from random import uniform
from random import random
from random import expovariate
from functools import reduce


class SetGenerator:
    def __init__(self, pHI, rHI, CmaxLO, Tmax, U, nbT=0):
        self.pHI = pHI
        self.rHI = rHI
        self.CmaxLO = CmaxLO
        self.Tmax = Tmax
        self.U = U
        self.nbT = nbT

    def generateTaskUniform(self):
        C = [0, 0]
        C[0] = max(1, round(uniform(1, self.CmaxLO)))

        T = round(uniform(C[0], self.Tmax))

        D = T
        X = int((random() <= self.pHI))

        if X == 0:
            C[1] = C[0]
        else:
            C[1] = round(uniform(C[0], min(self.rHI * C[0], D)))
        O = 0
        return Task.Task(O, T, D, X, C)

    def generateTaskExponential(self):
        T = round(uniform(1, self.Tmax))
        D = T
        X = int((random() <= self.pHI))
        C = [0, 0]
        while C[0] == 0:
            expo = expovariate(1.0 / (T * 0.35))
            C[0] = round(expo)
            # print(expo, C[0])
        if X == 0:
            C[1] = C[0]
        else:
            C[1] = round(uniform(C[0], min(self.rHI * C[0], T)))
        O = 0
        return Task.Task(O, T, D, X, C)

    def generateSetU(self):
        ts = TaskSet.TaskSet()
        done = False
        while not done:
            ts.clear()
            sizeOk = True
            while ts.getAverageUtilisation() < self.U - 0.005:
                ts.addTask(self.generateTaskUniform())
                if ts.getSize() > self.nbT and self.nbT > 0 and ts.getSize() > 0:
                    sizeOk = False
                    break

            if self.nbT > 0 and not sizeOk:
                pass
            elif ts.getAverageUtilisation() > self.U + 0.005:
                # print(ts.getAverageUtilisation())
                pass
            elif ts.getUtilisationOfLevel(0) > 1:
                pass
            elif ts.getUtilisationOfLevel(1) > 1:
                pass
            elif (ts.tasks["X"] == ts.tasks.loc[0, "X"]).all():
                pass
            else:
                done = True
        return ts

    def generateSetPerformance(self, nbTask):
        ts = TaskSet.TaskSet()
        done = False
        while not done:
            ts.clear()
            for i in range(nbTask):
                ts.addTask(self.generateTaskExponential())
            if ts.getAverageUtilisation() > 1:
                pass  # print("ug " + str(ts.getAverageUtilisation()))
            elif ts.getUtilisationOfLevel(0) > 1:
                pass  # print("u1 " + str(ts.getUtilisationOfLevel(1)))
            elif ts.getUtilisationOfLevel(1) > 1:
                pass  # print("u2 " + str(ts.getUtilisationOfLevel(2)))
            elif nbTask != 1 and (ts.tasks["X"] == ts.tasks.loc[0, "X"]).all():
                pass  # print("alleq")
            else:
                done = True
        return ts
