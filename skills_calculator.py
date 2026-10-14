# skills_calculator.py - 全職階主動奧義技能核心傷害計算機 (全技能 100% 覆蓋版)

def calculate_active_skill_damage(skill_name, base_weapon_atk, int_val, vit_val, str_val, agi_val, luk_val, men_val):
    """🔮 根據技能名稱、武器物傷以及六大清洗屬性，實體結算出最終的法術/實體傷害值"""
    # 純治療/防禦輔助類技能由 battle_core 處理回血與護盾，不額外造成直接傷害
    if skill_name in ("治癒術", "群體療癒", "淨化術", "復活預言"):
        return {"damage": 0, "log": ""}

    total_p_dmg = 0
    w_pure = max(0, base_weapon_atk - 12 - str_val)

    # ⚔️ 1. 戰士與修羅系奧義
    if skill_name == "蓄力重擊": total_p_dmg = int(base_weapon_atk * 1.6)
    elif skill_name == "橫掃千軍": total_p_dmg = int(base_weapon_atk * 1.8) + 50
    elif skill_name == "戰吼震懾": total_p_dmg = int(base_weapon_atk * 1.3) + 100
    elif skill_name == "破甲一擊": total_p_dmg = int(base_weapon_atk * 2.2) + 150
    elif skill_name == "血性狂暴": total_p_dmg = int(base_weapon_atk * 2.9) + 300
    elif skill_name == "旋風斬": total_p_dmg = int(base_weapon_atk * 3.4) + 450
    elif skill_name == "怒火重擊": total_p_dmg = int(base_weapon_atk * 4.0) + 600
    elif skill_name == "百裂拳": total_p_dmg = int(base_weapon_atk * 4.8) + 800
    elif skill_name == "虎咆爪": total_p_dmg = int(base_weapon_atk * 5.3) + 950
    elif skill_name == "阿修羅霸凰拳": total_p_dmg = int(base_weapon_atk * 6.5) + 1200

    # 🛡️ 2. 騎士與督軍系奧義
    elif skill_name == "盾擊": total_p_dmg = int((12 + vit_val + w_pure) * 1.5)
    elif skill_name == "挑釁": total_p_dmg = int((12 + vit_val + str_val) * 1.3) + 40
    elif skill_name == "神聖之光": total_p_dmg = int((10 + int_val + vit_val) * 1.7) + 60
    elif skill_name == "堅守陣線": total_p_dmg = int((12 + vit_val * 1.5) * 1.4) + 80
    elif skill_name in ("神聖盾擊", "神神聖盾擊"): total_p_dmg = int((12 + vit_val + w_pure) * 2.6) + 200
    elif skill_name == "審判聖刃": total_p_dmg = int((10 + int_val + str_val + w_pure) * 3.0) + 350
    elif skill_name == "光輝重擊": total_p_dmg = int((12 + vit_val + str_val + w_pure) * 3.4) + 450
    elif skill_name == "正義裁決": total_p_dmg = int((12 + vit_val + str_val + w_pure) * 4.8) + 900
    elif skill_name == "領主戰旗": total_p_dmg = int((12 + vit_val + men_val + w_pure) * 5.2) + 1000
    elif skill_name == "不滅意志": total_p_dmg = int((12 + vit_val * 2 + w_pure) * 5.8) + 1150

    # 🔮 3. 魔法師與元素使系奧義
    elif skill_name == "魔能彈": total_p_dmg = int((10 + int_val + w_pure) * 1.4)
    elif skill_name == "火球術": total_p_dmg = int((10 + int_val + w_pure) * 2.0) + 60
    elif skill_name == "閃電術": total_p_dmg = int((10 + int_val + w_pure) * 2.4) + 110
    elif skill_name == "奧術飛彈": total_p_dmg = int((10 + int_val + w_pure) * 2.7) + 160
    elif skill_name == "冰凍術": total_p_dmg = int((10 + int_val + w_pure) * 3.0) + 300
    elif skill_name == "魔力燃燒": total_p_dmg = int((10 + int_val + men_val + w_pure) * 3.3) + 350
    elif skill_name == "元素暴風": total_p_dmg = int((10 + int_val + w_pure) * 3.8) + 450
    elif skill_name == "雷神之怒": total_p_dmg = int((10 + int_val + w_pure) * 5.0) + 850
    elif skill_name == "極凍終焉": total_p_dmg = int((10 + int_val + w_pure) * 5.8) + 1000
    elif skill_name == "末日流星": total_p_dmg = int((10 + int_val + w_pure) * 6.6) + 1300

    # 🗡️ 4. 盜賊與暗夜行者系奧義
    elif skill_name == "毒塗抹": total_p_dmg = int((12 + agi_val + w_pure) * 1.4) + 30
    elif skill_name == "背刺": total_p_dmg = int((12 + agi_val + w_pure) * 1.7) + 50
    elif skill_name == "飛刀射擊": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 1.6) + 60
    elif skill_name == "煙霧彈": total_p_dmg = int((12 + agi_val + luk_val) * 1.8) + 90
    elif skill_name == "毒刃襲擊": total_p_dmg = int((12 + agi_val + w_pure) * 2.4) + 150
    elif skill_name == "致命淬毒": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 2.9) + 260
    elif skill_name == "影分身": total_p_dmg = int((12 + agi_val + w_pure) * 3.5) + 400
    elif skill_name == "弒神終結": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 5.0) + 900
    elif skill_name == "幽冥夜刃": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 5.6) + 1050
    elif skill_name == "瞬獄殺": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 6.4) + 1250

    # 🏹 5. 弓箭手與遊俠系奧義
    elif skill_name == "疾風步": total_p_dmg = int((12 + agi_val + w_pure) * 1.4) + 30
    elif skill_name == "二連矢": total_p_dmg = int((12 + agi_val + w_pure) * 1.8) + 50
    elif skill_name == "毒箭": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 1.9) + 80
    elif skill_name == "蓄力箭": total_p_dmg = int((12 + agi_val + str_val + w_pure) * 2.1) + 120
    elif skill_name == "冰霜陷阱": total_p_dmg = int((12 + agi_val + int_val + w_pure) * 2.5) + 200
    elif skill_name == "爆影狂襲": total_p_dmg = int((12 + agi_val + w_pure) * 3.3) + 400
    elif skill_name == "狙擊一擊": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 3.8) + 550
    elif skill_name == "暴風萬箭破": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 5.4) + 1100
    elif skill_name == "風行者之箭": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 6.0) + 1250
    elif skill_name == "群星墜落": total_p_dmg = int((12 + agi_val + luk_val + w_pure) * 6.6) + 1400

    # ⛪ 6. 祭師與大主教系奧義
    elif skill_name in ("神聖祝福", "神神盛祝福"): total_p_dmg = int((10 + int_val + men_val + w_pure) * 1.5) + 50
    elif skill_name == "聖光彈": total_p_dmg = int((10 + int_val + men_val + w_pure) * 1.8) + 80
    elif skill_name == "聖光懲戒": total_p_dmg = int((10 + int_val + men_val + w_pure) * 2.6) + 200
    elif skill_name in ("神聖結界", "神神盛結界"): total_p_dmg = int((10 + int_val + men_val + w_pure) * 3.0) + 320
    elif skill_name == "天使之翼": total_p_dmg = int((10 + int_val + men_val + w_pure) * 4.5) + 750
    elif skill_name in ("神聖讚美詩", "神神盛讚美詩"): total_p_dmg = int((10 + int_val + men_val + w_pure) * 6.0) + 1200

    # 🛡️ 保底兜底
    else:
        total_p_dmg = int((str_val + int_val + agi_val + w_pure) * 1.8)

    log_message = f"💥 重創命中！技能對【{{enemy_name}}】造成了 {total_p_dmg} 點實體法術傷害！\n"
    return {"damage": total_p_dmg, "log": log_message}
