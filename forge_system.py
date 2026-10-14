# forge_system.py - 皇家禁忌工坊與隨機熔煉核心大腦 v5.6 (完整相容防爆版)

import json
import random
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction
import db_core
import weapons
import equipment_system

FORGE_RECIPES = {
    "新手鐵短劍": {"slot": "武器", "base": "鐵劍", "mat": "史萊姆黏液", "mat_qty": 3},
    "微光木藤弓": {"slot": "武器", "base": "長弓", "mat": "強韌蜘蛛絲", "mat_qty": 5},
    "見習魔法杖": {"slot": "武器", "base": "法杖", "mat": "不融冰塊", "mat_qty": 5},
    "黑曜熔岩大劍": {"slot": "武器", "base": "鐵劍", "mat": "熔岩核心", "mat_qty": 8}
}

def add_to_weapon_inventory(p, item_name):
    """⚡ 相容轉接器：供 shop.py 與 battle_core.py 直接呼叫"""
    equipment_system.add_to_weapon_inventory_individual(p, item_name, slot_name="武器")

def get_forge_menu(p):
    """🛠️ 生成工坊手工鍛造藍圖 Flex 展售選單（回傳標準 flex + quick_reply 結構）"""
    contents = [
        {"type": "text", "text": "⚒️ 皇家遠古鍛造熔煉工坊", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": f"🪙 勇者流動金幣：🪙 {p['gold']} 金幣", "size": "xs", "color": "#FFCC00", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]

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

    flex_bubble = {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 我的背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="🛡️ 我的裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="🚪 出城冒險", text="世界地圖")),
        QuickReplyItem(action=MessageAction(label="🦅 返回主城", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items).to_dict()}

def execute_forge_weapon(p, cmd_str):
    """⚒️ 核心熔煉大腦：洗鍊高品質裝備，並以【完全不堆疊】的獨立個體塞入新包包"""
    blueprint = cmd_str.replace("鍛造", "").replace(" ", "").strip()

    if blueprint not in FORGE_RECIPES or blueprint not in weapons.SHOP_WEAPONS:
        return "❌ 打造失敗！遠古工坊中沒有記載該裝備的神聖圖紙配方。"

    recipe = FORGE_RECIPES[blueprint]
    w_config = weapons.SHOP_WEAPONS[blueprint]

    if p["gold"] < w_config["price"]:
        return f"❌ 打造失敗！🪙 資金不足！打造【{blueprint}】需要 {w_config['price']} 金幣，你目前只有 {p['gold']} 金幣。"

    inv = p.get("inventory", {})
    if isinstance(inv, str):
        try:
            inv = json.loads(inv)
        except Exception:
            inv = {"items": {}, "materials": {}}

    materials_dict = inv.get("materials", {})
    current_mat_qty = materials_dict.get(recipe["mat"], 0)

    if current_mat_qty < recipe["mat_qty"]:
        return f"❌ 打造失敗！🛠️ 鍛造素材不足！你需要【{recipe['mat']}】x{recipe['mat_qty']}，但你目前只有 {current_mat_qty} 個。"

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

    final_eq_name = f"{rolled_rarity} {blueprint}"
    actual_atk = weapons.get_weapon_atk(final_eq_name)

    equipment_system.add_to_weapon_inventory_individual(p, final_eq_name, slot_name=recipe["slot"])
    db_core.save_player(p)

    return (
        f"⚒️ 🔥 【 工坊熔煉天啟大成功 】 🔥 ⚒️\n"
        f"───────────────────\n"
        f"鐵匠揮舞重錘，熔岩鐵水四濺！你投入的素材在法陣中完美凝聚！\n\n"
        f"🔨 成功打造：{final_eq_name} ({recipe['slot']})！\n"
        f"💥 武器品質物傷：+{actual_atk}\n"
        f"✨ 品質天啟：成功洗鍊出 ── 【{rolled_rarity}】階級！\n"
        f"📦 存放去向：神兵利器已全自動以【獨立個體】送入【我的背包】，請開啟背包手動穿戴上身！"
    )

def get_equipment_card(p):
    """🛡️ 生成勇者神聖裝備欄面板，直連當前穿戴武器屬性"""
    current_weapon = p.get("weapon", "赤手空拳")
    pure_w_name = weapons.get_pure_weapon_name(current_weapon)
    w_info = weapons.SHOP_WEAPONS.get(pure_w_name, {"atk_bonus": 0, "desc": "赤手空拳，毫無攻擊力加成。"})
    forge_bonus = int(p.get("forge_weapon_bonus", 0))
    total_atk = weapons.get_weapon_atk(current_weapon) + forge_bonus

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

    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 我的背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="⚒️ 鍛造工坊", text="工坊")),
        QuickReplyItem(action=MessageAction(label="🏃 返回世界尋怪", text="尋怪"))
    ]
    qr_dict = QuickReply(items=quick_items).to_dict()

    if current_weapon != "赤手空拳":
        contents.append({
            "type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "marginTop": "sm",
            "action": {"type": "message", "label": "❌ 卸下裝備放回背包", "text": "脫下裝備"}
        })

    return {
        "flex": {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}},
        "quick_reply": qr_dict
    }

def execute_unequip_weapon(p):
    """卸下當前主手裝備放回備用收藏庫"""
    current_weapon = p.get("weapon", "赤手空拳")
    if current_weapon == "赤手空拳":
        return "❌ 脫除失敗！你目前本來就赤手空拳。"

    equipment_system.add_to_weapon_inventory_individual(p, current_weapon, slot_name="武器")
    p["weapon"] = "赤手空拳"
    p["forge_weapon_bonus"] = 0
    db_core.save_player(p)

    return f"❌ 🛡️ 【裝備卸下成功】放回背包 ❌\n─────────────────\n你成功將手持的神兵利器 ── ⚔️【{current_weapon}】安全解下！已完整存入您的武器背包欄！"
