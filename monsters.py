# monsters.py - 皇家時空魔物動態生成工廠 v3.0

import random

# 🗺️ 全新 20 張地圖與怪物生成綁定庫（大分散架構）
MAP_MONSTER_SPAWN = {
    "新手村": ["slime", "goblin", "wild_boar", "hornet", "wolf", "mushroom"],
    "微光森林": ["forest_spider", "treant", "pixie", "thief", "bat", "witch_apprentice"],
    "寒冰極地": ["ice_slime", "frost_wolf", "yeti", "ice_golem", "snow_witch", "frost_dragon_baby"],
    "炙熱熔岩": ["fire_imp", "lava_slime", "magma_crab", "fire_lizard", "hell_hound", "efreet"],
    "骷髏荒漠": ["skeleton", "desert_thief", "scorpion", "mummy", "desert_vulture", "anubis_guard"],
    "風暴峽谷": ["thunder_bird", "wind_element", "gargoyle", "harpy", "griffin", "storm_giant"],
    "幽暗地窖": ["zombie", "ghoul", "shadow_creeper", "necromancer", "lich_minion", "death_knight"],
    "翡翠竹林": ["bamboo_panda", "green_snake", "fox_spirit", "ronin", "ninja", "bamboo_golem"],
    "亞特蘭提斯": ["merman", "shark_warrior", "sea_witch", "kraken_tentacle", "coral_golem", "poseidon_guard"],
    "天空之城": ["sky_whale", "angel_soldier", "pegasus", "valkyrie_scout", "archangel_pawn", "zeus_statue"],
    "巨龍巢穴": ["dragon_guard", "wyvern", "dragon_egg_thief", "drake", "dragon_mage", "dragon"],
    "精靈古都": ["elf_archer", "centaur", "unicorn", "dryad", "fairy_queen_guard", "ancient_protector"],
    "機械工廠": ["clockwork_spider", "drone", "steam_golem", "laser_turret", "cyborg_pawn", "mecha_boss_v1"],
    "迷霧沼澤": ["swamp_frog", "crocodile", "hydra_spawn", "will_o_wisp", "mud_monster", "swamp_witch"],
    "黃金陵墓": ["gold_beetle", "terracotta_warrior", "pharaoh_mummy", "sphinx_scout", "anubis_executioner", "cursed_gold_golem"],
    "翡翠天境": ["jade_butterfly", "feathered_serpent", "kirin_calf", "spirit_deer", "cloud_leopard", "jade_emperor_guard"],
    "遺忘孤島": ["pirate_skeleton", "cannibal_plant", "raptor", "giant_ape", "siren", "island_guardian"],
    "星空虛無": ["cosmic_jellyfish", "meteor_sprite", "nebula_stalker", "alien_soldier", "void_ray", "star_devourer"],
    "湮滅神殿": ["void_specter", "cthulhu_avatar", "faceless_one", "star_spawn", "shoggoth", "mind_flayer"],
    "諸神黃昏": ["fenrir_wolf", "jormungandr_spawn", "surtr_giant", "valkyrie_elite", "odin_phantom", "loki_illusion"]
}

# 🎭 隨機怪物「史詩詞綴系統」
MONSTER_AFFIXES = [
    {"prefix": "⭐【普通】", "hp_mod": 1.0, "atk_mod": 1.0, "gold_mod": 1.0, "default_skill": "⚡ 近戰肉搏（無特殊威脅）"},
    {"prefix": "⚡【迅捷】", "hp_mod": 0.9, "atk_mod": 1.4, "gold_mod": 1.5, "default_skill": "💨 殘影步（閃避勇者 15% 的普通攻擊）"},
    {"prefix": "🛡️【狂暴】", "hp_mod": 1.6, "atk_mod": 1.8, "gold_mod": 2.5, "default_skill": "🔥 嗜血渴望（反擊時有機率造成雙倍暴擊）"},
    {"prefix": "👑【遠古神聖】", "hp_mod": 3.5, "atk_mod": 2.2, "gold_mod": 6.0, "default_skill": "🌟 神聖領域（每次受到傷害，反彈 10% 威力給勇者）"}
]

# 🦾 各地圖階級動態補償器（當資料庫未手工填寫該怪物時，全自動公式化保底生成數值，100%防爆）
MAP_TIER_CONFIG = {
    "新手村": {"lvl": 2, "hp": 45, "atk": 6, "gold": (15, 60), "exp": 30, "drop": "小魔核"},
    "微光森林": {"lvl": 7, "hp": 140, "atk": 16, "gold": (60, 200), "exp": 140, "drop": "微光魔核"},
    "寒冰極地": {"lvl": 12, "hp": 350, "atk": 28, "gold": (130, 450), "exp": 400, "drop": "寒冰魔核"},
    "炙熱熔岩": {"lvl": 17, "hp": 650, "atk": 45, "gold": (250, 850), "exp": 1100, "drop": "熔岩魔核"},
    "骷髏荒漠": {"lvl": 22, "hp": 1000, "atk": 65, "gold": (400, 1300), "exp": 2800, "drop": "荒漠魔核"},
    "風暴峽谷": {"lvl": 28, "hp": 1800, "atk": 95, "gold": (600, 2200), "exp": 8000, "drop": "風暴魔核"},
    "幽暗地窖": {"lvl": 33, "hp": 3000, "atk": 130, "gold": (900, 3500), "exp": 16000, "drop": "地窖魔核"},
    "翡翠竹林": {"lvl": 38, "hp": 4500, "atk": 180, "gold": (1500, 5000), "exp": 28000, "drop": "竹林魔核"},
    "亞特蘭提斯": {"lvl": 43, "hp": 6500, "atk": 240, "gold": (2500, 8000), "exp": 45000, "drop": "深海魔核"},
    "天空之城": {"lvl": 48, "hp": 9000, "atk": 320, "gold": (4000, 12000), "exp": 75000, "drop": "天空魔核"},
    "巨龍巢穴": {"lvl": 53, "hp": 14000, "atk": 420, "gold": (6000, 18000), "exp": 130000, "drop": "巨龍魔核"},
    "精靈古都": {"lvl": 58, "hp": 22000, "atk": 550, "gold": (9000, 25000), "exp": 220000, "drop": "精靈魔核"},
    "機械工廠": {"lvl": 63, "hp": 35000, "atk": 720, "gold": (15000, 40000), "exp": 400000, "drop": "機械零件"},
    "迷霧沼澤": {"lvl": 68, "hp": 55000, "atk": 950, "gold": (25000, 65000), "exp": 750000, "drop": "沼澤毒腺"},
    "黃金陵墓": {"lvl": 73, "hp": 85000, "atk": 1300, "gold": (40000, 100000), "exp": 1500000, "drop": "陵墓古物"},
    "翡翠天境": {"lvl": 78, "hp": 140000, "atk": 1800, "gold": (70000, 160000), "exp": 3000000, "drop": "天境仙靈"},
    "遺忘孤島": {"lvl": 83, "hp": 220000, "atk": 2500, "gold": (120000, 260000), "exp": 6000000, "drop": "孤島化石"},
    "星空虛無": {"lvl": 88, "hp": 380000, "atk": 3600, "gold": (200000, 450000), "exp": 12000000, "drop": "星空殘渣"},
    "湮滅神殿": {"lvl": 94, "hp": 650000, "atk": 5200, "gold": (400000, 850000), "exp": 25000000, "drop": "湮滅觸手"},
    "諸神黃昏": {"lvl": 100, "hp": 1500000, "atk": 8800, "gold": (800000, 2000000), "exp": 60000000, "drop": "末日餘燼"}
}

# 👾 包含核心填寫怪物的精英數據庫 (其餘由上方自動依照地圖位階核算)
MONSTERS_BASE = {
    "slime": {"name": "綠色史萊姆", "level": 1, "min_hp": 20, "max_hp": 30, "atk": 3, "gold_range": (10, 50), "exp": 20, "drop_item": "史萊姆黏液"},
    "goblin": {"name": "哥布林小偷", "level": 2, "min_hp": 35, "max_hp": 50, "atk": 5, "gold_range": (15, 70), "exp": 35, "drop_item": "破爛的匕速"},
    "wild_boar": {"name": "暴躁野豬", "level": 3, "min_hp": 50, "max_hp": 70, "atk": 7, "gold_range": (20, 90), "exp": 50, "drop_item": "野豬獠牙"},
    "forest_spider": {"name": "微光蜘蛛", "level": 6, "min_hp": 100, "max_hp": 140, "atk": 15, "gold_range": (50, 180), "exp": 120, "drop_item": "強韌蜘蛛絲"},
    "treant": {"name": "詛咒古木", "level": 7, "min_hp": 150, "max_hp": 200, "atk": 14, "gold_range": (60, 220), "exp": 150, "drop_item": "古樹核心"},
    "ice_slime": {"name": "極寒史萊姆", "level": 11, "min_hp": 250, "max_hp": 330, "atk": 24, "gold_range": (110, 380), "exp": 320, "drop_item": "不融冰塊"},
    "fire_imp": {"name": "烈焰小惡魔", "level": 16, "min_hp": 500, "max_hp": 650, "atk": 45, "gold_range": (220, 750), "exp": 900, "drop_item": "惡魔尖角"},
    "magma_crab": {"name": "黑曜石熔岩蟹", "level": 18, "min_hp": 700, "max_hp": 950, "atk": 40, "gold_range": (260, 900), "exp": 1150, "drop_item": "黑曜石外殼"},
    "skeleton": {"name": "骷髏精英戰士", "level": 21, "min_hp": 900, "max_hp": 1200, "atk": 55, "gold_range": (350, 1200), "exp": 2200, "drop_item": "古老生鏽長劍"},
    "shadow_creeper": {"name": "暗影潛行者", "level": 33, "min_hp": 1800, "max_hp": 2500, "atk": 135, "gold_range": (750, 3200), "exp": 15000, "drop_item": "永夜陰影"},
    "dragon": {"name": "世界Boss・地獄紅蓮巨龍", "level": 50, "min_hp": 15000, "max_hp": 22000, "atk": 320, "gold_range": (8000, 30000), "exp": 100000, "drop_item": "巨龍逆鱗"},
    "cthulhu_avatar": {"name": "至高神・邪神克蘇魯化身", "level": 100, "min_hp": 99999, "max_hp": 150000, "atk": 880, "gold_range": (50000, 200000), "exp": 999999, "drop_item": "舊神支配者之眼"}
}

# 🌌 地圖動態氣候事件資料庫
WEATHER_EVENTS = {
    "新手村": ["🟢 風和日麗 (普通)", "🌧️ 暴雨滂沱 (勇者防禦力稍微下降)"],
    "微光森林": ["🌲 妖精迷霧 (命中率微幅震盪)", "🦇 百鬼夜行 (黑夜怪物暴擊倍率翻倍)"],
    "寒冰極地": ["❄️ 萬里無雲 (普通)", "🏔️ 暴風雪降臨 (每回合刺骨寒毒流血)"],
    "炙熱熔岩": ["🔥 熔岩平靜 (普通)", "🌋 岩漿暴走 (怪物基礎攻擊力暴增 1.5 倍)"],
    "骷髏荒漠": ["🌵 流沙肆虐 (怪物閃避率提升)", "🌪️ 劇毒沙塵暴 (反擊異常慘烈)"],
    "湮滅神殿": ["👁️ 虛空扭曲 (不可名狀威壓)", "🔮 魔能潮汐 (魔法增幅異常狂暴)"]
}

def generate_random_monster(map_name):
    """結合詞綴與地圖動態氣候，無死角動態泵出安全魔物封包"""
    available = MAP_MONSTER_SPAWN.get(map_name, ["slime"])
    chosen_id = random.choice(available)
    tier = MAP_TIER_CONFIG.get(map_name, MAP_TIER_CONFIG["新手村"])
    
    # 🔍 動態提取或保底泵出原始生物範本
    if chosen_id in MONSTERS_BASE:
        base = MONSTERS_BASE[chosen_id]
    else:
        # 當抽到未手工建置的其餘 100 多隻怪物時，全自動激活公式補償，保證體驗流暢！
        chinese_name = chosen_id.replace("_", " ").title()
        base = {"name": f"地境生靈·{chinese_name}", "level": tier["lvl"], "min_hp": int(tier["hp"]*0.8), "max_hp": int(tier["hp"]*1.2), "atk": tier["atk"], "gold_range": tier["gold"], "exp": tier["exp"], "drop_item": tier["drop"]}
        
    affix = random.choice(MONSTER_AFFIXES)
    weather = random.choice(WEATHER_EVENTS.get(map_name, ["🟢 氣候穩定 (戰力無增減)"]))
    
    # 氣候乘算加成
    weather_atk_mod = 1.5 if "岩漿暴走" in weather else 1.0
    final_hp = int(random.randint(base["min_hp"], base["max_hp"]) * affix["hp_mod"])
    final_atk = int(base["atk"] * affix["atk_mod"] * weather_atk_mod)
    
    # 世界 Boss 詞綴特判保護牆
    is_boss = chosen_id in ["dragon", "cthulhu_avatar"]
    skill_desc = "🔥 世界Boss神格：免疫一切控制，有機率秒殺勇者！" if is_boss else affix["default_skill"]
    
    return {
        "name": f"{affix['prefix']}{base['name']} (Lv.{base['level']})",
        "hp": final_hp, 
        "max_hp": final_hp, 
        "atk": final_atk,
        "gold_range": (int(base["gold_range"][0] * affix["gold_mod"]), int(base["gold_range"][1] * affix["gold_mod"])),
        "exp": int(base["exp"] * affix["hp_mod"]),
        "skill": skill_desc,
        "drop_item": base["drop_item"], 
        "spawn_map": map_name, 
        "env": weather
    }
