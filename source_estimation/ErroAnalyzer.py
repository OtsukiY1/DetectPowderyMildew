class ErrorAnalyzer:
    """
    推定誤差データの集計・統計分析および結果の表示を行うクラス。
    """
    def __init__(self, days, combinations, error_list):
        self.days = days
        self.combinations = combinations
        self.error_list = error_list
        self.comb_names = ["-".join(comb) for comb in combinations]

    def calculate_averages(self):
        """組み合わせごとに誤差の平均値を計算して返す (Noneは除外)"""
        averages = []
        for col_idx in range(len(self.combinations)):
            valid_errors = [
                self.error_list[row_idx][col_idx] 
                for row_idx in range(len(self.days)) 
                if self.error_list[row_idx][col_idx] is not None
            ]
            avg = sum(valid_errors) / len(valid_errors) if valid_errors else None
            averages.append(avg)
        return averages

    def calculate_variances(self):
        """組み合わせごとに誤差の分散値を計算して返す (Noneは除外)"""
        variances = []
        averages = self.calculate_averages()
        for col_idx, avg in enumerate(averages):
            if avg is None:
                variances.append(None)
                continue
            valid_errors = [
                self.error_list[row_idx][col_idx] 
                for row_idx in range(len(self.days)) 
                if self.error_list[row_idx][col_idx] is not None
            ]
            if valid_errors:
                # 標本分散の計算
                var = sum((x - avg) ** 2 for x in valid_errors) / len(valid_errors)
                variances.append(var)
            else:
                variances.append(None)
        return variances
  
    def calculate_standard_deviations(self):
        """組み合わせごとに誤差の標準偏差を計算して返す (Noneは除外)"""
        variances = self.calculate_variances()
        std_devs = []
        for var in variances:
            if var is None:
                std_devs.append(None)
            else:
                std_devs.append(var ** 0.5)
        return std_devs

    def calculate_percentiles(self, percentile=90):
        """組み合わせごとに指定されたパーセンタイル（誤差半径）を計算して返す (Noneは除外)"""
        percentiles = []
        for col_idx in range(len(self.combinations)):
            valid_errors = [
                self.error_list[row_idx][col_idx] 
                for row_idx in range(len(self.days)) 
                if self.error_list[row_idx][col_idx] is not None
            ]
            
            if not valid_errors:
                percentiles.append(None)
                continue
                
            sorted_errors = sorted(valid_errors)
            n = len(sorted_errors)
            
            if n == 1:
                percentiles.append(sorted_errors[0])
                continue
                
            p = percentile / 100.0
            idx = p * (n - 1)
            k = int(idx)
            d = idx - k
            
            if k >= n - 1:
                val = sorted_errors[-1]
            else:
                val = sorted_errors[k] + d * (sorted_errors[k+1] - sorted_errors[k])
            percentiles.append(val)
            
        return percentiles

    def print_table(self):
        """日付ごとの誤差、平均誤差、誤差の分散、標準偏差、および90%誤差半径を表形式で出力する"""
        print("\n=== Error Table (Row: Day, Column: Combination) ===")
        
        # ヘッダーの出力
        header = f"{'Date':<12} | " + " | ".join([f"{name:^8}" for name in self.comb_names])
        print(header)
        print("-" * len(header))
        
        # 日ごとのデータ行を出力
        for i, day in enumerate(self.days):
            row_errors = self.error_list[i]
            formatted_row = [f"{'N/A':^8}" if err is None else f"{err:^8.3f}" for err in row_errors]
            print(f"{day:<12} | " + " | ".join(formatted_row))
            
        print("-" * len(header))
        
        # 平均値行の出力
        averages = self.calculate_averages()
        formatted_avg = [f"{'N/A':^8}" if avg is None else f"{avg:^8.3f}" for avg in averages]
        print(f"{'Average':<12} | " + " | ".join(formatted_avg))
        
        # 分散行の出力
        variances = self.calculate_variances()
        formatted_var = [f"{'N/A':^8}" if var is None else f"{var:^8.3f}" for var in variances]
        print(f"{'Variance':<12} | " + " | ".join(formatted_var))

        # 標準偏差行の出力
        std_devs = self.calculate_standard_deviations()
        formatted_std = [f"{'N/A':^8}" if std is None else f"{std:^8.3f}" for std in std_devs]
        print(f"{'Std Dev':<12} | " + " | ".join(formatted_std))

        # 90%誤差半径行の出力
        percentiles = self.calculate_percentiles(90)
        formatted_pct = [f"{'N/A':^8}" if val is None else f"{val:^8.3f}" for val in percentiles]
        print(f"{'90% Radius':<12} | " + " | ".join(formatted_pct))

        # 50%誤差半径行の出力
        percentiles = self.calculate_percentiles(50)
        formatted_pct = [f"{'N/A':^8}" if val is None else f"{val:^8.3f}" for val in percentiles]
        print(f"{'50% Radius':<12} | " + " | ".join(formatted_pct)) 
        # 書式指定子について．:以降が書式指定子．^ は中央寄せ，8は出力する全体の文字数. .3は小数点以下3桁(四捨五入される)．fはfloat型にするという指示．
        #このif文はvalがNoneだったらN/Aと書くということ．三項演算子という.　
        #　A if 条件 else B でもし条件が成り立つならA, そうでなければBという意味．
