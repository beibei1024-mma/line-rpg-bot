import random

# 🗺️ 怪物生成地圖綁定庫（由 game_core 根據地圖名稱來調用，完全解決地圖規劃問題！）
MAP_MONSTER_SPAWN = {
    "新手村": ["slime", "goblin"],
    "骷髏荒漠": ["skeleton", "desert_thief"],
    "巨龍巢穴": ["dragon"]
}

# 🎭 隨機怪物「詞綴系統」（當怪物出生時，會隨機抽一個頭銜，並直接改變怪物的血量和傷害倍率！）
MONSTER_AFFIXES = [
    {"prefix": "⭐ 普通的", "hp_mod": 1.0, "atk_mod": 1.0, "gold_mod": 1.0, "skill": "無特別威脅"},
    {"prefix": "⚡ 迅捷的", "hp_mod": 0.8, "atk_mod": 1.3, "gold_mod": 1.2, "skill": "極速連擊（閃避率提升）"},
    {"prefix": "🛡️ 狂暴的", "hp_mod": 1.5, "atk_mod": 1.5, "gold_mod": 2.0, "skill": "嗜血狂暴（攻擊機率暴擊）"},
    {"prefix": "👑 遠古神聖的", "hp_mod": 3.0, "atk_mod": 2.0, "gold_mod": 5.0, "skill": "神聖反震（反彈勇者傷害）"}
]

# 👾 怪物原始生物大數據庫
MONSTERS_BASE = {
    "slime": {
        "name": "綠色史萊姆", "level": 1, "min_hp": 20, "max_hp": 20, "atk": 3, 
        "gold_range": (10, 500), "exp": 50, "drop_item": "史萊姆黏液"
    },
    "goblin": {
        "name": "哥布林小偷", "level": 2, "min_hp": 45, "max_hp": 45, "atk": 6, 
        "gold_range": (25, 1000), "exp": 100, "drop_item": "破爛的匕首"
    },
    "desert_thief": {
        "name": "荒漠流浪強盜", "level": 4, "min_hp": 90, "max_hp": 90, "atk": 12, 
        "gold_range": (80, 2000), "exp": 240, "drop_item": "強盜面罩"
    },
    "skeleton": {
        "name": "骷髏精英戰士", "level": 5, "min_hp": 150, "max_hp": 150, "atk": 18, 
        "gold_range": (150, 3000), "exp": 400, "drop_item": "古老生鏽長劍"
    },
    "dragon": {
        "name": "地獄紅蓮巨龍", "level": 8, "min_hp": 600, "max_hp": 600, "atk": 50, 
        "gold_range": (1000, 15000), "exp": 2000, "drop_item": "巨龍逆鱗"
    }
}

def generate_random_monster(map_name):
    """根據玩家目前所在的地圖，隨機抽取並計算出帶有隨機頭銜、隨機血量增幅的最終戰鬥對象"""
    # 1. 根據地圖名稱抓取可以生成的怪物清單，如果沒有，預設在新手村
    available_monsters = MAP_MONSTER_SPAWN.get(map_name, ["slime"])
    chosen_base_type = random.choice(available_monsters)
    base = MONSTERS_BASE[chosen_base_type]
    
    # 2. 隨機抽取怪物隨機詞綴（頭銜）
    affix = random.choice(MONSTER_AFFIXES)
    
    # 3. 根據詞綴進行隨機屬性增幅計算
    final_hp = int(random.randint(base["min_hp"], base["max_hp"]) * affix["hp_mod"])
    final_atk = int(base["atk"] * affix["atk_mod"])
    
    # 計算出此戰隨機波動的金幣範圍
    min_gold = int(base["gold_range"][0] * affix["gold_mod"])
    max_gold = int(base["gold_range"][1] * affix["gold_mod"])
    
    return {
        "name": f"{affix['prefix']}{base['name']} (Lv.{base['level']})",
        "hp": final_hp,
        "max_hp": final_hp,
        "atk": final_atk,
        "gold_range": (min_gold, max_gold),
        "exp": int(base["exp"] * affix["hp_mod"]), # 血越厚經驗越多
        "skill": affix["skill"],
        "drop_item": base["drop_item"],
        "spawn_map": map_name
    }
