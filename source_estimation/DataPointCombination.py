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

    def get_combinations(self):
        '''
        センサーIDのすべての組み合わせ（1個から5個まで）のリストを返す．
        '''
        combinations = []
        for i in range(1, len(self.l) + 1):
            for v in itertools.combinations(self.l, i):
                combinations.append(v)
        return combinations

if __name__ == "__main__":
    DPComb = DataPointCombination()
    DPComb.calcComb()
