import Scheduler
from itertools import *
import PeriodicSystemState


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


EDFVD = 0
LWLF = 1


class PeriodicGraph:
    def __init__(self, ts, sched=EDFVD):
        self.ts = ts
        self.maxO = ts.tasks["O"].max()
        self.maxT = ts.tasks["T"].max()
        self.K = ts.tasks["X"].max()
        self.maxC = ts.tasks[self.K].max()
        self.size = ts.getSize()
        self.nbVisited = 0
        self.nbInterVisited = 0
        self.scheduler = Scheduler.Scheduler(ts, sched)
        self.visited = set()

    def getInitialVertex(self):
        ss0 = self.ts.tasks[["O", 0]].rename(columns={0: "rct", "O": "at"})
        crit0 = 0
        return PeriodicSystemState.SystemState(ss0, crit0, self.ts.tasks)

    def isStateOK(self, ss):
        if ss.crit < 0 or ss.crit > self.K:
            print(ss.crit)
            print("crit")
            return False

        for i in range(self.size):
            if ss.ss.rct[i] < 0 or ss.ss.rct[i] > self.ts.tasks.loc[i, self.K]:
                print(ss.rct[i], i)
                print("rct")
                return False
            if ss.at[i] > self.ts.tasks.loc[i, "T"]:
                print(ss.at[i], i)
                print("at")
                return False
        """for t in ss.getLaxity(self.ts.getD):
            if t < -1:
                return False"""
        return True

    def getNeighbour(self, ss):
        neighbours = []
        run = self.scheduler.run(ss)
        ssP = ss.getExecutionTransition(run)

        self.nbInterVisited += 1

        ssPPs = []
        for combination in powerset(run):
            current = ssP.getTerminationTransition(set(combination))
            ssPPs.append(current)
            self.nbInterVisited += 1

        for ssPP in ssPPs:
            ssPPP = ssPP.getCriticalTransition()
            neighbours.append(ssPPP)
            self.nbInterVisited += 1

        return neighbours

    def bfs(self):
        queue = [self.getInitialVertex()]
        m_v_nodes = queue[0].compute_max_nodes()
        visited = set()

        at = set()
        rct = set()
        for i in tqdm(range(m_v_nodes)):
            # while queue:
            vertex = queue.pop(0)

            at.add(vertex.ss.loc[0, "at"])
            rct.add(vertex.ss.loc[0, "rct"])

            if not vertex in visited:
                visited.add(vertex)
                self.nbVisited += 1
                if vertex.isFail():
                    # print(vertex)
                    # print("FAIL")
                    # print(at, rct)
                    return (
                        False,
                        self.nbInterVisited,
                        self.nbVisited,
                        self.nbVisited,
                        self.nbVisited,
                    )
                queue.extend(set(self.getNeighbour(vertex)))

            if len(queue) == 0:
                break

        # print(at, rct)

        return (
            True,
            self.nbInterVisited,
            self.nbVisited,
            self.nbVisited,
            self.nbVisited,
        )
