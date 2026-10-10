import db_core
import weapons
import jobs

def get_status_text(p):
    """【原創職業與屬性面板】讀取資料庫職業與六大天賦，並動態套用職業乘數加成"""
    level = p.get("level", 1)
    
    # 🎭 1. 讀取與初始化職業名稱（預設為初心者）
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]
    
    # 🎲 2. 讀取基礎屬性（若為新玩家，自動依等級給予基礎值）
    base_str = p.get("strength", 10 + (level * 3))       
    base_agi = p.get("agility", 10 + (level * 2))        
    base_int = p.get("intelligence", 10 + (level * 2))   
    base_vit = p.get("vitality", 10 + (level * 3))       
    base_luk = p.get("luck", 10 + (level * 1))           
    base_men = p.get("sprit", 10 + (level * 2))          
    
    # 🧮 3. 實體套用職業天賦倍率加成公式（完全對齊你的設計需求！）
    str_val = int(base_str * job_mod["str_mod"]) # 力量受職業加成
    agi_val = int(base_agi * job_mod["agi_mod"]) # 敏捷受職業加成
    int_val = int(base_int * job_mod["int_mod"]) # 智力受職業加成
    vit_val = int(base_vit * job_mod["vit_mod"]) # 體力受職業加成
    luk_val = int(base_luk * job_mod["luk_mod"]) # 幸運受職業加成
    men_val = int(base_men * job_mod["men_mod"]) # 精神受職業加成
    
    # ⚔️ 4. 讀取裝備與基礎物理攻擊力
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    
    # 💪 力量影響：物理傷害最大與最小值起伏
    min_p_dmg = 5 + (str_val // 2) + w_bonus
    max_p_dmg = 12 + str_val + w_bonus
    
    # ⚡ 敏捷影響：閃避率、連續攻擊機率
    evade_chance = min(50, 5 + (agi_val // 8))          
    double_atk_chance = min(60, 2 + (agi_val // 6))     
    
    # 🔮 智力影響：魔法攻擊最大與最小魔法傷害
    min_m_dmg = 3 + (int_val // 2)
    max_m_dmg = 10 + int_val
    
    # 🛡️ 體力影響：物理防禦力與最大血量上限
    defense = vit_val // 2
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    
    # 🍀 幸運影響：爆擊率、爆擊傷害倍率
    crit_chance = min(80, 10 + (luk_val // 5))          
    crit_dmg_multiplier = 1.5 + (luk_val * 0.005)       
    
    # 🌟 精神影響：魔法防禦力、最大魔力(MP)
    m_defense = men_val // 2
    max_mp = 50 + (men_val * 4) + (level * 5)
    current_mp = p.get("mp", max_mp)

    # 📜 5. 動態串接目前職業解鎖的技能列表
    skill_text = ""
    for s_name, s_info in job_mod["skills"].items():
        skill_text += f"   ⚡ 【{s_name}】：{s_info['desc']}\n"

    return (
        f"👤 【勇者狀態面板】\n"
        f"─────────────────\n"
        f"🏅 冒險等級：Lv.{level}\n"
        f"🎭 當前職業：🔥【{current_job}】(階級 {job_mod['tier']})\n"
        f"📍 當前位置：📍【{p.get('current_map', '新手村')}】\n"
        f"💖 生命狀態：{p['hp']} / {calculated_max_hp}\n"
        f"🔷 魔力狀態：{current_mp} / {max_mp}\n"
        f"⚔️ 當前裝備：{p['weapon']} (傷害+{w_bonus})\n"
        f"💰 擁有金幣：💰 {p['gold']}\n"
        f"🌟 經驗進度：{p['exp']} / {level * 50}\n"
        f"─────────────────\n"
        f"💪 力量 (STR)：{str_val} 點 (基礎:{base_str}x{job_mod['str_mod']})\n"
        f"   ┠ 🚀 物理傷害：⚔️ {min_p_dmg} ～ {max_p_dmg}\n"
        f"⚡ 敏捷 (AGI)：{agi_val} 點 (基礎:{base_agi}x{job_mod['agi_mod']})\n"
        f"   ┠ 💨 戰場閃避率：{evade_chance}%\n"
        f"   ┠ 🌪️ 連續攻擊率：{double_atk_chance}%\n"
        f"🔮 智力 (INT)：{int_val} 點 (基礎:{base_int}x{job_mod['int_mod']})\n"
        f"   ┠ 🔮 魔法傷害：✨ {min_m_dmg} ～ {max_m_dmg}\n"
        f"🛡️ 體力 (VIT)：{vit_val} 點 (基礎:{base_vit}x{job_mod['vit_mod']})\n"
        f"   ┠ 🧱 物理防禦：{defense} 點\n"
        f"🍀 幸運 (LUK)：{luk_val} 點 (基礎:{base_luk}x{job_mod['luk_mod']})\n"
        f"   ┠ 🔥 致命爆擊率：{crit_chance}%\n"
        f"   ┠ 💥 爆擊傷害：{int(crit_dmg_multiplier * 100)}%\n"
        f"🌟 精神 (MEN)：{men_val} 點 (基礎:{base_men}x{job_mod['men_mod']})\n"
        f"   ┠ 🌀 魔法防禦：{m_defense} 點\n"
        f"─────────────────\n"
        f"📖 【當前職業學會技能】\n"
        f"{skill_text}"
        f"─────────────────\n"
        f"💡 提示：輸入【世界地圖】或點擊選單即可出發探險！"
    )

def handle_resurrect(p):
    if p["hp"] > 0:
        return "你還活著呢！"
    else:
        level = p.get("level", 1)
        current_job = p.get("job", "初心者")
        job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
        
        base_vit = p.get("vitality", 10 + (level * 3))
        vit_val = int(base_vit * job_mod["vit_mod"])
        max_hp = 100 + (vit_val * 5) + (level * 15)
        
        p["hp"] = int(max_hp * 0.5)
        p["gold"] = max(0, p["gold"] - 20)
        db_core.save_player(p)
        return f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
