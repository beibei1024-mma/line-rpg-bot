import json
import random
import db_core

CONSUMABLES = {
    "初級生命藥水": {"heal_range": (30, 50), "price": 30, "desc": "飲用後可隨記恢復 30~50 點血量。"},
    "高級生命藥水": {"heal_range": (80, 120), "price": 100, "desc": "飲用後可隨機恢復 80~120 點特大血量！"}
}

def get_bag_card(p):
    """【企劃 C 視覺大翻新】告別純文字，使用 Flex 打造極簡倉庫網格卡片"""
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
        
    inv = p["inventory"]
    if isinstance(inv, str):
        inv = json.loads(inv)
        
    items = inv.get("items", {})
    materials = inv.get("materials", {})
    
    contents = [
        {"type": "text", "text": "🎒 勇者私人物品倉庫", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"⚔️ 裝備中武器：【{p.get('weapon', '赤手空拳')}】", "size": "xs", "color": "#007AFF", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "md", "color": "#333333"}
    ]
    
    # 渲染消耗品
    contents.append({"type": "text", "text": "🧪 【藥水與補給區】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
    if not items:
        contents.append({"type": "text", "text": "   (倉庫目前空空如也)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in items.items():
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                    {"type": "text", "text": f"🔹 {name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                    {"type": "text", "text": f"x{count}", "size": "xs", "color": "#4CD964", "align": "end", "flex": 1}
                ]
            })
            
    # 渲染素材
    contents.append({"type": "text", "text": "💎 【怪物珍稀素材區】", "weight": "bold", "size": "sm", "color": "#AF52DE", "margin": "md"})
    if not materials:
        contents.append({"type": "text", "text": "   (尚未搜刮到任何原料)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in materials.items():
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                    {"type": "text", "text": f"🔸 {name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                    {"type": "text", "text": f"x{count}", "size": "xs", "color": "#FFCC00", "align": "end", "flex": 1}
                ]
            })
            
    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}, "footer": {"backgroundColor": "#2A2A2A"}},
        "body": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": contents},
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{"type": "text", "text": "✍️ 補血口令：輸入【使用 物品名稱】\n（例如：使用 初級生命藥水）", "size": "xs", "color": "#8E8E93", "align": "center", "wrap": True}]
        }
    }

def add_to_inventory(p, item_name, is_material=False):
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
    inv = p["inventory"]
    category = "materials" if is_material else "items"
    if category not in inv: inv[category] = {}
    inv[category][item_name] = inv[category].get(item_name, 0) + 1
    p["inventory"] = inv

def use_potion(p, potion_name):
    if "inventory" not in p or not p["inventory"]: return "❌ 背包空無一物！"
    inv = p["inventory"]
    items = inv.get("items", {})
    if potion_name not in items or items[potion_name] <= 0: return f"❌ 沒有【{potion_name}】。"
    if p["hp"] <= 0: return "💀 你已經陣亡了！請先【復活】。"
    if p["hp"] >= p["max_hp"]: return "💚 生命值已滿，不需浪費藥水！"
    if potion_name not in CONSUMABLES: return "❌ 非可食用的藥水。"
    
    config = CONSUMABLES[potion_name]
    heal_amount = random.randint(config["heal_range"][0], config["heal_range"][1])
    old_hp = p["hp"]
    p["hp"] = min(p["max_hp"], p["hp"] + heal_amount)
    items[potion_name] -= 1
    if items[potion_name] == 0: del items[potion_name]
    inv["items"] = items
    p["inventory"] = inv
    db_core.save_player(p)
    return f"🧪 ✨ 你喝下了【{potion_name}】！\n💖 隨機恢復了 {p['hp'] - old_hp} 點生命！\n🩸 血量狀態：{p['hp']} / {p['max_hp']}"
