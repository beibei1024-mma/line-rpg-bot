# equipment_system.py - 皇家全身 14 欄位獨立裝備穿脫與屬性加成核心大腦
import json
import db_core
import weapons

# 🗺️ 14 大裝備欄位部位映射防火牆：自動過濾道具名稱，將其分類至正確的 Supabase 欄位格子
SLOT_MAPPING = {
    "頭盔": "helmet", "上衣": "armor", "下褲": "pants", "鞋子": "shoes",
    "武器": "weapon", "項鍊": "necklace", "戒指1": "ring1", "戒指2": "ring2",
    "手環": "bracelet", "副手": "sub_hand", "徽章": "badge",
    "付費道具1": "cash_item1", "付費道具2": "cash_item2", "付費道具3": "cash_item3"
}

def get_equipment_slot_by_name(item_name):
    """🔍 根據道具名稱，自動判定它應該穿在哪個黃金格子欄位（文字原樣防呆匹配）"""
    if "頭盔" in item_name or "頭巾" in item_name or "冠" in item_name: return "頭盔"
    elif "上衣" in item_name or "皮甲" in item_name or "鎧甲" in item_name or "衣" in item_name: return "上衣"
    elif "下褲" in item_name or "長褲" in item_name or "裙" in item_name: return "下褲"
    elif "鞋" in item_name or "靴" in item_name: return "鞋子"
    elif "項鍊" in item_name or "墜飾" in item_name: return "項鍊"
    elif "手環" in item_name or "護腕" in item_name: return "手環"
    elif "盾" in item_name or "副手" in item_name: return "副手"
    elif "徽章" in item_name or "勳章" in item_name: return "徽章"
    elif "課金1" in item_name or "付費1" in item_name: return "付費道具1"
    elif "課金2" in item_name or "付費2" in item_name: return "付費道具2"
    elif "課金3" in item_name or "付費3" in item_name: return "付費道具3"
    elif item_name in weapons.SHOP_WEAPONS: return "武器"
    
    # 預設多指環防呆自動分流
    elif "戒指" in item_name or "指環" in item_name: return "戒指1"
    return None

def execute_equip_item(p, user_msg):
    """⚔️ 核心換裝大腦：從包包將任何防具、飾品、付費道具穿戴上身，並把舊裝備放回背包"""
    clean_cmd = user_msg.replace("裝備", "").replace("穿上", "").replace(" ", "").strip()
    
    # 1. 驗證玩家背包內是否真的擁有此件裝備
    w_inv_str = p.get("weapon_inventory", "{}")
    if w_inv_str in (None, "None", ""): w_inv_str = "{}"
    try: w_dict = json.loads(w_inv_str)
    except: w_dict = {}
        
    if clean_cmd not in w_dict or w_dict[clean_cmd] <= 0:
        return f"❌ 裝備失敗！您的武器與裝備收藏庫中，目前沒有【{clean_cmd}】這件物品。"
        
    # 2. 自動偵測部位欄位
    slot_type = get_equipment_slot_by_name(clean_cmd)
    if not slot_type:
        return f"❌ 裝備失敗！系統無法辨識【{clean_cmd}】屬於哪一個神聖裝備欄位，請在名字中加入部位關鍵字（如頭盔、上衣、戒指）。"
        
    db_field = SLOT_MAPPING[slot_type]
    
    # 特殊特殊戒指雙格子自動分流博弈邏輯
    if slot_type == "戒指1" and p.get("ring1", "無") != "無" and p.get("ring2", "無") == "無":
        slot_type = "戒指2"
        db_field = "ring2"
        
    # 3. 執行脫下舊裝備，放回背包
    old_eq = p.get(db_field, "無") if db_field != "weapon" else p.get("weapon", "赤手空拳")
    if old_eq not in ("無", "赤手空拳"):
        w_dict[old_eq] = w_dict.get(old_eq, 0) + 1
        
    # 4. 扣除新裝備數量並正式穿戴上身
    w_dict[clean_cmd] -= 1
    if w_dict[clean_cmd] <= 0:
        w_dict.pop(clean_cmd, None)
        
    p[db_field] = clean_cmd
    
    # 如果更換的是主手武器，重置手工鍛造洗鍊加成
    if db_field == "weapon":
        p["forge_weapon_bonus"] = 0
        
    p["weapon_inventory"] = json.dumps(w_dict, ensure_ascii=False)
    db_core.save_player(p)
    
    return f"🛡️ ✨ 【 皇家全身部位換裝成功 】 ✨ 🛡️\n───────────────────\n你從備用收藏庫中取出神兵防具，引導靈魂完美契合！\n\n📦 穿戴部位：【 {slot_type} 】欄位\n⚔️ 卸下舊裝：{old_eq}\n🔥 穿上新裝：【 {clean_cmd} 】\n\n💡 操作提示：輸入【我的狀態】即可查閱全身 14 大網格黑曜石面板的最新即時穿戴外觀！"

def calculate_total_equipment_stats(p):
    """📊 全身裝備屬性大總加：未來可用於 battle_core 計算防禦力或攻擊力加成（保留擴充擴展性）"""
    total_bonus = {
        "atk": weapons.SHOP_WEAPONS[p['weapon']]['atk_bonus'] if p.get('weapon') in weapons.SHOP_WEAPONS else 0,
        "def": 0
    }
    total_bonus["atk"] += int(p.get("forge_weapon_bonus", 0))
    return total_bonus
