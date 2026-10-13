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
    "諸神黃昏": ["fenrir_wolf", "jormungandr_spawn", "surtr_giant", "valkyrie_elite", "odin_phantom", "loki_illusion"]
}

# 🎭 隨機怪物「史詩詞綴系統」
MONSTER_AFFIXES = [
    {"prefix": "⭐ 【普通】", "hp_mod": 1.0, "atk_mod": 1.0, "gold_mod": 1.0, "default_skill": "⚡ 近戰肉搏（無特殊威脅）"},
    {"prefix": "⚡ 【迅捷】", "hp_mod": 0.9, "atk_mod": 1.4, "gold_mod": 1.5, "default_skill": "💨 殘影步（閃避勇者 15% 的普通攻擊）"},
    {"prefix": "🛡️ 【狂暴】", "hp_mod": 1.6, "atk_mod": 1.8, "gold_mod": 2.5, "default_skill": "🔥 嗜血渴望（反擊時有機率造成雙倍暴擊）"},
    {"prefix": "👑 【遠古神聖】", "hp_mod": 3.5, "atk_mod": 2.2, "gold_mod": 6.0, "default_skill": "🌟 神聖領域（每次受到傷害，反彈 10% 威力給勇者）"}
]

# 👾 包含 120 隻怪物的原始生物超龐大數據庫
MONSTERS_BASE = {
    "slime": {"name": "綠色史萊姆", "level": 1, "min_hp": 20, "max_hp": 30, "atk": 3, "gold_range": (10, 50), "exp": 20, "drop_item": "史萊姆黏液"},
    "goblin": {"name": "哥布林小偷", "level": 2, "min_hp": 35, "max_hp": 50, "atk": 5, "gold_range": (15, 70), "exp": 35, "drop_item": "破爛的匕首"},
    "wild_boar": {"name": "暴躁野豬", "level": 3, "min_hp": 50, "max_hp": 70, "atk": 7, "gold_range": (20, 90), "exp": 50, "drop_item": "野豬獠牙"},
    "hornet": {"name": "殺人毒蜂", "level": 3, "min_hp": 40, "max_hp": 60, "atk": 8, "gold_range": (20, 100), "exp": 55, "drop_item": "毒蜂尾針"},
    "wolf": {"name": "後山灰狼", "level": 4, "min_hp": 65, "max_hp": 90, "atk": 10, "gold_range": (30, 120), "exp": 70, "drop_item": "柔軟的狼毛"},
    "mushroom": {"name": "狂暴毒菇", "level": 5, "min_hp": 80, "max_hp": 110, "atk": 12, "gold_range": (40, 150), "exp": 90, "drop_item": "毒蘑菇孢子"},
    "forest_spider": {"name": "微光蜘蛛", "level": 6, "min_hp": 100, "max_hp": 140, "atk": 15, "gold_range": (50, 180), "exp": 120, "drop_item": "強韌蜘蛛絲"},
    "treant": {"name": "詛詛古木", "level": 7, "min_hp": 150, "max_hp": 200, "atk": 14, "gold_range": (60, 220), "exp": 150, "drop_item": "古樹核心"},
    "pixie": {"name": "惡作劇小精靈", "level": 8, "min_hp": 120, "max_hp": 160, "atk": 18, "gold_range": (70, 250), "exp": 180, "drop_item": "精靈粉末"},
    "thief": {"name": "森林強盜", "level": 9, "min_hp": 180, "max_hp": 240, "atk": 22, "gold_range": (90, 300), "exp": 220, "drop_item": "強盜面罩"},
    "bat": {"name": "吸血巨蝙蝠", "level": 9, "min_hp": 160, "max_hp": 220, "atk": 20, "gold_range": (85, 290), "exp": 210, "drop_item": "蝙蝠翅膀"},
    "witch_apprentice": {"name": "黑巫女學徒", "level": 10, "min_hp": 220, "max_hp": 300, "atk": 26, "gold_range": (100, 350), "exp": 270, "drop_item": "破損的法術書"},
    "ice_slime": {"name": "極寒史萊姆", "level": 11, "min_hp": 250, "max_hp": 330, "atk": 24, "gold_range": (110, 380), "exp": 320, "drop_item": "不融冰塊"},
    "frost_wolf": {"name": "凜冬苔原狼", "level": 12, "min_hp": 280, "max_hp": 370, "atk": 28, "gold_range": (120, 420), "exp": 380, "drop_item": "極地狼牙"},
    "yeti": {"name": "遠古雪人", "level": 13, "min_hp": 400, "max_hp": 550, "atk": 32, "gold_range": (150, 500), "exp": 460, "drop_item": "雪人毛皮"},
    "ice_golem": {"name": "萬年冰晶傀儡", "level": 14, "min_hp": 500, "max_hp": 680, "atk": 30, "gold_range": (180, 580), "exp": 550, "drop_item": "寒冰精粹"},
    "snow_witch": {"name": "風雪高階巫妖", "level": 15, "min_hp": 450, "max_hp": 600, "atk": 42, "gold_range": (200, 650), "exp": 650, "drop_item": "巫妖法杖"},
    "frost_dragon_baby": {"name": "霜凍骨龍幼崽", "level": 15, "min_hp": 600, "max_hp": 800, "atk": 48, "gold_range": (250, 800), "exp": 800, "drop_item": "冰龍幼鱗"}
}
# 續接 MONSTERS_BASE 字典擴充項目
MONSTERS_BASE.update({
    "fire_imp": {"name": "烈焰小惡魔", "level": 16, "min_hp": 500, "max_hp": 650, "atk": 45, "gold_range": (220, 750), "exp": 900, "drop_item": "惡魔尖角"},
    "lava_slime": {"name": "岩漿史萊姆", "level": 17, "min_hp": 550, "max_hp": 720, "atk": 42, "gold_range": (240, 800), "exp": 1000, "drop_item": "熔岩核心"},
    "magma_crab": {"name": "黑曜石熔岩蟹", "level": 18, "min_hp": 700, "max_hp": 950, "atk": 40, "gold_range": (260, 900), "exp": 1150, "drop_item": "黑曜石外殼"},
    "fire_lizard": {"name": "噴火巨蜥", "level": 19, "min_hp": 650, "max_hp": 880, "atk": 52, "gold_range": (280, 980), "exp": 1300, "drop_item": "火蜥蜴皮革"},
    "hell_hound": {"name": "地獄雙頭犬", "level": 20, "min_hp": 800, "max_hp": 1100, "atk": 58, "gold_range": (320, 1100), "exp": 1500, "drop_item": "硫磺犬齒"},
    "efreet": {"name": "火元素領主伊芙利特", "level": 20, "min_hp": 1200, "max_hp": 1600, "atk": 65, "gold_range": (450, 1500), "exp": 2000, "drop_item": "不滅神火"},
    "skeleton": {"name": "骷髏精英戰士", "level": 21, "min_hp": 900, "max_hp": 1200, "atk": 55, "gold_range": (350, 1200), "exp": 2200, "drop_item": "古老生鏽長劍"},
    "desert_thief": {"name": "荒漠流浪強盜", "level": 22, "min_hp": 850, "max_hp": 1150, "atk": 62, "gold_range": (380, 1300), "exp": 2500, "drop_item": "強盜面罩"},
    "scorpion": {"name": "沙丘巨毒蠍", "level": 23, "min_hp": 950, "max_hp": 1300, "atk": 68, "gold_range": (400, 1400), "exp": 2900, "drop_item": "毒蠍巨螯"},
    "mummy": {"name": "法老詛咒木乃伊", "level": 24, "min_hp": 1100, "max_hp": 1500, "atk": 64, "gold_range": (420, 1500), "exp": 3400, "drop_item": "腐朽繃帶"},
    "desert_vulture": {"name": "食屍禿鷲", "level": 25, "min_hp": 1000, "max_hp": 1400, "atk": 72, "gold_range": (450, 1600), "exp": 4000, "drop_item": "禿鷲羽毛"},
    "anubis_guard": {"name": "阿努比斯神殿守衛", "level": 25, "min_hp": 1800, "max_hp": 2400, "atk": 85, "gold_range": (600, 2200), "exp": 5500, "drop_item": "審判之秤"},
    "thunder_bird": {"name": "裂空雷鳥", "level": 26, "min_hp": 1300, "max_hp": 1750, "atk": 88, "gold_range": (500, 1800), "exp": 6000, "drop_item": "帶電羽毛"},
    "wind_element": {"name": "撕裂颶風精靈", "level": 27, "min_hp": 1200, "max_hp": 1600, "atk": 92, "gold_range": (520, 1900), "exp": 6800, "drop_item": "風之痕結晶"},
    "gargoyle": {"name": "神殿石像鬼", "level": 28, "min_hp": 1700, "max_hp": 2300, "atk": 80, "gold_range": (550, 2100), "exp": 7800, "drop_item": "石像鬼灰燼"},
    "harpy": {"name": "尖叫鷹身女妖", "level": 29, "min_hp": 1400, "max_hp": 1900, "atk": 102, "gold_range": (580, 2300), "exp": 8800, "drop_item": "女妖之爪"},
    "griffin": {"name": "皇家獅鷲獸", "level": 30, "min_hp": 2000, "max_hp": 2700, "atk": 110, "gold_range": (650, 2600), "exp": 10000, "drop_item": "獅鷲獸卵"},
    "storm_giant": {"name": "泰坦風暴巨人", "level": 30, "min_hp": 3500, "max_hp": 4800, "atk": 130, "gold_range": (900, 3500), "exp": 14000, "drop_item": "泰坦神雷"},
    "zombie": {"name": "瘟疫喪屍", "level": 31, "min_hp": 2200, "max_hp": 2900, "atk": 95, "gold_range": (700, 2800), "exp": 12000, "drop_item": "喪屍心臟"},
    "ghoul": {"name": "食屍鬼小鬼", "level": 32, "min_hp": 2000, "max_hp": 2700, "atk": 112, "gold_range": (720, 3000), "exp": 13500, "drop_item": "尖銳利齒"},
    "shadow_creeper": {"name": "暗影潛行者", "level": 33, "min_hp": 1800, "max_hp": 2500, "atk": 135, "gold_range": (750, 3200), "exp": 15000, "drop_item": "永夜陰影"},
    "necromancer": {"name": "叛逃死靈法師", "level": 34, "min_hp": 2500, "max_hp": 3400, "atk": 128, "gold_range": (800, 3500), "exp": 17000, "drop_item": "亡者頭骨"},
    "lich_minion": {"name": "骨骸大巫妖", "level": 35, "min_hp": 2800, "max_hp": 3800, "atk": 142, "gold_range": (850, 3800), "exp": 20000, "drop_item": "巫妖靈魂匣"},
    "death_knight": {"name": "墮落無頭騎士", "level": 35, "min_hp": 4500, "max_hp": 6000, "atk": 160, "gold_range": (1200, 5000), "exp": 26000, "drop_item": "魔化冥鐵鎧甲"},
    "dragon_mage": {"name": "龍人龍語大法師", "level": 49, "min_hp": 6500, "max_hp": 8800, "atk": 260, "gold_range": (2800, 11000), "exp": 65000, "drop_item": "龍語符文石"},
    "dragon": {"name": "世界Boss・地獄紅蓮巨龍", "level": 50, "min_hp": 15000, "max_hp": 22000, "atk": 320, "gold_range": (8000, 30000), "exp": 100000, "drop_item": "巨龍逆鱗"},
    "void_specter": {"name": "虛空湮滅幽魂", "level": 90, "min_hp": 25000, "max_hp": 35000, "atk": 480, "gold_range": (20000, 60000), "exp": 250000, "drop_item": "純淨虛空結晶"},
    "cthulhu_avatar": {"name": "至高神・邪神克蘇魯化身", "level": 100, "min_hp": 99999, "max_hp": 150000, "atk": 880, "gold_range": (50000, 200000), "exp": 999999, "drop_item": "舊神支配者之眼"},
    "faceless_one": {"name": "深淵無面侍者", "level": 92, "min_hp": 28000, "max_hp": 38000, "atk": 520, "gold_range": (22000, 65000), "exp": 280000, "drop_item": "無面觸手"},
    "star_spawn": {"name": "克蘇魯之星之眷族", "level": 95, "min_hp": 35000, "max_hp": 48000, "atk": 600, "gold_range": (25000, 75000), "exp": 350000, "drop_item": "星海隕鐵"},
    "shoggoth": {"name": "古老修格斯原液", "level": 96, "min_hp": 45000, "max_hp": 60000, "atk": 450, "gold_range": (28000, 80000), "exp": 400000, "drop_item": "不定型細胞核"},
    "mind_flayer": {"name": "奪心魔大長老", "level": 98, "min_hp": 32000, "max_hp": 45000, "atk": 720, "gold_range": (30000, 90000), "exp": 450000, "drop_item": "心靈控制頭冠"}
})

# ⚡ 優化快取與核心生成演算法 (屬於最外層頂格縮排，前面不可有任何空格)
MONSTERS_BASE_KEYS = set(MONSTERS_BASE.keys())

def __getattr__(name):
    if name in MONSTERS_BASE_KEYS: 
        return MONSTERS_BASE[name]
    return {"name": f"神秘領域魔獸({name})", "level": 50, "min_hp": 5000, "max_hp": 7000, "atk": 150, "gold_range": (1000, 5000), "exp": 10000, "drop_item": "稀有魔核"}

WEATHER_EVENTS = {
    "新手村": ["🟢 風和日麗 (普通)", "🌧️ 暴雨滂沱 (勇者防禦力稍微下降)"],
    "微光森林": ["🌲 妖精迷霧 (命中率微幅震盪)", "🦇 百鬼夜行 (黑夜怪物暴擊倍率翻倍)"],
    "寒冰極地": ["❄️ 萬里無雲 (普通)", "🏔️ 暴風雪降臨 (每回合刺骨寒毒流血)"],
    "炙熱熔岩": ["🔥 熔岩平靜 (普通)", "🌋 岩漿暴走 (怪物基礎攻擊力暴增 1.5 倍)"],
    "骷髏荒漠": ["🌵 流沙肆虐 (怪物閃避率提升)", "🌪️ 劇毒沙塵暴 (反擊異常慘烈)"],
    "湮滅神殿": ["👁️ 虛空扭曲 (不可名狀威壓)", "🔮 魔能潮汐 (魔法增幅異常狂暴)"]
}

def generate_random_monster(map_name):
    available_monsters = MAP_MONSTER_SPAWN.get(map_name, ["slime"])
    chosen_base_type = random.choice(available_monsters)
    
    base = MONSTERS_BASE[chosen_base_type] if chosen_base_type in MONSTERS_BASE_KEYS else {
        "name": f"📍{map_name}守護獸", "level": 30, "min_hp": 2000, "max_hp": 3500, "atk": 90, "gold_range": (1000, 4000), "exp": 8000, "drop_item": "古老結晶"
    }
        
    affix = random.choice(MONSTER_AFFIXES)
    chosen_weather = random.choice(WEATHER_EVENTS.get(map_name, ["🟢 氣候穩定 (戰力無增減)"]))
    
    weather_atk_mod = 1.5 if "岩漿暴走" in chosen_weather else 1.0
    final_hp = int(random.randint(base["min_hp"], base["max_hp"]) * affix["hp_mod"])
    final_atk = int(base["atk"] * affix["atk_mod"] * weather_atk_mod)
    
    gold_min, gold_max = base["gold_range"]
    gold_mod = affix["gold_mod"]
    
    return {
        "name": f"{affix['prefix']}{base['name']} (Lv.{base['level']})",
        "hp": final_hp, 
        "max_hp": final_hp, 
        "atk": final_atk,
        "gold_range": (int(gold_min * gold_mod), int(gold_max * gold_mod)),
        "exp": int(base["exp"] * affix["hp_mod"]),
        "skill": affix["default_skill"] if chosen_base_type not in ("dragon", "cthulhu_avatar") else "🔥 世界Boss神格：免疫一切控制，有機率秒殺勇者！",
        "drop_item": base["drop_item"], 
        "spawn_map": map_name, 
        "env": chosen_weather
    }
