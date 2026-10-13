# forge_system.py - 皇家禁忌工坊與隨機熔煉核心大腦 v5.5 (不堆疊獨立個體完全體版)

import json
import random
import db_core
import weapons  # ✨【核心數據鏈接】直連神兵利器數據庫，消除打造不匹配Bug
# ⭕ 終極修復：移除引發閃退的 player_equipment，改為直連您最新獨立出來的不堆疊裝備大腦！
import equipment_system

# 📜 皇家遠古手工鍛造圖紙配方庫 (材料消耗對齊您在 monsters.py 定義的野外素材)
FORGE_RECIPES = {
    "新手鐵短劍": {"slot": "武器", "base": "鐵劍", "mat": "史萊姆黏液", "mat_qty": 3},
    "微光木藤弓": {"slot": "武器", "base": "長弓", "mat": "強韌蜘蛛絲", "mat_qty": 5},
    "見習魔法杖": {"slot": "武器", "base": "法杖", "mat": "不融冰塊", "mat_qty": 5},
    "黑曜熔岩大劍": {"slot": "武器", "base": "鐵劍", "mat": "熔岩核心", "mat_qty": 8}
}

def get_forge_menu(p):
    """🛠️ 生成極致奢華的工坊手工鍛造藍圖 Flex 展售選單"""
    contents = [
        {"type": "text", "text": "⚒️ 皇家遠古皇家鍛造熔煉工坊", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 勇者流動金幣：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # 遍歷展示所有配方圖紙，價格會全自動去 weapons.py 中動態抓取
    for name, r in FORGE_RECIPES.items():
        if name in weapons.SHOP_WEAPONS:
            w_info = weapons.SHOP_WEAPONS[name]
            contents.append({
                "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": f"📜 圖紙：【{name}】({r['slot']})", "size": "xs", "color": "#FF9500", "weight": "bold"},
                    {"type": "text", "text": f"💰 打造消耗：🪙 {w_info['price']} 金幣", "size": "xxs", "color": "#FFCC00", "margin": "xs"},
                    {"type": "text", "text": f"🛡️ 所需材料：🛠️ {r['mat']} x{r['mat_qty']}", "size": "xxs", "color": "#34AADC"},
                    {"type": "text", "text": f"📖 描述：{w_info['desc']}", "size": "xxs", "color": "#8E8E93", "margin": "xs"},
                    {"type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                     "action": {"type": "message", "label": "⚒️ 投入素材開始熔煉", "text": f"鍛造 {name}"}}
                ]
            })
        
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

def execute_forge_weapon(p, cmd_str):
    """⚒️ 核心熔煉大腦：洗鍊高品質裝備，並以【完全不堆疊】的獨立個體塞入新包包"""
    blueprint = cmd_str.replace("鍛造", "").replace(" ", "").strip()
    if blueprint not in FORGE_RECIPES or blueprint not in weapons.SHOP_WEAPONS:
        return "❌ 打造失敗！遠古工坊中沒有記載該裝備的神聖圖紙配方。"
        
    recipe = FORGE_RECIPES[blueprint]
    w_config = weapons.SHOP_WEAPONS[blueprint]
    
    # 1. 檢查金幣是否足夠
    if p["gold"] < w_config["price"]:
        return f"❌ 打造失敗！🪙 資金不足！打造【{blueprint}】需要 {w_config['price']} 金幣，你目前只有 {p['gold']} 金幣。"
        
    # 2. 檢查背包素材數量 (100% 適配您原有的 p["inventory"]["materials"] 雙層巢狀結構)
    inv = p.get("inventory", {})
    if isinstance(inv, str):
        try: inv = json.loads(inv)
        except: inv = {"items": {}, "materials": {}}
        
    materials_dict = inv.get("materials", {})
    current_mat_qty = materials_dict.get(recipe["mat"], 0)
    
    if current_mat_qty < recipe["mat_qty"]:
        return f"❌ 打造失敗！🛠️ 鍛造素材不足！你需要【{recipe['mat']}】x{recipe['mat_qty']}，但你目前只有 {current_mat_qty} 個。"
        
    # 3. 扣除代價
    p["gold"] -= w_config["price"]
    materials_dict[recipe["mat"]] = current_mat_qty - recipe["mat_qty"]
    inv["materials"] = materials_dict
    p["inventory"] = json.dumps(inv, ensure_ascii=False)
    
    # 4. 手工打造隨機洗鍊品質 (有 10% 概率爆出史詩或遠古神話！)
    rolled_rarity = random.choices(
        ["⭐普通", "🔷魔法", "🌟稀有", "🔥史詩", "👑遠古神話"],
        weights=[0.50, 0.25, 0.15, 0.07, 0.03], k=1
    )[0]
    
    final_eq_name = f"{rolled_rarity} {blueprint}"
    
    # 5. ⚡ 終極防爆對接：調用您獨立大腦的 add_to_weapon_inventory_individual 函數
    # 產生帶有獨立 UUID 識別碼、完全不堆疊的專屬 JSON 個體包，安全送入武器背包欄！
    equipment_system.add_to_weapon_inventory_individual(p, final_eq_name, slot_name=recipe["slot"])
    db_core.save_player(p)
    
    return f"⚒️ 🔥 【 工坊熔煉天啟大成功 】 🔥 ⚒️\n───────────────────\n鐵匠揮舞重錘，熔岩鐵水四濺！你投入的素材在法陣中完美凝聚！\n\n🔨 成功打造：{final_eq_name} ({recipe['slot']})！\n💥 武器基礎物傷：+{w_config['atk_bonus']}\n✨ 品質天啟：成功洗鍊出 ── 【{rolled_rarity}】階級！\n📦 存放去向：神兵利器已全自動以【獨立個體】送入【我的背包】，請開啟背包手動穿戴上身！"

# ── ⚙️ 核心解鎖函數 (屬於最外層頂格縮排，前面不可有任何空格，直接對接大腦) ──

def get_equipment_card(p):
    """🛡️ 生成勇者神聖裝備欄面板，直連當前穿戴武器屬性"""
    current_weapon = p.get("weapon", "赤手空拳")
    pure_w_name = current_weapon.split(" ] 的 ")[-1] if " ] 的 " in current_weapon else current_weapon
    pure_w_name = pure_w_name.split("】")[-1] if "】" in pure_w_name else pure_w_name
    pure_w_name = pure_w_name.strip()
    
    w_info = weapons.SHOP_WEAPONS.get(pure_w_name, {"atk_bonus": 0, "desc": "赤手空拳，毫無攻擊力加成。"})
    forge_bonus = int(p.get("forge_weapon_bonus", 0))
    total_atk = w_info["atk_bonus"] + forge_bonus
    
    slot_contents = [
        {"type": "text", "text": "⚔️ 主手武器 (Main-Hand Weapon)", "size": "xs", "color": "#007AFF", "weight": "bold"},
        {"type": "text", "text": f"【 {current_weapon} 】", "size": "md", "color": "#4CD964", "weight": "bold", "marginTop": "xs"},
        {"type": "text", "text": f"💥 實體物理傷害總增幅：+{total_atk} 點", "size": "xs", "color": "#FF9500", "margin": "xs"}
    ]
    
    if forge_bonus > 0:
        slot_contents.append({"type": "text", "text": f"   ↳ (其中內含工坊神匠覺醒：+{forge_bonus} 點)", "size": "xs", "color": "#FFCC00"})
        
    slot_contents.append({"type": "text", "text": f"📖 兵器神話：{w_info['desc']}", "size": "xs", "color": "#8E8E93", "margin": "xs", "wrap": True})
    
    contents = [
        {"type": "text", "text": "🛡️ 勇者神聖裝備欄面板", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"},
        {
            "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
            "contents": slot_contents
        }
    ]
    
    from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 我的背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="⚒️ 鍛造工坊", text="工坊")),
        QuickReplyItem(action=MessageAction(label="🏃 返回世界尋怪", text="尋怪"))
    ]
    qr_object = QuickReply(items=quick_items)
    
    if current_weapon != "赤手空拳":
        contents.append({"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "marginTop": "sm", "action": {"type": "message", "label": "❌ 卸下裝備放回背包", "text": "脫下裝備"}})
        
    return {"flex": {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}, "quick_reply": qr_object}

def execute_unequip_weapon(p):
    """卸下當前主手裝備放回備用收藏庫"""
    current_weapon = p.get("weapon", "赤手空拳")
    if current_weapon == "赤手空拳": 
        return "❌ 脫除失敗！你目前本來就赤手空拳。"
        
    # ⚡ 卸下武器時，同步打包成獨立非堆疊個體，高效率退回背包
    equipment_system.add_to_weapon_inventory_individual(p, current_weapon, slot_name="武器")
    p["weapon"] = "赤手空拳"
    p["forge_weapon_bonus"] = 0 
    db_core.save_player(p)
    return f"❌ 🛡️ 【裝備卸下成功】放回背包 ❌\n─────────────────\n你成功將手持的神兵利器 ── ⚔️【{current_weapon}】安全解下！已完整存入您的武器背包欄！"
