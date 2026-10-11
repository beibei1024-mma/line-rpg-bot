import json
import db_core
import weapons
import bag

# 🏪 冒險商店：上架販售的商品數據庫（金幣計價）
# 您可以自由修改這裡的價格、名稱與庫存種類！
SHOP_ITEMS = {
    # 🧪 【消耗品區】：買完會進到玩家背包 items 裡面
    "初級生命藥水": {"type": "potion", "price": 30, "desc": "隨機恢復 30~50 點生命值。"},
    "高級生命藥水": {"type": "potion", "price": 100, "desc": "隨機恢復 80~120 點生命值。"},
    
    # ⚔️ 【基礎武器區】：買完直接替換玩家身上的 weapon 裝備欄位並增加攻擊力
    "新手鐵短劍": {"type": "weapon", "price": 150, "desc": "物傷 +15。适合剛出村的新手勇者。"},
    "微光木藤弓": {"type": "weapon", "price": 800, "desc": "物傷 +45。森林老獵人常用的木弓。"},
    "凜冬不融碎冰刺": {"type": "weapon", "price": 2500, "desc": "物傷 +95。散發著淡淡寒氣的冰刺。"},
    "黑曜熔岩大劍": {"type": "weapon", "price": 6000, "desc": "物傷 +160。黑曜石打造，揮砍帶有熱浪。"}
}

def get_shop_card(p):
    """🎨 生成極具質感的黑曜石風格「視覺化商店按鈕圖卡」"""
    contents = [
        {"type": "text", "text": "🏪 冒險者公會・皇家補給商店", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
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
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"購買 {name}"}}
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
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"購買 {name}"}}
                ]
            })

    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "contents": contents}
    }

def buy_weapon(p, item_name):
    """🛒 執行商店交易購買大腦，自動判定錢扣款，核發道具至背包或換裝"""
    item_name = item_name.replace("購買", "").replace("下單", "").replace(" ", "").strip()
    
    if item_name not in SHOP_ITEMS:
        return f"❌ 交易失敗！冒險商店目前沒有販售【{item_name}】這件商品。"
        
    config = SHOP_ITEMS[item_name]
    
    # 1. 檢查勇者金幣是否足夠
    if p["gold"] < config["price"]:
        return f"❌ 🪙 餘額不足！購買【{item_name}】需要 {config['price']} 金幣，你口袋裡目前只有 {p['gold']} 金幣！"
        
    # 2. 扣除金幣
    p["gold"] -= config["price"]
    
    # 3. 根據商品類型進行分流核發
    if config["type"] == "potion":
        # 🧪 如果買的是藥水：呼叫 bag.py 塞進玩家的消耗品背包
        bag.add_to_inventory(p, item_name, is_material=False)
        db_core.save_player(p)
        return f"🛒 🧪 【交易成功】 🧪 🛒\n─────────────────\n你支付了 {config['price']} 金幣，成功購買了【{item_name}】x1！\n📦 物資已為您送入【我的背包】倉庫，輸入【使用 {item_name}】即可喝藥補血！\n\n🪙 剩餘資金：🪙 {p['gold']} 金幣"
        
    elif config["type"] == "weapon":
        # ⚔️ 如果買的是武器：直接覆蓋替換裝備欄位 `weapon`
        if p.get("weapon") == item_name:
            return f"❌ 你目前已經裝備著【{item_name}】了，不需要重複購買一樣的兵器。"
            
        p["weapon"] = item_name
        db_core.save_player(p)
        return f"🛒 ⚔️ 【神兵武裝成功】 ⚔️ 🛒\n─────────────────\n你支付了 {config['price']} 金幣，成功購買了【{item_name}】！\n🔥 鐵匠當場為你換裝！你已成功裝備全新武器 ── ⚔️【{item_name}】！\n\n💡 戰力加成：往後的每一刀普通攻擊與技能，都將獲得該武器的實體物傷加成！輸入【我的狀態】縱覽戰力！"
