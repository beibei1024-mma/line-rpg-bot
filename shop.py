# shop.py - 皇家一般常駐物資補給商店 v4.5

import json
import db_core
import bag
import equipment_core
import player_equipment

# 🏪 冒險商店：上架販售的常駐商品數據庫（金幣計價，完全保留您的文字文案與說明）
SHOP_ITEMS = {
    # 🧪 【消耗品區】
    "初級生命藥水": {"type": "potion", "price": 30, "desc": "隨機恢復 30~50 點生命值。"},
    "高級生命藥水": {"type": "potion", "price": 100, "desc": "隨機恢復 80~120 點生命值。"},
    
    # ⚔️ 【基礎武器區】（連通多部位基本底層白字對照）
    "生鏽的鐵劍": {"atk_bonus": 15000, "price": 50, "desc": "一把在倉庫角落翻出來的古舊鐵劍，雖然鈍了點但總比拳頭好。"},
    "新手短弓": {"atk_bonus": 8, "price": 150, "desc": "獵人學徒常用的基礎短弓，拉力普通但勝在輕巧靈活。"},
    "見習魔法仗": {"atk_bonus": 12, "price": 400, "desc": "白樺木製成的見習法杖，頂端鑲嵌著一顆微弱的低階魔能碎晶。"},
    "精鋼圓盾劍": {"atk_bonus": 18, "price": 1000, "desc": "騎士團制式的攻防一體武裝，劍身厚重且附帶一面小型護手圓盾。"},
}

def get_shop_card(p):
    """🎨 生成極具質感的黑曜石風格「視覺化商店按鈕圖卡」"""
    contents = [
        {"type": "text", "text": "🏪 冒險者公會・皇家常駐補給商店", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 您目前的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # 1. 渲染藥水消耗品區
    contents.append({"type": "text", "text": "🧪 【煉金藥水補給物資】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info["type"] == "potion":
            contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🔹 {name} (🪙 {info['price']} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"商店購買 {name}"}} # ✨【分流點】改為商店購買，避免與黑市指令打架
                ]
            })

    # 2. 渲染基礎武器裝備區
    contents.append({"type": "text", "text": "⚔️ 【鐵匠鋪現貨基礎兵器】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info["type"] == "weapon":
            contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🗡️ {name} (🪙 {info['price']} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"商店購買 {name}"}} # ✨【分流點】改為商店購買
                ]
            })

    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {
            "type": "box", "layout": "vertical", "contents": contents
        }
    }

def buy_weapon(p, item_name):
    """🛒 一般商店標準採購判定大腦：買完後會安全送入多部位裝備備用背包，拒絕直接覆蓋"""
    item_name = item_name.replace("商店購買", "").replace("購買", "").replace("下單", "").replace(" ", "").strip()
    
    if item_name not in SHOP_ITEMS:
        return f"❌ 交易失敗！一般常駐商店目前沒有販售【{item_name}】這件商品。"
        
    config = SHOP_ITEMS[item_name]
    
    # 1. 檢查勇者金幣是否足夠
    if p["gold"] < config["price"]:
        return f"❌ 🪙 餘額不足！購買【{item_name}】需要 {config['price']} 金幣，你口袋裡目前只有 {p['gold']} 金幣！"
        
    # 2. 扣除金幣
    p["gold"] -= config["price"]
    
    # 3. 根據商品類型進行分流核發
    if config["type"] == "potion":
        bag.add_to_inventory(p, item_name, is_material=False)
        db_core.save_player(p)
        return f"🛒 🧪 【交易成功】 🧪 🛒\n─────────────────\n你支付了 {config['price']} 金幣，成功購買了【{item_name}】x1！\n📦 物資已為您送入【我的背包】物資倉庫，輸入【使用 {item_name}】即可補血調息！\n\n🪙 剩餘資金：🪙 {p['gold']} 金幣"
        
    elif config["type"] == "weapon":
        # ✨ 【多部位合流機制】生成一件制式普通的白字實體裝備
        eq = equipment_core.generate_random_equipment(config["slot"], config["base"], forced_rarity="⭐普通")
        eq["name"] = f"⭐【普通】{item_name}" # 完美契合您原有的名稱文案
        
        # 安全灌入新版多部位備用包
        player_equipment._add_to_equipment_inventory(p, eq)
        db_core.save_player(p)
        return f"🛒 ⚔️ 【 兵器交易成功 】 🛒 ⚔️\n─────────────────\n你支付了 {config['price']} 金幣，成功購買了常駐現貨兵器 ── ⚔️【{item_name}】！\n\n📦 存放去向：新武裝已送入您的【 裝備背包 】中！\n💡 操作提示：請手動輸入【裝備包】或【裝備背包】，即可一鍵點擊穿戴上身！\n\n🪙 剩餘資金：🪙 {p['gold']} 金幣"
