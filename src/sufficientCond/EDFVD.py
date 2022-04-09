class EDFVD:
    def __init__(self, ts):
        self.ts = ts

    def test(self):
        res = self.ts.getUtilisationOfLevelAtLevel(0, 0)
        if self.ts.getUtilisationOfLevelAtLevel(1, 1) < 1:
            res += min(
                self.ts.getUtilisationOfLevelAtLevel(1, 1),
                self.ts.getUtilisationOfLevelAtLevel(1, 0)
                / (1 - self.ts.getUtilisationOfLevelAtLevel(1, 1)),
            )
        else:
            res += self.ts.getUtilisationOfLevelAtLevel(1, 1)
        return res <= 1


"""
ts = TaskSet([Task(0, 4,5, 1, [2,2]), Task(0, 6, 7, 2, [1,2]), Task(0, 6, 6, 2, [2,4])] )
o = EDFVD(ts)
print(o.test())"""
