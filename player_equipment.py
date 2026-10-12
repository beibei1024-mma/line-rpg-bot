# player_equipment.py - 六大部位多維度實體更換與面版系統 v3.9 (完全體修復版)

import json
import db_core

# 初始化六大部位實體插槽
EQUIP_SLOTS = ["武器", "頭盔", "鎧甲", "護手", "鞋子", "飾品"]

def _add_to_equipment_inventory(p, eq_data):
    """✨【核心修正點】全域獨立裝備入庫大腦，專供黑市、盲盒與工坊熔煉調用"""
    eq_inv_str = p.get("equipment_inventory", "[]")
    if not eq_inv_str or eq_inv_str == "None": eq_inv_str = "[]"
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    inv.append(eq_data)
    p["equipment_inventory"] = json.dumps(inv, ensure_ascii=False)

def get_equipped_panel(p):
    """🛡️ 生成極致硬核的六大部位實體裝備面板"""
    eq_slots_str = p.get("equipped_slots", "{}")
    if not eq_slots_str or eq_slots_str == "None": eq_slots_str = "{}"
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    contents = [
        {"type": "text", "text": "🛡️ 勇者多維度裝備欄面板", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    for slot in EQUIP_SLOTS:
        item = equipped.get(slot)
        if item:
            affix_text = " | ".join([f"{k[:3].upper()}+{v}" for k, v in item.get("affixes", {}).items()])
            desc_str = f"💥ATK+{item['atk']} 🛡️DEF+{item['def']}"
            if affix_text: desc_str += f"\n✨詞綴: {affix_text}"
            
            contents.append({
                "type": "box", "layout": "vertical", "margin": "sm", "backgroundColor": "#2C2C2E", "paddingAll": "xs", "cornerRadius": "sm",
                "contents": [
                    {"type": "text", "text": f"● 【{slot}】: {item['name']}", "size": "xs", "color": "#4CD964", "weight": "bold"},
                    {"type": "text", "text": desc_str, "size": "xxs", "color": "#FF9500", "wrap": True},
                    {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": f"❌ 卸下{slot}", "text": f"脫下裝備 {slot}"}}
                ]
            })
        else:
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "sm", "backgroundColor": "#1C1C1E", "paddingAll": "xs",
                "contents": [
                    {"type": "text", "text": f"○ 【{slot}】: 🍃 空無一物", "size": "xs", "color": "#8E8E93", "gravity": "center"}
                ]
            })
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def get_equipment_bag_flex(p):
    """🎒 生成裝備背包專屬的網格化 Flex 卡片"""
    eq_inv_str = p.get("equipment_inventory", "[]")
    if not eq_inv_str or eq_inv_str == "None": eq_inv_str = "[]"
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    
    contents = [
        {"type": "text", "text": "⚔️ 勇者皇家神兵防具備用包", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    if not inv:
        contents.append({"type": "text", "text": "   (您的裝備背包空空如也！)", "size": "xs", "color": "#8E8E93", "margin": "md"})
    else:
        for item in inv[:8]:
            aff_text = " | ".join([f"{k[:3].upper()}+{v}" for k, v in item.get("affixes", {}).items()])
            stat_str = f"Slot: {item['slot']} | 💥ATK+{item['atk']} 🛡️DEF+{item['def']}"
            if aff_text: stat_str += f"\n✨屬性: {aff_text}"
            
            contents.append({
                "type": "box", "layout": "vertical", "margin": "sm", "backgroundColor": "#2C2C2E", "paddingAll": "xs", "cornerRadius": "sm",
                "contents": [
                    {"type": "text", "text": f"🗡️ {item['name']}", "size": "xs", "color": "#FF9500", "weight": "bold"},
                    {"type": "text", "text": stat_str, "size": "xxs", "color": "#E0E0E0", "wrap": True},
                    {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": "⚡ 立即穿戴", "text": f"穿戴裝備 {item['id']}"}}
                ]
            })
            
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def wear_equipment_by_id(p, item_id):
    """⚡ 核心換裝大腦"""
    item_id = item_id.replace("穿戴裝備", "").strip()
    eq_inv_str = p.get("equipment_inventory", "[]")
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    
    eq_item = next((item for item in inv if item["id"] == item_id), None)
    if not eq_item: return "❌ 裝備包中找不到該裝備。"
    
    slot = eq_item["slot"]
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    old_item = equipped.get(slot)
    if old_item: inv.append(old_item)
        
    inv.remove(eq_item)
    equipped[slot] = eq_item
    
    if slot == "武器": p["weapon"] = eq_item["name"]
        
    p["equipment_inventory"] = json.dumps(inv, ensure_ascii=False)
    p["equipped_slots"] = json.dumps(equipped, ensure_ascii=False)
    db_core.save_player(p)
    return f"🛡️ 換裝成功！已將 ── ✨【{eq_item['name']}】穿戴至【{slot}】！"

def unwear_equipment_by_slot(p, slot):
    """❌ 卸下指定部位裝備"""
    slot = slot.replace("脫下裝備", "").strip()
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    target_item = equipped.get(slot)
    if not target_item: return f"❌ 該【{slot}】欄位本來就空無一物。"
    
    del equipped[slot]
    if slot == "武器": p["weapon"] = "赤手空拳"
    
    eq_inv_str = p.get("equipment_inventory", "[]")
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    inv.append(target_item)
    
    p["equipped_slots"] = json.dumps(equipped, ensure_ascii=False)
    p["equipment_inventory"] = json.dumps(inv, ensure_ascii=False)
    db_core.save_player(p)
    return f"❌ 裝備卸下成功！已將【{target_item['name']}】收回背包！"
