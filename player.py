# player.py - 勇者皇家私人物資與狀態控制中心 (指定屬性排序完全體)

import db_core
import jobs
import json

def get_status_card(p):
    """👤 生成 100% 不白漏、不外流、硬核戰力四維狀態面板"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 1. 讀取基礎點數與職涯實體乘算最終面板
    b_str = p.get("strength", 10)
    b_agi = p.get("agility", 10)
    b_int = p.get("intelligence", 10)
    b_vit = p.get("vitality", 10)
    b_luk = p.get("luck", 10)
    b_men = p.get("sprit", 10)

    str_val = int(b_str * job_mod["str_mod"])
    agi_val = int(b_agi * job_mod.get("agi_mod", 1.0))
    int_val = int(b_int * job_mod["int_mod"])
    vit_val = int(b_vit * job_mod["vit_mod"])
    luk_val = int(b_luk * job_mod["luk_mod"])
    men_val = int(b_men * job_mod["men_mod"])

    # 2. 累加多部位已穿戴裝備的隨機副詞綴
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    eq_atk, eq_def = 0, 0
    for slot, eq in equipped.items():
        eq_atk += eq.get("atk", 0)
        eq_def += eq.get("def", 0)
        str_val += eq.get("affixes", {}).get("strength", 0)
        agi_val += eq.get("affixes", {}).get("agility", 0)
        int_val += eq.get("affixes", {}).get("intelligence", 0)
        vit_val += eq.get("affixes", {}).get("vitality", 0)
        luk_val += eq.get("affixes", {}).get("luck", 0)
        men_val += eq.get("affixes", {}).get("sprit", 0)

    # 🧮 3. 精算四大實戰高階白字屬性
    phys_atk = 12 + str_val + eq_atk
    magic_atk = 10 + int_val
    double_chance = min(60.0, 2.0 + (agi_val / 600.0) * 100.0)
    crit_chance = min(80.0, 10.0 + (luk_val / 500.0) * 100.0)

    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)

    if p.get("mp") is None or p["mp"] == "None" or str(p["mp"]).strip() == "":
        p["mp"] = calculated_max_mp
        db_core.save_player(p)

    contents = [
        {"type": "text", "text": f"👤 勇者：[ {p['user_id'][:8]} ]", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"✨ 信仰：{current_job} (T{job_mod['tier']})", "size": "sm", "color": "#34AADC", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"},
        {"type": "text", "text": f"📊 等級：Lv.{level} (EXP: {p['exp']} / {level * 50})", "size": "xs", "color": "#E0E0E0"},
        {"type": "text", "text": f"🩸 血量：{p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#4CD964"},
        {"type": "text", "text": f"🔷 魔力：{p['mp']} / {calculated_max_mp}", "size": "xs", "color": "#007AFF"},
        {"type": "text", "text": f"🪙 資產：{p['gold']} 金幣", "size": "xs", "color": "#FFCC00"},
        {"type": "text", "text": f"📍 座標：📍【 {p.get('current_map', '主城')} 】", "size": "xs", "color": "#AF52DE"},
        {"type": "separator", "margin": "md", "color": "#333333"},
        
        # 🔥 高階實戰面板展示區
        {"type": "text", "text": "⚔️ 【 皇家高階核心戰力屬性 】", "weight": "bold", "size": "xs", "color": "#FF9500"},
        {"type": "box", "layout": "horizontal", "margin": "sm", "contents": [
            {"type": "text", "text": f"💥 物攻: {phys_atk}", "size": "xs", "color": "#FF3B30", "flex": 1},
            {"type": "text", "text": f"🔮 魔攻: {magic_atk}", "size": "xs", "color": "#AF52DE", "flex": 1}
        ]},
        {"type": "box", "layout": "horizontal", "margin": "xs", "contents": [
            {"type": "text", "text": f"⚡ 連擊: {double_chance:.1f}%", "size": "xs", "color": "#34AADC", "flex": 1},
            {"type": "text", "text": f"💥 暴擊: {crit_chance:.1f}%", "size": "xs", "color": "#4CD964", "flex": 1}
        ]},
        {"type": "text", "text": f"🛡️ 防禦: +{eq_def} (多部位附加防禦)", "size": "xs", "color": "#E0E0E0", "margin": "xs"},
        
        {"type": "separator", "margin": "md", "color": "#333333"},
        
        # ✨【💥 完美連通您的全新指定屬性排序】高密度三元素橫向安全 Box
        {"type": "text", "text": "💪 【 六大遠古天賦屬性 】", "weight": "bold", "size": "xs", "color": "#FFCC00"},
        {"type": "box", "layout": "horizontal", "margin": "sm", "spacing": "xs", "contents": [
            {"type": "text", "text": f"🔸力量: {str_val}", "size": "xs", "color": "#E0E0E0", "flex": 1},
            {"type": "text", "text": f"🔸敏捷: {agi_val}", "size": "xs", "color": "#E0E0E0", "flex": 1},
            {"type": "text", "text": f"🔸體力: {vit_val}", "size": "xs", "color": "#E0E0E0", "flex": 1}
        ]},
        {"type": "box", "layout": "horizontal", "margin": "xs", "spacing": "xs", "contents": [
            {"type": "text", "text": f"🔸幸運: {luk_val}", "size": "xs", "color": "#E0E0E0", "flex": 1},
            {"type": "text", "text": f"🔸智力: {int_val}", "size": "xs", "color": "#E0E0E0", "flex": 1},
            {"type": "text", "text": f"🔸精神: {men_val}", "size": "xs", "color": "#E0E0E0", "flex": 1}
        ]},
        {"type": "text", "text": f"💡 (剩餘潛能點數：{p.get('attribute_points', 0)} 點)", "size": "xs", "color": "#FFCC00", "margin": "sm", "weight": "bold"}
    ]

    flex_bubble = {
        "type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": contents}
    }
    return {"flex": flex_bubble, "quick_reply": db_core.make_battle_card("", p, None)["quick_reply"]}

def handle_resurrect(p):
    """😇 處理勇者復活大腦"""
    if p["hp"] > 0:
        return db_core.make_battle_card("💚 提示：您的生命值完好，不需要耗費復活禱告神力！", p, None)
        
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    vit_val = int(p.get("vitality", 10) * job_mod["vit_mod"])
    max_hp = 100 + (vit_val * 5) + (level * 15)

    p["hp"] = max_hp
    p["enemy"] = None
    p["current_map"] = "主城"
    p["gold"] = max(0, p["gold"] - int(p["gold"] * 0.05))
    db_core.save_player(p)
    
    log = "😇 🌟 【 聖光降臨 · 大天使之復活預言 】 🌟 😇\n───────────────────\n✨ 復活成功：傷勢痊癒，體力完全恢復！\n🚪 傳送位置：已被安全送回 ── 📍【主城】！\n💸 死亡代價：扣除 5% 金幣作為靈魂維修費。"
    return db_core.make_battle_card(log, p, None)
