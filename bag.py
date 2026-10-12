import json
import random
import db_core
import weapons
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

CONSUMABLES = {
    "初級生命藥水": {"heal_range": (30, 50), "price": 30, "desc": "飲用後可隨機恢復 30~50 點血量。"},
    "高級生命藥水": {"heal_range": (80, 120), "price": 100, "desc": "飲用後可隨機恢復 80~120 點特大血量！"}
}

def get_bag_card(p):
    """🎒 生成網格化勇者私人物資倉庫卡片 (全面視覺化武器素質欄與一鍵穿戴熱鍵)"""
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
        
    inv = p["inventory"]
    if isinstance(inv, str):
        inv = json.loads(inv)
        
    items = inv.get("items", {})
    materials = inv.get("materials", {})
    
    # 讀取玩家儲存在 weapon_inventory 裡的備用武器包
    w_inv_str = p.get("weapon_inventory", "{}")
    if w_inv_str is None or w_inv_str == "None" or w_inv_str == "": w_inv_str = "{}"
    try: 
        weapons_held = json.loads(w_inv_str)
    except Exception: 
        weapons_held = {}
    
    contents = [
        {"type": "text", "text": "🎒 勇者皇家私人物資倉庫", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"👤 目前手持武裝：【{p.get('weapon', '赤手空拳')}】", "size": "xs", "color": "#4CD964", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "md", "color": "#333333"}
    ]
    
    # 1. 核心優化：【 ⚔️ 裝備與兵器收藏庫 】視覺化網格圖卡化展示
    contents.append({"type": "text", "text": "⚔️ 【 裝備與兵器收藏庫 】", "weight": "bold", "size": "sm", "color": "#007AFF", "margin": "md"})
    
    active_weapons = {k: v for k, v in weapons_held.items() if v > 0}
    if not active_weapons:
        contents.append({"type": "text", "text": "   (您的裝備背包空空如也，快去商店或野外打寶！)", "size": "xs", "color": "#8E8E93"})
    else:
        for w_name, count in active_weapons.items():
            pure_w_name = w_name.split(" 的 ")[-1] if " 的 " in w_name else w_name
            w_info = weapons.SHOP_WEAPONS.get(pure_w_name, {"atk_bonus": 0, "desc": "未知神秘兵器。"})
            
            contents.append({
                "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "box", "layout": "horizontal", "contents": [
                        {"type": "text", "text": f"🗡️ {w_name}", "size": "sm", "color": "#FF9500", "weight": "bold", "flex": 4},
                        {"type": "text", "text": f"擁有: {count} 把", "size": "xs", "color": "#34AADC", "align": "end", "flex": 2}
                    ]},
                    {"type": "text", "text": f"💥 物理傷害加成：+{w_info['atk_bonus']} 點", "size": "xs", "color": "#4CD964", "margin": "xs", "weight": "bold"},
                    {"type": "text", "text": f"📖 兵器神話：{w_info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs", "wrap": True},
                    {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "sm",
                     "action": {"type": "message", "label": "⚔️ 立即裝備上身", "text": f"裝備 {w_name}"}}
                ]
            })
            
    # 2. 渲染消耗品
    contents.append({"type": "text", "text": "🧪 【 藥水與補給物資 】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "lg"})
    if not items:
        contents.append({"type": "text", "text": "   (消耗品倉庫目前空空如也)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in items.items():
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                    {"type": "text", "text": f"🔹 {name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                    {"type": "text", "text": f"x{count}", "size": "xs", "color": "#4CD964", "align": "end", "flex": 1}
                ]
            })
            
    # 3. 渲染素材
    contents.append({"type": "text", "text": "💎 【 怪物珍稀原料區 】", "weight": "bold", "size": "sm", "color": "#AF52DE", "margin": "md"})
    if not materials:
        contents.append({"type": "text", "text": "   (尚未搜刮到任何魔物原料)", "size": "xs", "color": "#8E8E93"})
    else:
        for name, count in materials.items():
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                    {"type": "text", "text": f"🔸 {name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                    {"type": "text", "text": f"x{count}", "size": "xs", "color": "#FFCC00", "align": "end", "flex": 1}
                ]
            })
            
    flex_bubble = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}, "footer": {"backgroundColor": "#2A2A2A"}},
        "body": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": contents},
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{"type": "text", "text": "💡 提示：點擊上方兵器格子內的【⚔️ 立即裝備上身】按鈕，鐵匠鋪將全自動為您調度武裝！換下來的舊武器會安全移回包包中。", "size": "xs", "color": "#8E8E93", "align": "center", "wrap": True}]
        }
    }

    quick_items = [
        QuickReplyItem(action=MessageAction(label="👤 我的狀態", text="我的狀態")),
        QuickReplyItem(action=MessageAction(label="🛡️ 我的裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="🏪 補給商店", text="冒險商店")),
        QuickReplyItem(action=MessageAction(label="🦅 返回城鎮", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items)}

def equip_weapon_from_bag(p, user_cmd):
    """⚔️ 🤖 一鍵換裝大腦"""
    w_name = user_cmd.replace("裝備", "").replace("穿上", "").replace(" ", "").strip()
    
    w_inv_str = p.get("weapon_inventory", "{}")
    if w_inv_str is None or w_inv_str == "None" or w_inv_str == "": w_inv_str = "{}"
    try: 
        w_dict = json.loads(w_inv_str)
    except Exception: 
        w_dict = {}
        
    if w_dict.get(w_name, 0) <= 0:
        return f"❌ 換裝失敗！您的【裝備收藏庫】中目前沒有庫存【{w_name}】這把武器！"
        
    w_dict[w_name] -= 1
    if w_dict[w_name] == 0: 
        del w_dict[w_name]
        
    old_w = p.get("weapon", "赤手空拳")
    if old_w != "赤手空拳":
        w_dict[old_w] = w_dict.get(old_w, 0) + 1
        
    p["weapon_inventory"] = json.dumps(w_dict, ensure_ascii=False)
    p["weapon"] = w_name
    if " 的 " not in w_name:
        p["forge_weapon_bonus"] = 0
        
    db_core.save_player(p)
    return f"⚔️ 🔥 【 皇家更換裝備成功 】 🔥 ⚔️\n─────────────────\n你成功將私藏庫的 ── ⚔️【{w_name}】拔出披掛上身！\n\n🔄 換下來的舊武裝【{old_w}】已安全送回背包收藏庫！"

def add_to_inventory(p, item_name, is_material=False):
    if "inventory" not in p or not p["inventory"]: p["inventory"] = {"items": {}, "materials": {}}
    inv = p["inventory"]
    category = "materials" if is_material else "items"
    if category not in inv: inv[category] = {}
    inv[category][item_name] = inv[category].get(item_name, 0) + 1
    p["inventory"] = inv

def use_potion(p, potion_name):
    """🧪 喝藥水補血大腦"""
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
    
    # ✨ 【Bug 終極封印】精準為元組加上索引值 0 與 1，拆解出最小值與最大值，徹底消滅 random.randint 閃退！
    heal_amount = random.randint(int(config["heal_range"][0]), int(config["heal_range"][1]))
    
    old_hp = p["hp"]
    p["hp"] = min(max_hp, p["hp"] + heal_amount)
    items[potion_name] -= 1
    if items[potion_name] == 0: del items[potion_name]
    inv["items"] = items; p["inventory"] = inv
    db_core.save_player(p)
    return f"🧪 ✨ 你喝下了【{potion_name}】！\n💖 順利恢復了 {p['hp'] - old_hp} 點生命！\n🩸 血量狀態：{p['hp']} / {max_hp}"
