# jobs.py

# 🎭 遊戲六大本命體系、一線到底三階死鎖升階大數據庫
JOBS_DATA = {
    "初心者": {
        "tier": 0, "req_lvl": 1, "next_jobs": ["戰士", "騎士", "魔法師", "盜賊", "祭師", "弓箭手"],
        "str_mod": 1.0, "agi_mod": 1.0, "int_mod": 1.0, "vit_mod": 1.0, "luk_mod": 1.0, "men_mod": 1.0,
        "skills": {"普通攻擊": {"type": "active", "mp_cost": 0, "desc": "基礎揮砍，造成物理傷害。"}}
    },
    
    # ⚔️ 1. 戰士本命升階線
    "戰士": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["狂戰士"],
        "str_mod": 1.3, "agi_mod": 1.0, "int_mod": 0.7, "vit_mod": 1.1, "luk_mod": 1.0, "men_mod": 0.9,
        "skills": {"蓄力重擊": {"type": "active", "mp_cost": 15, "dmg_mod": 1.6, "desc": "💪 力量凝聚一擊！造成物理基礎傷害 1.6 倍的巨額傷害！"}}
    },
    "狂戰士": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["修羅"],
        "str_mod": 1.7, "agi_mod": 1.2, "int_mod": 0.5, "vit_mod": 0.9, "luk_mod": 1.3, "men_mod": 0.6,
        "skills": {
            "蓄力重擊": {"type": "active", "mp_cost": 15, "dmg_mod": 1.6, "desc": "💪 力量凝聚一擊！造成物理基礎傷害 1.6 倍的巨額傷害！"},
            "血性狂暴": {"type": "passive", "desc": "🩸 狂暴被動：血量低於 50% 時，爆擊傷害額外飆升 50%！"}
        }
    },
    "修羅": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 2.3, "agi_mod": 1.5, "int_mod": 0.4, "vit_mod": 0.8, "luk_mod": 1.6, "men_mod": 0.4,
        "skills": {
            "蓄力重擊": {"type": "active", "mp_cost": 15, "dmg_mod": 1.6, "desc": "💪 力量凝聚一擊！造成物理基礎傷害 1.6 倍的巨額傷害！"},
            "阿修羅霸凰拳": {"type": "active", "mp_cost": 80, "min_mod": 4.0, "max_mod": 6.0, "desc": "🔥 燃燒靈魂！消耗 80 點魔力，隨機轟出 4.0 到 6.0 倍的力量物理極限毀滅傷害！"}
        }
    },

    # 🛡️ 2. 騎士本命升階線
    "騎士": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["十字軍"],
        "str_mod": 1.1, "agi_mod": 0.9, "int_mod": 0.8, "vit_mod": 1.4, "luk_mod": 0.9, "men_mod": 1.1,
        "skills": {"鋼鐵防壁": {"type": "passive", "desc": "🧱 騎士被動：物理防禦力額外增幅 30 點！"}}
    },
    "十字軍": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["督軍"],
        "str_mod": 1.2, "agi_mod": 0.8, "int_mod": 1.1, "vit_mod": 1.8, "luk_mod": 0.9, "men_mod": 1.4,
        "skills": {
            "鋼鐵防壁": {"type": "passive", "desc": "🧱 騎士被動：物理防禦力額外增幅 30 點！"},
            "神聖盾擊": {"type": "active", "mp_cost": 20, "def_mod": 2.5, "desc": "🛡️ 以盾為劍！將你防禦力的 2.5 倍轉化為神聖盾擊傷害砸向怪物！"}
        }
    },
    "督軍": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 1.5, "agi_mod": 0.9, "int_mod": 1.2, "vit_mod": 2.5, "luk_mod": 1.0, "men_mod": 1.9,
        "skills": {
            "鋼鐵防壁": {"type": "passive", "desc": "🧱 騎士被動：物理防禦力額外增幅 30 點！"},
            "神聖盾擊": {"type": "active", "mp_cost": 20, "def_mod": 2.5, "desc": "🛡️ 以盾為劍！將你防禦力的 2.5 倍轉化為神盛盾擊傷害砸向怪物！"},
            "不滅意志": {"type": "passive", "desc": "👑 督軍被動：最大生命值永久暴增 1000 點，且怪物對你造成的傷害減少 25%！"}
        }
    },

    # 🔮 3. 魔法師本命升階線
    "魔法師": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["魔導士"],
        "str_mod": 0.5, "agi_mod": 1.0, "int_mod": 1.4, "vit_mod": 0.8, "luk_mod": 1.0, "men_mod": 1.3,
        "skills": {"火球術": {"type": "active", "mp_cost": 25, "int_mod": 1.8, "desc": "🔥 消耗 25 魔力，轟出智力倍率 1.8 倍的致命高額魔法傷害！"}}
    },
    "魔導士": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["元素使"],
        "str_mod": 0.4, "agi_mod": 1.1, "int_mod": 1.9, "vit_mod": 0.7, "luk_mod": 1.1, "men_mod": 1.6,
        "skills": {
            "火球術": {"type": "active", "mp_cost": 25, "int_mod": 1.8, "desc": "🔥 消耗 25 魔力，轟出智力倍率 1.8 倍的致命高額魔法傷害！"},
            "元素暴風": {"type": "active", "mp_cost": 45, "min_mod": 2.5, "max_mod": 3.5, "desc": "🌪️ 消耗 45 魔力，掀起奧術暴風，隨機轟出 2.5 到 3.5 倍的純魔法重傷！"}
        }
    },
    "元素使": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 0.3, "agi_mod": 1.3, "int_mod": 2.6, "vit_mod": 0.6, "luk_mod": 1.2, "men_mod": 2.0,
        "skills": {
            "火球術": {"type": "active", "mp_cost": 25, "int_mod": 1.8, "desc": "🔥 消耗 25 魔力，轟出智力倍率 1.8 倍的致命高額魔法傷害！"},
            "元素暴風": {"type": "active", "mp_cost": 45, "min_mod": 2.5, "max_mod": 3.5, "desc": "🌪️ 消耗 45 魔力，掀起奧術暴風，隨機轟出 2.5 到 3.5 倍的純魔法重傷！"},
            "極凍終焉": {"type": "active", "mp_cost": 90, "int_mod": 5.0, "desc": "❄️ 消耗 90 魔力，將智力狂暴催化！對怪物傾瀉 5.0 倍的極致絕對零度冰爆！"}
        }
    },

    # 🗡️ 4. 盜賊本命升階線
    "盜賊": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["刺客"],
        "str_mod": 1.0, "agi_mod": 1.4, "int_mod": 0.6, "vit_mod": 0.9, "luk_mod": 1.3, "men_mod": 0.8,
        "skills": {"伏擊雙刺": {"type": "passive", "desc": "🌪️ 盜賊被動：戰場連續攻擊機率額外暴增 20%！"}}
    },
    "刺客": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["暗夜行者"],
        "str_mod": 1.2, "agi_mod": 1.9, "int_mod": 0.5, "vit_mod": 0.8, "luk_mod": 1.6, "men_mod": 0.6,
        "skills": {
            "伏擊雙刺": {"type": "passive", "desc": "🌪️ 盜賊被動：戰場連續攻擊機率額外暴增 20%！"},
            "毒刃襲擊": {"type": "active", "mp_cost": 20, "agi_mod": 1.5, "desc": "🩸 刺客之刃！造成敏捷增幅 1.5 倍的物理背刺傷害，且怪物必定無法閃避！"}
        }
    },
    "暗夜行者": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 1.4, "agi_mod": 2.6, "int_mod": 0.4, "vit_mod": 0.7, "luk_mod": 2.2, "men_mod": 0.5,
        "skills": {
            "伏擊雙刺": {"type": "passive", "desc": "🌪️ 盜賊被動：戰場連續攻擊機率額外暴增 20%！"},
            "毒刃襲擊": {"type": "active", "mp_cost": 20, "agi_mod": 1.5, "desc": "🩸 刺客之刃！造成敏捷增幅 1.5 倍的物理背刺傷害，且怪物必定無法閃避！"},
            "弒神終結": {"type": "active", "mp_cost": 50, "dmg_mod": 4.5, "desc": "💥 隱匿終結！消耗 50 魔力，將幸運與敏捷完美揉合，轟出高達 4.5 倍的物理極限爆擊巨傷！"}
        }
    },

    # ⛪ 5. 祭師本命升階線
    "祭師": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["賢者"],
        "str_mod": 0.8, "agi_mod": 0.9, "int_mod": 1.2, "vit_mod": 1.1, "luk_mod": 1.1, "men_mod": 1.4,
        "skills": {"治癒術": {"type": "active", "mp_cost": 20, "heal_mod": 1.5, "desc": "💖 聖光降臨！消耗 20 魔力，隨機為勇者補回智力與精神總和 1.5 倍的生命值！"}}
    },
    "賢者": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["大主教"],
        "str_mod": 0.9, "agi_mod": 0.9, "int_mod": 1.5, "vit_mod": 1.3, "luk_mod": 1.3, "men_mod": 1.9,
        "skills": {
            "治癒術": {"type": "active", "mp_cost": 20, "heal_mod": 1.5, "desc": "💖 聖光降臨！消耗 20 魔力，隨機為勇者補回智力與精神總和 1.5 倍的生命值！"},
            "聖光懲戒": {"type": "active", "mp_cost": 35, "men_mod": 2.2, "desc": "✨ 聖光法陣！消耗 35 魔力，將神聖法力轉化，轟出精神力 2.2 倍的魔法傷害！"}
        }
    },
    "大主教": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 1.0, "agi_mod": 1.0, "int_mod": 1.9, "vit_mod": 1.5, "luk_mod": 1.5, "men_mod": 2.6,
        "skills": {
            "治癒術": {"type": "active", "mp_cost": 20, "heal_mod": 1.5, "desc": "💖 聖光降臨！消耗 20 魔力，隨機為勇者補回智力與精神總和 1.5 倍的生命值！"},
            "聖光懲戒": {"type": "active", "mp_cost": 35, "men_mod": 2.2, "desc": "✨ 聖光法陣！消耗 35 魔力，將神聖法力轉化，轟出精神力 2.2 倍的魔法傷害！"},
            "神聖讚美詩": {"type": "passive", "desc": "☀️ 大主教神格：最大魔力永久提升 300 點，且戰場閃避率額外提升 15%！"}
        }
    },

    # 🏹 6. 弓箭手本命升階線
    "弓箭手": {
        "tier": 1, "req_lvl": 25, "next_jobs": ["獵人"],
        "str_mod": 1.1, "agi_mod": 1.3, "int_mod": 0.7, "vit_mod": 0.9, "luk_mod": 1.2, "men_mod": 0.8,
        "skills": {"二連矢": {"type": "active", "mp_cost": 15, "desc": "🏹 箭步神速！消耗 15 魔力，必定射出兩箭物理穿透傷害！"}}
    },
    "獵人": {
        "tier": 2, "req_lvl": 50, "next_jobs": ["遊俠"],
        "str_mod": 1.3, "agi_mod": 1.7, "int_mod": 0.6, "vit_mod": 0.9, "luk_mod": 1.5, "men_mod": 0.6,
        "skills": {
            "二連矢": {"type": "active", "mp_cost": 15, "desc": "🏹 箭步神速！消耗 15 魔力，必定射出兩箭物理穿透傷害！"},
            "陷阱奇襲": {"type": "passive", "desc": "🐾 獵人被動：每回合戰鬥有 25% 機率使怪物的閃避率直接歸零！"}
        }
    },
    "遊俠": {
        "tier": 3, "req_lvl": 100, "next_jobs": [],
        "str_mod": 1.5, "agi_mod": 2.3, "int_mod": 0.5, "vit_mod": 0.9, "luk_mod": 2.0, "men_mod": 0.5,
        "skills": {
            "二連矢": {"type": "active", "mp_cost": 15, "desc": "🏹 箭步神速！消耗 15 魔力，必定射出兩箭物理穿透傷害！"},
            "陷阱奇襲": {"type": "passive", "desc": "🐾 獵人被動：每回合戰鬥有 25% 機率使怪物的閃避率直接歸零！"},
            "暴風萬箭破": {"type": "active", "mp_cost": 60, "agi_mod": 4.5, "desc": "🎯 終極遊俠！消耗 60 魔力，對怪物傾瀉滿天箭雨，隨機轟出敏捷倍率 3.8 到 5.0 倍的物理致命重傷！"}
        }
    }
}

def get_job_options_text(p):
    current_job = p.get("job", "初心者")
    level = p.get("level", 1)
    job_info = JOBS_DATA.get(current_job, JOBS_DATA["初心者"])
    next_list = job_info["next_jobs"]
    if not next_list:
        return f"👑 傳奇大巔峰！你目前已經晉升為最終神職【{current_job}】，實力已傲視凡塵！"
    text = "🔔 💎 【本命天賦覺醒 ・ 職業進階提示】 💎 🔔\n"
    text += f"✨ 勇者，你當前的本命職涯為：【{current_job}】\n"
    text += "─────────────────\n"
    if current_job == "初心者":
        text += "🔮 冒險的起點！請選擇你這輩子唯一的守護信仰：\n\n"
        for next_job in next_list:
            target_info = JOBS_DATA[next_job]
            text += f"🚩 【{next_job}】(Lv.25 轉職門檻)\n"
            text += f"   ┗ 🔮 專屬技能：{list(target_info['skills'].keys())[0]}\n"
    else:
        next_job = next_list[0]
        target_info = JOBS_DATA[next_job]
        text += f"🔮 境界突破！你即將迎來突破，覺醒為更高階的職位：\n\n"
        text += f"🚩 👑 真・本命進階：【{next_job}】(Lv.{target_info['req_lvl']} 解鎖)\n"
        text += "   📜 覺醒附加專屬能力與技能：\n"
        for s_name, s_info in target_info["skills"].items():
            text += f"   ┗ 🔮 {s_name}：{s_info['desc']}\n"
    text += "─────────────────\n"
    text += "✍️ 突破法術口令：輸入【轉職 職業名稱】即可完成覺醒！\n（例如：轉職 戰士）"
    return text
