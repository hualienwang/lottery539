#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析台彩539號碼機率並產生組合
"""

import json
import random
from datetime import datetime
from collections import Counter

# 讀取資料
with open('lotto539_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

draws = data['draws']

# 篩選2026年2月2日到2026年3月10日的資料（標準化日期格式）
def normalize_date(date_str):
    """標準化日期格式為 YYYY-MM-DD"""
    parts = date_str.split('-')
    if len(parts) == 3:
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    return date_str

start_date = "2026-02-02"
end_date = "2026-03-10"

filtered_draws = []
for d in draws:
    norm_date = normalize_date(d['date'])
    if start_date <= norm_date <= end_date:
        filtered_draws.append({
            'date': norm_date,  # 使用標準化後的日期
            'numbers': d['numbers'],
            'added_time': d.get('added_time', '')
        })

print(f"總開獎期數: {len(filtered_draws)}期")
# print(f"篩選後的日期範圍: {filtered_draws[0]['date']} ~ {filtered_draws[-1]['date']}")

# 取前20期進行分析
analysis_draws = filtered_draws[-20:]
print(f"\n分析前20期: {analysis_draws[-20]['date']} ~ {analysis_draws[-1]['date']}")

# 統計每個號碼出現次數
all_nums = []
for draw in analysis_draws:
    all_nums.extend(draw['numbers'])

counter = Counter(all_nums)

# 計算平均值
total_numbers = len(all_nums)  # 25期 * 5個號碼 = 125
unique_numbers = len(counter)  # 出現過的號碼數量
avg_frequency = total_numbers / 39  # 39個號碼的平均出現次數

print(f"\n=== 前20期號碼分析 ===")
print(f"總開出號碼數: {total_numbers}")
print(f"平均出現次數 (平均值): {avg_frequency:.2f}")

# 橫向顯示所有號碼的出現次數
print(f"\n號碼出現次數 (熱門>= 2):")
hot_row = []
cold_row = []
for num in range(1, 40):
    count = counter.get(num, 0)
    status = "熱門" if count >= 2 else "冷門"
    if count >= 2:
        hot_row.append(f"{num}({count})")
    else:
        cold_row.append(f"{num}({count})")

print(f"  熱門: {' '.join(hot_row)}")
print(f"  冷門: {' '.join(cold_row)}")

#區分熱門牌與冷門牌
hot_numbers = [num for num in range(1, 40) if counter.get(num, 0) >= 2]
cold_numbers = [num for num in range(1, 40) if counter.get(num, 0) == 1]

print(f"\n熱門號碼 (>= 2): {sorted(hot_numbers)}")
print(f"冷門號碼 (== 1): {sorted(cold_numbers)}")

# 用戶指定的號碼
user_numbers = [2, 7, 8, 9, 10, 13, 16, 21, 22, 23, 25, 27, 29, 31, 34, 35, 36, 39]

# 區分用戶指定號碼中的熱門牌與冷門牌
user_hot = []
user_cold = []

print(f"\n=== 用戶指定號碼分析 ===")
print(f"指定號碼數: {len(user_numbers)}")
print(f"用戶號碼: {user_numbers}")

for num in user_numbers:
    count = counter.get(num, 0)
    if count >= 2:
        user_hot.append(num)
        print(f"  {num}: {count}次 [熱門]")
    else:
        user_cold.append(num)
        print(f"  {num}: {count}次 [冷門]")

print(f"\n用戶熱門牌: {sorted(user_hot)}")
print(f"用戶冷門牌: {sorted(user_cold)}")

# 使用熱門權重3產生2組牌
# 策略：從用戶的熱門牌和冷門牌中選擇
hot_weight = 3

# 產生組合
random.seed()  # 固定隨機種子以便重現

def generate_combination(hot_list, cold_list, hot_weight, exclude=None):
    """產生一組號碼"""
    exclude = exclude or []
    
    # 合併候選號碼
    all_candidates = []
    weights = []
    
    for num in user_numbers:
        if num not in exclude:
            all_candidates.append(num)
            if num in hot_list:
                weights.append(hot_weight)
            else:
                weights.append(1)
    
    if len(all_candidates) < 5:
        return None
    
    # 隨機選擇5個號碼（加權）
    selected = random.choices(all_candidates, weights=weights, k=5)
    
    # 確保不重複
    while len(set(selected)) < 5:
        selected = random.choices(all_candidates, weights=weights, k=5)
    
    return sorted(set(selected))

# 產生2組牌
combinations = []
attempts = 0

while len(combinations) < 2 and attempts < 100:
    attempts += 1
    combo = generate_combination(user_hot, user_cold, hot_weight)
    
    # 避免重複
    if combo and combo not in combinations:
        # 確保湊滿5個號碼
        while len(combo) < 5:
            additional = generate_combination(user_hot, user_cold, hot_weight, exclude=combo)
            if additional:
                combo = sorted(set(combo + additional))[:5]
        
        if len(combo) == 5:
            combinations.append(combo)

print(f"\n=== 產生的組合 (熱門權重={hot_weight}) ===")
for i, combo in enumerate(combinations, 1):
    # 判斷每個號碼是熱門還是冷門
    combo_info = []
    for num in combo:
        if num in user_hot:
            combo_info.append(f"{num}(熱)")
        else:
            combo_info.append(f"{num}(冷)")
    print(f"  第{i}組: {combo} - {' '.join(combo_info)}")

