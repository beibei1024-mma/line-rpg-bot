import random

MAP_MONSTER_SPAWN = {
    "新手村": ["slime", "goblin"],
    "骷髏荒漠": ["skeleton", "desert_thief"],
    "巨龍巢穴": ["dragon_guard", "dragon"],
    "湮滅神殿": ["void_specter", "cthulhu_avatar"]
}

# 🌌 企劃 B：全新地圖氣候動態大數據庫
WEATHER_EVENTS = {
    "新手村": ["🟢 風和日麗 (普通)", "🌧️ 暴雨滂沱 (勇者防禦力稍微下降)"],
    "骷髏荒漠": ["🌵 流沙肆虐 (怪物閃避率提升)", "🌪️ 劇毒沙塵暴 (反擊異常慘烈)"],
    "巨龍巢穴": ["🔥 熔岩平靜 (普通)", "🌋 岩漿暴走 (怪物基礎攻擊力暴增 1.5 倍)"],
    "湮滅神殿": ["👁️ 虛空扭曲 (不可名狀威壓)", "🔮 魔能潮汐 (魔法增幅異常狂暴)"]
}

MONSTER_AFFIXES = [
    {"prefix": "⭐ 【普通】", "hp_mod": 1.0, "atk_mod": 1.0, "gold_mod": 1.0, "default_skill": "⚡ 近戰肉搏（無特殊威脅）"},
    {"prefix": "⚡ 【迅捷】", "hp_mod": 0.9, "atk_mod": 1.4, "gold_mod": 1.5, "default_skill": "💨 殘影步（閃避勇者 15% 的普通攻擊）"},
    {"prefix": "🛡️ 【狂暴】", "hp_mod": 1.6, "atk_mod": 1.8, "gold_mod": 2.5, "default_skill": "🔥 嗜血渴望（反擊時有機率造成雙倍暴擊）"},
    {"prefix": "👑 【遠古神聖】", "hp_mod": 3.5, "atk_mod": 2.2, "gold_mod": 6.0, "default_skill": "🌟 神聖領域（每次受到傷害，反彈 10% 威力給勇者）"}
]

MONSTERS_BASE = {
    "slime": {"name": "綠色史萊姆", "level": 1, "min_hp": 20, "max_hp": 30, "atk": 3, "gold_range": (10, 500), "exp": 500, "drop_item": "史萊姆黏液"},
    "goblin": {"name": "哥布林小偷", "level": 3, "min_hp": 45, "max_hp": 65, "atk": 7, "gold_range": (25, 1000), "exp": 1000, "drop_item": "破爛的匕首"},
    "desert_thief": {"name": "荒漠流浪強盜", "level": 12, "min_hp": 250, "max_hp": 350, "atk": 22, "gold_range": (200, 3000), "exp": 4500, "drop_item": "強盜面罩"},
    "skeleton": {"name": "骷髏精英戰士", "level": 15, "min_hp": 400, "max_hp": 550, "atk": 35, "gold_range": (400, 5000), "exp": 7000, "drop_item": "古老生鏽長劍"},
    "dragon_guard": {"name": "赤焰守護飛龍", "level": 22, "min_hp": 900, "max_hp": 1200, "atk": 65, "gold_range": (800, 8000), "exp": 15000, "drop_item": "飛龍雙翼"},
    "dragon": {"name": "世界Boss・地獄紅蓮巨龍", "level": 30, "min_hp": 3500, "max_hp": 5000, "atk": 120, "gold_range": (5000, 30000), "exp": 50000, "drop_item": "巨龍逆鱗"},
    "void_specter": {"name": "虛空湮滅幽魂", "level": 55, "min_hp": 2500, "max_hp": 3500, "atk": 180, "gold_range": (8000, 50000), "exp": 120000, "drop_item": "純淨虛空結晶"},
    "cthulhu_avatar": {"name": "至高神・邪神克蘇魯化身", "level": 80, "min_hp": 12000, "max_hp": 20000, "atk": 380, "gold_range": (50000, 200000), "exp": 500000, "drop_item": "舊神支配者之眼"}
}

BOSS_SKILLS = [
    "🔥 紅蓮業火（每回合空氣灼燒，勇者額外承受隨機熱毒）",
    "🌋 岩漿護體（巨龍防禦力在岩漿中大幅提升，免疫暴擊）",
    "🌪️ 巨龍威壓（遠古龍威降臨，勇者的攻擊力被壓制 20%）",
    "👁️精神污染（舊神凝視！每回合隨機瘋狂扣除勇者 20 點 MP 魔力）"
]

def generate_random_monster(map_name):
    """【企劃 B 優化】遭遇強敵時，高機率切換地圖隨機天氣環境狀態"""
    available_monsters = MAP_MONSTER_SPAWN.get(map_name, ["slime"])
    chosen_base_type = random.choice(available_monsters)
    base = MONSTERS_BASE[chosen_base_type]
    
    affix = random.choice(MONSTER_AFFIXES)
    
    # 隨機抽取目前地圖的當前天象氣候
    chosen_weather = random.choice(WEATHER_EVENTS.get(map_name, ["🟢 平靜"]))
    
    # 計算屬性增幅 (融入天氣要素)
    weather_atk_mod = 1.5 if "岩漿暴走" in chosen_weather else 1.0
    final_hp = int(random.randint(base["min_hp"], base["max_hp"]) * affix["hp_mod"])
    final_atk = int(base["atk"] * affix["atk_mod"] * weather_atk_mod)
    
    min_gold, max_gold = base["gold_range"][0], base["gold_range"][1]
    
    if chosen_base_type in ["dragon", "cthulhu_avatar"]:
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
        "gold_range": (int(min_gold * affix["gold_mod"]), int(max_gold * affix["gold_mod"])),
        "exp": int(base["exp"] * affix["hp_mod"]),
        "skill": final_skill,
        "drop_item": base["drop_item"],
        "spawn_map": map_name,
        "env": chosen_weather # 將環境保存入怪物的即時狀態
    }
