# forge_system.py - 皇家禁忌工坊與隨機熔煉核心大腦 v5.0 (數據完全同步版)

import json
import random
import db_core
import equipment_core
import player_equipment
import weapons  # ✨【核心數據鏈接】直連神兵利器數據庫，消除打造不匹配Bug

# 📜 皇家遠古手工鍛造圖紙配方庫 (材料消耗對齊您在 monsters.py 定義的野外素材)
# 請將 forge_system.py 的圖紙字典名稱同步修改對齊木字旁的「杖」：
FORGE_RECIPES = {
    "新手鐵短劍": {"slot": "武器", "base": "鐵劍", "mat": "史萊姆黏液", "mat_qty": 3},
    "微光木藤弓": {"slot": "武器", "base": "長弓", "mat": "強韌蜘蛛絲", "mat_qty": 5},
    "見習魔法杖": {"slot": "武器", "base": "法杖", "mat": "不融冰塊", "mat_qty": 5}, # ✨【修正點：仗 ➡️ 杖】
    "黑曜熔岩大劍": {"slot": "武器", "base": "鐵劍", "mat": "熔岩核心", "mat_qty": 8},
    # ... 其餘配方保持不變 ...
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
    """⚒️ 核心熔煉大腦：自動對齊 weapons.py 價格與物傷，博弈概率打造裝備"""
    blueprint = cmd_str.replace("鍛造", "").replace(" ", "").strip()
    if blueprint not in FORGE_RECIPES or blueprint not in weapons.SHOP_WEAPONS:
        return "❌ 打造失敗！遠古工坊中沒有記載該裝備的神聖圖紙配方。"
        
    recipe = FORGE_RECIPES[blueprint]
    w_config = weapons.SHOP_WEAPONS[blueprint] # ✨【動態匹配連通】直接提取您的資料庫定價與物傷
    
    # 1. 檢查金幣是否足夠 (依照 weapons.py 定價)
    if p["gold"] < w_config["price"]:
        return f"❌ 打造失敗！🪙 資金不足！打造【{blueprint}】需要 {w_config['price']} 金幣，你目前只有 {p['gold']} 金幣。"
        
    # 2. 檢查背包素材數量
    inv = p.get("inventory", {})
    if isinstance(inv, str):
        try: inv = json.loads(inv)
        except: inv = {}
        
    current_mat_qty = inv.get(recipe["mat"], 0)
    if current_mat_qty < recipe["mat_qty"]:
        return f"❌ 打造失敗！🛠️ 鍛造素材不足！你需要【{recipe['mat']}】x{recipe['mat_qty']}，但你目前只有 {current_mat_qty} 個。"
        
    # 3. 扣除代價
    p["gold"] -= w_config["price"]
    inv[recipe["mat"]] = current_mat_qty - recipe["mat_qty"]
    p["inventory"] = json.dumps(inv, ensure_ascii=False)
    
    # 4. 手工打造隨機洗鍊品質 (有 10% 概率爆出史詩或遠古神話！)
    rolled_rarity = random.choices(
        ["⭐普通", "🔷魔法", "🌟稀有", "🔥史詩", "👑遠古神話"],
        weights=[0.50, 0.25, 0.15, 0.07, 0.03], k=1
    )[0]
    
    # 5. 生成對應部位的暗黑屬性裝備封包
    new_eq = equipment_core.generate_random_equipment(recipe["slot"], recipe["base"], forced_rarity=rolled_rarity)
    new_eq["name"] = f"{rolled_rarity} {blueprint}" # 重新格式化成：品質 + 手工神兵名
    new_eq["atk"] = w_config["atk_bonus"]          # ✨ 傷害 100% 繼承匹配您設定的 weapons.py 白字物傷
    new_eq["price"] = w_config["price"]            # ✨ 價值 100% 繼承匹配您設定的 weapons.py 價格
    
    # 6. 安全塞入新版多部位備用包
    player_equipment._add_to_equipment_inventory(p, new_eq)
    db_core.save_player(p)
    
    return f"⚒️ 🔥 【 工坊熔煉天啟大成功 】 🔥 ⚒️\n───────────────────\n鐵匠揮舞重錘，熔岩鐵水四濺！你投入的素材在法陣中完美凝聚！\n\n🔨 成功打造：{new_eq['name']} ({recipe['slot']})！\n💥 武器基礎物傷：+{new_eq['atk']}\n✨ 品質天啟：成功洗鍊出 ── 【{rolled_rarity}】階級！\n📦 存放去向：神兵利器已全自動送入【我的裝備包】，請輸入【裝備包】手動穿戴上身！"
