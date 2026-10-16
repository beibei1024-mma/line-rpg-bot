# combat_engine.py - 皇家戰鬥傷害與技能奧義計算獨立核心

import random
import weapons
import skills_calculator

def calculate_player_attack(p, job_mod, eq_bonus, w_bonus):
    """⚔️ 計算玩家普通攻擊（含爆擊與連擊）"""
    level = p.get("level", 1)
    base_str = p.get("strength", 10 + (level * 3)) + eq_bonus["strength"]
    base_luk = p.get("luck", 10 + (level * 1)) + eq_bonus["luck"]
    base_agi = p.get("agility", 10 + (level * 2)) + eq_bonus["agility"]

    str_val = int(base_str * job_mod["str_mod"])
    luk_val = int(base_luk * job_mod["luk_mod"])
    agi_val = int(base_agi * job_mod["agi_mod"])

    crit_chance = min(80, 10 + (luk_val // 5)) / 100.0
    crit_dmg_mod = 1.5 + (luk_val * 0.005)
    double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0
    is_double = random.random() < double_atk_chance

    log = ""
    total_dmg = 0

    # 第 1 擊
    d1 = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
    if random.random() < crit_chance:
        d1 = int(d1 * crit_dmg_mod)
        log += f"💥 致命爆擊！第 1 擊斬出 {d1} 點爆擊物理傷害！\n"
    else:
        log += f"⚔️ 第 1 擊普通命中，造成 {d1} 點物理傷害！\n"
    total_dmg += d1

    # 第 2 擊（連擊）
    if is_double:
        d2 = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
        if random.random() < crit_chance:
            d2 = int(d2 * crit_dmg_mod)
            log += f"💥 致命爆擊！第 2 擊斬出 {d2} 點爆擊物理傷害！\n"
        else:
            log += f"⚔️ 第 2 擊普通命中，造成 {d2} 點物理傷害！\n"
        total_dmg += d2

    return total_dmg, log

def calculate_skill_attack(p, job_mod, eq_bonus, w_bonus, skill_name):
    """🔮 計算玩家施放技能奧義傷害"""
    level = p.get("level", 1)
    base_str = p.get("strength", 10 + (level * 3)) + eq_bonus["strength"]
    base_int = p.get("intelligence", 10 + (level * 2)) + eq_bonus["intelligence"]
    base_vit = p.get("vitality", 10 + (level * 3)) + eq_bonus["vitality"]
    base_agi = p.get("agility", 10 + (level * 2)) + eq_bonus["agility"]
    base_luk = p.get("luck", 10 + (level * 1)) + eq_bonus["luck"]
    base_men = p.get("sprit", 10 + (level * 2)) + eq_bonus["sprit"]

    str_val = int(base_str * job_mod["str_mod"])
    int_val = int(base_int * job_mod["int_mod"])
    vit_val = int(base_vit * job_mod["vit_mod"])
    agi_val = int(base_agi * job_mod["agi_mod"])
    luk_val = int(base_luk * job_mod["luk_mod"])
    men_val = int(base_men * job_mod["men_mod"])

    log = ""
    total_dmg = 0

    if skill_name in ("治癒術", "群體療癒", "淨化術", "復活預言"):
        mult = 3.5 if skill_name in ("群體療癒", "復活預言") else 2.5
        heal = int((int_val + men_val) * mult)
        old_h = p["hp"]
        max_hp_val = 100 + (vit_val * 5) + (level * 15)
        p["hp"] = min(max_hp_val, p["hp"] + heal)
        log += f"💖 聖光治癒！神聖恢復了生命值 +{p['hp'] - old_h} 點！\n"
        if skill_name in ("淨化術", "復活預言"):
            log += "✨ 聖光護體！本回合防禦力額外提升 2 倍！\n"
        return 0, log

    base_weapon_atk = 12 + str_val + w_bonus
    calc_res = skills_calculator.calculate_active_skill_damage(
        skill_name, base_weapon_atk, int_val, vit_val, str_val, agi_val, luk_val, men_val
    )
    total_dmg = calc_res["damage"]
    if calc_res["log"]:
        log += calc_res["log"]

    return total_dmg, log
# === END OF FILE ===
