from itertools import combinations
import random

data = range(1,40) 
lottery_count = 5 
exclude_numbers = [32, 38, 7, 11, 12, 14, 15, 17, 30,1, 22, 25, 26, 33,2, 4, 16, 19, 26,2, 3, 8, 10, 18,4, 6, 23, 27, 34]  #要排除的數字列表
data = [num for num in data if num not in exclude_numbers]      # 排除指定數字後的列表
print(f"排除後的資料: {data}")
print(f"資料總數: {len(data)}")

combos = list(combinations(data, lottery_count))  # 產生所有可能的組合
print(f"總組數: {len(combos)}")

hot_numbers = []  #熱門號碼列表
qty = 2  #要預測抽出的組數
if len(hot_numbers) > 0 and all(hot in data for hot in hot_numbers):

    print(f"熱門號碼: {hot_numbers}")
    sampled = []  #儲存篩選後的組合列表
    for combo in combos:
        if all(hot in combo for hot in hot_numbers):
            sampled.append(combo)  # 篩選出包含所有熱門號碼的組合
                
    print(f"包含熱門號碼的組數: {len(sampled)}")   
    
    sampled = random.sample(sampled, qty) #從篩選後的組合中隨機抽取指定數量的組合
    
else:
    sampled = random.sample(combos, qty)  #隨機抽取指定數量的組合

print(f"隨機抽出的 {qty} 個組合：")
for s in sampled:
    print(s)