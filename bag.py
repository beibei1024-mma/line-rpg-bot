import random
import db_core

# 🧪 消耗性道具大數據庫（定義點擊使用時效果與基礎數值）
CONSUMABLES = {
    "初級生命藥水": {"heal_range": (30, 50), "price": 30, "desc": "飲用後可隨機恢復 30~50 點血量。"},
    "高級生命藥水": {"heal_range": (80, 120), "price": 100, "desc": "飲用後可隨機恢復 80~120 點特大血量！"}
}

def get_bag_text(p):
    """將玩家資料庫裡的隨機背包字串（JSON 格式），包裝成精美排列的清單"""
    # 預防新玩家資料庫無背包欄位，做安全防呆
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
        
    inv = p["inventory"]
    if isinstance(inv, str):
        inv = json.loads(inv)
        
    text = "🎒 💼 【勇者私人物品倉庫】\n"
    text += "─────────────────\n"
    text += f"⚔️ 當前裝備武器：【{p.get('weapon', '赤手空拳')}】\n\n"
    
    # 1. 解析消耗性道具（藥水類）
    text += "🧪 【藥水/消耗品區】\n"
    items = inv.get("items", {})
    if not items:
        text += "   （目前沒有任何藥水）\n"
    else:
        for name, count in items.items():
            text += f"   🔹 {name} x {count}\n"
            
    text += "\n"
    
    # 2. 解析怪物掉落材料
    text += "💎 【怪物素材/原料區】\n"
    materials = inv.get("materials", {})
    if not materials:
        text += "   （目前沒有任何戰利品原料）\n"
    else:
        for name, count in materials.items():
            text += f"   🔸 {name} x {count}\n"
            
    text += "─────────────────\n"
    text += "✍️ 提示：輸入【使用 物品名稱】即可在戰場外使用藥水補血！\n（例如：使用 初級生命藥水）"
    return text

def add_to_inventory(p, item_name, is_material=False):
    """當擊敗怪物時，由 game_core 調用，將素材或道具隨機丟進雲端背包"""
    if "inventory" not in p or not p["inventory"]:
        p["inventory"] = {"items": {}, "materials": {}}
        
    inv = p["inventory"]
    category = "materials" if is_material else "items"
    
    if category not in inv:
        inv[category] = {}
        
    # 數量 + 1
    inv[category][item_name] = inv[category].get(item_name, 0) + 1
    p["inventory"] = inv
    # 注意：這裡不主動儲存，由外部呼叫牠的戰鬥結算大事件統一儲存，回傳速度最快！

def use_potion(p, potion_name):
    """處理玩家輸入使用藥水的隨機補血判定"""
    if "inventory" not in p or not p["inventory"]:
        return "❌ 你的背包裡空無一物，無法使用道具！"
        
    inv = p["inventory"]
    items = inv.get("items", {})
    
    if potion_name not in items or items[potion_name] <= 0:
        return f"❌ 道具不足！你的背包裡沒有【{potion_name}】。"
        
    if p["hp"] <= 0:
        return "💀 你已經陣亡了！請先使用【復活】神聖法術，無法直接喝藥水。"
        
    if p["hp"] >= p["max_hp"]:
        return "💚 你的生命值已經是滿的，不需要浪費珍貴的藥水！"
        
    if potion_name not in CONSUMABLES:
        return f"❌ 【{potion_name}】不是可以使用的消耗性藥水。"
        
    # 🎲 啟動隨機性優化：計算隨機補血量
    config = CONSUMABLES[potion_name]
    heal_amount = random.randint(config["heal_range"][0], config["heal_range"][1])
    
    # 計算補血後的數值
    old_hp = p["hp"]
    p["hp"] = min(p["max_hp"], p["hp"] + heal_amount)
    actual_heal = p["hp"] - old_hp
    
    # 扣除背包道具數量
    items[potion_name] -= 1
    if items[potion_name] == 0:
        del items[potion_name]
        
    inv["items"] = items
    p["inventory"] = inv
    
    # 喝藥水屬於大事件，立刻跨海同步鎖進 Supabase 雲端資料庫
    db_core.save_player(p)
    
    return f"🧪 ✨ 你咕嚕嚕地喝下了【{potion_name}】！\n💖 隨機恢復了 {actual_heal} 點生命值！\n🩸 血量狀態：{p['hp']} / {p['max_hp']}"
