# -*- coding: utf-8 -*-
"""
539 樂透號碼組合生成器
- 只使用熱門牌
- 不使用冷門牌
- 不使用尾數預測
- 不使用權重
- 排除最近2期開獎號碼
- 輸出: 2 組 539 號碼
"""

import random
import sys
import io
from collections import Counter
from typing import List, Set
from lotto_data import load_draws_from_db

# 設定輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOT_THRESHOLD = 3
COLD_THRESHOLD = 2

def load_latest_draws(db_path: str = "lotto.db", count: int = 30) -> List[List[int]]:
    """載入最新的開獎資料"""
    latest_draws = load_draws_from_db(db_path, limit=count)
    
    return [draw['numbers'] for draw in latest_draws]

def get_hot_numbers(draws: List[List[int]]) -> List[int]:
    """取得出現次數 >= 3 的熱門牌"""
    counter = Counter(num for draw in draws for num in draw)
    return sorted(
        [num for num in range(1, 40) if counter.get(num, 0) >= HOT_THRESHOLD],
        key=lambda x: (-counter[x], x)
    )

def get_cold_numbers(draws: List[List[int]]) -> List[int]:
    """取得出現次數 < 2 的冷門牌"""
    counter = Counter(num for draw in draws for num in draw)
    return sorted(
        [num for num in range(1, 40) if counter.get(num, 0) < COLD_THRESHOLD],
        key=lambda x: (counter[x], x)
    )

def get_recent_numbers(draws: List[List[int]], count: int = 2) -> Set[int]:
    """取得最近N期的所有開獎號碼"""
    recent = draws[-count:]
    numbers = set()
    for draw in recent:
        numbers.update(draw)
    return numbers

def filter_hot_numbers(hot: List[int], exclude: Set[int]) -> List[int]:
    """過濾熱門牌，排除最近2期開出的號碼"""
    return [n for n in hot if n not in exclude]

def generate_539_from_hot(available_numbers: List[int]) -> Set[int]:
    """
    從熱門牌中隨機生成一組 539 號碼
    
    Args:
        available_numbers: 可用的熱門牌列表
    
    Returns:
        5 個不重複的號碼集合
    """
    if len(available_numbers) < 5:
        # 如果可用號碼不足5個，從全部1-39中補充
        all_numbers = set(range(1, 40)) - set(available_numbers)
        available_numbers = available_numbers + list(all_numbers)
    
    return set(random.sample(available_numbers, 5))

def generate_two_sets(available_numbers: List[int]) -> List[Set[int]]:
    """生成 2 組 539 號碼"""
    results: List[Set[int]] = []
    
    for i in range(2):
        number_set = generate_539_from_hot(available_numbers)
        
        # 確保與前一組不重複
        if i > 0:
            attempts = 0
            while number_set == results[i-1] and attempts < 100:
                number_set = generate_539_from_hot(available_numbers)
                attempts += 1
        
        results.append(number_set)
        print(f"第 {i+1} 組: {sorted(number_set)}")
    
    return results

def main():
    """主程式入口"""
    print("=" * 65)
    print("539 樂透號碼組合生成器 (熱門牌>=3 / 冷門<2 / 無尾數預測 / 無權重)")
    print("=" * 65)
    
    # 載入最近30期資料
    print("\n[1] 載入最近30期開獎資料...")
    latest_draws = load_latest_draws()
    print(f"    已載入 {len(latest_draws)} 期資料")
    
    # 取得最近2期開獎號碼
    print("\n[2] 取得最近2期開獎號碼...")
    recent_numbers = get_recent_numbers(latest_draws, count=2)
    print(f"    最近2期號碼: {sorted(recent_numbers)}")
    
    # 依出現次數統計熱門牌並過濾最近開獎號碼
    print("\n[3] 過濾熱門牌 (排除最近2期開獎號碼)...")
    hot_numbers = get_hot_numbers(latest_draws)
    cold_numbers = get_cold_numbers(latest_draws)
    filtered_hot = filter_hot_numbers(hot_numbers, recent_numbers)
    print(f"    原始熱門牌 ({len(hot_numbers)} 個): {hot_numbers}")
    print(f"    冷門牌 (<{COLD_THRESHOLD}, 不使用): {cold_numbers}")
    print(f"    過濾後熱門牌 ({len(filtered_hot)} 個): {filtered_hot}")
    
    # 檢查是否足夠
    if len(filtered_hot) < 5:
        print(f"    警告: 過濾後號碼不足5個，將使用原始熱門牌")
        filtered_hot = hot_numbers
    
    # 生成兩組
    print("\n[4] 生成 539 號碼組合...")
    print("-" * 65)
    results = generate_two_sets(filtered_hot)
    
    print("-" * 65)
    print("\n最終結果:")
    for i, result in enumerate(results, 1):
        print(f"  第 {i} 組: {sorted(result)}")
    print("=" * 65)

if __name__ == "__main__":
    main()
