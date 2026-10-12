# dynamic_market.py (續篇) - 黑市 Flex 面板與採購核心大腦

import random
import db_core
import equipment_core
import bag

def get_market_flex(p):
    """🏪 生成極致奢華的動態黑市限量限量貨架 Flex 卡片"""
    goods = refresh_shop_stock(p)
    contents = [
        {"type": "text", "text": "🏪 皇家暗黑動態時空黑市", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 勇者流動金幣：🪙 {p['gold']} | ⏳ 每小時全自動更換貨架", "size": "xs", "color": "#FFCC00", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    for item in goods:
        stock_text = f"庫存: {item['stock']}" if item['stock'] > 0 else "🛑 售罄"
        btn_color = "#444444" if item['stock'] <= 0 else ("#FF9500" if item["type"]=="mystery_box" else "#1478FF")
        
        contents.append({
            "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
            "contents": [
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"📦 [{item['index']}] {item['name']}", "size": "xs", "color": "#E0E0E0", "weight": "bold", "flex": 4},
                    {"type": "text", "text": item["discount_label"], "size": "xs", "color": "#FF3B30", "align": "end", "flex": 2}
                ]},
                {"type": "box", "layout": "horizontal", "margin": "xs", "contents": [
                    {"type": "text", "text": f"🪙 金幣價格：{item['price']}", "size": "xxs", "color": "#FFCC00", "flex": 1},
                    {"type": "text", "text": stock_text, "size": "xxs", "color": "#4CD964" if item['stock']>0 else "#FF3B30", "align": "end", "flex": 1}
                ]},
                {"type": "button", "style": "primary", "color": btn_color, "height": "sm", "marginTop": "xs",
                 "action": {"type": "message", "label": "🛒 立即掏錢採購" if item['stock']>0 else "❌ 已售罄", "text": f"黑市購買 {item['index']}"}}
            ]
        })
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def execute_market_buy(p, idx_str):
    """🛒 黑市精準採購大腦 (包含盲盒博弈隨機洗鍊公式)"""
    try: idx = int(idx_str.replace("黑市購買", "").strip())
    except: return "❌ 黑市指令解析失敗！範例：【黑市購買 1】"
    
    goods = p.get("shop_goods", [])
    target_item = next((g for g in goods if g["index"] == idx), None)
    if not target_item: return "❌ 商品編號不存在或貨架已更新！"
    if target_item["stock"] <= 0: return "❌ 採購失敗！該限量商品已被其他勇者洗劫一空，售罄了！"
    if p["gold"] < target_item["price"]: return f"❌ 購買失敗！🪙 資金不足！需要 {target_item['price']} 金幣！"
    
    p["gold"] -= target_item["price"]
    target_item["stock"] -= 1
    log = f"🛒 交易成功！花費 🪙 {target_item['price']} 金幣購買了 ── "
    
    # 藥水管線
    if target_item["type"] == "potion":
        bag.add_to_inventory(p, target_item["name"], is_material=False)
        log += f"🧪【{target_item['name']}】！已送入您的背包物資區。"
    
    # 盲盒博弈管線
    elif target_item["type"] == "mystery_box":
        slots = ["武器", "頭盔", "鎧甲", "護手", "鞋子", "飾品"]
        r_slot = random.choice(slots)
        r_base = random.choice(list(equipment_core.BASE_TEMPLATES[r_slot].keys()))
        # 盲盒高機率開出魔法/稀有，極低機率(3%)開出遠古神話！
        r_rare = random.choices(["⭐普通", "🔷魔法", "🌟稀有", "🔥史詩", "👑遠古神話"], weights=[15, 50, 25, 7, 3], k=1)[0]
        eq = equipment_core.generate_random_equipment(r_slot, r_base, r_rare)
        _add_to_equipment_inventory(p, eq)
        log += f"🎁【命運神祕盲盒】！\n\n🔥 開箱異象爆發：獲得 {eq['name']} ({r_slot})！已直接安全移送至裝備收藏背包！"
        
    # 一般隨機裝備管線
    elif target_item["type"] == "equipment":
        eq = target_item["data"]
        _add_to_equipment_inventory(p, eq)
        log += f"🛡️【{eq['name']}】！已安全移送至裝備收藏背包，快去開包穿戴吧！"
        
    db_core.save_player(p)
    return log

def _add_to_equipment_inventory(p, eq_data):
    """將隨機裝備封包(JSON)寫入備用武裝包中"""
    eq_inv_str = p.get("equipment_inventory", "[]")
    if not eq_inv_str or eq_inv_str == "None": eq_inv_str = "[]"
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    inv.append(eq_data)
    p["equipment_inventory"] = json.dumps(inv, ensure_ascii=False)
