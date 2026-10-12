# player.py - 勇者皇家私人物資與狀態控制中心

import db_core
import jobs
import weapons

def get_status_card(p):
    """👤 生成網格化勇者個人神聖屬性面板與自由配點 UI"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 六大基礎屬性
    b_str = p.get("strength", 10)
    b_agi = p.get("agility", 10)
    b_int = p.get("intelligence", 10)
    b_vit = p.get("vitality", 10)
    b_luk = p.get("luck", 10)
    b_men = p.get("sprit", 10)

    # 實體乘算最終面板戰力
    str_val = int(b_str * job_mod["str_mod"])
    agi_val = int(b_agi * job_mod["agi_mod"])
    int_val = int(b_int * job_mod["int_mod"])
    vit_val = int(b_vit * job_mod["vit_mod"])
    luk_val = int(b_luk * job_mod["luk_mod"])
    men_val = int(b_men * job_mod["men_mod"])

    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    
    # 讀取當前裝備總攻擊力
    current_weapon = p.get("weapon", "赤手空拳")
    pure_w_name = current_weapon.split(" 的 ")[-1] if " 的 " in current_weapon else current_weapon
    w_bonus = weapons.SHOP_WEAPONS[pure_w_name]["atk_bonus"] if pure_w_name in weapons.SHOP_WEAPONS else 0
    w_bonus += int(p.get("forge_weapon_bonus", 0))

    contents = [
        {"type": "text", "text": f"👤 勇者：【 {p['user_id'][:8]}... 】", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"👑 職業信仰：✨ {current_job} (階級 T{job_mod['tier']})", "size": "sm", "color": "#34AADC", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"},
        {"type": "text", "text": f"📊 當前等級：Lv.{p['level']}  (經驗: {p['exp']}/{p['level']*50})", "size": "xs", "color": "#E0E0E0"},
        {"type": "text", "text": f"🩸 皇家血量：{p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#4CD964"},
        {"type": "text", "text": f"🔷 皇家魔力：{p.get('mp', calculated_max_mp)} / {calculated_max_mp}", "size": "xs", "color": "#007AFF"},
        {"type": "text", "text": f"🪙 流動資產：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00"},
        {"type": "text", "text": f"🗡️ 手持武裝：⚔️ {current_weapon} (物傷 +{w_bonus})", "size": "xs", "color": "#FF9500"},
        {"type": "text", "text": f"📍 當前星際座標：【 {p.get('current_map', '主城')} 】", "size": "xs", "color": "#AF52DE"},
        {"type": "separator", "margin": "md", "color": "#333333"},
        {"type": "text", "text": f"💪 六大核心潛能屬性 (剩餘自由潛能點：{p.get('attribute_points', 0)} 點)", "weight": "bold", "size": "sm", "color": "#FFCC00"}
    ]

    # 橫向網格化展示加點項目
    attr_list = [("力量 (STR)", str_val, "加點力量 1"), ("敏捷 (AGI)", agi_val, "加點敏捷 1"), 
                 {"name": "智力 (INT)", "val": int_val, "cmd": "加點智力 1"}, {"name": "體力 (VIT)", "val": vit_val, "cmd": "加點體力 1"},
                 {"name": "幸運 (LUK)", "val": luk_val, "cmd": "加點幸運 1"}, {"name": "精神 (MEN)", "val": men_val, "cmd": "加點精神 1"}]
                 
    for i in range(0, len(attr_list), 2):
        item1 = attr_list[i] if isinstance(attr_list[i], dict) else {"name": attr_list[i][0], "val": attr_list[i][1], "cmd": attr_list[i][2]}
        item2 = attr_list[i+1] if isinstance(attr_list[i+1], dict) else {"name": attr_list[i+1][0], "val": attr_list[i+1][1], "cmd": attr_list[i+1][2]}
        
        contents.append({
            "type": "box", "layout": "horizontal", "margin": "sm",
            "contents": [
                {"type": "text", "text": f"🔸 {item1['name']}: {item1['val']}", "size": "xs", "color": "#E0E0E0", "flex": 1, "gravity": "center"},
                {"type": "button", "style": "primary", "color": "#2C2C2E", "height": "sm", "flex": 1, "action": {"type": "message", "label": "➕ 點 1", "text": item1['cmd']}},
                {"type": "text", "text": f"🔸 {item2['name']}: {item2['val']}", "size": "xs", "color": "#E0E0E0", "flex": 1, "gravity": "center"},
                {"type": "button", "style": "primary", "color": "#2C2C2E", "height": "sm", "flex": 1, "action": {"type": "message", "label": "➕ 點 1", "text": item2['cmd']}}
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
        card = db_core.make_battle_card("💚 提示：您的生命值尚且完好，不需浪費大天使的復活禱告神力！", p, None)
        return card
        
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    vit_val = int(p.get("vitality", 10) * job_mod["vit_mod"])
    max_hp = 100 + (vit_val * 5) + (level * 15)

    # 執行復活：血量灌滿、清空遭遇怪物、自動移回主城、並扣除少量金幣罰則
    p["hp"] = max_hp
    p["enemy"] = None
    p["current_map"] = "主城"
    p["gold"] = max(0, p["gold"] - int(p["gold"] * 0.05)) # 死亡懲罰：扣除5%金幣
    db_core.save_player(p)
    
    log = "😇 🌟 【 聖光降臨・大天使之復活預言 】 🌟 😇\n───────────────────\n諸神聽到了你的悲鳴，神聖法陣在天際撕開裂縫！\n\n✨ 復活成功：你的傷勢已全數痊癒，體力完全恢復！\n🚪 傳送位置：你已被安全送回 ── 📍【主城】區域！\n💸 復活代價：搜刮陣亡軀殼，鐵匠鋪收走 5% 金幣作為維修費。"
    
    return db_core.make_battle_card(log, p, None)
