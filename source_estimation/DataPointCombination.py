'''
測定点の組み合わせを作るクラス
'''
import itertools

class DataPointCombination:

    l = ["A", "B", "C", "D", "E"]
    c = itertools.combinations(l, 2)
 
    '''
    コンビネーションを計算する．
    '''
    def calcComb(self):
        comb_len = 0
        for i in range(1, 5):
            for v in itertools.combinations(self.l, i):
                print(v)
            comb_len += len(list(itertools.combinations(self.l, i)))
        print(comb_len)

DPComb = DataPointCombination()
DPComb.calcComb()
