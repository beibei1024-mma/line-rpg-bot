# player.py - 勇者皇家私人物資與狀態控制中心 (Flex 防截斷排版修復版)

import db_core
import jobs
import json

def get_status_card(p):
    """👤 生成完全體防截斷、不字體外流的網格化勇者狀態面板"""
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
    agi_val = int(b_agi * job_mod["agi_mod"])
    int_val = int(b_int * job_mod["int_mod"])
    vit_val = int(b_vit * job_mod["vit_mod"])
    luk_val = int(b_luk * job_mod["luk_mod"])
    men_val = int(b_men * job_mod["men_mod"])

    # 2. 累加多部位已穿戴裝備的隨機副詞綴 (連通實體後台加算)
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    eq_atk = 0
    for slot, eq in equipped.items():
        eq_atk += eq.get("atk", 0)
        str_val += eq.get("affixes", {}).get("strength", 0)
        agi_val += eq.get("affixes", {}).get("agility", 0)
        int_val += eq.get("affixes", {}).get("intelligence", 0)
        vit_val += eq.get("affixes", {}).get("vitality", 0)
        luk_val += eq.get("affixes", {}).get("luck", 0)
        men_val += eq.get("affixes", {}).get("sprit", 0)

    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    
    current_weapon = p.get("weapon", "赤手空拳")

    contents = [
        {"type": "text", "text": f"👤 勇者：[ {p['user_id'][:8]} ]", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"✨ 信仰：{current_job} (T{job_mod['tier']})", "size": "sm", "color": "#34AADC", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"},
        {"type": "text", "text": f"📊 等級：Lv.{level} (EXP: {p['exp']}/{level*50})", "size": "xs", "color": "#E0E0E0"},
        {"type": "text", "text": f"🩸 血量：{p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#4CD964"},
        {"type": "text", "text": f"🔷 魔力：{p.get('mp', calculated_max_mp)} / {calculated_max_mp}", "size": "xs", "color": "#007AFF"},
        {"type": "text", "text": f"🪙 流動資產：{p['gold']} 金幣", "size": "xs", "color": "#FFCC00"},
        {"type": "text", "text": f"⚔️ 武器：{current_weapon} (總裝備物傷 +{eq_atk})", "size": "xs", "color": "#FF9500"},
        {"type": "text", "text": f"📍 座標：【 {p.get('current_map', '主城')} 】", "size": "xs", "color": "#AF52DE"},
        {"type": "separator", "margin": "md", "color": "#333333"},
        {"type": "text", "text": f"💪 潛能點分配 (剩餘可點數：{p.get('attribute_points', 0)} 點)", "weight": "bold", "size": "xs", "color": "#FFCC00", "margin": "xs"}
    ]

    # 🛠️ 重新設計防爆、防擠壓的兩列三行垂直緊湊網格佈局
    attrs = [
        ("力量", str_val, "加點力量 1"), ("敏捷", agi_val, "加點敏捷 1"),
        ("智力", int_val, "加點智力 1"), ("體力", vit_val, "加點體力 1"),
        ("幸運", luk_val, "加點幸運 1"), ("精神", men_val, "加點精神 1")
    ]
    
    for i in range(0, len(attrs), 2):
        name1, val1, cmd1 = attrs[i]
        name2, val2, cmd2 = attrs[i+1]
        
        contents.append({
            "type": "box", "layout": "horizontal", "margin": "md", "spacing": "sm",
            "contents": [
                # 左半邊屬性單元格
                {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                    {"type": "text", "text": f"🔸{name1}: {val1}", "size": "xs", "color": "#E0E0E0", "gravity": "center"},
                    {"type": "button", "style": "primary", "color": "#2C2C2E", "height": "sm", "margin": "xs", "action": {"type": "message", "label": "➕分配 1", "text": cmd1}}
                ]},
                # 右半邊屬性單元格
                {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                    {"type": "text", "text": f"🔸{name2}: {val2}", "size": "xs", "color": "#E0E0E0", "gravity": "center"},
                    {"type": "button", "style": "primary", "color": "#2C2C2E", "height": "sm", "margin": "xs", "action": {"type": "message", "label": "➕分配 1", "text": cmd2}}
                ]}
            ]
        })

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
