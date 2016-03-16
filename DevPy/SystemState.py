



class SystemState:
    def __init__(self, at, rct, crit, hashInfo):
        self.at = at
        self.rct = rct
        self.crit = crit
        self.hashInfo = hashInfo

    def getActive(self):
        res = []
        for i in range(len(self.at)):
            if self.at[i] < 0 or (self.at[i] == 0 and self.rct[i] > 0):
                res.append(i)
        return res

    def getCrit(self):
        for it in self.getActive():
            if self.rct[it] == 0:
                return self.crit+1
        return self.crit

    def getLaxity(self, D):
        laxity = []
        for i in range(len(self.at)):
           laxity.append(self.at[i]-self.rct[i]+D[i])
        return laxity

    def isFail(self, D):
        laxity = self.getLaxity(D)
        for t in laxity:
            if t < 0:
                return True
        return False

    def getImplicitelyDone(self, X):
        res = []
        for i in self.getActive():
            if self.rct[i] == 0 and self.crit == X[i]:
                res.append(i)
        return res

    def getExecutionTransition(self, run, X):
        critP = self.crit
        rctP = list(self.rct)
        for i in run:
            rctP[i]-=1
        atP = list(self.at)
        for i in range(len(self.at)):
            if X[i] >= self.crit:
                atP[i] -= 1
            else:
                #useless
                atP[i] = 0


        return SystemState(atP, rctP, critP, self.hashInfo)

    def getTerminationTransition(self, toTerminate, X, C, T):
        critP = self.crit
        toTerminate = toTerminate.union(self.getImplicitelyDone(X))
        rctP = list(self.rct)
        atP = list(self.at)
        for i in toTerminate:
            rctP[i] = C[i][self.crit-1]
            atP[i] += T[i]
        return SystemState(atP, rctP, critP, self.hashInfo)

    def getCriticalTransition(self, X, C):
        critP = self.getCrit()
        rctP = list(self.rct)
        atP = list(self.at)
        for i in range(len(self.at)):
            if X[i] >= self.getCrit():
                rctP[i] += C[i][self.getCrit()-1]-C[i][self.crit-1]
            else:
                rctP[i] = 0
                atP[i] = 0
        return SystemState(atP, rctP, critP, self.hashInfo)


    def __repr__(self):
        return("at :"+str(self.at)+"\n rct :"+str(self.rct)+"\n crit :"+str(self.crit))

    def __eq__(self, other):
        return (self.at == other.at and self.rct == other.rct and self.crit == other.crit)

    def __hash__(self):
        #hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        #-D-1 <= at <= T
        #0 <= at+D+1 <= T+D+1
        #0 <= rct <= Cmax
        #1 <= crit <= K
        h = 0

        h = self.crit
        factor = K
        for i in range(len(self.at)):
            h += self.rct[i]*factor
            factor*=Cmax[i]
            h += (self.at[i]+D[i]+1)*factor
            factor*=(T[i]+D[i]+1)
        return h


