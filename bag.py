import json
import random
import db_core
import weapons
import equipment_system
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

CONSUMABLES = {
    "初級生命藥水": {"heal_range": (30, 50), "price": 30, "desc": "飲用後可隨機恢復 30~50 點血量。"},
    "高級生命藥水": {"heal_range": (80, 120), "price": 100, "desc": "飲用後可隨機恢復 80~120 點特大血量！"}
}

def get_bag_card(p):
    """🎒 生成網格化勇者私人物資倉庫卡片 (緊湊不堆疊素質展示版)"""
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
        
    inv = p["inventory"]
    if isinstance(inv, str):
        try: inv = json.loads(inv)
        except: inv = {"items": {}, "materials": {}}
        
    items = inv.get("items", {})
    materials = inv.get("materials", {})
    
    # 讀取獨立不堆疊的 JSON 裝備背包列表
    w_inv_str = p.get("weapon_inventory", "[]")
    if w_inv_str in (None, "None", "", "{}"): w_inv_str = "[]"
    try: w_list = json.loads(w_inv_str)
    except: w_list = []
    
    contents = [
        {"type": "text", "text": "🎒 勇者皇家私人物資倉庫", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"👤 目前手持武裝：【{p.get('weapon', '赤手空拳')}】", "size": "xs", "color": "#4CD964", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "md", "color": "#333333"}
    ]
    
    # 1. ⚔️ 【 裝備與兵器收藏庫 】緊湊素質流網格
    contents.append({"type": "text", "text": "⚔️ 【 裝備與兵器收藏庫 】", "weight": "bold", "size": "sm", "color": "#007AFF", "margin": "md"})
    
    if not w_list:
        contents.append({"type": "text", "text": "   (您的裝備背包空空如也，快去商店或野外打寶！)", "size": "xs", "color": "#8E8E93"})
    else:
        # ⚡ 核心優化：採用超緊湊單行橫向布局，完全拔除說明，僅亮出核心白字物傷或部位
        for item in w_list:
            eq_name = item.get("name", "未知裝備")
            
            # 清洗名號去 weapons.py 匹配數值
            pure_w_name = eq_name.split(" ] 的 ")[-1] if " ] 的 " in eq_name else eq_name
            pure_w_name = pure_w_name.split("】")[-1] if "】" in pure_w_name else pure_w_name
            pure_w_name = pure_w_name.strip()
            
            pure_w_name = weapons.get_pure_weapon_name(eq_name)
    if pure_w_name in weapons.SHOP_WEAPONS and pure_w_name != "赤手空拳":
            atk_val = weapons.get_weapon_atk(eq_name)
            stat_text = f"💥 攻擊力 +{atk_val}"
            else:
                detected_slot = equipment_system.get_equipment_slot_by_name(eq_name) or "防具"
                stat_text = f"🛡️ 部位：{detected_slot}"
                
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "xs", "cornerRadius": "sm", "alignItems": "center",
                "contents": [
                    {
                        "type": "box", "layout": "vertical", "flex": 4,
                        "contents": [
                            {"type": "text", "text": f"🔸 {eq_name}", "size": "xs", "color": "#FFFFFF", "weight": "bold"},
                            {"type": "text", "text": stat_text, "size": "xxs", "color": "#FF9500", "marginTop": "xs"}
                        ]
                    },
                    {
                        "type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "flex": 2,
                        "action": {"type": "message", "label": "⚡ 穿戴", "text": f"裝備 {eq_name}"}
                    }
                ]
            })
            
    # 2. 🧪 【 藥水與補給物資 】 (保持您原本的結構)
    contents.append({"type": "text", "text": "🧪 【 藥水與補給物資 】", "weight": "bold", "size": "sm", "color": "#34AADC", "margin": "lg"})
    if not items:
        contents.append({"type": "text", "text": "   (消耗品倉庫目前空空如也)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in items.items():
            if count > 0:
                contents.append({
                    "type": "box", "layout": "horizontal", "margin": "xs",
                    "contents": [
                        {"type": "text", "text": f"🔹 {name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                        {"type": "text", "text": f"x{count}", "size": "xs", "color": "#4CD964", "align": "end", "flex": 1}
                    ]
                })
            
    # 3. 💎 【 怪物珍稀原料區 】 (保持您原本的結構)
    contents.append({"type": "text", "text": "💎 【 怪物珍稀原料區 】", "weight": "bold", "size": "sm", "color": "#AF52DE", "margin": "md"})
    if not materials:
        contents.append({"type": "text", "text": "   (尚未搜刮到任何魔物原料)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in materials.items():
            if count > 0:
                contents.append({
                    "type": "box", "layout": "horizontal", "margin": "xs",
                    "contents": [
                        {"type": "text", "text": f"🔸 {name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                        {"type": "text", "text": f"x{count}", "size": "xs", "color": "#FFCC00", "align": "end", "flex": 1}
                    ]
                })
            
    flex_bubble = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": contents}
    }

    quick_items = [
        QuickReplyItem(action=MessageAction(label="👤 我的狀態", text="我的狀態")),
        QuickReplyItem(action=MessageAction(label="🛡️ 我的裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="🏪 補給商店", text="冒險商店")),
        QuickReplyItem(action=MessageAction(label="🦅 返回城鎮", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items)}

def equip_weapon_from_bag(p, user_cmd):
    """⚔️ 🤖 換裝管線：全自動轉接至全新獨立的 equipment_system 非堆疊換裝核心"""
    # 100% 直連獨立裝備大腦，一行解鎖全身 14 欄位
    return equipment_system.execute_equip_item(p, user_cmd)

def add_to_inventory(p, item_name, is_material=False):
    """🧪 常規堆疊物品入庫大腦"""
    if "inventory" not in p or not p["inventory"]: 
        p["inventory"] = {"items": {}, "materials": {}}
    inv = p["inventory"]
    category = "materials" if is_material else "items"
    if category not in inv: 
        inv[category] = {}
    inv[category][item_name] = inv[category].get(item_name, 0) + 1
    p["inventory"] = inv

def use_potion(p, potion_name):
    """🧪 喝藥水補血大腦 (100% 無損保留您的元組防空解包優化)"""
    if "inventory" not in p or not p["inventory"]: return "❌ 背包空無一物！"
    inv = p["inventory"]
    items = inv.get("items", {})
    if potion_name not in items or items[potion_name] <= 0: return f"❌ 沒有【{potion_name}】。"
    
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    vit_val = int(p.get("vitality", 10) * job_mod["vit_mod"])
    max_hp = 100 + (vit_val * 5) + (level * 15)

    if p["hp"] <= 0: return "💀 你已經陣亡了！請先【復活】。"
    if p["hp"] >= max_hp: return "💚 生命值已滿，不需浪費藥水！"
    if potion_name not in CONSUMABLES: return "❌ 非可食用的藥水。"
    
    config = CONSUMABLES[potion_name]
    
    # 100% 保留您的防空安全索引解包
    heal_amount = random.randint(int(config["heal_range"][0]), int(config["heal_range"][1]))
    
    old_hp = p["hp"]
    p["hp"] = min(max_hp, p["hp"] + heal_amount)
    items[potion_name] -= 1
    if items[potion_name] == 0: del items[potion_name]
    inv["items"] = items; p["inventory"] = inv
    db_core.save_player(p)
    return f"🧪 ✨ 你喝下了【{potion_name}】！\n💖 順利恢復了 {p['hp'] - old_hp} 點生命！\n🩸 血量狀態：{p['hp']} / {max_hp}"
