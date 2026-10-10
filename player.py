import db_core
import weapons
import jobs

def get_status_text(p):
    """【原創天賦面板】讀取資料庫六大屬性與剩餘自由點數，動態計算衍生戰鬥數據"""
    level = p.get("level", 1)
    
    # 🎭 1. 讀取與初始化職業名稱
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]
    
    # 🎲 2. 讀取基礎屬性與未分配自由點數
    base_str = p.get("strength", 10 + (level * 3))       
    base_agi = p.get("agility", 10 + (level * 2))        
    base_int = p.get("intelligence", 10 + (level * 2))   
    base_vit = p.get("vitality", 10 + (level * 3))       
    base_luk = p.get("luck", 10 + (level * 1))           
    base_men = p.get("sprit", 10 + (level * 2))          
    free_pts = p.get("attribute_points", 0) # 讀取未分配點數
    
    # 🧮 3. 實體套用職業天賦倍率加成公式
    str_val = int(base_str * job_mod["str_mod"]) 
    agi_val = int(base_agi * job_mod["agi_mod"]) 
    int_val = int(base_int * job_mod["int_mod"]) 
    vit_val = int(base_vit * job_mod["vit_mod"]) 
    luk_val = int(base_luk * job_mod["luk_mod"]) 
    men_val = int(base_men * job_mod["men_mod"]) 
    
    # ⚔️ 4. 讀取裝備與基礎物理攻擊力
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    
    min_p_dmg = 5 + (str_val // 2) + w_bonus
    max_p_dmg = 12 + str_val + w_bonus
    evade_chance = min(50, 5 + (agi_val // 8))          
    double_atk_chance = min(60, 2 + (agi_val // 6))     
    min_m_dmg = 3 + (int_val // 2)
    max_m_dmg = 10 + int_val
    defense = vit_val // 2
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    crit_chance = min(80, 10 + (luk_val // 5))          
    crit_dmg_multiplier = 1.5 + (luk_val * 0.005)       
    m_defense = men_val // 2
    max_mp = 50 + (men_val * 4) + (level * 5)
    current_mp = p.get("mp", max_mp)

    # 📜 5. 動態串接目前職業解鎖的技能列表
    skill_text = ""
    for s_name, s_info in job_mod["skills"].items():
        skill_text += f"   ⚡ 【{s_name}】：{s_info['desc']}\n"

    # 🔮 6. 點數提示文字優化：如果有剩下的點數，亮起發光驚嘆號
    if free_pts > 0:
        pts_notice = f"✨ 🌟 【未分配潛能點數】：🔥 {free_pts} 點\n"
    else:
        pts_notice = f"✨ 🌟 【未分配潛能點數】：0 點\n"

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
        f"{pts_notice}" # 渲染剩餘潛能點數
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
        f"✍️ 加點口令：輸入【加點 屬性名稱 點數】手動變強！\n（屬性可填：力量、敏捷、智力、體力、幸運、精神。例如：加點 敏捷 5）"
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
