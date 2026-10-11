import json
import db_core
import weapons
import bag

# 🏪 冒險商店：常駐販售的基礎商品數據庫
SHOP_ITEMS = {
    "初級生命藥水": {"type": "potion", "price": 30, "desc": "隨機恢復 30~50 點生命值。"},
    "高級生命藥水": {"type": "potion", "price": 100, "desc": "隨機恢復 80~120 點生命值。"},
    
    "新手鐵短劍": {"type": "weapon", "price": 150, "desc": "物傷 +15。適合剛出村的新手勇者。"},
    "微光木藤弓": {"type": "weapon", "price": 800, "desc": "物傷 +45。森林老獵人常用的木弓。"},
    "凜冬不融碎冰刺": {"type": "weapon", "price": 2500, "desc": "物傷 +95。散發著淡淡寒氣的冰刺。"},
    "黑曜熔岩大劍": {"type": "weapon", "price": 6000, "desc": "物傷 +160。黑曜石打造，揮砍帶有熱浪。"}
}

def get_shop_card(p):
    """🎨 生成極具質感的黑曜石風格「視覺化商店補給圖卡」"""
    contents = [
        {"type": "text", "text": "🏪 冒險者公會・皇家補給商店", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 您目前的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    contents.append({"type": "text", "text": "🧪 【煉金藥水補給物資】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info["type"] == "potion":
            contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🔹 {name} (🪙 {info['price']} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"購買 {name}"}}
                ]
            })

    contents.append({"type": "text", "text": "⚔️ 【鐵匠鋪現貨基礎兵器】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info["type"] == "weapon":
            contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🗡️ {name} (🪙 {info['price']} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"購買 {name}"}}
                ]
            })

    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def buy_weapon(p, item_name):
    """🛒 商店交易大腦：已完美接通武器背包備用庫防丟機制！"""
    item_name = item_name.replace("購買", "").replace("下單", "").replace(" ", "").strip()
    
    if item_name not in SHOP_ITEMS:
        return f"❌ 交易失敗！冒險商店目前沒有販售【{item_name}】這件商品。"
        
    config = SHOP_ITEMS[item_name]
    if p["gold"] < config["price"]:
        return f"❌ 🪙 餘額不足！購買【{item_name}】需要 {config['price']} 金幣，你目前只有 {p['gold']} 金幣！"
        
    p["gold"] -= config["price"]
    
    if config["type"] == "potion":
        bag.add_to_inventory(p, item_name, is_material=False)
        db_core.save_player(p)
        return f"🛒 🧪 【交易成功】 🧪 🛒\n─────────────────\n你支付了 {config['price']} 金幣，購買了【{item_name}】x1！\n📦 物資已存入【我的背包】倉庫！"
        
    elif config["type"] == "weapon":
        if p.get("weapon") == item_name:
            return f"❌ 你目前已經裝備著【{item_name}】了，不需要重複購買一模一樣的兵器。"
            
        # ✨ 【Bug 核心校正點】買新裝備換衣服前，全自動將舊身上的武器塞入「備用武器庫」
        # ✨ 連動 forge_system 格式，徹底消滅商店貨脫下被吃掉的漏洞！
        old_w = p.get("weapon", "赤手空拳")
        if old_w != "赤手空拳":
            w_inv_str = p.get("weapon_inventory", "{}")
            if w_inv_str is None or w_inv_str == "None" or w_inv_str == "": w_inv_str = "{}"
            try: 
                w_dict = json.loads(w_inv_str)
            except Exception: 
                w_dict = {}
            w_dict[old_w] = w_dict.get(old_w, 0) + 1
            p["weapon_inventory"] = json.dumps(w_dict, ensure_ascii=False)
            
        # 換上新武器，並重置神匠加成防止作弊
        p["weapon"] = item_name
        p["forge_weapon_bonus"] = 0 
        db_core.save_player(p)
        return f"🛒 ⚔️ 【神兵補給成功】 ⚔️ 🛒\n─────────────────\n你支付了 {config['price']} 金幣，成功購買了【{item_name}】！\n🔥 皇家鐵匠當場為你更換武裝！換下來的舊武器已安全移入您的備用倉庫中！\n💡 輸入【我的裝備】即可一鍵穿脫此商店兵器！"
