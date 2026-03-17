# -*- coding: utf-8 -*-
"""
539 樂透號碼組合生成器
- 熱門牌權重: 3
- 冷門牌權重: 1
- 熱門牌個數隨機: 2-3 個
- 輸出: 2 組 539 號碼
- 尾數組合: 熱門尾數 3 個 + 冷門尾數 2 個 (3:2 比例)
"""

import random
import json
import sys
import io
from typing import List, Set, Dict, Tuple
from collections import Counter

# 設定輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定義冷門牌
cold_numbers: List[int] = [6, 9, 13, 14, 24, 25, 28]

# 定義熱門牌
hot_numbers: List[int] = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 29, 31, 32, 34, 35, 36, 37, 38, 39]

# 權重設定
HOT_WEIGHT: int = 3
COLD_WEIGHT: int = 1

def load_latest_draws(filename: str = "lotto539_data.json", count: int = 30) -> List[List[int]]:
    """載入最新的開獎資料"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    draws = data['draws']
    latest_draws = draws[-count:]
    
    return [draw['numbers'] for draw in latest_draws]

def analyze_last_digits(draws: List[List[int]]) -> Dict[int, int]:
    """分析最近N期的尾數出現頻率"""
    last_digit_counter: Counter = Counter()
    
    for draw_numbers in draws:
        for num in draw_numbers:
            last_digit = num % 10
            last_digit_counter[last_digit] += 1
    
    return dict(last_digit_counter)

def get_hot_and_cold_last_digits(last_digit_counts: Dict[int, int]) -> Tuple[List[int], List[int]]:
    """
    區分熱門尾數和冷門尾數
    
    Returns:
        (熱門尾數列表, 冷門尾數列表)
    """
    sorted_digits = sorted(last_digit_counts.items(), key=lambda x: x[1], reverse=True)
    
    # 前 5 個為熱門尾數 (出現次數較多)
    # 後 5 個為冷門尾數 (出現次數較少)
    hot_digits = [digit for digit, count in sorted_digits[:5]]
    cold_digits = [digit for digit, count in sorted_digits[5:]]
    
    return hot_digits, cold_digits

def filter_numbers_by_last_digits(numbers: List[int], valid_last_digits: List[int]) -> List[int]:
    """過濾號碼，保留尾數在有效尾數清單中的號碼"""
    return [num for num in numbers if num % 10 in valid_last_digits]

def generate_539_with_last_digit_ratio(
    available_hots: List[int], 
    available_colds: List[int],
    hot_last_digits: List[int],
    cold_last_digits: List[int]
) -> Set[int]:
    """
    生成一組 539 號碼
    - 2-3 個號碼尾數來自熱門尾數 (隨機)
    - 其餘號碼尾數來自冷門尾數
    
    Args:
        available_hots: 可用的熱門牌列表 (已過濾: 尾數為熱門尾數)
        available_colds: 可用的冷門牌列表 (已過濾: 尾數為冷門尾數)
        hot_last_digits: 熱門尾數列表
        cold_last_digits: 冷門尾數列表
    
    Returns:
        5 個不重複的號碼集合
    """
    # 隨機決定熱門尾數個數 (2-3個)
    hot_last_count = random.randint(2, 3)
    cold_last_count = 5 - hot_last_count
    
    result: Set[int] = set()
    
    # 從過濾後的熱門牌中選擇 (這些號碼尾數本來就是熱門尾數)
    if len(available_hots) >= hot_last_count:
        selected_hot = random.sample(available_hots, hot_last_count)
    else:
        selected_hot = available_hots
    result.update(selected_hot)
    
    # 從過濾後的冷門牌中選擇 (這些號碼尾數本來就是冷門尾數)
    available_colds_filtered = [n for n in available_colds if n not in result]
    if len(available_colds_filtered) >= cold_last_count:
        selected_cold = random.sample(available_colds_filtered, cold_last_count)
    else:
        selected_cold = available_colds_filtered
    result.update(selected_cold)
    
    # 如果號碼不足 5 個，從剩餘號碼中補充
    if len(result) < 5:
        all_available = list(set(available_hots + available_colds) - result)
        additional = random.sample(all_available, 5 - len(result))
        result.update(additional)
    
    return result

def generate_two_sets(
    available_hots: List[int], 
    available_colds: List[int],
    hot_last_digits: List[int],
    cold_last_digits: List[int]
) -> List[Set[int]]:
    """生成 2 組 539 號碼"""
    results: List[Set[int]] = []
    
    for i in range(2):
        number_set = generate_539_with_last_digit_ratio(
            available_hots, available_colds, hot_last_digits, cold_last_digits
        )
        
        # 確保與前一組不重複
        if i > 0:
            attempts = 0
            while number_set == results[i-1] and attempts < 100:
                number_set = generate_539_with_last_digit_ratio(
                    available_hots, available_colds, hot_last_digits, cold_last_digits
                )
                attempts += 1
        
        results.append(number_set)
        
        # 分析這組號碼的尾數分布
        hot_count = sum(1 for n in number_set if n % 10 in hot_last_digits)
        cold_count = 5 - hot_count
        print(f"第 {i+1} 組: {sorted(number_set)} (熱門尾數: {hot_count}個, 冷門尾數: {cold_count}個)")
    
    return results

def main():
    """主程式入口"""
    print("=" * 65)
    print("539 樂透號碼組合生成器 (尾數 3:2 比例)")
    print("=" * 65)
    
    # 載入最近30期資料
    print("\n[1] 載入最近30期開獎資料...")
    latest_draws = load_latest_draws()
    print(f"    已載入 {len(latest_draws)} 期資料")
    
    # 分析尾數
    print("\n[2] 分析尾數出現頻率...")
    last_digit_counts = analyze_last_digits(latest_draws)
    print(f"    尾數統計: {dict(sorted(last_digit_counts.items()))}")
    
    # 區分熱門尾數和冷門尾數
    hot_last_digits, cold_last_digits = get_hot_and_cold_last_digits(last_digit_counts)
    print(f"\n[3] 尾數分類:")
    print(f"    熱門尾數 (前5名): {hot_last_digits}")
    print(f"    冷門尾數 (後5名): {cold_last_digits}")
    
    # 過濾冷門牌和熱門牌
    # - 熱門牌只保留尾數為熱門尾數的號碼
    # - 冷門牌只保留尾數為冷門尾數的號碼
    print("\n[4] 過濾號碼...")
    filtered_hot = filter_numbers_by_last_digits(hot_numbers, hot_last_digits)
    filtered_cold = filter_numbers_by_last_digits(cold_numbers, cold_last_digits)
    
    print(f"    原始熱門牌 ({len(hot_numbers)} 個): {hot_numbers}")
    print(f"    過濾後熱門牌 ({len(filtered_hot)} 個): {filtered_hot}")
    print(f"    原始冷門牌 ({len(cold_numbers)} 個): {cold_numbers}")
    print(f"    過濾後冷門牌 ({len(filtered_cold)} 個): {filtered_cold}")
    
    # 檢查是否有足夠的號碼
    total_available = len(filtered_hot) + len(filtered_cold)
    print(f"\n    可用號碼總數: {len(filtered_hot) + len(filtered_cold)}")
    
    if len(filtered_hot) + len(filtered_cold) < 5:
        print("    警告: 可用號碼不足5個，將使用全部號碼")
        filtered_hot = hot_numbers
        filtered_cold = cold_numbers
    
    # 生成兩組 (尾數 3:2 比例)
    print("\n[5] 生成 539 號碼組合 (熱門尾數:冷門尾數 = 3:2)...")
    print("-" * 65)
    results = generate_two_sets(filtered_hot, filtered_cold, hot_last_digits, cold_last_digits)
    
    # 隨機選取尾數號碼
    print("\n[6] 隨機選取尾數號碼...")
    all_last_digits = list(range(10))  # 尾數 0-9
    num_random_last_digits = random.randint(2, 4)  # 隨機選取 2-4 個尾數
    random_selected_last_digits = sorted(random.sample(all_last_digits, num_random_last_digits))
    print(f"    隨機選取的尾數號碼: {random_selected_last_digits}")
    
    print("-" * 65)
    print("\n最終結果:")
    for i, result in enumerate(results, 1):
        print(f"  第 {i} 組: {sorted(result)}")
    print("=" * 65)

if __name__ == "__main__":
    main()
