# shop.py - 皇家常駐補給物資商店 v6.0 (名字完全對齊版)

import json
import db_core
import bag
import equipment_core
import player_equipment
import weapons  # 直連神兵利器基礎數據庫

# 🏪 冒險商店：常駐上架販售的商品數據庫（名字完全對齊 weapons.py 經典白字）
SHOP_ITEMS = {
    # 🧪 【消耗品區】
    "初級生命藥水": {"type": "potion", "price": 30, "desc": "隨機恢復 30~50 點生命值。"},
    "高級生命藥水": {"type": "potion", "price": 100, "desc": "隨機恢復 80~120 點生命值。"},
    
    # ⚔️ 【基礎武器區】（✨錯字全面校正：仗 ➡️ 杖！完美匹配 weapons.py）
    "生鏽的鐵劍": {"type": "weapon", "slot": "武器", "base": "鐵劍", "price": 50, "desc": "一把在倉庫角落翻出來的古舊鐵劍。"},
    "新手短弓": {"type": "weapon", "slot": "武器", "base": "長弓", "price": 150, "desc": "獵人學徒常用的基礎短弓。"},
    "見習魔法杖": {"type": "weapon", "slot": "武器", "base": "法杖", "price": 400, "desc": "白樺木製成的見習法杖。"},
    "精鋼圓盾劍": {"type": "weapon", "slot": "武器", "base": "鐵劍", "price": 1000, "desc": "騎士團制式的攻防一體武裝。"}
}

def get_shop_card(p):
    """🎨 生成公會常駐商店 Flex 按鈕圖卡面版"""
    contents = [
        {"type": "text", "text": "🏪 冒險者公會 · 皇家常駐補給商店", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 您目前的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # 1. 渲染藥水消耗品區
    contents.append({"type": "text", "text": "🧪 【煉金藥水補給物資】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info.get("type") == "potion":
            contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🔹 {name} (🪙 {info['price']} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"商店購買 {name}"}}
                ]
            })

    # 2. 渲染基礎武器裝備區 (完美同步武器庫最新數據)
    contents.append({"type": "text", "text": "⚔️ 【鐵匠鋪現貨基礎兵器】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info.get("type") == "weapon":
            w_price = weapons.SHOP_WEAPONS[name]["price"] if name in weapons.SHOP_WEAPONS else info["price"]
            w_atk = weapons.SHOP_WEAPONS[name]["atk_bonus"] if name in weapons.SHOP_WEAPONS else 15
            
            contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🗡️ {name} (🪙 {w_price} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ 物傷 +{w_atk}。{info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"商店購買 {name}"}}
                ]
            })

    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def buy_weapon(p, item_name):
    """🛒 商店大腦：扣除對齊後的實體金幣，新裝備安全送入多部位備用包"""
    item_name = item_name.replace("商店購買", "").replace("購買", "").replace("下單", "").replace(" ", "").strip()
    
    if item_name not in SHOP_ITEMS:
        return f"❌ 交易失敗！常駐商店目前沒有現貨展示【{item_name}】這件商品。"
        
    config = SHOP_ITEMS[item_name]
    final_price = weapons.SHOP_WEAPONS[item_name]["price"] if item_name in weapons.SHOP_WEAPONS else config["price"]
    
    if p["gold"] < final_price:
        return f"❌ 🪙 餘額不足！購買【{item_name}】需要 {final_price} 金幣，你口袋目前只有 {p['gold']} 金幣！"
        
    p["gold"] -= final_price
    
    if config.get("type") == "potion":
        bag.add_to_inventory(p, item_name, is_material=False)
        db_core.save_player(p)
        return f"🛒 🧪 【交易成功】\n你支付了 {final_price} 金幣，成功購買了【{item_name}】x1！"
        
    elif config.get("type") == "weapon":
        w_atk = weapons.SHOP_WEAPONS[item_name]["atk_bonus"] if item_name in weapons.SHOP_WEAPONS else 15
        
        eq = equipment_core.generate_random_equipment(config.get("slot", "武器"), config.get("base", "鐵劍"), forced_rarity="⭐普通")
        eq["name"] = f"⭐【普通】{item_name}"
        eq["atk"] = w_atk
        eq["price"] = final_price
        
        player_equipment._add_to_equipment_inventory(p, eq)
        db_core.save_player(p)
        return f"🛒 ⚔️ 【 兵器交易成功 】\n你支付了 {final_price} 金幣，成功購買了現貨兵器 ── ⚔️【{item_name}】！\n📦 存放去向：新武裝已送入您的【 裝備背包 】中！"
