# skills_calculator.py - 全職階主動奧義技能核心傷害計算機

def calculate_active_skill_damage(skill_name, base_weapon_atk, int_val, vit_val, str_val, agi_val, luk_val, men_val):
    """🔮 根據技能名稱、武器物傷以及六大清洗屬性，實體結算出最終的法術/實體傷害值"""
    total_p_dmg = 0
    log_message = ""
    
    # ⚔️ 戰士與修羅系奧義
    if skill_name == "蓄力重擊": total_p_dmg = int(base_weapon_atk * 1.5)
    elif skill_name == "橫掃千軍": total_p_dmg = int(base_weapon_atk * 1.8) + 50
    elif skill_name == "戰吼震懾": total_p_dmg = int(base_weapon_atk * 1.3) + 100
    elif skill_name == "破甲一擊": total_p_dmg = int(base_weapon_atk * 2.2) + 150
    elif skill_name == "血性狂暴": total_p_dmg = int(base_weapon_atk * 2.9) + 300
    elif skill_name == "旋風斬": total_p_dmg = int(base_weapon_atk * 3.4) + 450
    elif skill_name == "怒火重擊": total_p_dmg = int(base_weapon_atk * 4.0) + 600
    elif skill_name == "阿修羅霸凰拳": total_p_dmg = int(base_weapon_atk * 6.5) + 1200
    elif skill_name == "百裂拳": total_p_dmg = int(base_weapon_atk * 4.8) + 800
    elif skill_name == "虎咆爪": total_p_dmg = int(base_weapon_atk * 5.3) + 950
    
    # 🛡️ 騎士與督軍系奧義
    elif skill_name == "盾擊": total_p_dmg = int((12 + vit_val + (base_weapon_atk - 12 - str_val)) * 1.4)
    elif skill_name == "神聖之光": total_p_dmg = int((10 + int_val) * 1.6) + 40
    elif skill_name == "神聖盾擊": total_p_dmg = int((12 + vit_val + (base_weapon_atk - 12 - str_val)) * 2.6) + 200
    elif skill_name == "審判聖刃": total_p_dmg = int((10 + int_val) * 3.2) + 400
    elif skill_name == "正義裁決": total_p_dmg = int((12 + vit_val + str_val) * 4.8) + 900
    
    # 🔮 魔法師與元素使系奧義
    elif skill_name == "魔能彈": total_p_dmg = int((10 + int_val) * 1.3)
    elif skill_name == "火球術": total_p_dmg = int((10 + int_val) * 2.0) + 60
    elif skill_name == "閃電術": total_p_dmg = int((10 + int_val) * 2.4) + 110
    elif skill_name == "奧術飛彈": total_p_dmg = int((10 + int_val) * 2.7) + 160
    elif skill_name == "元素暴風": total_p_dmg = int((10 + int_val) * 3.6) + 400
    elif skill_name == "冰凍術": total_p_dmg = int((10 + int_val) * 3.0) + 300
    elif skill_name == "魔力燃燒": total_p_dmg = int((10 + int_val) * 3.3) + 350
    elif skill_name == "極凍終焉": total_p_dmg = int((10 + int_val) * 5.8) + 1000
    elif skill_name == "末日流星": total_p_dmg = int((10 + int_val) * 6.6) + 1300
    elif skill_name == "雷神之怒": total_p_dmg = int((10 + int_val) * 5.0) + 850
    
    # 🗡️ 盜賊與暗夜行者系奧義
    elif skill_name == "背刺": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 1.6)
    elif skill_name == "毒刃襲擊": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 2.3) + 100
    elif skill_name == "影分身": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 3.4) + 350
    elif skill_name == "弒神終結": total_p_dmg = int((12 + agi_val + luk_val + (base_weapon_atk - 12 - str_val)) * 5.6) + 900
    elif skill_name == "瞬獄殺": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 6.3) + 1200
    
    # 🏹 弓箭手與遊俠系奧義
    elif skill_name == "二連矢": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 1.7) + 40
    elif skill_name == "狙擊一擊": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 2.5) + 200
    elif skill_name == "爆影狂襲": total_p_dmg = int((12 + agi_val + (base_weapon_atk - 12 - str_val)) * 3.3) + 400
    elif skill_name == "暴風萬箭破": total_p_dmg = int((12 + agi_val + luk_val + (base_weapon_atk - 12 - str_val)) * 5.4) + 1100
    
    # ⛪ 祭師與大主教系奧義 (補血類邏輯由外側同步運算)
    elif skill_name == "聖光懲戒": total_p_dmg = int((10 + int_val + men_val) * 2.4) + 150
    elif skill_name == "神聖讚美詩": total_p_dmg = int((10 + int_val + men_val) * 5.5) + 1000
    
    # 🛡️ 保底兜底：若未命中任何特定技能名，則走基本混合倍率
    else: 
        total_p_dmg = int((str_val + int_val + agi_val) * 1.5)
        
    log_message = f"💥 重創命中！技能對【{{enemy_name}}】造成了 {total_p_dmg} 點實體法術傷害！\n"
    return {"damage": total_p_dmg, "log": log_message}
