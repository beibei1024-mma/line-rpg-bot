# jobs.py - 全新精簡版「6/4/3 主被動核心技能樹數據庫」

JOBS_DATA = {
    "初心者": {
        "tier": 0, "req_lvl": 1, "next_jobs": ["戰士", "騎士", "魔法師", "盜賊", "祭師", "弓箭手"],
        "str_mod": 1.0, "agi_mod": 1.0, "int_mod": 1.0, "vit_mod": 1.0, "luk_mod": 1.0, "men_mod": 1.0,
        "skills": {
            "普通攻擊": {"type": "active", "mp_cost": 0, "desc": "基礎肉搏戰擊。"}
        }
    },
    
    # ⚔️ 1. 戰士系 (狂戰、修羅)
    "戰士": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["狂戰士"],
        "str_mod": 1.3, "agi_mod": 1.0, "int_mod": 0.6, "vit_mod": 1.2, "luk_mod": 1.0, "men_mod": 0.9,
        "skills": {
            "蓄力重擊": {"type": "active", "mp_cost": 15, "desc": "1.6倍物理猛擊"},
            "橫掃千軍": {"type": "active", "mp_cost": 20, "desc": "猛烈揮砍周圍敵軍"},
            "戰吼震懾": {"type": "active", "mp_cost": 10, "desc": "發出怒吼震懾目標"},
            "破甲一擊": {"type": "active", "mp_cost": 25, "desc": "削弱敵方防禦力"},
            "肌肉強化": {"type": "passive", "desc": "被動：力量倍率獲得基礎提升"},
            "鋼鐵意志": {"type": "passive", "desc": "被動：最大生命上限獲得增幅"}
        }
    },
    "狂戰士": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["修羅"],
        "str_mod": 1.8, "agi_mod": 1.2, "int_mod": 0.4, "vit_mod": 1.4, "luk_mod": 1.2, "men_mod": 0.7,
        "skills": {
            "蓄力重擊": {"type": "active", "mp_cost": 15, "desc": "1.6倍物理猛擊"},
            "橫掃千軍": {"type": "active", "mp_cost": 20, "desc": "猛烈揮砍周圍敵軍"},
            "戰吼震懾": {"type": "active", "mp_cost": 10, "desc": "發出怒吼震懾目標"},
            "破甲一擊": {"type": "active", "mp_cost": 25, "desc": "削弱敵方防禦力"},
            "血性狂暴": {"type": "active", "mp_cost": 30, "desc": "燃燒血液獲得高傷"},
            "旋風斬": {"type": "active", "mp_cost": 35, "desc": "化身旋風割裂敵軍"},
            "怒火重擊": {"type": "active", "mp_cost": 40, "desc": "累積怒氣爆發揮砍"},
            "不滅狂暴": {"type": "passive", "desc": "被動：暴擊機率永久獲得提煉"},
            "肌肉強化": {"type": "passive", "desc": "被動"}, "鋼鐵意志": {"type": "passive", "desc": "被動"}
        }
    },
    "修羅": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 2.4, "agi_mod": 1.5, "int_mod": 0.3, "vit_mod": 1.6, "luk_mod": 1.5, "men_mod": 0.5,
        "skills": {
            "蓄力重擊": {"type": "active", "mp_cost": 15, "desc": "1.6倍物理猛擊"},
            "橫掃千軍": {"type": "active", "mp_cost": 20, "desc": "猛烈揮砍周圍敵軍"},
            "戰吼震懾": {"type": "active", "mp_cost": 10, "desc": "發出怒吼震懾目標"},
            "破甲一擊": {"type": "active", "mp_cost": 25, "desc": "削弱敵方防禦力"},
            "血性狂暴": {"type": "active", "mp_cost": 30, "desc": "燃燒血液獲得高傷"},
            "旋風斬": {"type": "active", "mp_cost": 35, "desc": "化身旋風割裂敵軍"},
            "怒火重擊": {"type": "active", "mp_cost": 40, "desc": "累積怒氣爆發揮砍"},
            "阿修羅霸凰拳": {"type": "active", "mp_cost": 80, "desc": "爆發靈魂！砸出5倍驚天重擊！"},
            "百裂拳": {"type": "active", "mp_cost": 50, "desc": "幻影般的極速連打"},
            "虎咆爪": {"type": "active", "mp_cost": 60, "desc": "修羅撕裂破空一爪"},
            "不滅狂暴": {"type": "passive", "desc": "被動"}, "肌肉強化": {"type": "passive", "desc": "被動"}, "鋼鐵意志": {"type": "passive", "desc": "被動"}
        }
    },

    # 🛡️ 2. 騎士系 (十字軍、督軍)
    "騎士": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["十字軍"],
        "str_mod": 1.1, "vit_mod": 1.5, "agi_mod": 0.8, "int_mod": 0.7, "luk_mod": 0.9, "men_mod": 1.2,
        "skills": {
            "盾擊": {"type": "active", "mp_cost": 15, "desc": "基礎防禦盾牌重擊"},
            "挑釁": {"type": "active", "mp_cost": 10, "desc": "強行吸引怪物注意力"},
            "神聖之光": {"type": "active", "mp_cost": 20, "desc": "聖光戰技附體"},
            "堅守陣線": {"type": "active", "mp_cost": 15, "desc": "大幅強化防禦防護"},
            "鋼鐵防壁": {"type": "passive", "desc": "被動：基礎防禦力固定獲得加成"},
            "光輝信仰": {"type": "passive", "desc": "被動：魔防與精神力獲得基礎增幅"}
        }
    },
    "十字軍": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["督軍"],
        "str_mod": 1.3, "vit_mod": 2.0, "agi_mod": 0.8, "int_mod": 1.0, "luk_mod": 1.0, "men_mod": 1.5,
        "skills": {
            "盾擊": {"type": "active", "mp_cost": 15, "desc": "基礎防禦盾牌重擊"},
            "挑釁": {"type": "active", "mp_cost": 10, "desc": "強行吸引怪物注意力"},
            "神聖之光": {"type": "active", "mp_cost": 20, "desc": "聖光戰技附體"},
            "堅守陣線": {"type": "active", "mp_cost": 15, "desc": "大幅強化防禦防護"},
            "神聖盾擊": {"type": "active", "mp_cost": 25, "desc": "將體防換算為神聖真實傷害"},
            "審判聖刃": {"type": "active", "mp_cost": 30, "desc": "召喚十字聖刃重傷目標"},
            "光輝重擊": {"type": "active", "mp_cost": 35, "desc": "附加神聖光系震盪傷害"},
            "神聖鎧甲": {"type": "passive", "desc": "被動：受到的所有傷害固定免除一部分"},
            "鋼鐵防壁": {"type": "passive", "desc": "被動"}, "光輝信仰": {"type": "passive", "desc": "被動"}
        }
    },
    "督軍": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 1.6, "vit_mod": 2.7, "agi_mod": 0.9, "int_mod": 1.1, "luk_mod": 1.1, "men_mod": 1.9,
        "skills": {
            "盾擊": {"type": "active", "mp_cost": 15, "desc": "基礎防禦盾牌重擊"},
            "挑釁": {"type": "active", "mp_cost": 10, "desc": "強行吸引怪物注意力"},
            "神聖之光": {"type": "active", "mp_cost": 20, "desc": "聖光戰技附體"},
            "堅守陣線": {"type": "active", "mp_cost": 15, "desc": "大幅強化防禦防護"},
            "神聖盾擊": {"type": "active", "mp_cost": 25, "desc": "將體防換算為神聖真實傷害"},
            "審判聖刃": {"type": "active", "mp_cost": 30, "desc": "召喚十字聖刃重傷目標"},
            "光輝重擊": {"type": "active", "mp_cost": 35, "desc": "附加神聖光系震盪傷害"},
            "不滅意志": {"type": "active", "mp_cost": 70, "desc": "極限鎖血並激發防禦姿態"},
            "正義裁決": {"type": "active", "mp_cost": 55, "desc": "至高法律秩序巨盾重砸"},
            "領主戰旗": {"type": "active", "mp_cost": 60, "desc": "降下戰旗提供永恆防禦氣場"},
            "神聖鎧甲": {"type": "passive", "desc": "被動"}, "鋼鐵防壁": {"type": "passive", "desc": "被動"}, "光輝信仰": {"type": "passive", "desc": "被動"}
        }
    },

    # 🔮 3. 魔法師系 (魔導、元素)
    "魔法師": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["魔導士"],
        "int_mod": 1.5, "men_mod": 1.3, "str_mod": 0.4, "agi_mod": 1.0, "vit_mod": 0.8, "luk_mod": 1.1,
        "skills": {
            "火球術": {"type": "active", "mp_cost": 20, "desc": "智力倍率1.8倍高額火系魔傷"},
            "魔能彈": {"type": "active", "mp_cost": 15, "desc": "基礎魔法射擊"},
            "閃電術": {"type": "active", "mp_cost": 25, "desc": "引導落雷割裂目標"},
            "奧術飛彈": {"type": "active", "mp_cost": 30, "desc": "多重射出追蹤奧術飛彈"},
            "冥想調息": {"type": "passive", "desc": "被動：魔力源泉獲得大幅基礎恢復"},
            "元素親和": {"type": "passive", "desc": "被動：魔法傷害與智力獲得基礎提升"}
        }
    },
    "魔導士": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["元素使"],
        "int_mod": 2.1, "men_mod": 1.6, "str_mod": 0.3, "agi_mod": 1.1, "vit_mod": 0.7, "luk_mod": 1.2,
        "skills": {
            "火球術": {"type": "active", "mp_cost": 20, "desc": "智力倍率1.8倍高額火系魔傷"},
            "魔能彈": {"type": "active", "mp_cost": 15, "desc": "基礎魔法射擊"},
            "閃電術": {"type": "active", "mp_cost": 25, "desc": "引導落雷割裂目標"},
            "奧術飛彈": {"type": "active", "mp_cost": 30, "desc": "多重射出追蹤奧術飛彈"},
            "元素暴風": {"type": "active", "mp_cost": 45, "desc": "狂暴引導2.5至3.5倍法術重傷"},
            "冰凍術": {"type": "active", "mp_cost": 35, "desc": "凝結寒冰降低目標抗性"},
            "魔力燃燒": {"type": "active", "mp_cost": 40, "desc": "點燃目標殘餘魔能造成爆炸"},
            "法力護盾": {"type": "passive", "desc": "被動：法力上限獲得額外增幅"},
            "冥想調息": {"type": "passive", "desc": "被動"}, "元素親和": {"type": "passive", "desc": "被動"}
        }
    },
    "元素使": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "int_mod": 2.8, "men_mod": 2.1, "str_mod": 0.2, "agi_mod": 1.3, "vit_mod": 0.6, "luk_mod": 1.3,
        "skills": {
            "火球術": {"type": "active", "mp_cost": 20, "desc": "智力倍率1.8倍高額火系魔傷"},
            "魔能彈": {"type": "active", "mp_cost": 15, "desc": "基礎魔法射擊"},
            "閃電術": {"type": "active", "mp_cost": 25, "desc": "引導落雷割裂目標"},
            "奧術飛彈": {"type": "active", "mp_cost": 30, "desc": "多重射出追蹤奧術飛彈"},
            "元素暴風": {"type": "active", "mp_cost": 45, "desc": "狂暴引導2.5至3.5倍法術重傷"},
            "冰凍術": {"type": "active", "mp_cost": 35, "desc": "凝結寒冰降低目標抗性"},
            "魔力燃燒": {"type": "active", "mp_cost": 40, "desc": "點燃目標殘餘魔能造成爆炸"},
            "極凍終焉": {"type": "active", "mp_cost": 90, "desc": "釋放絕對零度5倍極寒霜爆奧義"},
            "末日流星": {"type": "active", "mp_cost": 100, "desc": "撕裂天際召喚滅世隕石雨重創"},
            "雷神之怒": {"type": "active", "mp_cost": 75, "desc": "引導九天狂雷發動極限閃擊"},
            "法力護盾": {"type": "passive", "desc": "死被動"}, "冥想調息": {"type": "passive", "desc": "被動"}, "元素親和": {"type": "passive", "desc": "被動"}
        }
    },

    # 🗡️ 4. 盜賊系 (刺客、暗夜行者)
    "盜賊": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["刺客"],
        "agi_mod": 1.5, "luk_mod": 1.4, "str_mod": 1.0, "int_mod": 0.5, "vit_mod": 0.9, "men_mod": 0.8,
        "skills": {
            "背刺": {"type": "active", "mp_cost": 15, "desc": "基礎潛行刺擊傷害"},
            "毒塗抹": {"type": "active", "mp_cost": 10, "desc": "武器刀刃附加基礎毒素"},
            "煙霧彈": {"type": "active", "mp_cost": 20, "desc": "投擲煙霧進行戰術致盲"},
            "飛刀射擊": {"type": "active", "mp_cost": 15, "desc": "遠程投擲銳利暗器"},
            "伏擊雙刺": {"type": "passive", "desc": "被動：戰場連擊率基礎增幅"},
            "幻影步": {"type": "passive", "desc": "被動：角色基本閃避機率提升"}
        }
    },
    "刺客": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["暗夜行者"],
        "agi_mod": 2.1, "luk_mod": 1.8, "str_mod": 1.1, "int_mod": 0.4, "vit_mod": 0.8, "men_mod": 0.6,
        "skills": {
            "背刺": {"type": "active", "mp_cost": 15, "desc": "基礎潛行刺擊傷害"},
            "毒塗抹": {"type": "active", "mp_cost": 10, "desc": "武器刀刃附加基礎毒素"},
            "煙霧彈": {"type": "active", "mp_cost": 20, "desc": "投擲煙霧進行戰術致盲"},
            "飛刀射擊": {"type": "active", "mp_cost": 15, "desc": "遠程投擲銳利暗器"},
            "毒刃襲擊": {"type": "active", "mp_cost": 20, "desc": "1.5倍敏捷物傷且無視目標閃避"},
            "影分身": {"type": "active", "mp_cost": 35, "desc": "召喚殘影進行多段切割"},
            "致命淬毒": {"type": "active", "mp_cost": 25, "desc": "刀刃換上神經毒素大幅重傷"},
            "刺客信條": {"type": "passive", "desc": "被動：物理基礎爆擊倍率固定增長"},
    # ── 續接第一部分：JOBS_DATA 字典內部追加盜賊系尾端與後續職業 (注意：此段前面固定為 4 個空格縮排) ──
    "暗夜行者": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "agi_mod": 2.9, "luk_mod": 2.5, "str_mod": 1.3, "int_mod": 0.3, "vit_mod": 0.7, "men_mod": 0.5,
        "skills": {
            "背刺": {"type": "active", "mp_cost": 15, "desc": "基礎潛行刺擊傷害"},
            "毒塗抹": {"type": "active", "mp_cost": 10, "desc": "武器刀刃附加基礎毒素"},
            "煙霧彈": {"type": "active", "mp_cost": 20, "desc": "投擲煙霧進行戰術致盲"},
            "飛刀射擊": {"type": "active", "mp_cost": 15, "desc": "遠程投擲銳利暗器"},
            "毒刃襲擊": {"type": "active", "mp_cost": 20, "desc": "造成1.5倍敏捷背刺傷害，怪必定無法閃避"},
            "影分身": {"type": "active", "mp_cost": 35, "desc": "分身殘影切割"},
            "致命淬毒": {"type": "active", "mp_cost": 25, "desc": "注入神經劇毒"},
            "弒神終結": {"type": "active", "mp_cost": 50, "desc": "融合運氣與速度，轟出4.5倍爆擊終結奧義"},
            "瞬獄殺": {"type": "active", "mp_cost": 85, "desc": "影牢覆蓋！瞬間發動影殺百裂斬"},
            "幽冥夜刃": {"type": "active", "mp_cost": 65, "desc": "引導冥界永夜地裂之斬"},
            "刺客信條": {"type": "passive", "desc": "被動"}, "伏擊雙刺": {"type": "passive", "desc": "被動"}, "幻影步": {"type": "passive", "desc": "被動"}
        }
    },
    
    # ⛪ 5. 祭師系 (賢者、大主教)
    "祭師": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["賢者"],
        "men_mod": 1.5, "int_mod": 1.3, "str_mod": 0.7, "agi_mod": 0.8, "vit_mod": 1.1, "luk_mod": 1.1,
        "skills": {
            "治癒術": {"type": "active", "mp_cost": 20, "desc": "恢復智力與精神總和1.5倍生命"},
            "聖光彈": {"type": "active", "mp_cost": 15, "desc": "發射純淨聖光射擊"},
            "神神聖祝福": {"type": "active", "mp_cost": 10, "desc": "祈福提升短暫基礎物傷加成"},
            "淨化術": {"type": "active", "mp_cost": 12, "desc": "光耀驅散自身異常減益"},
            "神聖信仰": {"type": "passive", "desc": "被動：基本精神與抗性獲得公會增幅"},
            "光輝守護": {"type": "passive", "desc": "被動：法術基本防禦力獲得永久提升"}
        }
    },
    "賢者": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["大主教"],
        "men_mod": 2.1, "int_mod": 1.6, "str_mod": 0.8, "agi_mod": 0.8, "vit_mod": 1.2, "luk_mod": 1.2,
        "skills": {
            "治癒術": {"type": "active", "mp_cost": 20, "desc": "恢復智力與精神總和1.5倍生命"},
            "聖光彈": {"type": "active", "mp_cost": 15, "desc": "發射純淨聖光射擊"},
            "神神聖祝福": {"type": "active", "mp_cost": 10, "desc": "祈福提升短暫基礎物傷加成"},
            "淨化術": {"type": "active", "mp_cost": 12, "desc": "光耀驅散自身異常減益"},
            "聖光懲戒": {"type": "active", "mp_cost": 35, "desc": "召喚光系法陣，砸出精神2.2倍魔法傷害"},
            "群體療癒": {"type": "active", "mp_cost": 45, "desc": "大範圍光系神聖修復生機"},
            "神神聖結界": {"type": "active", "mp_cost": 40, "desc": "降下免除一部分傷害的光之結界"},
            "祈禱光環": {"type": "passive", "desc": "被動：每回合戰鬥自動修復部分受損生命"},
            "神聖信仰": {"type": "passive", "desc": "被動"}, "光輝守護": {"type": "passive", "desc": "被動"}
        }
    },
    "大主教": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "men_mod": 2.9, "int_mod": 2.0, "str_mod": 0.9, "agi_mod": 0.9, "vit_mod": 1.4, "luk_mod": 1.3,
        "skills": {
            "治癒術": {"type": "active", "mp_cost": 20, "desc": "恢復智力與精神總和1.5倍生命"},
            "聖光彈": {"type": "active", "mp_cost": 15, "desc": "發射純淨聖光射擊"},
            "神神聖祝福": {"type": "active", "mp_cost": 10, "desc": "祈福提升短暫基礎物傷加成"},
            "淨化術": {"type": "active", "mp_cost": 12, "desc": "光耀驅散自身異常減益"},
            "聖光懲戒": {"type": "active", "mp_cost": 35, "desc": "砸出精神2.2倍魔法傷害"},
            "群體療癒": {"type": "active", "mp_cost": 45, "desc": "大範圍光系神聖修復"},
            "神神聖結界": {"type": "active", "mp_cost": 40, "desc": "降下免傷光之結界"},
            "神神聖讚美詩": {"type": "active", "mp_cost": 95, "desc": "大主教全螢幕光明大洗禮極限奧義"},
            "復活預言": {"type": "active", "mp_cost": 80, "desc": "加持預言光環大幅豁免致命死傷"},
            "天使之翼": {"type": "active", "mp_cost": 55, "desc": "召喚高階光輝羽翼發動重創衝擊"},
            "祈禱光環": {"type": "passive", "desc": "被動"}, "神聖信仰": {"type": "passive", "desc": "被動"}, "光輝守護": {"type": "passive", "desc": "被動"}
        }
    },

    # 🏹 6. 弓箭手系 (獵人、遊俠)
    "弓箭手": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["獵人"],
        "agi_mod": 1.4, "luk_mod": 1.3, "str_mod": 1.1, "int_mod": 0.6, "vit_mod": 0.9, "men_mod": 0.8,
        "skills": {
            "二連矢": {"type": "active", "mp_cost": 15, "desc": "神速拉弓！必定射出兩箭物理穿透箭"},
            "蓄力箭": {"type": "active", "mp_cost": 20, "desc": "穩固身形射出強能精準重擊"},
            "毒箭": {"type": "active", "mp_cost": 18, "desc": "箭頭附帶劇毒引發持續流血"},
            "疾風步": {"type": "active", "mp_cost": 12, "desc": "短暫提升角色在戰場中的閃避機率"},
            "鷹眼": {"type": "passive", "desc": "被動：角色戰場命中率與暴擊率基本提升"},
            "精確瞄準": {"type": "passive", "desc": "被動：敏捷基本屬性獲得皇家永久強化"}
        }
    },
    "獵人": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["遊俠"],
        "agi_mod": 1.9, "luk_mod": 1.6, "str_mod": 1.2, "int_mod": 0.5, "vit_mod": 0.9, "men_mod": 0.6,
        "skills": {
            "二連矢": {"type": "active", "mp_cost": 15, "desc": "神速拉弓！必定射出兩箭物理穿透箭"},
            "蓄力箭": {"type": "active", "mp_cost": 20, "desc": "穩固身形射出強能精準重擊"},
            "毒箭": {"type": "active", "mp_cost": 18, "desc": "箭頭附帶劇毒引發持續流血"},
            "疾風步": {"type": "active", "mp_cost": 12, "desc": "短暫提升角色在戰場中的閃避機率"},
            "狙擊一擊": {"type": "active", "mp_cost": 40, "desc": "發動致命遠程獵人物理重狙"},
            "冰霜陷阱": {"type": "active", "mp_cost": 25, "desc": "佈置陷阱限制怪物閃避與防禦"},
            "爆影狂襲": {"type": "active", "mp_cost": 35, "desc": "幻化漫天箭影傾瀉重創目標"},
            "野性呼喚": {"type": "passive", "desc": "被動：每回合戰鬥有機率直接使怪物閃避歸零"},
            "鷹眼": {"type": "passive", "desc": "被動"}, "精確瞄準": {"type": "passive", "desc": "被動"}
        }
    },
    "遊俠": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "agi_mod": 2.6, "luk_mod": 2.1, "str_mod": 1.4, "int_mod": 0.4, "vit_mod": 0.9, "men_mod": 0.5,
        "skills": {
            "二連矢": {"type": "active", "mp_cost": 15, "desc": "必定射出兩箭物理穿透箭"},
            "蓄力箭": {"type": "active", "mp_cost": 20, "desc": "穩固身形射出強能精準重擊"},
            "毒箭": {"type": "active", "mp_cost": 18, "desc": "箭頭附帶劇毒引發持續流血"},
            "疾風步": {"type": "active", "mp_cost": 12, "desc": "短暫提升角色在戰場中的閃避機率"},
            "狙擊一擊": {"type": "active", "mp_cost": 40, "desc": "發動致命遠程獵人物理重狙"},
            "冰霜陷阱": {"type": "active", "mp_cost": 25, "desc": "佈置陷阱限制怪物閃避與防禦"},
            "爆影狂襲": {"type": "active", "mp_cost": 35, "desc": "幻化漫天箭影傾瀉重創目標"},
            "暴風萬箭破": {"type": "active", "mp_cost": 60, "desc": "萬箭齊發！狂暴傾瀉最高5倍穿透物理奧義"},
            "風行者之箭": {"type": "active", "mp_cost": 80, "desc": "凝聚風元引力射出撕裂虛空之箭"},
            "群星墜落": {"type": "active", "mp_cost": 95, "desc": "召喚上古星辰箭雨發動全屏寂滅"},
            "野性呼喚": {"type": "passive", "desc": "被動"}, "鷹眼": {"type": "passive", "desc": "被動"}, "精確瞄準": {"type": "passive", "desc": "被動"}
        }
    }
}

# ── 獨立功能函數 (屬於最外層頂格縮排，前面不可有任何空格) ──
def get_job_options_text(p):
    """🔮 轉職導引提示面板大腦"""
    current_job = p.get("job", "初心者")
    job_info = JOBS_DATA.get(current_job, JOBS_DATA["初心者"])
    next_list = job_info["next_jobs"]
    if not next_list:
        return f"👑 傳奇大巔峰！你目前已經晉升為最終神職【{current_job}】，實力已傲視凡塵！"
    
    # ⚡ 優化：改用高效的列表推導式配合 ''.join() 進行字串組裝，消除重複的 text += 帶來的 CPU 配置浪費
    lines = [
        "🔔 💎 【本命天賦覺醒職業進階提示】 💎 🔔\n",
        f"✨ 勇者，你當前的本命職涯為：【{current_job}】\n",
        "─────────────────\n"
    ]
    if current_job == "初心者":
        lines.append("🔮 冒險的起點！請選擇你這輩子唯一的守護信仰：\n\n")
        lines.extend([f"🚩 【{next_job}】(Lv.25 轉職門檻)\n" for next_job in next_list])
    else:
        next_job = next_list[0]
        target_info = JOBS_DATA[next_job]
        lines.extend([
            "🔮 境界突破！你即將迎來突破，覺醒為更高階的職位：\n\n",
            f"🚩 👑 真・本命進階：【{next_job}】(Lv.{target_info['req_lvl']} 解鎖)\n",
            "   📜 覺醒新增主動技能（會自動生成戰鬥標籤）：\n"
        ])
        # ⚡ 優化：預先建立快取集合，將重複搜尋技能的開銷降為 O(1)
        current_skills = JOBS_DATA[current_job]["skills"]
        lines.extend([
            f"   ┗ 🔮 {s_name}：{s_info['desc']}\n"
            for s_name, s_info in target_info["skills"].items()
            if s_info.get("type") == "active" and s_name not in current_skills
        ])
    lines.extend([
        "─────────────────\n",
        "✍️ 突破法術口令：輸入【轉職 職業名稱】即可完成覺醒！\n",
        "（例如：轉職 戰士）"
    ])
    return "".join(lines)
