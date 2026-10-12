# player_equipment.py (續篇) - 實體一鍵換裝與副詞綴屬性回流大腦

import json
import db_core

def get_equipment_bag_flex(p):
    """🎒 生成裝備背包專屬的網格化 Flex 卡片，供勇者一鍵點擊穿戴上身"""
    eq_inv_str = p.get("equipment_inventory", "[]")
    if not eq_inv_str or eq_inv_str == "None": eq_inv_str = "[]"
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    
    contents = [
        {"type": "text", "text": "⚔️ 勇者皇家神兵防具備用包", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    if not inv:
        contents.append({"type": "text", "text": "   (您的裝備背包空空如也，快去黑市或野外打寶！)", "size": "xs", "color": "#8E8E93", "margin": "md"})
    else:
        # 只展示前 8 件，防止 LINE Flex 爆版，其餘安全保留在資料庫
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
                     "action": {"type": "message", "label": "⚡ 立即穿戴上身", "text": f"穿戴裝備 {item['id']}"}}
                ]
            })
            
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def wear_equipment_by_id(p, item_id):
    """⚡ 核心換裝大腦：依 UUID 提取裝備、移出背包、頂替部位、舊裝回存包包"""
    item_id = item_id.replace("穿戴裝備", "").strip()
    
    # 1. 讀取裝備背包
    eq_inv_str = p.get("equipment_inventory", "[]")
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    
    # 2. 搜尋目標裝備
    eq_item = next((item for item in inv if item["id"] == item_id), None)
    if not eq_item: return "❌ 換裝失敗！裝備備用包中找不到該裝備識別碼，可能已被更換或出售。"
    
    slot = eq_item["slot"]
    
    # 3. 讀取當前已穿戴部位
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    # 4. 頂替邏輯：如果該部位本來就有穿裝備，先拔下來塞回背包
    old_item = equipped.get(slot)
    if old_item:
        inv.append(old_item)
        
    # 5. 從背包移除新裝備，並披掛上身
    inv.remove(eq_item)
    equipped[slot] = eq_item
    
    # 6. 狀態回寫與實體舊武器(相容舊代碼欄位)同步更新
    if slot == "武器":
        p["weapon"] = eq_item["name"]
        
    p["equipment_inventory"] = json.dumps(inv, ensure_ascii=False)
    p["equipped_slots"] = json.dumps(equipped, ensure_ascii=False)
    
    # 重新洗鍊實體數值加成（此處將在戰鬥端動態加算，防止改寫基礎屬性死鎖）
    db_core.save_player(p)
    return f"🛡️ 換裝成功！你已將 ── ✨【{eq_item['name']}】披掛至【{slot}】欄位！\n🔄 換下來的舊裝備已安全移回備用裝備包中！"

def unwear_equipment_by_slot(p, slot):
    """❌ 卸下指定部位裝備，並安全收回包包"""
    slot = slot.replace("脫下裝備", "").strip()
    
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    target_item = equipped.get(slot)
    if not target_item: return f"❌ 脫除失敗！勇者目前的【{slot}】欄位本來就空無一物。"
    
    # 從身上拔除
    del equipped[slot]
    if slot == "武器": p["weapon"] = "赤手空拳"
    
    # 收回包包
    eq_inv_str = p.get("equipment_inventory", "[]")
    try: inv = json.loads(eq_inv_str)
    except: inv = []
    inv.append(target_item)
    
    p["equipped_slots"] = json.dumps(equipped, ensure_ascii=False)
    p["equipment_inventory"] = json.dumps(inv, ensure_ascii=False)
    
    db_core.save_player(p)
    return f"❌ 🛡️ 裝備卸下成功！你已將【{slot}】欄位的【{target_item['name']}】安全解下，並放回裝備包！"
