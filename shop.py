# shop.py - 皇家常駐補給物資商店 v5.5 (KeyError終極修復版)

import json
import db_core
import bag
import equipment_core
import player_equipment
import weapons  # 直連神兵利器基礎數據庫

# 🏪 冒險商店：常駐上架販售的商品數據庫（完全保留並補齊所有數據標籤）
SHOP_ITEMS = {
    # 🧪 【消耗品區】（強制補齊 type: "potion" 標籤，徹底根除 KeyError 地雷）
    "初級生命藥水": {"type": "potion", "price": 30, "desc": "隨機恢復 30~50 點生命值。"},
    "高級生命藥水": {"type": "potion", "price": 100, "desc": "隨機恢復 80~120 點生命值。"},
    
    # ⚔️ 【基礎武器區】
    "新手鐵短劍": {"type": "weapon", "slot": "武器", "base": "鐵劍", "price": 150, "desc": "物傷 +15。适合剛出村的新手勇者。"},
    "微光木藤弓": {"type": "weapon", "slot": "武器", "base": "長弓", "price": 800, "desc": "物傷 +45。森林老獵人常用的木弓。"},
    "凜冬不融碎冰刺": {"type": "weapon", "slot": "武器", "base": "法杖", "price": 2500, "desc": "物傷 +95。散發著淡淡寒氣的冰刺。"},
    "黑曜熔岩大劍": {"type": "weapon", "slot": "武器", "base": "鐵劍", "price": 6000, "desc": "物傷 +160。黑曜石打造，揮砍帶有熱浪。"}
}

def get_shop_card(p):
    """🎨 生成極具質感的黑曜石風格「數據同步公會常駐商店」"""
    contents = [
        {"type": "text", "text": "🏪 冒險者公會 · 皇家常駐補給商店", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 您目前的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # 1. 渲染藥水消耗品區
    contents.append({"type": "text", "text": "🧪 【煉金藥水補給物資】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        # ✨【💥 安全防護一】改用安全字典 .get() 語法，就算漏寫標籤也絕對不崩潰已讀不回！
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

    # 2. 渲染基礎武器裝備區 (自動動態與 weapons.py 完成售價同步)
    contents.append({"type": "text", "text": "⚔️ 【鐵匠鋪現貨基礎兵器】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
    for name, info in SHOP_ITEMS.items():
        if info.get("type") == "weapon":
            # 智慧同步：如果 weapons.py 有這把武器，自動同步採用您設定的價格與白字！
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
    """🛒 商店大腦：扣除對齊後的實體金幣，新武器安全送入多部位裝備備用包"""
    item_name = item_name.replace("商店購買", "").replace("購買", "").replace("下單", "").replace(" ", "").strip()
    
    if item_name not in SHOP_ITEMS:
        return f"❌ 交易失敗！常駐商店目前沒有現貨展示【{item_name}】這件商品。"
        
    config = SHOP_ITEMS[item_name]
    
    # 動態拉取對齊後的實體價格
    final_price = weapons.SHOP_WEAPONS[item_name]["price"] if item_name in weapons.SHOP_WEAPONS else config["price"]
    
    if p["gold"] < final_price:
        return f"❌ 🪙 餘額不足！購買【{item_name}】需要 {final_price} 金幣，你口袋目前只有 {p['gold']} 金幣！"
        
    p["gold"] -= final_price
    
    if config.get("type") == "potion":
        bag.add_to_inventory(p, item_name, is_material=False)
        db_core.save_player(p)
        return f"🛒 🧪 【交易成功】 🧪 🛒\n─────────────────\n你支付了 {final_price} 金幣，成功購買了【{item_name}】x1！\n📦 物資已為您送入【我的背包】物資倉庫，輸入【使用 {item_name}】即可補血調息！"
        
    elif config.get("type") == "weapon":
        w_atk = weapons.SHOP_WEAPONS[item_name]["atk_bonus"] if item_name in weapons.SHOP_WEAPONS else 15
        
        # 生成與 weapons.py 數值完全對齊的普通實體裝備
        eq = equipment_core.generate_random_equipment(config.get("slot", "武器"), config.get("base", "鐵劍"), forced_rarity="⭐普通")
        eq["name"] = f"⭐【普通】{item_name}"
        eq["atk"] = w_atk
        eq["price"] = final_price
        
        # 安全存入多部位背包，防止覆蓋吃裝
        player_equipment._add_to_equipment_inventory(p, eq)
        db_core.save_player(p)
        return f"🛒 ⚔️ 【 兵器交易成功 】 🛒 265 \n─────────────────\n你支付了 {final_price} 金幣，成功購買了現貨兵器 ── ⚔️【{item_name}】！\n📦 存放去向：新武裝已送入您的【 裝備背包 】中，請輸入【裝備包】手動穿戴上身！"
