import random

# 🗺️ 怪物生成地圖綁定庫
MAP_MONSTER_SPAWN = {
    "新手村": ["slime", "goblin"],
    "骷髏荒漠": ["skeleton", "desert_thief"],
    "巨龍巢穴": ["dragon_guard", "dragon"]
}

# 🎭 隨機怪物「史詩詞綴系統」
MONSTER_AFFIXES = [
    {"prefix": "⭐ 【普通】", "hp_mod": 1.0, "atk_mod": 1.0, "gold_mod": 1.0, "default_skill": "⚡ 近戰肉搏（無特殊威脅）"},
    {"prefix": "⚡ 【迅捷】", "hp_mod": 0.9, "atk_mod": 1.4, "gold_mod": 1.5, "default_skill": "💨 殘影步（閃避勇者 15% 的普通攻擊）"},
    {"prefix": "🛡️ 【狂暴】", "hp_mod": 1.6, "atk_mod": 1.8, "gold_mod": 2.5, "default_skill": "🔥 嗜血渴望（反擊時有機率造成雙倍暴擊）"},
    {"prefix": "👑 【遠古神聖】", "hp_mod": 3.5, "atk_mod": 2.2, "gold_mod": 6.0, "default_skill": "🌟 神聖領域（每次受到傷害，反彈 10% 威力給勇者）"}
]

# 👾 怪物原始生物大數據庫（大幅增強高階地圖怪物血量與多樣性）
MONSTERS_BASE = {
    "slime": {
        "name": "綠色史萊姆", "level": 1, "min_hp": 20, "max_hp": 30, "atk": 3, 
        "gold_range": (10, 500), "exp": 500, "drop_item": "史萊姆黏液"
    },
    "goblin": {
        "name": "哥布林小偷", "level": 3, "min_hp": 45, "max_hp": 65, "atk": 7, 
        "gold_range": (25, 1000), "exp": 1000, "drop_item": "破爛的匕首"
    },
    "desert_thief": {
        "name": "荒漠流浪強盜", "level": 12, "min_hp": 250, "max_hp": 350, "atk": 22, 
        "gold_range": (200, 3000), "exp": 4500, "drop_item": "強盜面罩"
    },
    "skeleton": {
        "name": "骷髏精英戰士", "level": 15, "min_hp": 400, "max_hp": 550, "atk": 35, 
        "gold_range": (400, 5000), "exp": 7000, "drop_item": "古老生鏽長劍"
    },
    "dragon_guard": {
        "name": "赤焰守護飛龍", "level": 22, "min_hp": 900, "max_hp": 1200, "atk": 65, 
        "gold_range": (800, 8000), "exp": 15000, "drop_item": "飛龍雙翼"
    },
    "dragon": {
        "name": "世界Boss・地獄紅蓮巨龍", "level": 30, "min_hp": 3500, "max_hp": 5000, "atk": 120, 
        "gold_range": (5000, 30000), "exp": 50000, "drop_item": "巨龍逆鱗"
    }
}

# 🔮 隨機 Boss 被動環境技能庫（當遇到 Boss 或高階怪時，有機會觸發更炫酷的戰場效果）
BOSS_SKILLS = [
    "🔥 紅蓮業火（每回合空氣灼燒，勇者額外承受隨機熱毒）",
    "🌋 岩漿護體（巨龍防禦力在岩漿中大幅提升，免疫暴擊）",
    "🌪️ 巨龍威壓（遠古龍威降臨，勇者的攻擊力被壓制 20%）"
]

def generate_random_monster(map_name):
    """根據玩家所在的地圖，隨機生成極具隨機性與史詩技能的震撼強敵"""
    available_monsters = MAP_MONSTER_SPAWN.get(map_name, ["slime"])
    chosen_base_type = random.choice(available_monsters)
    base = MONSTERS_BASE[chosen_base_type]
    
    # 隨機抽取怪物隨機詞綴
    affix = random.choice(MONSTER_AFFIXES)
    
    # 計算屬性增幅
    final_hp = int(random.randint(base["min_hp"], base["max_hp"]) * affix["hp_mod"])
    final_atk = int(base["atk"] * affix["atk_mod"])
    
    min_gold = int(base["gold_range"][0] * affix["gold_mod"])
    max_gold = int(base["gold_range"][1] * affix["gold_mod"])
    
    # 🎲 特殊技能優化：如果是巨龍（Boss），強制發動巨龍專屬高階環境技能！
    if chosen_base_type == "dragon":
        final_skill = random.choice(BOSS_SKILLS)
        monster_title = f"{affix['prefix']}{base['name']}"
    else:
        final_skill = affix["default_skill"]
        monster_title = f"{affix['prefix']}{base['name']} (Lv.{base['level']})"
    
    return {
        "name": monster_title,
        "hp": final_hp,
        "max_hp": final_hp,
        "atk": final_atk,
        "gold_range": (min_gold, max_gold),
        "exp": int(base["exp"] * affix["hp_mod"]),
        "skill": final_skill,
        "drop_item": base["drop_item"],
        "spawn_map": map_name
    }
