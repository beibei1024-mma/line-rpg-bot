import json
import db_core
import weapons

# ⚒️ 遠古神兵利器合成配方大數據庫 (維持原樣)
FORGE_RECIPES = {
    "新手鐵短劍": {"cost_gold": 100, "materials": {"史萊姆黏液": 3, "破爛的匕首": 1}, "target": "新手鐵短劍"},
    "微光木藤弓": {"cost_gold": 500, "materials": {"強韌蜘蛛絲": 5, "古樹核心": 1}, "target": "微光木藤弓"},
    "凜冬不融碎冰刺": {"cost_gold": 1500, "materials": {"不融冰塊": 10, "寒冰精粹": 2}, "target": "凜冬不融碎冰刺"},
    "黑曜熔岩大劍": {"cost_gold": 4000, "materials": {"熔岩核心": 12, "黑曜石外殼": 4}, "target": "黑曜熔岩大劍"},
    "荒漠斬馬刀": {"cost_gold": 9000, "materials": {"古老生鏽長劍": 3, "強盜面罩": 5}, "target": "荒漠斬馬刀"},
    "魔化冥鐵重鐮": {"cost_gold": 25000, "materials": {"永夜陰影": 15, "魔化冥鐵鎧甲": 2}, "target": "魔化冥鐵重鐮"},
    "紅蓮龍骨逆鱗劍": {"cost_gold": 100000, "materials": {"飛龍雙翼": 10, "巨龍逆鱗": 1}, "target": "紅蓮龍骨逆鱗劍"},
    "舊神支配者之刃": {"cost_gold": 500000, "materials": {"純淨虛空結晶": 20, "舊神支配者之眼": 1}, "target": "舊神支配者之刃"}
}

def get_forge_menu(p):
    """🛠️ 生成極高質感的純黑工坊合成格子清單 (維持原樣)"""
    contents = [
        {"type": "text", "text": "⚒️ 皇家遠古禁忌鍛造工坊", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 當前持有的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    for w_name, req in FORGE_RECIPES.items():
        w_atk = weapons.SHOP_WEAPONS[w_name]["atk_bonus"]
        mat_text = ", ".join([f"{k}x{v}" for k, v in req["materials"].items()])
        contents.append({
            "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
            "contents": [
                {"type": "text", "text": f"⚔️ {w_name} (永久物傷 +{w_atk})", "size": "sm", "color": "#4CD964", "weight": "bold"},
                {"type": "text", "text": f"📋 所需材料：{mat_text}", "size": "xs", "color": "#E0E0E0", "margin": "xs"},
                {"type": "text", "text": f"🪙 手工合成手續費：{req['cost_gold']} 金幣", "size": "xs", "color": "#FF9500", "margin": "xs"},
                {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "sm",
                 "action": {"type": "message", "label": f"🔨 開爐鍛造 {w_name}", "text": f"鍛造 {w_name}"}}
            ]
        })
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def execute_forge_weapon(p, target_weapon):
    """🔨 執行工坊合成大腦判定，扣除怪物材料並核發武器 (維持原樣)"""
    target_weapon = target_weapon.replace("鍛造", "").replace("打造", "").replace(" ", "").strip()
    if target_weapon not in FORGE_RECIPES: return f"❌ 遠古圖紙中沒有【{target_weapon}】的合成配方。"
    recipe = FORGE_RECIPES[target_weapon]
    if p["gold"] < recipe["cost_gold"]: return f"❌ 金幣不足！需要手續費 {recipe['cost_gold']} 金幣！"
    inv = p.get("inventory", {"items": {}, "materials": {}})
    if isinstance(inv, str): inv = json.loads(inv)
    player_materials = inv.get("materials", {})
    for mat_name, req_count in recipe["materials"].items():
        if player_materials.get(mat_name, 0) < req_count: return f"❌ 素材短缺！需要【{mat_name}】x{req_count}！"
    p["gold"] -= recipe["cost_gold"]
    for mat_name, req_count in recipe["materials"].items():
        player_materials[mat_name] -= req_count
        if player_materials[mat_name] == 0: del player_materials[mat_name]
    inv["materials"] = player_materials
    p["inventory"] = inv
    
    # ✨ 核心機制優化：如果原本身上有舊武器，全自動丟入「備用武器庫」，再換上新神裝
    old_w = p.get("weapon", "赤手空拳")
    if old_w != "赤手空拳": add_to_weapon_inventory(p, old_w)
    
    p["weapon"] = recipe["target"]
    db_core.save_player(p)
    return f"🔨 🔥 ✨ 【神兵熔煉大成功】 ✨ 🔥 🔨\n恭喜你成功打造出了神裝 ── ⚔️【{recipe['target']}】！\n已全自動為你披掛上身！"

# ─────────────────────────────────────────────────────────────
# 🌟 以下為全新擴充的「查看裝備欄、脫下裝備、放回武器背包」的核心大腦
# ─────────────────────────────────────────────────────────────

def get_equipment_card(p):
    """⚔️ 🤖 生成極高質感的純黑風格「勇者實體裝備欄面板」卡片"""
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0
    w_desc = weapons.SHOP_WEAPONS[current_weapon]["desc"] if current_weapon in weapons.SHOP_WEAPONS else "赤手空拳，毫無攻擊力加成。"
    
    contents = [
        {"type": "text", "text": "🛡️ 勇者神聖裝備欄面板", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"},
        # 當前手持神兵展示區
        {"type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
         "contents": [
             {"type": "text", "text": "⚔️ 主手武器 (Main-Hand Weapon)", "size": "xs", "color": "#007AFF", "weight": "bold"},
             {"type": "text", "text": f"【 {current_weapon} 】", "size": "md", "color": "#4CD964", "weight": "bold", "marginTop": "xs"},
             {"type": "text", "text": f"💥 實體物理傷害增幅：+{w_bonus} 點", "size": "xs", "color": "#FF9500", "margin": "xs"},
             {"type": "text", "text": f"📖 兵器神話：{w_desc}", "size": "xs", "color": "#8E8E93", "margin": "xs", "wrap": True}
         ]}
    ]
    
    # 如果玩家手上有裝備，動態解鎖「一鍵脫掉」的按鈕
    if current_weapon != "赤手空拳":
        contents.append({
            "type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "marginTop": "sm",
            "action": {"type": "message", "label": f"❌ 卸下【{current_weapon}】放回背包", "text": "脫下裝備"}
        })
    else:
        contents.append({"type": "text", "text": "💡 提示：目前正赤手空拳，您可以點擊下方控制選單的【我的背包】或【冒險商店】來物色並裝備武器道具！", "size": "xs", "color": "#8E8E93", "margin": "md", "wrap": True})
        
    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "contents": contents}
    }

def execute_unequip_weapon(p):
    """❌ 執行脫下裝備大腦：將身上武器換回赤手空拳，並將舊武器完整丟回武器背包欄"""
    current_weapon = p.get("weapon", "赤手空拳")
    if current_weapon == "赤手空拳":
        return "❌ 脫除失敗！你目前本來就赤手空拳，身上沒有任何防具或兵器可以卸下。"
        
    # 將舊武器安全塞入備用武器背包庫
    add_to_weapon_inventory(p, current_weapon)
    
    # 身上狀態回復為赤手空拳
    p["weapon"] = "赤手空拳"
    db_core.save_player(p)
    
    return f"❌ 🛡️ 【裝備卸下成功】放回背包 ❌\n─────────────────\n你輕巧地解開了扣環，將手持的神兵利器 ── ⚔️【{current_weapon}】安全解下！\n\n📦 去向：該武器已完美存入您的【武器背包欄】倉庫中！\n💡 戰力變動：你的裝備攻擊力加成已暫時歸零，快點擊底部滑動選單開啟【我的背包】重新物色或更換神裝吧！"

def add_to_weapon_inventory(p, w_name):
    """📦 內部代理工具：負責將多餘武器包裝成 JSON 寫入字串欄位"""
    w_inv_str = p.get("weapon_inventory", "{}")
    if w_inv_str is None or w_inv_str == "None" or w_inv_str == "": w_inv_str = "{}"
    try:
        w_dict = json.loads(w_inv_str)
    except Exception:
        w_dict = {}
    w_dict[w_name] = w_dict.get(w_name, 0) + 1
    p["weapon_inventory"] = json.dumps(w_dict, ensure_ascii=False)
