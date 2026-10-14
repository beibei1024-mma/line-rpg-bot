# dynamic_market.py - 皇家時空動態黑市交易中心 v4.0 (獨立裝備背包完全連通版)

import random
import time
import json
import db_core
import equipment_core
import equipment_system
import bag

def refresh_shop_stock(p):
    """⏳ 時空齒輪流轉：每小時全自動刷新動態限量貨架"""
    current_time_seed = int(time.time() // 3600)

    if p.get("shop_seed") == current_time_seed and p.get("shop_goods"):
        if isinstance(p["shop_goods"], str):
            try:
                return json.loads(p["shop_goods"])
            except Exception:
                pass
        else:
            return p["shop_goods"]

    new_goods = []

    # 欄位 1~2：保底藥水補給物資
    for i, p_name in enumerate(list(bag.CONSUMABLES.keys())[:2]):
        discount = random.choice([0.7, 0.85, 1.0, 1.0])
        orig_price = bag.CONSUMABLES[p_name]["price"]
        new_goods.append({
            "index": i + 1, "type": "potion", "name": p_name,
            "price": int(orig_price * discount),
            "discount_label": f"🔥 {int(discount*10)}折" if discount < 1.0 else "制式價",
            "stock": random.randint(3, 8), "data": {}
        })

    # 欄位 3~5：黑市隨機品質神兵防具展售
    slots = ["武器", "頭盔", "鎧甲", "護手", "鞋子", "飾品"]
    for i in range(3):
        r_slot = random.choice(slots)
        r_base = random.choice(list(equipment_core.BASE_TEMPLATES[r_slot].keys()))
        eq_data = equipment_core.generate_random_equipment(r_slot, r_base)
        new_goods.append({
            "index": i + 3, "type": "equipment", "name": eq_data["name"],
            "price": eq_data["price"], "discount_label": f"✨ {eq_data['rarity']}",
            "stock": 1, "data": eq_data
        })

    # 欄位 6：命運神祕盲盒
    new_goods.append({
        "index": 6, "type": "mystery_box", "name": "🎁 命運至高神祕盲盒",
        "price": int(p.get("level", 1) * 300), "discount_label": "🎲 碰運氣",
        "stock": 1, "data": {}
    })

    p["shop_seed"] = current_time_seed
    p["shop_goods"] = new_goods
    db_core.save_player(p)
    return new_goods

def get_market_flex(p):
    """🏪 生成動態黑市限量貨架 Flex 卡片"""
    goods = refresh_shop_stock(p)
    contents = [
        {"type": "text", "text": "🏪 皇家暗黑動態時空黑市", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 金幣：{p['gold']} | ⏳ 每小時全自動更新", "size": "xs", "color": "#FFCC00", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]

    for item in goods:
        stock_text = f"庫存: {item['stock']}" if item['stock'] > 0 else "🛑 售罄"
        btn_color = "#444444" if item['stock'] <= 0 else ("#FF9500" if item["type"] == "mystery_box" else "#1478FF")
        contents.append({
            "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
            "contents": [
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"📦 [{item['index']}] {item['name']}", "size": "xs", "color": "#E0E0E0", "weight": "bold", "flex": 4},
                    {"type": "text", "text": item["discount_label"], "size": "xs", "color": "#FF3B30", "align": "end", "flex": 2}
                ]},
                {"type": "box", "layout": "horizontal", "margin": "xs", "contents": [
                    {"type": "text", "text": f"🪙 價格：{item['price']}", "size": "xxs", "color": "#FFCC00", "flex": 1},
                    {"type": "text", "text": stock_text, "size": "xxs", "color": "#4CD964" if item['stock'] > 0 else "#FF3B30", "align": "end", "flex": 1}
                ]},
                {"type": "button", "style": "primary", "color": btn_color, "height": "sm", "marginTop": "xs",
                 "action": {"type": "message", "label": "🛒 立即採購" if item['stock'] > 0 else "❌ 已售罄", "text": f"黑市購買 {item['index']}"}}
            ]
        })

    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def execute_market_buy(p, idx_str):
    """🛒 黑市精準採購大腦"""
    try:
        idx = int(idx_str.replace("黑市購買", "").strip())
    except Exception:
        return "❌ 黑市指令解析失敗！範例：【黑市購買 1】"

    goods = refresh_shop_stock(p)
    target_item = next((g for g in goods if g["index"] == idx), None)
    if not target_item:
        return "❌ 商品編號不存在或貨架已更新！"
    if target_item["stock"] <= 0:
        return "❌ 該限量商品已被採購一空！"
    if p["gold"] < target_item["price"]:
        return f"❌ 金幣不足！需要 {target_item['price']} 金幣！"

    p["gold"] -= target_item["price"]
    target_item["stock"] -= 1
    p["shop_goods"] = goods

    log = f"🛒 交易成功！花費 🪙 {target_item['price']} 金幣購買了 "
    if target_item["type"] == "potion":
        bag.add_to_inventory(p, target_item["name"], is_material=False)
        log += f"🧪【{target_item['name']}】！"
    elif target_item["type"] in ["equipment", "mystery_box"]:
        slots = ["武器", "頭盔", "鎧甲", "護手", "鞋子", "飾品"]
        r_slot = random.choice(slots)
        r_base = random.choice(list(equipment_core.BASE_TEMPLATES[r_slot].keys()))
        eq = target_item["data"] if target_item["type"] == "equipment" else equipment_core.generate_random_equipment(r_slot, r_base)
        slot_map = {"鎧甲": "上衣", "護手": "手環", "飾品": "戒指1"}
        mapped_slot = slot_map.get(eq.get("slot", "武器"), eq.get("slot", "武器"))
        equipment_system.add_to_weapon_inventory_individual(p, eq["name"], slot_name=mapped_slot)
        log += f"🛡️【{eq['name']}】！已送入裝備背包。"

    db_core.save_player(p)
    return log
