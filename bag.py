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
    """🎒 生成網格化勇者私人物資倉庫卡片 (全新解鎖裝備收藏庫與換裝引導)"""
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
        
    inv = p["inventory"]
    if isinstance(inv, str):
        inv = json.loads(inv)
        
    items = inv.get("items", {})
    materials = inv.get("materials", {})
    
    # ✨ 讀取玩家儲存在 weapon_inventory 裡的備用武器包
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
    
    # 🌟 1. 全新解鎖：【 ⚔️ 裝備與兵器收藏庫 】網格欄位
    contents.append({"type": "text", "text": "⚔️ 【 裝備與兵器收藏庫 】", "weight": "bold", "size": "sm", "color": "#007AFF", "margin": "md"})
    
    # 過濾清除無效的空資料
    active_weapons = {k: v for k, v in weapons_held.items() if v > 0}
    if not active_weapons:
        contents.append({"type": "text", "text": "   (您的裝備背包空空如也，快去商店或野外打寶！)", "size": "xs", "color": "#8E8E93"})
    else:
        for w_name, count in active_weapons.items():
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                    {"type": "text", "text": f"🗡️ {w_name}", "size": "xs", "color": "#E0E0E0", "flex": 4},
                    {"type": "text", "text": f"x{count}", "size": "xs", "color": "#34AADC", "align": "end", "flex": 1}
                ]
            })
            
    # 2. 渲染消耗品
    contents.append({"type": "text", "text": "🧪 【 藥水與補給物資 】", "weight": "bold", "size": "sm", "color": "#FF9500", "margin": "md"})
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
            # ✨ 【UX 大升級】在底部加入「裝備口令」的雙重智慧提示！
            "contents": [{"type": "text", "text": "✍️ 換裝口令：輸入【裝備 武器名稱】(例如：裝備 新手鐵短劍)\n🧪 補血口令：輸入【使用 藥水名稱】(例如：使用 初級生命藥水)", "size": "xs", "color": "#8E8E93", "align": "center", "wrap": True}]
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
    """⚔️ 🤖 全新一鍵換裝大腦：從背包中提取兵器裝備上身，並把舊武器丟回收藏庫"""
    w_name = user_cmd.replace("裝備", "").replace("穿上", "").replace(" ", "").strip()
    
    w_inv_str = p.get("weapon_inventory", "{}")
    if w_inv_str is None or w_inv_str == "None" or w_inv_str == "": w_inv_str = "{}"
    try: 
        w_dict = json.loads(w_inv_str)
    except Exception: 
        w_dict = {}
        
    if w_dict.get(w_name, 0) <= 0:
        return f"❌ 換裝失敗！您的【裝備收藏庫】中目前沒有庫存【{w_name}】這把武器！"
        
    # 1. 扣除背包裡要穿上的武器數量 1 把
    w_dict[w_name] -= 1
    if w_dict[w_name] == 0: 
        del w_dict[w_name]
        
    # 2. 將原本手上的舊武器，安全存入背包收藏庫
    old_w = p.get("weapon", "赤手空拳")
    if old_w != "赤手空拳":
        w_dict[old_w] = w_dict.get(old_w, 0) + 1
        
    # 3. 回存資料庫，並重置測試字首加成
    p["weapon_inventory"] = json.dumps(w_dict, ensure_ascii=False)
    p["weapon"] = w_name
    # 如果穿上的是不含詞綴的乾淨商店現貨，歸零附加白字；如果是極品打造裝，保留原有詞綴加乘
    if " 的 " not in w_name:
        p["forge_weapon_bonus"] = 0
        
    db_core.save_player(p)
    return f"⚔️ 🔥 【 皇家更換裝備成功 】 🔥 ⚔️\n─────────────────\n你打開了兵器私藏庫，將全新兵器 ── ⚔️【{w_name}】拔出披掛上身！\n\n🔄 去向：換下來的舊武裝【{old_w}】已全自動送入背包收藏庫！\n💡 提示：輸入【我的狀態】或【裝備】即可查看全新暴漲的戰力數據面板！"

# (以下維護藥水與素材基礎功能不變)
def add_to_inventory(p, item_name, is_material=False):
    if "inventory" not in p or not p["inventory"]: p["inventory"] = {"items": {}, "materials": {}}
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
    heal_amount = random.randint(config["heal_range"][0], config["heal_range"][1])
    old_hp = p["hp"]
    p["hp"] = min(max_hp, p["hp"] + heal_amount)
    items[potion_name] -= 1
    if items[potion_name] == 0: del items[potion_name]
    inv["items"] = items; p["inventory"] = inv
    db_core.save_player(p)
    return f"🧪 ✨ 你喝下了【{potion_name}】！\n💖 順利恢復了 {p['hp'] - old_hp} 點生命！\n🩸 血量狀態：{p['hp']} / {max_hp}"
