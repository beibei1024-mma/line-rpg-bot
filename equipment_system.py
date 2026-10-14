# equipment_system.py - 皇家全身 14 欄位獨立裝備穿脫與屬性加成核心大腦 (非堆疊獨立個體版)

import json
import random
import db_core
import weapons

SLOT_MAPPING = {
    "頭盔": "helmet", "上衣": "armor", "下褲": "pants", "鞋子": "shoes",
    "武器": "weapon", "項鍊": "necklace", "戒指1": "ring1", "戒指2": "ring2",
    "手環": "bracelet", "副手": "sub_hand", "徽章": "badge",
    "付費道具1": "cash_item1", "付費道具2": "cash_item2", "付費道具3": "cash_item3"
}

def get_equipment_slot_by_name(item_name):
    """🔍 根據道具名稱中的關鍵字，自動判定它應該穿在哪個黃金格子欄位"""
    if not item_name:
        return None
    if "頭盔" in item_name or "頭巾" in item_name or "冠" in item_name or "帽" in item_name: return "頭盔"
    elif "上衣" in item_name or "皮甲" in item_name or "鎧甲" in item_name or "衣" in item_name or "袍" in item_name: return "上衣"
    elif "下褲" in item_name or "長褲" in item_name or "裙" in item_name: return "下褲"
    elif "鞋" in item_name or "靴" in item_name: return "鞋子"
    elif "項鍊" in item_name or "墜飾" in item_name: return "項鍊"
    elif "手環" in item_name or "護腕" in item_name: return "手環"
    elif "盾" in item_name or "副手" in item_name: return "副手"
    elif "徽章" in item_name or "勳章" in item_name: return "徽章"
    elif "課金1" in item_name or "付費1" in item_name: return "付費道具1"
    elif "課金2" in item_name or "付費2" in item_name: return "付費道具2"
    elif "課金3" in item_name or "付費3" in item_name: return "付費道具3"

    pure_name = weapons.get_pure_weapon_name(item_name)
    for w_base in weapons.SHOP_WEAPONS.keys():
        if w_base in pure_name:
            return "武器"
    if "劍" in pure_name or "弓" in pure_name or "杖" in pure_name or "刺" in pure_name or "刀" in pure_name or "錘" in pure_name or "鐮" in pure_name or "戟" in pure_name or "槍" in pure_name or "砲" in pure_name or "匕" in pure_name or "刃" in pure_name or "弩" in pure_name:
        return "武器"

    if "戒指" in item_name or "指環" in item_name:
        return "戒指1"
    return None

def execute_equip_item(p, user_msg):
    """⚒️ 核心換裝大腦：依據獨立名字精準換裝（支援無空格模糊比對），脫下的裝備 100% 原樣打包退回"""
    target_eq_name = user_msg.replace("裝備", "").replace("穿上", "").replace(" ", "").strip()

    w_inv_str = p.get("weapon_inventory", "[]")
    if w_inv_str in (None, "None", "", "{}"):
        w_inv_str = "[]"
    try:
        w_list = json.loads(w_inv_str) if isinstance(w_inv_str, str) else list(w_inv_str)
    except Exception:
        w_list = []

    # 忽略空白差異比對，徹底解決「🔥史詩 新手鐵短劍」被清洗空白後找不到的問題
    matched_item = None
    for item in w_list:
        if item.get("name", "").replace(" ", "") == target_eq_name:
            matched_item = item
            break

    if not matched_item:
        return f"❌ 裝備失敗！您的裝備收藏庫中，目前找不到符合【{target_eq_name}】名號的獨立物品。"

    actual_eq_name = matched_item["name"]
    slot_type = matched_item.get("slot")
    if not slot_type or slot_type not in SLOT_MAPPING:
        slot_type = get_equipment_slot_by_name(actual_eq_name)
    if not slot_type:
        return f"❌ 裝備失敗！無法辨識【{actual_eq_name}】對應的欄位部位。"

    db_field = SLOT_MAPPING[slot_type]

    if slot_type == "戒指1" and p.get("ring1", "無") != "無" and p.get("ring2", "無") == "無":
        slot_type = "戒指2"
        db_field = "ring2"

    old_eq_name = p.get(db_field, "無") if db_field != "weapon" else p.get("weapon", "赤手空拳")

    if old_eq_name not in ("無", "赤手空拳"):
        old_slot = get_equipment_slot_by_name(old_eq_name) or "武器"
        w_list.append({"id": f"eq_{random.randint(100000, 999999)}", "name": old_eq_name, "slot": old_slot})

    w_list.remove(matched_item)
    p[db_field] = actual_eq_name

    if db_field == "weapon":
        p["forge_weapon_bonus"] = 0

    p["weapon_inventory"] = json.dumps(w_list, ensure_ascii=False)
    db_core.save_player(p)

    return (
        f"🛡️ ✨ 【 傳奇個體部位換裝成功 】 ✨ 🛡️\n"
        f"───────────────────\n"
        f"你從背包取出獨立神兵，舊裝備已原封不動完整退回倉庫！\n\n"
        f"📦 穿戴部位：【 {slot_type} 】欄位\n"
        f"❌ 卸下舊裝：{old_eq_name}\n"
        f"🔥 穿上新裝：【 {actual_eq_name} 】\n\n"
        f"💡 提示：每一件裝備都是獨立個體，輸入【我的狀態】或【我的裝備】即可查看最新加成！"
    )

def add_to_weapon_inventory_individual(p, item_name, slot_name="未知"):
    """⭕ 終極獨立入庫函式：專供商店購買、野外掉落與工坊打造"""
    w_inv_str = p.get("weapon_inventory", "[]")
    if w_inv_str in (None, "None", "", "{}"):
        w_inv_str = "[]"
    try:
        w_list = json.loads(w_inv_str) if isinstance(w_inv_str, str) else list(w_inv_str)
    except Exception:
        w_list = []

    new_item = {
        "id": f"eq_{random.randint(100000, 999999)}",
        "name": item_name,
        "slot": slot_name if slot_name != "未知" else (get_equipment_slot_by_name(item_name) or "武器")
    }
    w_list.append(new_item)
    p["weapon_inventory"] = json.dumps(w_list, ensure_ascii=False)
