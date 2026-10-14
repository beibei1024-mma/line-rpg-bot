import random

# 🗺️ 擴建後的 25 張地圖與怪物生成綁定庫（100% 完整對齊 20 張野外地圖 + 5 大打寶副本）
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
    "湮滅神殿": ["void_specter", "faceless_one", "star_spawn", "shoggoth", "mind_flayer", "cthulhu_avatar"],
    "諸神黃昏": ["fenrir_wolf", "jormungandr_spawn", "surtr_giant", "valkyrie_elite", "odin_phantom", "loki_illusion"],
    # 🔮 專屬打寶副本地圖與守關魔王生成對照鏈接
    "幽冥礦坑[20等副本]": ["sub_boss_20"],
    "沉沒古船[40等副本]": ["sub_boss_40"],
    "不朽王陵[60等副本]": ["sub_boss_60"],
    "天外天境[80等副本]": ["sub_boss_80"],
    "諸神黃昏[100等副本]": ["sub_boss_100"]
}

MONSTER_AFFIXES = [
    {"prefix": "⭐ 【普通】", "hp_mod": 1.0, "atk_mod": 1.0, "gold_mod": 1.0, "default_skill": "⚡ 近戰肉搏（無特殊威脅）"},
    {"prefix": "⚡ 【迅捷】", "hp_mod": 0.9, "atk_mod": 1.4, "gold_mod": 1.5, "default_skill": "💨 殘影步（閃避勇者 15% 的普通攻擊）"},
    {"prefix": "🛡️ 【狂暴】", "hp_mod": 1.6, "atk_mod": 1.8, "gold_mod": 2.5, "default_skill": "🔥 嗜血渴望（反擊時有機率造成雙倍暴擊）"},
    {"prefix": "👑 【遠古神聖】", "hp_mod": 3.5, "atk_mod": 2.2, "gold_mod": 6.0, "default_skill": "🌟 神聖領域（每次受到傷害，反彈 10% 威力給勇者）"}
]

MONSTERS_BASE = {
    # Lv.1~5 新手村
    "slime": {"name": "綠色史萊姆", "level": 1, "min_hp": 20, "max_hp": 30, "atk": 3, "gold_range": (10, 50), "exp": 20, "drop_item": "史萊姆黏液"},
    "goblin": {"name": "哥布林小偷", "level": 2, "min_hp": 35, "max_hp": 50, "atk": 5, "gold_range": (15, 70), "exp": 35, "drop_item": "破爛的匕首"},
    "wild_boar": {"name": "暴躁野豬", "level": 3, "min_hp": 50, "max_hp": 70, "atk": 7, "gold_range": (20, 90), "exp": 50, "drop_item": "野豬獠牙"},
    "hornet": {"name": "殺人毒蜂", "level": 3, "min_hp": 40, "max_hp": 60, "atk": 8, "gold_range": (20, 100), "exp": 55, "drop_item": "毒蜂尾針"},
    "wolf": {"name": "後山灰狼", "level": 4, "min_hp": 65, "max_hp": 90, "atk": 10, "gold_range": (30, 120), "exp": 70, "drop_item": "柔軟的狼毛"},
    "mushroom": {"name": "狂暴毒菇", "level": 5, "min_hp": 80, "max_hp": 110, "atk": 12, "gold_range": (40, 150), "exp": 90, "drop_item": "毒蘑菇孢子"},
    # Lv.6~10 微光森林
    "forest_spider": {"name": "微光蜘蛛", "level": 6, "min_hp": 100, "max_hp": 140, "atk": 15, "gold_range": (50, 180), "exp": 120, "drop_item": "強韌蜘蛛絲"},
    "treant": {"name": "詛咒古木", "level": 7, "min_hp": 150, "max_hp": 200, "atk": 14, "gold_range": (60, 220), "exp": 150, "drop_item": "古樹核心"},
    "pixie": {"name": "惡作劇小精靈", "level": 8, "min_hp": 120, "max_hp": 160, "atk": 18, "gold_range": (70, 250), "exp": 180, "drop_item": "精靈粉末"},
    "thief": {"name": "森林強盜", "level": 9, "min_hp": 180, "max_hp": 240, "atk": 22, "gold_range": (90, 300), "exp": 220, "drop_item": "強盜面罩"},
    "bat": {"name": "吸血巨蝙蝠", "level": 9, "min_hp": 160, "max_hp": 220, "atk": 20, "gold_range": (85, 290), "exp": 210, "drop_item": "蝙蝠翅膀"},
    "witch_apprentice": {"name": "黑巫女學徒", "level": 10, "min_hp": 220, "max_hp": 300, "atk": 26, "gold_range": (100, 350), "exp": 270, "drop_item": "破損的法術書"},
    # Lv.11~15 寒冰極地
    "ice_slime": {"name": "極寒史萊姆", "level": 11, "min_hp": 250, "max_hp": 330, "atk": 24, "gold_range": (110, 380), "exp": 320, "drop_item": "不融冰塊"},
    "frost_wolf": {"name": "凜冬苔原狼", "level": 12, "min_hp": 280, "max_hp": 370, "atk": 28, "gold_range": (120, 420), "exp": 380, "drop_item": "極地狼牙"},
    "yeti": {"name": "遠古雪人", "level": 13, "min_hp": 400, "max_hp": 550, "atk": 32, "gold_range": (150, 500), "exp": 460, "drop_item": "雪人毛皮"},
    "ice_golem": {"name": "萬年冰晶傀儡", "level": 14, "min_hp": 500, "max_hp": 680, "atk": 30, "gold_range": (180, 580), "exp": 550, "drop_item": "寒冰精粹"},
    "snow_witch": {"name": "風雪高階巫妖", "level": 15, "min_hp": 450, "max_hp": 600, "atk": 42, "gold_range": (200, 650), "exp": 650, "drop_item": "巫妖法杖"},
    "frost_dragon_baby": {"name": "霜凍骨龍幼崽", "level": 15, "min_hp": 600, "max_hp": 800, "atk": 48, "gold_range": (250, 800), "exp": 800, "drop_item": "冰龍幼鱗"},
    # Lv.16~20 炙熱熔岩
    "fire_imp": {"name": "烈焰小惡魔", "level": 16, "min_hp": 500, "max_hp": 650, "atk": 45, "gold_range": (220, 750), "exp": 900, "drop_item": "惡魔尖角"},
    "lava_slime": {"name": "岩漿史萊姆", "level": 17, "min_hp": 550, "max_hp": 720, "atk": 42, "gold_range": (240, 800), "exp": 1000, "drop_item": "熔岩核心"},
    "magma_crab": {"name": "黑曜石熔岩蟹", "level": 18, "min_hp": 700, "max_hp": 950, "atk": 40, "gold_range": (260, 900), "exp": 1150, "drop_item": "黑曜石外殼"},
    "fire_lizard": {"name": "噴火巨蜥", "level": 19, "min_hp": 650, "max_hp": 880, "atk": 52, "gold_range": (280, 980), "exp": 1300, "drop_item": "火蜥蜴皮革"},
    "hell_hound": {"name": "地獄雙頭犬", "level": 20, "min_hp": 800, "max_hp": 1100, "atk": 58, "gold_range": (320, 1100), "exp": 1500, "drop_item": "硫磺犬齒"},
    "efreet": {"name": "火元素領主伊芙利特", "level": 20, "min_hp": 1200, "max_hp": 1600, "atk": 65, "gold_range": (450, 1500), "exp": 2000, "drop_item": "不滅神火"},
    # Lv.21~25 骷髏荒漠
    "skeleton": {"name": "骷髏精英戰士", "level": 21, "min_hp": 900, "max_hp": 1200, "atk": 55, "gold_range": (350, 1200), "exp": 2200, "drop_item": "古老生鏽長劍"},
    "desert_thief": {"name": "荒漠流浪強盜", "level": 22, "min_hp": 850, "max_hp": 1150, "atk": 62, "gold_range": (380, 1300), "exp": 2500, "drop_item": "強盜面罩"},
    "scorpion": {"name": "沙丘巨毒蠍", "level": 23, "min_hp": 950, "max_hp": 1300, "atk": 68, "gold_range": (400, 1400), "exp": 2900, "drop_item": "毒蠍巨螯"},
    "mummy": {"name": "法老詛咒木乃伊", "level": 24, "min_hp": 1100, "max_hp": 1500, "atk": 64, "gold_range": (420, 1500), "exp": 3400, "drop_item": "腐朽繃帶"},
    "desert_vulture": {"name": "食屍禿鷲", "level": 25, "min_hp": 1000, "max_hp": 1400, "atk": 72, "gold_range": (450, 1600), "exp": 4000, "drop_item": "禿鷲羽毛"},
    "anubis_guard": {"name": "阿努比斯神殿守衛", "level": 25, "min_hp": 1800, "max_hp": 2400, "atk": 85, "gold_range": (600, 2200), "exp": 5500, "drop_item": "審判之秤"},
    # Lv.26~30 風暴峽谷
    "thunder_bird": {"name": "裂空雷鳥", "level": 26, "min_hp": 1300, "max_hp": 1750, "atk": 88, "gold_range": (500, 1800), "exp": 6000, "drop_item": "帶電羽毛"},
    "wind_element": {"name": "撕裂颶風精靈", "level": 27, "min_hp": 1200, "max_hp": 1600, "atk": 92, "gold_range": (520, 1900), "exp": 6800, "drop_item": "風之痕結晶"},
    "gargoyle": {"name": "神殿石像鬼", "level": 28, "min_hp": 1700, "max_hp": 2300, "atk": 80, "gold_range": (550, 2100), "exp": 7800, "drop_item": "石像鬼灰燼"},
    "harpy": {"name": "尖叫鷹身女妖", "level": 29, "min_hp": 1400, "max_hp": 1900, "atk": 102, "gold_range": (580, 2300), "exp": 8800, "drop_item": "女妖之爪"},
    "griffin": {"name": "皇家獅鷲獸", "level": 30, "min_hp": 2000, "max_hp": 2700, "atk": 110, "gold_range": (650, 2600), "exp": 10000, "drop_item": "獅鷲獸卵"},
    "storm_giant": {"name": "泰坦風暴巨人", "level": 30, "min_hp": 3500, "max_hp": 4800, "atk": 130, "gold_range": (900, 3500), "exp": 14000, "drop_item": "泰坦神雷"},
    # Lv.31~35 幽暗地窖
    "zombie": {"name": "瘟疫喪屍", "level": 31, "min_hp": 2200, "max_hp": 2900, "atk": 95, "gold_range": (700, 2800), "exp": 12000, "drop_item": "喪屍心臟"},
    "ghoul": {"name": "食屍鬼小鬼", "level": 32, "min_hp": 2000, "max_hp": 2700, "atk": 112, "gold_range": (720, 3000), "exp": 13500, "drop_item": "尖銳利齒"},
    "shadow_creeper": {"name": "暗影潛行者", "level": 33, "min_hp": 1800, "max_hp": 2500, "atk": 135, "gold_range": (750, 3200), "exp": 15000, "drop_item": "永夜陰影"},
    "necromancer": {"name": "叛逃死靈法師", "level": 34, "min_hp": 2500, "max_hp": 3400, "atk": 128, "gold_range": (800, 3500), "exp": 17000, "drop_item": "亡者頭骨"},
    "lich_minion": {"name": "骨骸大巫妖", "level": 35, "min_hp": 2800, "max_hp": 3800, "atk": 142, "gold_range": (850, 3800), "exp": 20000, "drop_item": "巫妖靈魂匣"},
    "death_knight": {"name": "墮落無頭騎士", "level": 35, "min_hp": 4500, "max_hp": 6000, "atk": 160, "gold_range": (1200, 5000), "exp": 26000, "drop_item": "魔化冥鐵鎧甲"},
    # Lv.36~40 翡翠竹林
    "bamboo_panda": {"name": "狂暴鐵掌熊貓", "level": 36, "min_hp": 3200, "max_hp": 4200, "atk": 150, "gold_range": (1000, 4000), "exp": 22000, "drop_item": "百年翠竹"},
    "green_snake": {"name": "竹葉劇毒青蛇", "level": 37, "min_hp": 2900, "max_hp": 3900, "atk": 165, "gold_range": (1100, 4200), "exp": 24000, "drop_item": "青蛇毒囊"},
    "fox_spirit": {"name": "九尾妖狐幻影", "level": 38, "min_hp": 3400, "max_hp": 4500, "atk": 175, "gold_range": (1200, 4600), "exp": 27000, "drop_item": "妖狐靈珠"},
    "ronin": {"name": "墮落東方浪人", "level": 39, "min_hp": 3800, "max_hp": 5000, "atk": 185, "gold_range": (1300, 5000), "exp": 30000, "drop_item": "斷裂名刀"},
    "ninja": {"name": "影流上忍刺客", "level": 40, "min_hp": 3600, "max_hp": 4800, "atk": 200, "gold_range": (1500, 5500), "exp": 34000, "drop_item": "暗影手裡劍"},
    "bamboo_golem": {"name": "萬年翠竹巨像", "level": 40, "min_hp": 5200, "max_hp": 6800, "atk": 190, "gold_range": (1800, 6200), "exp": 38000, "drop_item": "翡翠竹心"},
    # Lv.41~45 亞特蘭提斯
    "merman": {"name": "深海狂戰人魚", "level": 41, "min_hp": 4200, "max_hp": 5500, "atk": 195, "gold_range": (1600, 5800), "exp": 36000, "drop_item": "人魚彩鱗"},
    "shark_warrior": {"name": "巨齒鯊人戰士", "level": 42, "min_hp": 4800, "max_hp": 6200, "atk": 210, "gold_range": (1750, 6200), "exp": 40000, "drop_item": "深海鯊齒"},
    "sea_witch": {"name": "深淵海巫妖姬", "level": 43, "min_hp": 4400, "max_hp": 5800, "atk": 225, "gold_range": (1900, 6800), "exp": 44000, "drop_item": "海巫魔珠"},
    "kraken_tentacle": {"name": "克拉肯巨型觸手", "level": 44, "min_hp": 5500, "max_hp": 7200, "atk": 215, "gold_range": (2100, 7500), "exp": 48000, "drop_item": "深海吸盤"},
    "coral_golem": {"name": "遠古珊瑚魔像", "level": 45, "min_hp": 6200, "max_hp": 8000, "atk": 205, "gold_range": (2300, 8000), "exp": 52000, "drop_item": "七彩珊瑚核"},
    "poseidon_guard": {"name": "波賽頓皇家禁衛", "level": 45, "min_hp": 7500, "max_hp": 9500, "atk": 240, "gold_range": (2800, 9500), "exp": 58000, "drop_item": "海神三叉戟碎片"},
    # Lv.46~50 天空之城 & 巨龍巢穴
    "sky_whale": {"name": "雲海浮空巨鯨", "level": 46, "min_hp": 6800, "max_hp": 8800, "atk": 220, "gold_range": (2400, 8500), "exp": 54000, "drop_item": "空鯨浮游石"},
    "angel_soldier": {"name": "神殿熾翼戰兵", "level": 47, "min_hp": 5800, "max_hp": 7500, "atk": 245, "gold_range": (2600, 9000), "exp": 58000, "drop_item": "純白羽翼"},
    "pegasus": {"name": "天界雷霆飛馬", "level": 48, "min_hp": 6200, "max_hp": 8200, "atk": 255, "gold_range": (2700, 9600), "exp": 62000, "drop_item": "天馬金色鬃毛"},
    "valkyrie_scout": {"name": "女武神先鋒斥候", "level": 49, "min_hp": 6600, "max_hp": 8600, "atk": 270, "gold_range": (2900, 10500), "exp": 66000, "drop_item": "女武神戰羽"},
    "archangel_pawn": {"name": "審判大天使代行者", "level": 50, "min_hp": 8500, "max_hp": 11000, "atk": 290, "gold_range": (3500, 12000), "exp": 75000, "drop_item": "神聖光輝聖典"},
    "zeus_statue": {"name": "雷神宙斯黃金神像", "level": 50, "min_hp": 11000, "max_hp": 14500, "atk": 310, "gold_range": (4500, 15000), "exp": 85000, "drop_item": "神罰雷霆核心"},
    "dragon_guard": {"name": "紅蓮龍血近衛", "level": 47, "min_hp": 6000, "max_hp": 7800, "atk": 240, "gold_range": (2500, 9000), "exp": 56000, "drop_item": "龍血結晶"},
    "wyvern": {"name": "雙足飛龍掠奪者", "level": 48, "min_hp": 6400, "max_hp": 8400, "atk": 255, "gold_range": (2700, 9800), "exp": 60000, "drop_item": "飛龍翼膜"},
    "dragon_egg_thief": {"name": "盜龍卵暗影獵手", "level": 48, "min_hp": 5500, "max_hp": 7200, "atk": 265, "gold_range": (3000, 11000), "exp": 62000, "drop_item": "石化龍卵殼"},
    "drake": {"name": "熔岩亞龍巨獸", "level": 49, "min_hp": 7800, "max_hp": 10000, "atk": 275, "gold_range": (3200, 11500), "exp": 68000, "drop_item": "亞龍心臟"},
    "dragon_mage": {"name": "龍人龍語大法師", "level": 49, "min_hp": 6500, "max_hp": 8800, "atk": 260, "gold_range": (2800, 11000), "exp": 65000, "drop_item": "龍語符文石"},
    "dragon": {"name": "世界Boss・地獄紅蓮巨龍", "level": 50, "min_hp": 15000, "max_hp": 22000, "atk": 320, "gold_range": (8000, 30000), "exp": 100000, "drop_item": "巨龍逆鱗"},
    # Lv.55 精靈古都
    "elf_archer": {"name": "精靈王庭神射手", "level": 55, "min_hp": 8500, "max_hp": 11000, "atk": 290, "gold_range": (3500, 12000), "exp": 78000, "drop_item": "精靈翠綠長弓弦"},
    "centaur": {"name": "半人馬皇家鐵騎", "level": 56, "min_hp": 9500, "max_hp": 12500, "atk": 305, "gold_range": (3800, 13000), "exp": 82000, "drop_item": "半人馬戰蹄鐵"},
    "unicorn": {"name": "墮落聖光獨角獸", "level": 57, "min_hp": 10000, "max_hp": 13500, "atk": 320, "gold_range": (4200, 14500), "exp": 88000, "drop_item": "獨角獸螺旋聖角"},
    "dryad": {"name": "世界樹魅惑樹精", "level": 58, "min_hp": 9200, "max_hp": 12000, "atk": 315, "gold_range": (4000, 14000), "exp": 85000, "drop_item": "世界樹生命露珠"},
    "fairy_queen_guard": {"name": "妖精女王親衛隊長", "level": 59, "min_hp": 11500, "max_hp": 15000, "atk": 340, "gold_range": (4800, 16000), "exp": 95000, "drop_item": "妖精王冠寶石"},
    "ancient_protector": {"name": "太古世界樹守護巨木", "level": 60, "min_hp": 15000, "max_hp": 20000, "atk": 360, "gold_range": (6000, 20000), "exp": 110000, "drop_item": "世界樹萬年枝幹"},
    # Lv.60 機械工廠
    "clockwork_spider": {"name": "發條自爆機械蛛", "level": 61, "min_hp": 11000, "max_hp": 14500, "atk": 350, "gold_range": (5000, 16500), "exp": 105000, "drop_item": "精密發條齒輪"},
    "drone": {"name": "天網殲滅無人機", "level": 62, "min_hp": 10500, "max_hp": 13800, "atk": 370, "gold_range": (5200, 17500), "exp": 112000, "drop_item": "高能雷射晶體"},
    "steam_golem": {"name": "高壓蒸汽重裝泰坦", "level": 63, "min_hp": 14500, "max_hp": 19000, "atk": 355, "gold_range": (5800, 19000), "exp": 120000, "drop_item": "蒸汽動力爐心"},
    "laser_turret": {"name": "全自動粒子防禦砲塔", "level": 64, "min_hp": 12500, "max_hp": 16500, "atk": 395, "gold_range": (6200, 21000), "exp": 128000, "drop_item": "超導粒子線圈"},
    "cyborg_pawn": {"name": "生化改造狂戰兵", "level": 65, "min_hp": 13500, "max_hp": 17800, "atk": 410, "gold_range": (6500, 22000), "exp": 135000, "drop_item": "納米記憶晶片"},
    "mecha_boss_v1": {"name": "終結者・蒸汽機神零號機", "level": 65, "min_hp": 18000, "max_hp": 24000, "atk": 440, "gold_range": (8500, 28000), "exp": 155000, "drop_item": "機神不滅合金"},
    # Lv.65 迷霧沼澤
    "swamp_frog": {"name": "劇毒深淵巨蟾", "level": 66, "min_hp": 14000, "max_hp": 18500, "atk": 390, "gold_range": (6800, 22000), "exp": 140000, "drop_item": "巨蟾劇毒腺體"},
    "crocodile": {"name": "遠古裝甲帝王鱷", "level": 67, "min_hp": 16500, "max_hp": 21500, "atk": 415, "gold_range": (7200, 24000), "exp": 150000, "drop_item": "帝王鱷硬鱗"},
    "hydra_spawn": {"name": "九頭蛇劇毒幼體", "level": 68, "min_hp": 17500, "max_hp": 23000, "atk": 435, "gold_range": (7800, 26000), "exp": 162000, "drop_item": "九頭蛇再生毒牙"},
    "will_o_wisp": {"name": "迷霧噬魂鬼火", "level": 69, "min_hp": 13500, "max_hp": 17500, "atk": 450, "gold_range": (8000, 27000), "exp": 170000, "drop_item": "幽冥魂火結晶"},
    "mud_monster": {"name": "萬年腐敗泥沼巨怪", "level": 70, "min_hp": 20000, "max_hp": 26000, "atk": 420, "gold_range": (8500, 28500), "exp": 180000, "drop_item": "深淵腐殖核心"},
    "swamp_witch": {"name": "迷霧沼澤黑巫后", "level": 70, "min_hp": 18500, "max_hp": 24500, "atk": 470, "gold_range": (10000, 32000), "exp": 195000, "drop_item": "黑巫后詛咒魔杖"},
    # Lv.70 黃金陵墓
    "gold_beetle": {"name": "噬金聖甲蟲群", "level": 71, "min_hp": 16000, "max_hp": 21000, "atk": 440, "gold_range": (9500, 32000), "exp": 185000, "drop_item": "純金聖甲蟲殼"},
    "terracotta_warrior": {"name": "不朽帝王兵馬俑", "level": 72, "min_hp": 19000, "max_hp": 25000, "atk": 455, "gold_range": (10000, 34000), "exp": 195000, "drop_item": "千年古銅戈"},
    "pharaoh_mummy": {"name": "黃金法老王禁衛木乃伊", "level": 73, "min_hp": 21000, "max_hp": 27500, "atk": 475, "gold_range": (11000, 36000), "exp": 205000, "drop_item": "法老黃金面具"},
    "sphinx_scout": {"name": "獅身人面像守陵者", "level": 74, "min_hp": 23000, "max_hp": 30000, "atk": 490, "gold_range": (12000, 39000), "exp": 218000, "drop_item": "斯芬克斯之謎石板"},
    "anubis_executioner": {"name": "冥神阿努比斯處刑官", "level": 75, "min_hp": 24500, "max_hp": 32000, "atk": 515, "gold_range": (13500, 42000), "exp": 230000, "drop_item": "冥界死神鐮刃"},
    "cursed_gold_golem": {"name": "詛咒黃金法老巨像", "level": 75, "min_hp": 29000, "max_hp": 38000, "atk": 530, "gold_range": (16000, 50000), "exp": 250000, "drop_item": "太陽神黃金聖徽"},
    # Lv.75 翡翠天境
    "jade_butterfly": {"name": "仙靈翡翠幻蝶", "level": 76, "min_hp": 19500, "max_hp": 25500, "atk": 485, "gold_range": (12500, 40000), "exp": 225000, "drop_item": "仙靈蝶翼麟粉"},
    "feathered_serpent": {"name": "天境羽蛇神使", "level": 77, "min_hp": 22000, "max_hp": 28500, "atk": 510, "gold_range": (13500, 43000), "exp": 238000, "drop_item": "碧玉羽蛇鱗"},
    "kirin_calf": {"name": "瑞獸紫電麒麟幼崽", "level": 78, "min_hp": 25000, "max_hp": 32500, "atk": 535, "gold_range": (15000, 46000), "exp": 252000, "drop_item": "麒麟祥瑞真血"},
    "spirit_deer": {"name": "九色瑤池仙鹿", "level": 79, "min_hp": 23500, "max_hp": 30500, "atk": 520, "gold_range": (14500, 45000), "exp": 245000, "drop_item": "九色仙鹿茸"},
    "cloud_leopard": {"name": "踏雲雷光神豹", "level": 80, "min_hp": 26500, "max_hp": 34500, "atk": 560, "gold_range": (16000, 49000), "exp": 265000, "drop_item": "雷光神豹利爪"},
    "jade_emperor_guard": {"name": "凌霄天宮金甲神將", "level": 80, "min_hp": 33000, "max_hp": 43000, "atk": 590, "gold_range": (19000, 58000), "exp": 290000, "drop_item": "凌霄神將金甲片"},
    # Lv.80 遺忘孤島
    "pirate_skeleton": {"name": "被詛咒的海盜骷髏長", "level": 81, "min_hp": 24000, "max_hp": 31000, "atk": 540, "gold_range": (15500, 48000), "exp": 260000, "drop_item": "海盜王詛咒金幣"},
    "cannibal_plant": {"name": "蠻荒巨型霸王食人花", "level": 82, "min_hp": 27000, "max_hp": 35000, "atk": 555, "gold_range": (16500, 51000), "exp": 275000, "drop_item": "霸王花劇毒花蜜"},
    "raptor": {"name": "史前狂暴迅猛龍", "level": 83, "min_hp": 26000, "max_hp": 33500, "atk": 585, "gold_range": (17500, 53000), "exp": 285000, "drop_item": "迅猛龍撕裂趾爪"},
    "giant_ape": {"name": "孤島霸主・泰坦金剛", "level": 84, "min_hp": 34000, "max_hp": 44000, "atk": 600, "gold_range": (19000, 58000), "exp": 305000, "drop_item": "泰坦金剛巨牙"},
    "siren": {"name": "滅世歌姬・深淵海妖塞壬", "level": 85, "min_hp": 28000, "max_hp": 36500, "atk": 625, "gold_range": (20000, 62000), "exp": 320000, "drop_item": "海妖塞壬之淚"},
    "island_guardian": {"name": "遠古失落孤島石神", "level": 85, "min_hp": 38000, "max_hp": 49000, "atk": 640, "gold_range": (23000, 68000), "exp": 345000, "drop_item": "遠古孤島神核"},
    # Lv.85 星空虛無
    "cosmic_jellyfish": {"name": "星海漂流虛空水母", "level": 86, "min_hp": 29000, "max_hp": 37500, "atk": 610, "gold_range": (21000, 64000), "exp": 330000, "drop_item": "星海螢光觸鬚"},
    "meteor_sprite": {"name": "隕石火核星靈", "level": 87, "min_hp": 31000, "max_hp": 40000, "atk": 635, "gold_range": (22000, 66000), "exp": 345000, "drop_item": "天外隕鐵核心"},
    "nebula_stalker": {"name": "星雲暗影潛獵者", "level": 88, "min_hp": 32500, "max_hp": 42000, "atk": 660, "gold_range": (23500, 70000), "exp": 365000, "drop_item": "星雲濃縮暗物質"},
    "alien_soldier": {"name": "高等星際殖民戰兵", "level": 89, "min_hp": 35000, "max_hp": 45000, "atk": 680, "gold_range": (25000, 74000), "exp": 385000, "drop_item": "外星反物質電池"},
    "void_ray": {"name": "虛空裂艦相位光鰩", "level": 90, "min_hp": 38000, "max_hp": 49000, "atk": 700, "gold_range": (27000, 78000), "exp": 410000, "drop_item": "虛空相位稜鏡"},
    "star_devourer": {"name": "吞星巨獸・宇宙黑洞使徒", "level": 90, "min_hp": 46000, "max_hp": 60000, "atk": 730, "gold_range": (32000, 90000), "exp": 450000, "drop_item": "黑洞奇點核心"},
    # Lv.90~100 湮滅神殿
    "void_specter": {"name": "虛空湮滅幽魂", "level": 90, "min_hp": 25000, "max_hp": 35000, "atk": 480, "gold_range": (20000, 60000), "exp": 250000, "drop_item": "純淨虛空結晶"},
    "faceless_one": {"name": "深淵無面侍者", "level": 92, "min_hp": 28000, "max_hp": 38000, "atk": 520, "gold_range": (22000, 65000), "exp": 280000, "drop_item": "無面觸手"},
    "star_spawn": {"name": "克蘇魯之星之眷族", "level": 95, "min_hp": 35000, "max_hp": 48000, "atk": 600, "gold_range": (25000, 75000), "exp": 350000, "drop_item": "星海隕鐵"},
    "shoggoth": {"name": "古老修格斯原液", "level": 96, "min_hp": 45000, "max_hp": 60000, "atk": 450, "gold_range": (28000, 80000), "exp": 400000, "drop_item": "不定型細胞核"},
    "mind_flayer": {"name": "奪心魔大長老", "level": 98, "min_hp": 32000, "max_hp": 45000, "atk": 720, "gold_range": (30000, 90000), "exp": 450000, "drop_item": "心靈控制頭冠"},
    "cthulhu_avatar": {"name": "至高神・邪神克蘇魯化身", "level": 100, "min_hp": 99999, "max_hp": 150000, "atk": 880, "gold_range": (50000, 200000), "exp": 999999, "drop_item": "舊神支配者之眼"},
    # Lv.100 諸神黃昏
    "fenrir_wolf": {"name": "噬日魔狼・芬里爾", "level": 100, "min_hp": 65000, "max_hp": 85000, "atk": 780, "gold_range": (38000, 110000), "exp": 550000, "drop_item": "芬里爾斷裂神鏈"},
    "jormungandr_spawn": {"name": "塵世巨蟒・耶夢加得之影", "level": 100, "min_hp": 75000, "max_hp": 98000, "atk": 800, "gold_range": (40000, 120000), "exp": 600000, "drop_item": "塵世巨蟒逆鱗"},
    "surtr_giant": {"name": "穆斯貝爾火焰巨人王・蘇爾特爾", "level": 100, "min_hp": 85000, "max_hp": 115000, "atk": 850, "gold_range": (45000, 140000), "exp": 680000, "drop_item": "滅世炎魔之劍碎片"},
    "valkyrie_elite": {"name": "英靈殿至高女武神・布倫希爾德", "level": 100, "min_hp": 70000, "max_hp": 92000, "atk": 820, "gold_range": (42000, 130000), "exp": 640000, "drop_item": "英靈殿不朽金羽"},
    "loki_illusion": {"name": "詭計之神・洛基真身幻象", "level": 100, "min_hp": 68000, "max_hp": 90000, "atk": 860, "gold_range": (46000, 150000), "exp": 720000, "drop_item": "詭計之神假面"},
    "odin_phantom": {"name": "眾神之父・奧丁神王幻影", "level": 100, "min_hp": 110000, "max_hp": 160000, "atk": 920, "gold_range": (60000, 220000), "exp": 1000000, "drop_item": "永恆之槍岡格尼爾殘片"},
    # 💎 5 大打寶刷裝副本魔王數據庫
    "sub_boss_20": {"name": "副本魔王：【幽冥骷髏礦長・阿卡狂暴形態】", "level": 20, "min_hp": 1200, "max_hp": 1500, "atk": 45, "gold_range": (300, 600), "exp": 450, "drop_item": "精煉暗鐵礦石"},
    "sub_boss_40": {"name": "副本魔王：【幽靈船長・戴維瓊斯之影】", "level": 40, "min_hp": 4500, "max_hp": 5500, "atk": 85, "gold_range": (800, 1500), "exp": 1200, "drop_item": "深海淬火核心"},
    "sub_boss_60": {"name": "副本魔王：【不朽君王・始皇傀儡巨像】", "level": 60, "min_hp": 15000, "max_hp": 18000, "atk": 180, "gold_range": (2500, 4500), "exp": 4000, "drop_item": "皇家帝王金精"},
    "sub_boss_80": {"name": "副本魔王：【星空撕裂者・虛空巨噬異獸】", "level": 80, "min_hp": 55000, "max_hp": 65000, "atk": 380, "gold_range": (7000, 12000), "exp": 15000, "drop_item": "史詩星海晶核"},
    "sub_boss_100": {"name": "最終魔王：【隕落主神・奧丁殘存意志】", "level": 100, "min_hp": 180000, "max_hp": 220000, "atk": 750, "gold_range": (20000, 40000), "exp": 60000, "drop_item": "神話・至高誓約結晶"}
}

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
    "風暴峽谷": ["⚡ 狂風呼嘯 (普通)", "🌩️ 雷暴肆虐 (落雷環境，反擊威力驚人)"],
    "幽暗地窖": ["💀 陰風陣陣 (普通)", "👻 亡靈暴動 (死氣瀰漫，怪物戰意高昂)"],
    "翡翠竹林": ["🎋 清風徐來 (普通)", "🌫️ 竹林殺陣 (暗影迷蹤，危機四伏)"],
    "亞特蘭提斯": ["🌊 深海靜謐 (普通)", "🌀 海神漩渦 (深海高壓，行動受阻)"],
    "天空之城": ["☁️ 聖光普照 (普通)", "⚡ 神罰雷雲 (天界威壓)"],
    "巨龍巢穴": ["🔥 龍威瀰漫 (普通)", "🌋 岩漿暴走 (龍息熾熱，怪物攻擊力暴增 1.5 倍)"],
    "精靈古都": ["🍃 生命微風 (普通)", "✨ 魔力潮汐 (精靈結界共鳴)"],
    "機械工廠": ["⚙️ 齒輪運轉 (普通)", "⚡ 高壓過載 (電磁風暴)"],
    "迷霧沼澤": ["🌫️ 瘴氣瀰漫 (普通)", "🌧️ 暴雨滂沱 (泥沼深陷，勇者防禦力稍微下降)"],
    "黃金陵墓": ["👑 王陵死寂 (普通)", "👁️ 法老詛咒 (精神污染威壓)"],
    "翡翠天境": ["🌟 仙氣繚繞 (普通)", "⚡ 紫電祥瑞 (天劫雷罰)"],
    "遺忘孤島": ["🦖 蠻荒燥熱 (普通)", "🌧️ 暴雨滂沱 (熱帶風暴，勇者防禦力稍微下降)"],
    "星空虛無": ["🌌 無重力寂靜 (普通)", "☄️ 流星風暴 (星海引力亂流)"],
    "湮滅神殿": ["👁️ 虛空扭曲 (不可名狀威壓)", "🔮 魔能潮汐 (魔法增幅異常狂暴)"],
    "諸神黃昏": ["⚔️ 末日悲歌 (普通)", "🌋 岩漿暴走 (諸神戰火，怪物基礎攻擊力暴增 1.5 倍)"],
    # 副本環境特效
    "幽冥礦坑[20等副本]": ["⛏️ 礦坑落石 (震盪環境，防禦震碎)"],
    "沉沒古船[40等副本]": ["🌊 驚濤駭浪 (浸水環境，敏捷受限)"],
    "不朽王陵[60等副本]": ["🧱 萬箭齊發 (古代機關陷阱密布)"],
    "天外天境[80等副本]": ["🌌 星海風暴 (時空碎裂，魔能亂流)"],
    "諸神黃昏[100等副本]": ["⚡ 雷霆神怒 (諸神至高神罰審判)"]
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

    if chosen_base_type in ("dragon", "cthulhu_avatar"):
        skill_text = "👁️ 邪神被動：精神污染（每回合吸取勇者 20 點魔力）"
    elif "sub_boss" in chosen_base_type:
        skill_text = "🔥 副本Boss神格：全屏豁免控制，攻擊夾帶致命反噬！"
    else:
        skill_text = affix["default_skill"]

    return {
        "name": f"{affix['prefix']}{base['name']}",
        "hp": final_hp,
        "max_hp": final_hp,
        "atk": final_atk,
        "gold_range": (int(gold_min * gold_mod), int(gold_max * gold_mod)),
        "exp": int(base["exp"] * affix["hp_mod"]),
        "skill": skill_text,
        "drop_item": base["drop_item"],
        "spawn_map": map_name,
        "env": chosen_weather
    }
