import json
import db_core
import weapons

# ⚒️ 獨立工坊：20大區域史詩級隱藏神裝「合成配方大數據庫」
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
    """🛠️ 包裝生成極高質感的純黑工坊合成格子清單"""
    contents = [
        {"type": "text", "text": "⚒️ 皇家遠古禁忌鍛造工坊", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 當前持有的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # 動態並排渲染出所有可手工打造的史詩配方清單與所需材料
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
        
    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "contents": contents}
    }

def execute_forge_weapon(p, target_weapon):
    """🔨 執行工坊合成大腦判定，扣除怪物材料並核發武器"""
    target_weapon = target_weapon.replace("鍛造", "").replace("打造", "").replace(" ", "").strip()
    
    if target_weapon not in FORGE_RECIPES:
        return f"❌ 鍛造失敗！皇家圖紙中沒有【{target_weapon}】這把武器的合成配方。"
        
    recipe = FORGE_RECIPES[target_weapon]
    
    # 檢查金幣是否足夠
    if p["gold"] < recipe["cost_gold"]:
        return f"❌ 🪙 資金不足！鍛造【{target_weapon}】需要手續費 {recipe['cost_gold']} 金幣，你目前只有 {p['gold']} 金幣！"
        
    # 解包讀取玩家目前的材料背包
    inv = p.get("inventory", {"items": {}, "materials": {}})
    if isinstance(inv, str): inv = json.loads(inv)
    player_materials = inv.get("materials", {})
    
    # 驗證所有怪物材料的庫存數量是否達標
    for mat_name, req_count in recipe["materials"].items():
        if player_materials.get(mat_name, 0) < req_count:
            return f"❌ 💎 素材短缺！打造此武器需要【{mat_name}】x{req_count}，但你倉庫裡目前只有 {player_materials.get(mat_name, 0)} 個！"
            
    # 扣除物料金幣與材料數量
    p["gold"] -= recipe["cost_gold"]
    for mat_name, req_count in recipe["materials"].items():
        player_materials[mat_name] -= req_count
        if player_materials[mat_name] == 0: del player_materials[mat_name]
        
    # 回存背包與武器裝備欄位
    inv["materials"] = player_materials
    p["inventory"] = inv
    p["weapon"] = recipe["target"] # 自動神裝上身
    
    db_core.save_player(p)
    return f"🔨 🔥 ✨ 【遠古神兵利器 熔煉大成功】 ✨ 🔥 🔨\n─────────────────\n工坊熔爐中烈火噴湧，古老的符文全數覺醒！\n恭喜你成功打造出了神裝 ── ⚔️【{recipe['target']}】！\n\n💰 扣除手續費金幣：-{recipe['cost_gold']}\n💎 配方所需怪物材料已全數從倉庫扣減！\n💡 裝備狀態：神裝已全自動為你披掛上身，快輸入【我的狀態】縱覽全新爆發戰力！"
