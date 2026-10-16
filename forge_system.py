# forge_system.py - 皇家禁忌工坊與全身14欄位動態裝備面板 v7.0 (支援單一卸下與一鍵全部脫下)

import json
import random
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction
import db_core
import weapons
import equipment_core
import equipment_system

FORGE_RECIPES = {
    "新手鐵短劍": {"slot": "武器", "base": "鐵劍", "mat": "史萊姆黏液", "mat_qty": 3},
    "微光木藤弓": {"slot": "武器", "base": "長弓", "mat": "強韌蜘蛛絲", "mat_qty": 5},
    "見習魔法杖": {"slot": "武器", "base": "法杖", "mat": "不融冰塊", "mat_qty": 5},
    "黑曜熔岩大劍": {"slot": "武器", "base": "鐵劍", "mat": "熔岩核心", "mat_qty": 8}
}

def add_to_weapon_inventory(p, item_name):
    equipment_system.add_to_weapon_inventory_individual(p, item_name, slot_name="武器")

def get_forge_menu(p):
    contents = [
        {"type": "text", "text": "⚒️ 皇家遠古鍛造熔煉工坊", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": "🪙 勇者流動金幣：🪙 " + str(p['gold']) + " 金幣", "size": "xs", "color": "#FFCC00", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]

    for name, r in FORGE_RECIPES.items():
        if name in weapons.SHOP_WEAPONS:
            w_info = weapons.SHOP_WEAPONS[name]
            contents.append({
                "type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
                "contents": [
                    {"type": "text", "text": "📜 圖紙：【" + name + "】(" + r['slot'] + ")", "size": "xs", "color": "#FF9500", "weight": "bold"},
                    {"type": "text", "text": "💰 打造消耗：🪙 " + str(w_info['price']) + " 金幣", "size": "xxs", "color": "#FFCC00", "margin": "xs"},
                    {"type": "text", "text": "🛡️ 所需材料：🛠️ " + r['mat'] + " x" + str(r['mat_qty']), "size": "xxs", "color": "#34AADC"},
                    {"type": "text", "text": "📖 描述：" + w_info['desc'], "size": "xxs", "color": "#8E8E93", "margin": "xs"},
                    {
                        "type": "button", "style": "primary", "color": "#FF9500", "height": "sm", "marginTop": "xs",
                        "action": {"type": "message", "label": "⚒️ 投入素材開始熔煉", "text": "鍛造 " + name}
                    }
                ]
            })

    flex_bubble = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "contents": contents}
    }
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="🛡️ 裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="🚪 出城", text="世界地圖")),
        QuickReplyItem(action=MessageAction(label="🦅 回城", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items).to_dict()}

def execute_forge_weapon(p, cmd_str):
    blueprint = cmd_str.replace("鍛造", "").replace(" ", "").strip()
    if blueprint not in FORGE_RECIPES or blueprint not in weapons.SHOP_WEAPONS:
        return "❌ 打造失敗！遠古工坊中沒有記載該裝備的神聖圖紙配方。"

    recipe = FORGE_RECIPES[blueprint]
    w_config = weapons.SHOP_WEAPONS[blueprint]

    if p["gold"] < w_config["price"]:
        return "❌ 打造失敗！🪙 資金不足！\n打造【" + blueprint + "】需要 " + str(w_config['price']) + " 金幣，你目前只有 " + str(p['gold']) + " 金幣。"

    inv = p.get("inventory", {})
    if isinstance(inv, str):
        try:
            inv = json.loads(inv)
        except Exception:
            inv = {"items": {}, "materials": {}}

    materials_dict = inv.get("materials", {})
    current_mat_qty = materials_dict.get(recipe["mat"], 0)
    if current_mat_qty < recipe["mat_qty"]:
        return "❌ 打造失敗！🛠️ 鍛造素材不足！\n你需要【" + recipe['mat'] + "】x" + str(recipe['mat_qty']) + "，但你目前只有 " + str(current_mat_qty) + " 個。"

    p["gold"] -= w_config["price"]
    materials_dict[recipe["mat"]] = current_mat_qty - recipe["mat_qty"]
    if materials_dict[recipe["mat"]] <= 0:
        del materials_dict[recipe["mat"]]
    inv["materials"] = materials_dict
    p["inventory"] = inv

    rolled_rarity = random.choices(
        ["⭐普通", "🔷魔法", "🌟稀有", "🔥史詩", "👑遠古神話"],
        weights=[0.50, 0.25, 0.15, 0.07, 0.03], k=1
    )[0]

    final_eq_name = rolled_rarity + " " + blueprint
    actual_atk = weapons.get_weapon_atk(final_eq_name)

    equipment_system.add_to_weapon_inventory_individual(p, final_eq_name, slot_name=recipe["slot"])
    db_core.save_player(p)

    return (
        "⚒️ 🔥 【 工坊熔煉天啟大成功 】 🔥 ⚒️\n"
        "───────────────────\n"
        "鐵匠揮舞重錘，熔岩鐵水四濺！你投入的素材在法陣中完美凝聚！\n\n"
        "🔨 成功打造：" + final_eq_name + " (" + recipe['slot'] + ")！\n"
        "💥 武器品質物傷：+" + str(actual_atk) + "\n"
        "✨ 品質天啟：成功洗鍊出 ── 【" + rolled_rarity + "】階級！\n"
        "📦 存放去向：神兵利器已全自動以【獨立個體】送入【我的背包】，請開啟背包手動穿戴上身！"
    )

def get_equipment_card(p):
    """🛡️ 生成全身 14 欄位神聖裝備欄面板，並支援單一卸下與全部卸下"""
    eq_totals = equipment_core.get_player_total_equipment_bonus(p)
    summary_header = "💥總物傷+" + str(eq_totals['atk']) + " | 🧱總物防+" + str(eq_totals['def']) + " | 🌀總魔防+" + str(eq_totals['mdef'])

    contents = [
        {"type": "text", "text": "🛡️ 勇者全身神聖裝備面板", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": summary_header, "size": "xxs", "color": "#FF9500", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]

    display_slots = [
        ("⚔️ 武器", "weapon"), ("🪖 頭盔", "helmet"), ("🥋 上衣", "armor"),
        ("👖 下褲", "pants"), ("👢 鞋子", "shoes"), ("📿 項鍊", "necklace"),
        ("💍 戒指1", "ring1"), ("💍 戒指2", "ring2"), ("⌚ 手環", "bracelet"),
        ("🛡️ 副手", "sub_hand"), ("🎖️ 徽章", "badge")
    ]

    for label, field in display_slots:
        eq_name = p.get(field, "無")
        if not eq_name or eq_name in ("無", "赤手空拳"):
            eq_display = "赤手空拳" if field == "weapon" else "（未穿戴）"
            color = "#8E8E93"
            stat_str = ""
            btn_action = None
        else:
            eq_display = eq_name
            color = "#4CD964"
            st = equipment_core.parse_equipment_stats(eq_name)
            stat_str = " (" + st['summary'] + ")"
            # 建立單一卸下按鈕指令（例如：脫下 頭盔、脫下 武器）
            slot_key_name = label.replace("⚔️ ", "").replace("🪖 ", "").replace("🥋 ", "").replace("👖 ", "").replace("👢 ", "").replace("📿 ", "").replace("💍 ", "").replace("⌚ ", "").replace("🛡️ ", "").replace("🎖️ ", "").strip()
            btn_action = {"type": "message", "label": "卸下", "text": "脫下 " + slot_key_name}

        row_box = {
            "type": "box", "layout": "horizontal", "margin": "xs", "backgroundColor": "#2C2C2E", "paddingAll": "xs", "cornerRadius": "sm", "alignItems": "center", "spacing": "sm",
            "contents": [
                {"type": "text", "text": label, "size": "xs", "color": "#007AFF", "weight": "bold", "flex": 2},
                {"type": "text", "text": eq_display + stat_str, "size": "xs", "color": color, "flex": 5, "wrap": True}
            ]
        }
        if btn_action:
            row_box["contents"].append({
                "type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "flex": 2,
                "action": btn_action
            })
        contents.append(row_box)

    # 一鍵全部脫下按鈕
    contents.append({
        "type": "button", "style": "primary", "color": "#8E8E93", "height": "sm", "marginTop": "md",
        "action": {"type": "message", "label": "❌ 一鍵全部卸下放回背包", "text": "全部脫下"}
    })

    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="👤 狀態", text="我的狀態")),
        QuickReplyItem(action=MessageAction(label="⚒️ 工坊", text="工坊")),
        QuickReplyItem(action=MessageAction(label="🦅 回城", text="回城"))
    ]
    flex_bubble = {
        "type": "bubble",
        "size": "mega",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}},
        "body": {"type": "box", "layout": "vertical", "contents": contents}
    }
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items).to_dict()}

def execute_unequip_item(p, user_msg):
    """🛠️ 支援單一部位卸下與全部卸下的高階腦"""
    clean_cmd = user_msg.replace("脫下", "").replace("卸下", "").replace(" ", "").strip()
    
    if clean_cmd in ("全部", "所有", "裝備"):
        # 全部卸下
        slot_fields = [
            "weapon", "helmet", "armor", "pants", "shoes", "necklace",
            "ring1", "ring2", "bracelet", "sub_hand", "badge",
            "cash_item1", "cash_item2", "cash_item3"
        ]
        unequipped_count = 0
        for field in slot_fields:
            eq_name = p.get(field, "無")
            if eq_name and eq_name not in ("無", "赤手空拳"):
                slot_name = equipment_system.get_equipment_slot_by_name(eq_name) or "武器"
                equipment_system.add_to_weapon_inventory_individual(p, eq_name, slot_name=slot_name)
                if field == "weapon":
                    p["weapon"] = "赤手空拳"
                    p["forge_weapon_bonus"] = 0
                else:
                    p[field] = "無"
                unequipped_count += 1

        db_core.save_player(p)
        if unequipped_count == 0:
            return "💡 您目前身上沒有穿戴任何可卸下的裝備！"
        return "❌ 🛡️ 【一鍵全部卸下成功】\n─────────────────\n您已將身上所有 " + str(unequipped_count) + " 件裝備安全解下，全部原封不動存入您的背包！"

    # 單一部位卸下映射
    slot_map = {
        "武器": "weapon", "頭盔": "helmet", "上衣": "armor", "下褲": "pants",
        "鞋子": "shoes", "項鍊": "necklace", "戒指1": "ring1", "戒指2": "ring2",
        "手環": "bracelet", "副手": "sub_hand", "徽章": "badge"
    }

    target_field = slot_map.get(clean_cmd)
    if not target_field:
        return "❌ 卸下失敗！找不到【" + clean_cmd + "】這個裝備部位。範例：輸入【脫下 頭盔】或點擊面板按鈕。"

    current_eq = p.get(target_field, "無" if target_field != "weapon" else "赤手空拳")
    if current_eq in ("無", "赤手空拳"):
        return "❌ 卸下失敗！您的【" + clean_cmd + "】部位目前本來就是空的。"

    slot_name = equipment_system.get_equipment_slot_by_name(current_eq) or clean_cmd
    equipment_system.add_to_weapon_inventory_individual(p, current_eq, slot_name=slot_name)

    if target_field == "weapon":
        p["weapon"] = "赤手空拳"
        p["forge_weapon_bonus"] = 0
    else:
        p[target_field] = "無"

    db_core.save_player(p)
    return "❌ 🛡️ 【裝備卸下成功】\n─────────────────\n您成功將【" + clean_cmd + "】部位的 ── ⚔️【" + current_eq + "】安全解下！已完整存入您的背包！"

def execute_unequip_weapon(p):
    return execute_unequip_item(p, "脫下 武器")
# === END OF FILE ===
