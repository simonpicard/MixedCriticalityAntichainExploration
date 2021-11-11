from functools import reduce

from Scheduler import *


IDLE = 0
IDLEandWC = 1
WC = 2
NONE = 3
LAX = 4
WCnat = 5
WCnatRun = 5


class SystemState:
    def __init__(self, nat, rct, done, crit, sim, hashInfo, scheduler=0):
        self.nat = nat
        self.rct = rct
        self.done = done
        self.crit = crit
        self.hashInfo = hashInfo
        self.size = len(nat)
        self.SIM = sim
        self.scheduler = scheduler

    def setSched(self, run):
        self.run = run
        self.runned = [(i in run) for i in range(self.size)]
        self.hashrun = 0
        for i in range(len(self.runned)):
            self.hashrun += self.runned[i] * (2 ** i)

    def getRun(self):
        return self.run

    def getActive(self):
        res = []
        for i in range(len(self.nat)):
            if not self.done[i]:
                res.append(i)
        return res

    def getCrit(self):
        for it in self.getActive():
            if self.rct[it] == 0:
                return self.crit + 1
        return self.crit

    def getLaxity(self):
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        laxity = []
        for i in range(len(self.nat)):
            laxity.append(self.nat[i] - self.rct[i] + D[i] - T[i])
        return laxity

    def getWorstLaxity(self, C):
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        laxity = []

        for i in range(len(self.nat)):
            laxity.append(
                self.nat[i]
                - (self.rct[i] + (C[i][-1] - C[i][self.crit - 1]) * (not self.done[i]))
                + D[i]
                - T[i]
            )
        return laxity

    def isFail(self, C):
        laxity = self.getWorstLaxity(C)
        for t in laxity:
            if t < 0:
                return True
        return False

    def getImplicitelyDone(self, X, C):
        res = []
        for i in self.getActive():
            #            if self.rct[i] == 0 and self.crit == X[i]:
            if self.rct[i] == 0 and C[i][self.crit - 1] == C[i][-1]:
                res.append(i)
        return res

    def getEligible(self, X):
        res = []
        for i in range(len(self.nat)):
            if self.crit <= X[i] and self.done[i] and self.nat[i] <= 0:
                res.append(i)
        return res

    def getExecutionTransition(self, run, X):
        critP = self.crit
        doneP = list(self.done)
        rctP = list(self.rct)
        natP = list(self.nat)

        for i in run:
            rctP[i] -= 1
        for i in range(len(self.nat)):
            if not self.done[i]:
                natP[i] -= 1
            else:
                natP[i] = max(0, self.nat[i] - 1)

        return SystemState(
            natP, rctP, doneP, critP, self.SIM, self.hashInfo, self.scheduler
        )

    def getTerminationTransition(self, toTerminate, X, C):
        T = self.hashInfo[1]
        critP = self.crit
        toTerminate = toTerminate.union(self.getImplicitelyDone(X, C))
        rctP = list(self.rct)
        natP = list(self.nat)
        doneP = list(self.done)
        for i in toTerminate:
            rctP[i] = 0
            doneP[i] = True
        return SystemState(
            natP, rctP, doneP, critP, self.SIM, self.hashInfo, self.scheduler
        )

    def getCriticalTransition(self, X, C):
        critP = self.getCrit()
        rctP = list(self.rct)
        natP = list(self.nat)
        doneP = list(self.done)

        for i in range(len(self.nat)):
            if X[i] >= self.getCrit():
                if not self.done[i]:
                    rctP[i] += C[i][self.getCrit() - 1] - C[i][self.crit - 1]
            else:
                rctP[i] = 0
                natP[i] = 0
                doneP[i] = True
        return SystemState(
            natP, rctP, doneP, critP, self.SIM, self.hashInfo, self.scheduler
        )

    def getRequestTransition(self, request, C):
        T = self.hashInfo[1]
        res = []
        critP = self.getCrit()
        rctP = list(self.rct)
        natP = list(self.nat)
        doneP = list(self.done)
        for it in request:
            rctP[it] = C[it][self.crit - 1]
            doneP[it] = False
        size = []
        toCombinate = []
        nbCombinaison = 1
        for it in request:
            toCombinate.append(range(natP[it] + T[it], T[it] + 1))
            size.append(len(toCombinate[-1]))
            nbCombinaison *= size[-1]
        for i in range(nbCombinaison):
            for j in range(len(request)):
                div = 1
                for k in range(j + 1, len(request)):
                    div *= size[k]
                mod = size[j]
                natP[request[j]] = toCombinate[j][(i // div) % mod]
            res.append(
                SystemState(
                    list(natP),
                    list(rctP),
                    list(doneP),
                    critP,
                    self.SIM,
                    self.hashInfo,
                    self.scheduler,
                )
            )
        return res

    def getRelativeDeadline(self, D, T, i):
        return self.nat[i] - T + D

    def isSimulation(self, ss):
        if self.SIM == IDLE:
            return self.isIdleSimulation(ss)
        elif self.SIM == IDLEandWC:
            return self.isIdleWCSimulation(ss)
        elif self.SIM == NONE:
            return (
                self.nat == ss.nat
                and self.rct == ss.rct
                and self.crit == ss.crit
                and self.done == ss.done
            )

    def isIdleSimulation(self, ss):
        fullRes = map(
            int.__le__, self.getRelevantAttributeIdle(), ss.getRelevantAttributeIdle()
        )
        res = reduce(bool.__and__, fullRes, True)
        return res

    def isIdleWCSimulation(self, ss):
        resIdle = map(
            int.__le__, self.getRelevantAttributeIdle(), ss.getRelevantAttributeIdle()
        )
        resWC1 = map(
            int.__ge__, self.getRelevantAttributeWC(), ss.getRelevantAttributeWC()
        )
        resWC21 = map(int.__eq__, ss.getRelevantAttributeWC(), ss.size * [0])
        resWC22 = map(int.__eq__, self.getRelevantAttributeWC(), self.size * [0])
        resWC2 = map(bool.__eq__, resWC21, resWC22)
        res = reduce(bool.__and__, list(resIdle) + list(resWC1) + list(resWC2), True)
        return res

    def getRelevantAttributeIdle(self):
        return tuple(self.nat[i] for i in range(len(self.nat)) if self.done[i])

    def getRelevantAttributeWCnat(self):
        return tuple(self.nat[i] for i in range(len(self.nat)) if not self.done[i])

    def getRelevantAttributeWCnatRun(self):
        return tuple(self.nat[i] for i in range(len(self.nat)) if self.runned[i])

    def getRelevantAttributeWC(self):
        return tuple(
            self.rct[i]
            for i in range(len(self.rct))
            if ((not self.done[i]) and self.rct[i] > 0)
        )

    def getRelevantAttributeIdleWC(self):
        return (
            tuple(self.nat[i] for i in range(len(self.nat)) if self.done[i]),
            tuple(
                self.rct[i]
                for i in range(len(self.rct))
                if ((not self.done[i]) and self.rct[i] > 0)
            ),
        )

    def __repr__(self):
        # return("SS#"+str(hash(self))+"\n nat :"+str(self.nat)+"\n rct :"+str(self.rct)+"\n done :"+str(bool(self.done))+"\n crit :"+str(self.crit))
        return (
            "\n"
            + str(self.nat)
            + ", "
            + str(self.rct)
            + ", "
            + str(list(map(bool, self.done)))
            + ", "
            + str(self.crit)
        )

    def __eq__(self, other):
        # return (self.nat == other.nat and self.rct == other.rct and self.crit == other.crit and self.done == self.done)
        return self.isSimulation(other)

    def __hash__(self):
        if self.SIM == IDLE:
            return self.hashIdle()
        elif self.SIM == IDLEandWC:
            return self.hashIdleWC()
        elif self.SIM == WC:
            return self.hashWC()
        elif self.SIM == NONE:
            return self.hashNONE()
        elif self.SIM == LAX:
            return self.hashLAX()
        elif self.SIM == WCnat:
            return self.hashWCnatRun()

    def hashIdle(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1
        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):
            h += (Cmax[i] - self.rct[i]) * factor
            factor *= Cmax[i] + 1
            h += ((self.done[i] + 1) % 2) * (self.nat[i] + D[i] + 1 - T[i]) * factor
            h += 0 * factor
            factor *= (D[i] + 1) + 1
            h += int(self.done[i]) * factor
            factor *= 2
        return h

    def hashIdleWC(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1
        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):
            h += (self.done[i] or self.rct[i] == 0) * (Cmax[i] - self.rct[i]) * factor
            factor *= Cmax[i] + 1
            h += ((self.done[i] + 1) % 2) * (self.nat[i] + D[i] + 1 - T[i]) * factor
            factor *= (D[i] + 1) + 1
            h += int(self.done[i]) * factor
            factor *= 2
        return h

    def hashWC(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1
        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):
            h += (self.done[i] or self.rct[i] == 0) * (Cmax[i] - self.rct[i]) * factor
            factor *= Cmax[i] + 1
            h += (self.nat[i] + D[i] + 1 - T[i]) * factor
            factor *= (D[i] + 1) + 1
            h += int(self.done[i]) * factor
            factor *= 2
        return h

    def hashNONE(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1
        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):
            h += (Cmax[i] - self.rct[i]) * factor
            factor *= Cmax[i] + 1
            h += (self.nat[i] + D[i] + 1 - T[i]) * factor
            factor *= (D[i] + 1) + 1
            h += int(self.done[i]) * factor
            factor *= 2
        return h

    def hashLAX(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1

        # -1 <= lax <= T
        # 0 <= lax +1 <= T+1

        lax = self.getLaxity()
        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):

            h += (lax[i] + 1) * factor
            factor *= T[i] + 1

            h += (self.rct[i] == 0) * factor
            factor *= 2

            h += int(self.done[i]) * factor
            factor *= 2
        return h

    def hashWCnatRun(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1

        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):
            h += (Cmax[i] - self.rct[i]) * factor
            factor *= Cmax[i] + 1

            h += (not self.runned[i]) * (self.nat[i] + D[i] + 1 - T[i]) * factor

            factor *= (D[i] + 1) + 1
            h += int(self.done[i]) * factor
            factor *= 2

        return h

    def hashWCnat(self):
        # hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        # T-(D+1) <= nat <= T
        # 0 <= nat+D+1-T <= D+1
        # 0 <= rct <= Cmax
        # 1 <= crit <= K
        # 0 <= crit-1 <= K-1
        # 0 <= done <= 1
        h = 0

        h = self.crit - 1
        factor = K - 1 + 1
        for i in range(len(self.nat)):
            h += (Cmax[i] - self.rct[i]) * factor
            factor *= Cmax[i] + 1
            h += ((self.done[i]) % 2) * (self.nat[i] + D[i] + 1 - T[i]) * factor
            h += 0 * factor
            factor *= (D[i] + 1) + 1
            h += int(self.done[i]) * factor
            factor *= 2
        return h
