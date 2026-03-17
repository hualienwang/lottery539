#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今彩539 智慧選號系統 v4.1（指定路徑版）

特色:
- 自動儲存歷史資料到 D:\\develop\\lottery539
- 每次執行自動累積，不會遺失
- 支援命令列快速新增開獎號碼
- 自動檢查重複

資料儲存位置:
    D:\\develop\\lottery539\\lotto539_data.json
"""

import random
import json
import os
import sys
from datetime import datetime
from collections import Counter


class Lotto539Generator:
    """今彩539 智慧選號產生器 v4.1"""
    
    def __init__(self, latest_draw=None, data_dir=r'D:\develop\lottery539'):
        """
        初始化產生器
        
        參數:
            latest_draw: 最新一期開獎號碼（不儲存，只用於本次計算）
            data_dir: 資料儲存目錄（預設 D:\\develop\\lottery539）
        """
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, 'lotto539_data.json')
        self.history_draws = []
        
        # 確保目錄存在
        self._ensure_directory()
        
        # 載入既有資料
        self._load_data()
        
        # 如果沒有資料，使用預設值
        if not self.history_draws:
            self._init_default_data()
        
        # 加入最新開獎（僅記憶體，不儲存）
        if latest_draw:
            self._temp_draw = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'numbers': sorted(latest_draw),
                'is_temporary': True
            }
        else:
            self._temp_draw = None

    def _recent_exclude(self, recent_n=2):
        """取得最近N期的號碼列表，用於排除"""
        recent_exclude = []
        for draw in self.history_draws[-recent_n:]:
            recent_exclude.extend(draw['numbers'])
        return list(set(recent_exclude))  # 去重
    
    def _ensure_directory(self):
        """確保儲存目錄存在"""
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
                print(f"✅ 已建立資料目錄: {self.data_dir}")
            except Exception as e:
                print(f"⚠️ 無法建立目錄 {self.data_dir}: {e}")
                # 如果無法建立，使用目前目錄
                self.data_dir = os.getcwd()
                self.data_file = os.path.join(self.data_dir, 'lotto539_data.json')
                print(f"   改用目前目錄: {self.data_dir}")
    
    def _init_default_data(self):
        """初始化預設資料（只有第一次執行時）"""
        default_draws = [
            {"date": "2026-02-02", "numbers": [6, 8, 31, 37, 38]},
            {"date": "2026-02-03", "numbers": [3, 5, 11, 15, 23]},
            {"date": "2026-02-04", "numbers": [8, 17, 22, 27, 28]},
            {"date": "2026-02-05", "numbers": [8, 9, 13, 32, 35]},
            {"date": "2026-02-06", "numbers": [1, 6, 29, 32, 34]},
            {"date": "2026-02-07", "numbers": [3, 8, 22, 27, 32]},
            {"date": "2026-02-09", "numbers": [16, 21, 25, 31, 35]},
            {"date": "2026-02-10", "numbers": [10, 11, 17, 22, 36]},
            {"date": "2026-02-11", "numbers": [11, 15, 18, 29, 33]},
            {"date": "2026-02-12", "numbers": [1, 12, 21, 35, 37]},
            {"date": "2026-02-13", "numbers": [4, 28, 31, 33, 34]},
            {"date": "2026-02-14", "numbers": [1, 3, 13, 31, 36]},
            {"date": "2026-02-15", "numbers": [11, 13, 18, 22, 34]},
        ]
        
        for item in default_draws:
            self.history_draws.append({
                'date': item['date'],
                'numbers': sorted(item['numbers']),
                'added_time': datetime.now().isoformat()
            })
        
        self._save_data()
        print(f"✅ 已初始化預設資料（{len(self.history_draws)}期）")
    
    def _load_data(self):
        """從檔案載入資料"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history_draws = data.get('draws', [])
                    
                    # 資料驗證
                    valid_draws = []
                    for draw in self.history_draws:
                        if self._validate_draw(draw):
                            valid_draws.append(draw)
                        else:
                            print(f"⚠️ 跳過無效記錄: {draw}")
                    
                    self.history_draws = valid_draws
                    print(f"📂 已載入歷史資料（{len(self.history_draws)}期）")
                    print(f"   檔案位置: {self.data_file}")
            except json.JSONDecodeError as e:
                print(f"⚠️ 資料檔格式錯誤: {e}")
                self.history_draws = []
            except Exception as e:
                print(f"⚠️ 載入資料失敗: {e}")
                self.history_draws = []
    
    def _save_data(self):
        """儲存資料到檔案"""
        try:
            # 備份舊檔案
            backup_file = self.data_file + '.backup'
            if os.path.exists(self.data_file):
                try:
                    import shutil
                    shutil.copy2(self.data_file, backup_file)
                except:
                    pass  # 備份失敗不影響主程序
            
            data = {
                'draws': self.history_draws,
                'last_update': datetime.now().isoformat(),
                'total_count': len(self.history_draws),
                'version': '4.2'
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ 儲存資料失敗: {e}")
            return False
    
    def _validate_draw(self, draw):
        """驗證單筆開獎記錄"""
        try:
            if not isinstance(draw, dict):
                return False
            if 'date' not in draw or 'numbers' not in draw:
                return False
            if not isinstance(draw['numbers'], list):
                return False
            if len(draw['numbers']) != 5:
                return False
            if not all(isinstance(n, int) and 1 <= n <= 39 for n in draw['numbers']):
                return False
            if len(set(draw['numbers'])) != 5:
                return False
            # 驗證日期格式
            datetime.strptime(draw['date'], '%Y-%m-%d')
            return True
        except:
            return False
    
    def add_draw(self, numbers, date=None, save=True, validate=True):
        """新增一期開獎號碼到歷史資料
        
        參數:
            numbers: 5個開獎號碼
            date: 開獎日期 (格式: YYYY-MM-DD)
            save: 是否立即儲存
            validate: 是否進行驗證
        """
        # 驗證
        if validate:
            if len(numbers) != 5:
                raise ValueError("每期必須是5個號碼")
            if not all(isinstance(n, int) for n in numbers):
                raise ValueError("所有號碼必須是整數")
            if not all(1 <= n <= 39 for n in numbers):
                raise ValueError("號碼必須在1-39之間")
            if len(set(numbers)) != 5:
                raise ValueError("號碼不能重複")
        
        numbers_sorted = sorted(numbers)
        
        # 檢查是否重複
        for draw in self.history_draws:
            if draw['numbers'] == numbers_sorted:
                print(f"⚠️ 此期號碼已存在（{draw['date']}）: {numbers_sorted}")
                return False
        
        # 驗證日期格式
        if date:
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("日期格式錯誤，請使用 YYYY-MM-DD")
        
        draw_data = {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'numbers': numbers_sorted,
            'added_time': datetime.now().isoformat()
        }
        
        self.history_draws.append(draw_data)
        
        if save:
            if self._save_data():
                print(f"✅ 已新增並儲存: {numbers_sorted} (共{len(self.history_draws)}期)")
                print(f"   日期: {draw_data['date']}")
                print(f"   檔案: {self.data_file}")
                return True
            else:
                print(f"⚠️ 已新增但未儲存: {numbers_sorted}")
                return False
        
        return True
    
    def analyze(self, top_n=30, recent_draws=20):
        """分析統計資料
        
        參數:
            top_n: 顯示前N個熱門/冷門號碼
            recent_draws: 分析最近N期開獎
        """
        all_draws = self.history_draws.copy()
        if self._temp_draw:
            all_draws.append(self._temp_draw)
        
        if not all_draws:
            return None
            
        # 只分析最近指定期數
        analysis_draws = all_draws[-recent_draws:]
        
        all_nums = []
        for draw in analysis_draws:
            all_nums.extend(draw['numbers'])
        
        counter = Counter(all_nums)
        
        # 計算統計指標
        counts = list(counter.values())
        if counts:
            avg_count = sum(counts) / len(counts)
            max_count = max(counts)
            min_count = min(counts)
        else:
            avg_count = max_count = min_count = 0
        
        # 熱門號碼：出現次數 >= 平均值的號碼
        recent_exclude_nums = self._recent_exclude(recent_n=2)  # 最近分析期數的號碼列表
        hot = sorted(
            [num for num, count in counter.items() if count >= avg_count],
            key=lambda x: counter[x],
            reverse=True
        )[:top_n]
        hot = [num for num in hot if num not in recent_exclude_nums]  # 排除最近期數的號碼
        
        # 冷門號碼：出現次數 < 平均值的號碼
        cold = sorted(
            [num for num, count in counter.items() if count < avg_count],
            key=lambda x: counter[x]
        )[:top_n]
        cold = [num for num in cold if num not in recent_exclude_nums]  # 排除最近期數的號碼

        # 未出現號碼
        all_possible = set(range(1, 40))
        zero_times = sorted(all_possible - set(counter.keys()))
        
        # 計算最久未開的號碼
        last_seen = {}
        for i, draw in enumerate(reversed(analysis_draws)):
            for num in range(1, 40):
                if num in draw['numbers'] and num not in last_seen:
                    last_seen[num] = i
        
        due_numbers = sorted(
            [(num, last_seen.get(num, float('inf'))) for num in range(1, 40)],
            key=lambda x: x[1],
            reverse=True
        )
        
        
        return {
            'counter': counter,
            'total_draws': len(all_draws),
            'analysis_draws': len(analysis_draws),
            'stats': {
                'avg_frequency': round(avg_count, 2),
                'max_frequency': max_count,
                'min_frequency': min_count
            },
            'hot': hot,
            'cold': cold,
            'zero_times': zero_times,
            'due_numbers': due_numbers[0:],
            'latest_draw': all_draws[-1]['numbers'],
            'latest_date': all_draws[-1]['date'],
            'previous_draw': all_draws[-2]['numbers'] if len(all_draws) > 1 else None,
            'is_temp_latest': all_draws[-1].get('is_temporary', False)
            
        }
    
    def generate(self, exclude=None, hot=None, hot_weight=2, num_sets=1, 
                  seed=None, smart_mode=True, avoid_consecutive=False):
        """產生號碼組合
        
        參數:
            exclude: 排除的號碼列表
            hot: 熱門號碼列表（增加被選中機率）
            hot_weight: 熱門號碼的權重倍數
            num_sets: 產生組合數
            seed: 隨機種子
            smart_mode: 智能模式（避免產生重複組合）
            avoid_consecutive: 避免連續號碼（同一組內最多2個連續）
        """
        if seed is not None:
            random.seed(seed)
            
        exclude = exclude or []
        hot = hot or []
        # print(f"🔍 產生號碼組合，排除: {exclude} | 熱門: {hot} (權重{hot_weight}倍)")
        available = [n for n in range(1, 40) if n not in exclude]
        print(f"🔍 可用號碼: {available} (共{len(available)}個)")

        if len(available) < 5:
            raise ValueError(f"可用號碼不足！排除後只剩{len(available)}個")
        
        # 計算權重
        weights = [hot_weight if n in hot else 1 for n in available]
        
        results = []
        attempts = 0
        max_attempts = num_sets * 100  # 防止無限迴圈
        
        while len(results) < num_sets and attempts < max_attempts:
            attempts += 1
            selected = []
            temp_avail = available.copy()
            temp_weights = weights.copy()
            
            # 選擇5個號碼
            for _ in range(5):
                chosen = random.choices(temp_avail, weights=temp_weights, k=1)[0]
                selected.append(chosen)
                idx = temp_avail.index(chosen)
                temp_avail.pop(idx)
                temp_weights.pop(idx)
            
            selected_sorted = sorted(selected)
            
            # 檢查連續號碼（避免過多連續）
            if avoid_consecutive:
                consecutive_count = 0
                for i in range(len(selected_sorted) - 1):
                    if selected_sorted[i+1] - selected_sorted[i] == 1:
                        consecutive_count += 1
                if consecutive_count > 2:
                    continue  # 連續超過2個，重新選擇
            
            # 智能模式：避免重複
            if smart_mode and selected_sorted in results:
                continue
            
            results.append(selected_sorted)
        
        return results
    
    def show_history(self, n=10):
        """顯示最近n期歷史"""
        print(f"\n📜 最近{n}期開獎紀錄:")
        print(f"   資料來源: {self.data_file}")
        print("-" * 50)
        for draw in self.history_draws[-n:]:
            print(f"  {draw['date']}: {draw['numbers']}")
    
    def clear_data(self, confirm=False):
        """清除所有資料（慎用）"""
        if confirm:
            self.history_draws = []
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
                print(f"✅ 已刪除資料檔: {self.data_file}")
            print("✅ 所有資料已清除")
            return True
        return False


def print_usage():
    """顯示使用說明"""
    print("""
使用方法:
    python lotto539.py [選項] [號碼...]

選項:
    --add N1 N2 N3 N4 N5     新增開獎號碼到歷史資料（儲存到D:\\develop\\lottery539\\）
    --date YYYY-MM-DD        指定日期（配合 --add 使用）
    --history N              顯示最近N期開獎（預設10）
    --clear                  清除所有歷史資料（需確認）
    --seed N                 設定隨機種子
    -h, --help               顯示說明

範例:
    python lotto539.py                              # 基本使用
    python lotto539.py --add 11 13 18 22 34         # 新增今天開獎
    python lotto539.py --add 11 13 18 22 34 --date 2026-02-16
    python lotto539.py --history 5                  # 查看最近5期
    python lotto539.py 11 13 18 22 34               # 帶入計算但不儲存
    """)


def main():
    """主程式"""
    args = sys.argv[1:]
    
    # 無參數或需要說明
    # if not args or '-h' in args or '--help' in args:
    if '-h' in args or '--help' in args:    
        print("=" * 70)
        print("🎱 今彩539 智慧選號系統 v4.2")
        print("=" * 70)
        print_usage()
        return
    
    # 初始化產生器（使用預設路徑）
    gen = Lotto539Generator()
    
    # 處理 --clear
    if '--clear' in args:
        confirm = input("⚠️  確定要清除所有歷史資料嗎？輸入 'yes' 確認: ")
        if confirm.lower() == 'yes':
            gen.clear_data(confirm=True)
        else:
            print("已取消")
        return
    
    # 處理 --history
    if '--history' in args:
        idx = args.index('--history')
        try:
            n = int(args[idx + 1]) if idx + 1 < len(args) else 10
        except:
            n = 10
        gen.show_history(n)
        return
    
    # 處理 --add（新增到歷史）
    if '--add' in args:
        idx = args.index('--add')
        try:
            numbers = [int(args[i]) for i in range(idx + 1, idx + 6)]
            if not all(1 <= n <= 39 for n in numbers):
                print("❌ 錯誤：號碼必須在1-39之間")
                return
            if len(set(numbers)) != 5:
                print("❌ 錯誤：號碼不能重複")
                return
        except (IndexError, ValueError):
            print("❌ 錯誤：請提供5個有效的號碼")
            return
        
        # 檢查是否有 --date
        date = None
        if '--date' in args:
            date_idx = args.index('--date')
            try:
                date = args[date_idx + 1]
            except IndexError:
                pass
        
        gen.add_draw(numbers, date=date)
        return
    
    # 處理一般參數（帶入最新開獎但不儲存）
    if len(args) >= 5:
        try:
            # 檢查是否有 --seed
            seed = None
            if '--seed' in args:
                seed_idx = args.index('--seed')
                try:
                    seed = int(args[seed_idx + 1])
                    args = args[:seed_idx]
                except:
                    pass
            
            latest_draw = [int(x) for x in args[:5]]
            if not all(1 <= n <= 39 for n in latest_draw):
                print("❌ 錯誤：號碼必須在1-39之間")
                return
            if len(set(latest_draw)) != 5:
                print("❌ 錯誤：號碼不能重複")
                return
            
            # 重新初始化，帶入最新開獎
            gen = Lotto539Generator(latest_draw=sorted(latest_draw))
            
            print("=" * 70)
            print("🎱 今彩539 智慧選號系統 v4.2")
            print("=" * 70)
            print(f"\n📥 已載入最新開獎號碼（不儲存）: {sorted(latest_draw)}")
        except ValueError:
            print("❌ 錯誤：請輸入有效的數字")
            return
    else:
        print("=" * 70)
        print("🎱 今彩539 智慧選號系統 v4.2")
        print("=" * 70)
        print(f"\n📂 已載入歷史資料（{len(gen.history_draws)}期）")
        print(f"   儲存位置: {gen.data_file}")
    
    # 分析與產生號碼
    analysis = gen.analyze(top_n=30, recent_draws=25)
    
    print(f"\n{'='*70}")
    print("📊 統計分析結果")
    print(f"{'='*70}")
    print(f"總期數: {analysis['total_draws']} | 分析期數: {analysis['analysis_draws']}")
    if analysis['previous_draw']:
        print(f"上一期: {analysis['previous_draw']}")
    print(f"最新期: {analysis['latest_draw']}", end="")
    if analysis['is_temp_latest']:
        print(" （本次帶入）")
    else:
        print()
    
    # 統計指標
    stats = analysis['stats']
    print(f"\n📈 統計指標:")
    print(f"   平均出現: {stats['avg_frequency']}次 | 最高: {stats['max_frequency']}次 | 最低: {stats['min_frequency']}次")
    
    print(f"\n🔥 熱門號碼 TOP_hot: {analysis['hot'][0:]}")
    print(f"❄️ 冷門號碼 TOP_cold: {analysis['cold'][0:]}")
    print(f"🚫 0次號碼（未開出）: {analysis['zero_times']}")
    print(f"⏰ 最久未開 TOP5: {[n for n, d in analysis['due_numbers'][:5]]}")
    
    # 產生建議號碼
    print(f"\n{'='*70}")
    print("🎲 產生5組建議號碼")
    print(f"{'='*70}")

    # 排除所有未開過的號碼
    exclude_nums = analysis['zero_times'][0:]  
    print(f"策略: 排除最近20期未開過的{len(exclude_nums)}個號碼{exclude_nums}")
    # exclude_nums 加上前2期或3期的號碼（視情況調整）

    recent_exclude_nums = gen._recent_exclude(recent_n=4)
    print(f"排除最近4期開出的號碼: {recent_exclude_nums}")

    exclude_nums.extend(recent_exclude_nums)  # 加入最近期數的號碼到排除列表
    exclude_nums = list(set(exclude_nums))  # 去重
    
    # print(f"總共排除的號碼（含未開過的）: {exclude_nums}")
    hot_nums = analysis['hot'][0:]  # 使用所有熱門號碼
    hot_weight_value = 2
    
    print(f"策略: 排除後的所有{len(exclude_nums)}個號碼{exclude_nums}")
    print(f"       提升{len(hot_nums)}個熱門號碼{hot_nums}的權重({hot_weight_value}倍)\n")
    
    results = gen.generate(
        exclude=exclude_nums,
        hot=hot_nums,
        hot_weight=hot_weight_value,
        num_sets=2,
        seed=seed if 'seed' in locals() else None,
        smart_mode=True,
        avoid_consecutive=False
        
    )

    
    # 顯示結果並標註包含的熱門/冷門號碼
    for i, nums in enumerate(results, 1):
        hot_in = [n for n in nums if n in hot_nums]
        cold_in = [n for n in nums if n in analysis['cold']]
        status = ""
        if hot_in:
            status += f" 🔥:{hot_in}"
        if cold_in:
            status += f" ❄:{cold_in}"
        print(f"  第{i}組: {nums}{status}")
    
    print(f"\n{'='*70}")
    print("ℹ️  提示說明")
    print(f"{'='*70}")
    print("  • 🔥 熱門號碼: 在分析期間出現頻率較高的號碼")
    print("  • ❄️  冷門號碼: 在分析期間出現頻率較低的號碼")
    print("  • 🚫 未開號碼: 在分析期間尚未出現的號碼")
    print("  • ⏰ 最久未開: 距離上次開出最久的號碼\n")
    print("⚠️  提醒: 中獎機率相同，以上分析僅供參考，請理性投注")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()