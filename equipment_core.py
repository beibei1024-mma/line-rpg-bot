# equipment_core.py - 皇家多維度裝備與隨機詞綴核心大腦 v3.0

import random

# 1. ⚜️ 裝備基礎範本庫 (各大部位制式基本盤物傷、防禦、魔防)
BASE_TEMPLATES = {
    "武器": {
        "鐵劍": {"atk": 10, "def": 0, "mdef": 0, "price": 100, "desc": "制式鐵劍"},
        "長弓": {"atk": 15, "def": 0, "mdef": 0, "price": 250, "desc": "精準長弓"},
        "法杖": {"atk": 20, "def": 0, "mdef": 5, "price": 500, "desc": "導魔法杖"}
    },
    "頭盔": {
        "皮帽": {"atk": 0, "def": 3, "mdef": 2, "price": 80, "desc": "輕便皮帽"},
        "鐵盔": {"atk": 0, "def": 8, "mdef": 1, "price": 200, "desc": "精鋼重盔"}
    },
    "鎧甲": {
        "布袍": {"atk": 0, "def": 5, "mdef": 10, "price": 150, "desc": "法術布袍"},
        "鎖子甲": {"atk": 0, "def": 20, "mdef": 2, "price": 450, "desc": "防禦鎖子甲"}
    },
    "護手": {
        "護腕": {"atk": 2, "def": 4, "mdef": 2, "price": 100, "desc": "戰鬥護腕"}
    },
    "鞋子": {
        "皮靴": {"atk": 0, "def": 5, "mdef": 3, "price": 120, "desc": "遊俠皮靴"}
    },
    "飾品": {
        "古銅戒指": {"atk": 5, "def": 0, "mdef": 5, "price": 300, "desc": "附魔戒指"}
    }
}

# 2. 🌈 裝備品質階級與基礎數值乘算係數 (品質越高，基礎白字呈幾何增長！)
RARITY_CONFIG = {
    "⭐普通": {"multiplier": 1.0, "color": "#8E8E93", "affix_count": 0},
    "🔷魔法": {"multiplier": 1.4, "color": "#34AADC", "affix_count": 1},
    "🌟稀有": {"multiplier": 2.0, "color": "#4CD964", "affix_count": 2},
    "🔥史詩": {"multiplier": 3.2, "color": "#FF9500", "affix_count": 3},
    "👑遠古神話": {"multiplier": 6.5, "color": "#FF3B30", "affix_count": 4}
}

# 3. ✍️ 隨機屬性副詞綴池 (隨機挑選灌入裝備內，形成無限刷寶變化)
AFFIX_POOL = [
    {"name": "鋒利的", "stat": "strength", "min": 3, "max": 8, "desc": "力量"},
    {"name": "疾風的", "stat": "agility", "min": 2, "max": 7, "desc": "敏捷"},
    {"name": "深邃的", "stat": "intelligence", "min": 4, "max": 10, "desc": "智力"},
    {"name": "不壞的", "stat": "vitality", "min": 5, "max": 12, "desc": "體力"},
    {"name": "至運的", "stat": "luck", "min": 2, "max": 6, "desc": "幸運"},
    {"name": "神聖的", "stat": "sprit", "min": 3, "max": 9, "desc": "精神"}
]

def generate_random_equipment(slot, base_name, forced_rarity=None):
    """🎲 核心神級演算法：隨機洗鍊出一件具備暗黑風格的動態裝備封包"""
    if slot not in BASE_TEMPLATES or base_name not in BASE_TEMPLATES[slot]:
        slot, base_name = "武器", "鐵劍" # 保底
        
    base_stat = BASE_TEMPLATES[slot][base_name]
    rarity = forced_rarity if forced_rarity else random.choices(
        list(RARITY_CONFIG.keys()), weights=[50, 30, 14, 5, 1], k=1
    )[0]
    
    r_cfg = RARITY_CONFIG[rarity]
    mult = r_cfg["multiplier"]
    
    # 計算基礎白字
    final_atk = int(base_stat["atk"] * mult)
    final_def = int(base_stat["def"] * mult)
    final_mdef = int(base_stat["mdef"] * mult)
    
    # 抽取並注入隨機隨機副詞綴
    chosen_affixes = random.sample(AFFIX_POOL, k=r_cfg["affix_count"])
    item_affixes = {}
    prefix_name = ""
    
    for aff in chosen_affixes:
        roll_val = random.randint(aff["min"], aff["max"])
        item_affixes[aff["stat"]] = item_affixes.get(aff["stat"], 0) + roll_val
        prefix_name += f"{aff['name']}"
        
    final_title = f"{rarity} {prefix_name}{base_name}"
    final_price = int(base_stat["price"] * mult * (1 + len(chosen_affixes) * 0.5))
    
    # 用於生成獨一無二的動態 UUID 存檔識別碼
    item_id = f"eq_{slot[:2]}_{random.randint(100000, 999999)}"
    
    return {
        "id": item_id,
        "name": final_title,
        "slot": slot,
        "base_type": base_name,
        "rarity": rarity,
        "atk": final_atk,
        "def": final_def,
        "mdef": final_mdef,
        "affixes": item_affixes, # 例：{"strength": 5, "luck": 3}
        "price": final_price,
        "desc": base_stat["desc"]
    }
