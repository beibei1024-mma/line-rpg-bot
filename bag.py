# bag.py - 勇者私人物資倉庫與裝備一鍵販賣回收核心

import json
import random
import db_core
import weapons
import equipment_core
import equipment_system
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

CONSUMABLES = {
    "初級生命藥水": {"heal_range": (30, 50), "price": 30, "desc": "飲用後可隨機恢復 30~50 點血量。"},
    "高級生命藥水": {"heal_range": (80, 120), "price": 100, "desc": "飲用後可隨機恢復 80~120 點特大血量！"}
}

def get_bag_card(p):
    """🎒 生成網格化勇者私人物資倉庫卡片 (支援一鍵販賣普通裝備)"""
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
    inv = p["inventory"]
    if isinstance(inv, str):
        try:
            inv = json.loads(inv)
        except Exception:
            inv = {"items": {}, "materials": {}}

    items = inv.get("items", {})
    materials = inv.get("materials", {})

    w_inv_str = p.get("weapon_inventory", "[]")
    if w_inv_str in (None, "None", "", "{}"):
        w_inv_str = "[]"
    try:
        w_list = json.loads(w_inv_str) if isinstance(w_inv_str, str) else list(w_inv_str)
    except Exception:
        w_list = []

    contents = [
        {"type": "text", "text": "🎒 勇者皇家私人物資倉庫", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": "👤 目前手持武裝：【" + p.get('weapon', '赤手空拳') + "】", "size": "xs", "color": "#4CD964", "align": "center", "margin": "xs", "wrap": True},
        {"type": "separator", "margin": "md", "color": "#333333"}
    ]

    # 1. ⚔️ 【 裝備與兵器收藏庫 】
    contents.append({"type": "text", "text": "⚔️ 【 裝備與兵器收藏庫 】(" + str(len(w_list)) + "件)", "weight": "bold", "size": "sm", "color": "#007AFF", "margin": "md"})
    if not w_list:
        contents.append({"type": "text", "text": "   (您的裝備背包空空如也，快去商店或野外打寶！)", "size": "xs", "color": "#8E8E93"})
    else:
        for item in w_list:
            eq_name = item.get("name", "未知裝備")
            detected_slot = item.get("slot") or equipment_system.get_equipment_slot_by_name(eq_name) or "防具"
            parsed = equipment_core.parse_equipment_stats(eq_name)
            stat_str = "[" + detected_slot + "] " + parsed['summary']

            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "sm", "alignItems": "center", "spacing": "sm",
                "contents": [
                    {
                        "type": "box", "layout": "vertical", "flex": 5,
                        "contents": [
                            {"type": "text", "text": "🔸 " + eq_name, "size": "xs", "color": "#FFFFFF", "weight": "bold", "wrap": True},
                            {"type": "text", "text": stat_str, "size": "xxs", "color": "#FF9500", "marginTop": "xs", "wrap": True}
                        ]
                    },
                    {
                        "type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "flex": 2,
                        "action": {"type": "message", "label": "穿戴", "text": "裝備 " + eq_name}
                    }
                ]
            })

    # 2. 🧪 【 藥水與補給物資 】
    contents.append({"type": "text", "text": "🧪 【 藥水與補給物資 】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "lg"})
    if not items:
        contents.append({"type": "text", "text": "   (消耗品倉庫目前空空如也)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in items.items():
            if count > 0:
                contents.append({
                    "type": "box", "layout": "horizontal", "margin": "xs", "alignItems": "center",
                    "contents": [
                        {"type": "text", "text": "🔹 " + name + " (x" + str(count) + ")", "size": "xs", "color": "#E0E0E0", "flex": 5},
                        {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "flex": 2,
                         "action": {"type": "message", "label": "飲用", "text": "使用 " + name}}
                    ]
                })

    # 3. 💎 【 怪物珍稀原料區 】
    contents.append({"type": "text", "text": "💎 【 怪物珍稀原料區 】", "weight": "bold", "size": "sm", "color": "#AF52DE", "margin": "md"})
    if not materials:
        contents.append({"type": "text", "text": "   (尚未搜刮到任何魔物原料)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in materials.items():
            if count > 0:
                contents.append({
                    "type": "box", "layout": "horizontal", "margin": "xs",
                    "contents": [
                        {"type": "text", "text": "🔸 " + name, "size": "xs", "color": "#E0E0E0", "flex": 4},
                        {"type": "text", "text": "x" + str(count), "size": "xs", "color": "#FFCC00", "align": "end", "flex": 1}
                    ]
                })

    flex_bubble = {
        "type": "bubble",
        "size": "mega",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": contents}
    }

    quick_items = [
        QuickReplyItem(action=MessageAction(label="👤 狀態", text="我的狀態")),
        QuickReplyItem(action=MessageAction(label="🛡️ 裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="💰 賣普通裝", text="出售普通裝備")),
        QuickReplyItem(action=MessageAction(label="🏪 商店", text="冒險商店")),
        QuickReplyItem(action=MessageAction(label="🦅 回城", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items).to_dict()}

def sell_common_equipment(p):
    """💰 一鍵回收背包中【⭐普通】與新手裝備換取金幣"""
    w_inv_str = p.get("weapon_inventory", "[]")
    if w_inv_str in (None, "None", "", "{}"):
        w_inv_str = "[]"
    try:
        w_list = json.loads(w_inv_str) if isinstance(w_inv_str, str) else list(w_inv_str)
    except Exception:
        w_list = []

    kept = []
    sold_count = 0
    total_gold = 0
    for item in w_list:
        eq_name = item.get("name", "")
        if "⭐普通" in eq_name or eq_name.startswith("冒險者"):
            st = equipment_core.parse_equipment_stats(eq_name)
            total_gold += st.get("price", 30)
            sold_count += 1
        else:
            kept.append(item)

    if sold_count == 0:
        return "💡 您的背包中目前沒有【⭐普通】或【冒險者新手裝】可供一鍵回收！"

    p["gold"] = p.get("gold", 0) + total_gold
    p["weapon_inventory"] = json.dumps(kept, ensure_ascii=False)
    db_core.save_player(p)
    return "💰 ✨ 【 裝備回收大成功 】 ✨ 💰\n─────────────────\n已將背包中 " + str(sold_count) + " 件普通/新手淘汰裝備賣給鐵匠！\n🪙 獲得回收金幣：+" + str(total_gold) + " 金幣！"

def equip_weapon_from_bag(p, user_cmd):
    return equipment_system.execute_equip_item(p, user_cmd)

def add_to_inventory(p, item_name, is_material=False):
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
    inv = p["inventory"]
    if isinstance(inv, str):
        try:
            inv = json.loads(inv)
        except Exception:
            inv = {"items": {}, "materials": {}}
    category = "materials" if is_material else "items"
    if category not in inv:
        inv[category] = {}
    inv[category][item_name] = inv[category].get(item_name, 0) + 1
    p["inventory"] = inv

def use_potion(p, potion_name):
    if "inventory" not in p or not p["inventory"]:
        return "❌ 背包空無一物！"
    inv = p["inventory"]
    if isinstance(inv, str):
        try:
            inv = json.loads(inv)
        except Exception:
            inv = {"items": {}, "materials": {}}
    items = inv.get("items", {})
    if potion_name not in items or items[potion_name] <= 0:
        return "❌ 沒有【" + potion_name + "】。"

    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    eq_bonus = equipment_core.get_player_total_equipment_bonus(p)
    vit_val = int((p.get("vitality", 10) + eq_bonus["vitality"]) * job_mod["vit_mod"])
    max_hp = 100 + (vit_val * 5) + (level * 15)

    if p["hp"] <= 0:
        return "💀 你已經陣亡了！請先【復活】。"
    if p["hp"] >= max_hp:
        return "💚 生命值已滿，不需浪費藥水！"
    if potion_name not in CONSUMABLES:
        return "❌ 非可食用的藥水。"

    config = CONSUMABLES[potion_name]
    heal_amount = random.randint(int(config["heal_range"][0]), int(config["heal_range"][1]))
    old_hp = p["hp"]
    p["hp"] = min(max_hp, p["hp"] + heal_amount)
    items[potion_name] -= 1
    if items[potion_name] <= 0:
        del items[potion_name]
    inv["items"] = items
    p["inventory"] = inv
    db_core.save_player(p)

    return "🧪 ✨ 你喝下了【" + potion_name + "】！\n💖 順利恢復了 " + str(p['hp'] - old_hp) + " 點生命！\n🩸 血量狀態：" + str(p['hp']) + " / " + str(max_hp)
# === END OF FILE ===
