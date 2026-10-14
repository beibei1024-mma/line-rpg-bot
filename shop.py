import json
import db_core
import weapons
import bag
import forge_system

SHOP_ITEMS = {
    # 🧪 【消耗品區】
    "初級生命藥水": {"type": "potion", "price": 30, "desc": "隨機恢復 30~50 點生命值。"},
    "高級生命藥水": {"type": "potion", "price": 100, "desc": "隨機恢復 80~120 點生命值。"},
    # ⚔️ 【基礎武器區】
    "新手鐵短劍": {"type": "weapon", "price": 150, "desc": "物傷 +15。適合剛出村的新手勇者。"},
    "微光木藤弓": {"type": "weapon", "price": 800, "desc": "物傷 +45。森林老獵人常用的木弓。"},
    "見習魔法杖": {"type": "weapon", "price": 2500, "desc": "物傷 +95。鑲嵌極地不融冰塊的導魔法杖。"},
    "凜冬不融碎冰刺": {"type": "weapon", "price": 2500, "desc": "物傷 +95。散發著淡淡寒氣的冰刺。"},
    "黑曜熔岩大劍": {"type": "weapon", "price": 6000, "desc": "物傷 +160。黑曜石打造，揮砍帶有熱浪。"}
}

def get_shop_card(p):
    """🎨 生成黑曜石風格「視覺化商店按鈕圖卡」"""
    contents = [
        {"type": "text", "text": "🏪 冒險者公會・皇家補給商店", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 您目前的流動資金：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]

    potion_contents = []
    weapon_contents = []

    for name, info in SHOP_ITEMS.items():
        item_type = info["type"]
        price = info["price"]
        desc = info["desc"]

        if item_type == "potion":
            potion_contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🔹 {name} (🪙 {price} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {desc}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"購買 {name}"}}
                ]
            })
        elif item_type == "weapon":
            weapon_contents.append({
                "type": "box", "layout": "vertical", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"🗡️ {name} (🪙 {price} 金幣)", "size": "xs", "color": "#E0E0E0", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ {desc}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"🛒 購買 {name}", "text": f"購買 {name}"}}
                ]
            })

    contents.append({"type": "text", "text": "🧪 【煉金藥水補給物資】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "md"})
    contents.extend(potion_contents)
    contents.append({"type": "text", "text": "⚔️ 【鐵匠鋪現貨基礎兵器】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
    contents.extend(weapon_contents)

    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "contents": contents}
    }

def buy_weapon(p, item_name):
    """🛒 商店大腦：買到實體武器 100% 入庫武器備用背包收藏庫"""
    item_name = item_name.replace("購買", "").replace("下單", "").replace(" ", "").strip()

    if item_name not in SHOP_ITEMS:
        return f"❌ 交易失敗！冒險商店目前沒有販售【{item_name}】這件商品。"

    config = SHOP_ITEMS[item_name]
    price = config["price"]

    if p["gold"] < price:
        return f"❌ 🪙 餘額不足！購買【{item_name}】需要 {price} 金幣，你口袋裡目前只有 {p['gold']} 金幣！"

    p["gold"] -= price
    item_type = config["type"]

    if item_type == "potion":
        bag.add_to_inventory(p, item_name, is_material=False)
        db_core.save_player(p)
        return (
            f"🛒 🧪 【交易成功】 🧪 🛒\n"
            f"─────────────────\n"
            f"你支付了 {price} 金幣，成功購買了【{item_name}】x1！\n"
            f"📦 物資已為您送入【我的背包】倉庫，輸入【使用 {item_name}】即可喝藥補血！\n\n"
            f"🪙 剩餘資金：🪙 {p['gold']} 金幣"
        )
    elif item_type == "weapon":
        forge_system.add_to_weapon_inventory(p, item_name)
        db_core.save_player(p)
        return (
            f"🛒 ⚔️ 【 兵器交易成功 】 🛒 ⚔️\n"
            f"─────────────────\n"
            f"你支付了 {price} 金幣，成功購買了現貨基礎兵器 ── ⚔️【{item_name}】！\n\n"
            f"📦 存放去向：新兵器已妥善存入您的【 我的背包 -> 裝備與兵器收藏庫 】中！\n"
            f"💡 操作提示：開啟【我的背包】點擊穿戴，或輸入【裝備 {item_name}】進行更換！\n\n"
            f"🪙 剩餘資金：🪙 {p['gold']} 金幣"
        )
