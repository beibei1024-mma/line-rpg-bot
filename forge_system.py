# forge_system.py - 皇家禁忌工坊與隨機熔煉核心大腦 v3.0

import json
import random
import db_core
import equipment_core
import player_equipment

# 📜 皇家遠古手工鍛造圖紙配方庫 (消耗金幣與各地圖素材)
FORGE_RECIPES = {
    "新手鐵短劍": {"slot": "武器", "base": "鐵劍", "gold": 500, "mat": "史萊姆黏液", "mat_qty": 3},
    "微光木藤弓": {"slot": "武器", "base": "長弓", "gold": 1500, "mat": "強韌蜘蛛絲", "mat_qty": 5},
    "凜冬不融碎冰刺": {"slot": "武器", "base": "法杖", "gold": 5000, "mat": "不融冰塊", "mat_qty": 5},
    "黑曜熔岩大劍": {"slot": "武器", "base": "鐵劍", "gold": 12000, "mat": "熔岩核心", "mat_qty": 8},
    "荒漠斬馬刀": {"slot": "武器", "base": "鐵劍", "gold": 30000, "mat": "古老生鏽長劍", "mat_qty": 10},
    "皇家獅鷲精鋼重盔": {"slot": "頭盔", "base": "鐵盔", "gold": 25000, "mat": "迅捷羽毛", "mat_qty": 6},
    "魔化冥鐵重鐮": {"slot": "武器", "base": "法杖", "gold": 75000, "mat": "永夜陰影", "mat_qty": 12},
    "紅蓮龍骨逆鱗劍": {"slot": "武器", "base": "鐵劍", "gold": 200000, "mat": "巨龍逆鱗", "mat_qty": 1},
    "舊神支配者之刃": {"slot": "武器", "base": "鐵劍", "gold": 600000, "mat": "舊神支配者之眼", "mat_qty": 1}
}

def get_forge_menu(p):
    """🛠️ 生成極致奢華的工坊手工鍛造藍圖 Flex 展售選單"""
    contents = [
        {"type": "text", "text": "⚒️ 皇家遠古皇家鍛造熔煉工坊", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 勇者流動金幣：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # 展示前 5 檔核心神兵圖紙
    for name, r in list(FORGE_RECIPES.items())[:5]:
        contents.append({
            "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
            "contents": [
                {"type": "text", "text": f"📜 圖紙：【{name}】({r['slot']})", "size": "xs", "color": "#FF9500", "weight": "bold"},
                {"type": "text", "text": f"💰 消耗：🪙 {r['gold']} 金幣", "size": "xxs", "color": "#FFCC00", "margin": "xs"},
                {"type": "text", "text": f"📦 材料：🛠️ {r['mat']} x{r['mat_qty']}", "size": "xxs", "color": "#34AADC"},
                {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                 "action": {"type": "message", "label": "⚒️ 投入素材開始熔煉", "text": f"鍛造 {name}"}}
            ]
        })
        
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def execute_forge_weapon(p, cmd_str):
    """⚒️ 核心熔煉大腦：扣除金幣與包包素材，博弈概率洗鍊隨機品質裝備"""
    blueprint = cmd_str.replace("鍛造", "").replace(" ", "").strip()
    if blueprint not in FORGE_RECIPES:
        return "❌ 打造失敗！遠古工坊中沒有記載該裝備的神聖圖紙配方。"
        
    recipe = FORGE_RECIPES[blueprint]
    
    # 1. 檢查金幣
    if p["gold"] < recipe["gold"]:
        return f"❌ 打造失敗！🪙 資金不足！打造【{blueprint}】需要 {recipe['gold']} 金幣，你目前只有 {p['gold']} 金幣。"
        
    # 2. 檢查背包素材數量 (從 p 的 inventory 字典比對)
    inv = p.get("inventory", {})
    if isinstance(inv, str):
        try: inv = json.loads(inv)
        except: inv = {}
        
    current_mat_qty = inv.get(recipe["mat"], 0)
    if current_mat_qty < recipe["mat_qty"]:
        return f"❌ 打造失敗！🛠️ 鍛造素材不足！你需要【{recipe['mat']}】x{recipe['mat_qty']}，但你目前只有 {current_mat_qty} 個。"
        
    # 3. 扣除代價
    p["gold"] -= recipe["gold"]
    inv[recipe["mat"]] = current_mat_qty - recipe["recipe_mat_qty"] if "recipe_mat_qty" in recipe else current_mat_qty - recipe["mat_qty"]
    p["inventory"] = json.dumps(inv, ensure_ascii=False)
    
    # 4. 機率洗鍊裝備品質 (手工鍛造有高達 10% 的高機率直接爆出「史詩」或「遠古神話」品質！)
    rolled_rarity = random.choices(
        ["⭐普通", "🔷魔法", "🌟稀有", "🔥史詩", "👑遠古神話"],
        weights=[25, 40, 25, 8, 2], k=1
    )[0]
    
    # 生成對應部位的動態暗黑屬性裝備封包
    new_eq = equipment_core.generate_random_equipment(recipe["slot"], recipe["base"], forced_rarity=rolled_rarity)
    # 修改裝備名稱使其符合圖紙名稱
    new_eq["name"] = new_eq["name"].replace(recipe["base"], blueprint)
    
    # 5. 安全塞入備用裝備包
    from dynamic_market import _add_to_equipment_inventory
    _add_to_equipment_inventory(p, new_eq)
    
    db_core.save_player(p)
    
    return f"⚒️ 🔥 【 工坊熔煉天啟大成功 】 🔥 ⚒️\n───────────────────\n鐵匠揮舞重錘，熔岩鐵水四濺！你投入的素材在法陣中完美凝聚！\n\n🔨 成功打造：{new_eq['name']} ({recipe['slot']})！\n✨ 品質天啟：成功洗鍊出 ── 【{rolled_rarity}】階級！\n📦 存放去向：神兵利器已全自動送入【我的裝備包】，快去穿戴享受暴漲的白字屬性加成吧！"
