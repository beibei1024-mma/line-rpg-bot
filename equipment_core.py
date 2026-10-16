# equipment_core.py - 皇家多維度裝備與隨機詞綴核心大腦 v4.0 (全身14欄位屬性即時解析版)

import random
import weapons

# 1. ⚜️ 裝備基礎範本庫 (包含新手防具與黑市基礎裝備)
BASE_TEMPLATES = {
    "武器": {
        "鐵劍": {"atk": 15, "def": 0, "mdef": 0, "price": 100, "desc": "制式鐵劍"},
        "長弓": {"atk": 22, "def": 0, "mdef": 0, "price": 250, "desc": "精準長弓"},
        "法杖": {"atk": 30, "def": 0, "mdef": 8, "price": 500, "desc": "導魔法杖"}
    },
    "頭盔": {
        "冒險者頭巾": {"atk": 0, "def": 2, "mdef": 1, "price": 30, "desc": "新手布頭巾"},
        "皮帽": {"atk": 0, "def": 6, "mdef": 4, "price": 80, "desc": "輕便皮帽"},
        "鐵盔": {"atk": 0, "def": 15, "mdef": 3, "price": 200, "desc": "精鋼重盔"}
    },
    "鎧甲": {
        "冒險者皮甲": {"atk": 0, "def": 5, "mdef": 2, "price": 50, "desc": "新手輕皮甲"},
        "布袍": {"atk": 0, "def": 8, "mdef": 18, "price": 150, "desc": "法術布袍"},
        "鎖子甲": {"atk": 0, "def": 28, "mdef": 6, "price": 450, "desc": "防禦鎖子甲"}
    },
    "下褲": {
        "冒險者布長褲": {"atk": 0, "def": 3, "mdef": 2, "price": 40, "desc": "新手布長褲"}
    },
    "護手": {
        "護腕": {"atk": 5, "def": 8, "mdef": 4, "price": 100, "desc": "戰鬥護腕"}
    },
    "鞋子": {
        "冒險者草鞋": {"atk": 0, "def": 2, "mdef": 1, "price": 20, "desc": "新手草鞋"},
        "皮靴": {"atk": 0, "def": 10, "mdef": 6, "price": 120, "desc": "遊俠皮靴"}
    },
    "飾品": {
        "古銅戒指": {"atk": 12, "def": 3, "mdef": 10, "price": 300, "desc": "附魔戒指"}
    }
}

# 2. 🌈 裝備品質階級與基礎數值乘算係數
RARITY_CONFIG = {
    "⭐普通": {"multiplier": 1.0, "color": "#8E8E93", "affix_count": 0},
    "🔷魔法": {"multiplier": 1.4, "color": "#34AADC", "affix_count": 1},
    "🌟稀有": {"multiplier": 2.0, "color": "#4CD964", "affix_count": 2},
    "🔥史詩": {"multiplier": 3.2, "color": "#FF9500", "affix_count": 3},
    "👑遠古神話": {"multiplier": 6.5, "color": "#FF3B30", "affix_count": 4}
}

# 3. ✍️ 隨機屬性副詞綴池
AFFIX_POOL = [
    {"name": "鋒利的", "stat": "strength", "val": 6, "min": 3, "max": 8, "desc": "力量"},
    {"name": "疾風的", "stat": "agility", "val": 5, "min": 2, "max": 7, "desc": "敏捷"},
    {"name": "深邃的", "stat": "intelligence", "val": 7, "min": 4, "max": 10, "desc": "智力"},
    {"name": "不壞的", "stat": "vitality", "val": 8, "min": 5, "max": 12, "desc": "體力"},
    {"name": "至運的", "stat": "luck", "val": 5, "min": 2, "max": 6, "desc": "幸運"},
    {"name": "神聖的", "stat": "sprit", "val": 6, "min": 3, "max": 9, "desc": "精神"}
]

ALL_SLOTS_FIELDS = [
    ("武器", "weapon"), ("頭盔", "helmet"), ("上衣", "armor"), ("下褲", "pants"),
    ("鞋子", "shoes"), ("項鍊", "necklace"), ("戒指1", "ring1"), ("戒指2", "ring2"),
    ("手環", "bracelet"), ("副手", "sub_hand"), ("徽章", "badge"),
    ("付費1", "cash_item1"), ("付費2", "cash_item2"), ("付費3", "cash_item3")
]

def generate_random_equipment(slot, base_name, forced_rarity=None):
    """🎲 隨機洗鍊出一件具備暗黑風格的動態裝備封包"""
    if slot not in BASE_TEMPLATES or base_name not in BASE_TEMPLATES[slot]:
        slot, base_name = "武器", "鐵劍"

    base_stat = BASE_TEMPLATES[slot][base_name]
    rarity = forced_rarity if forced_rarity else random.choices(
        list(RARITY_CONFIG.keys()), weights=[50, 30, 14, 5, 1], k=1
    )[0]

    r_cfg = RARITY_CONFIG[rarity]
    mult = r_cfg["multiplier"]

    final_atk = int(base_stat["atk"] * mult)
    final_def = int(base_stat["def"] * mult)
    final_mdef = int(base_stat["mdef"] * mult)

    chosen_affixes = random.sample(AFFIX_POOL, k=r_cfg["affix_count"])
    item_affixes = {}
    prefix_name = ""

    for aff in chosen_affixes:
        roll_val = int(aff["val"] * mult)
        item_affixes[aff["stat"]] = item_affixes.get(aff["stat"], 0) + roll_val
        prefix_name += f"{aff['name']}"

    final_title = f"{rarity} {prefix_name}{base_name}"
    final_price = int(base_stat["price"] * mult * (1 + len(chosen_affixes) * 0.5))
    item_id = f"eq_{slot[:2]}_{random.randint(100000, 999999)}"

    return {
        "id": item_id, "name": final_title, "slot": slot, "base_type": base_name,
        "rarity": rarity, "atk": final_atk, "def": final_def, "mdef": final_mdef,
        "affixes": item_affixes, "price": final_price, "desc": base_stat["desc"]
    }

def parse_equipment_stats(eq_name):
    """🔍 根據裝備名稱（含品質與詞綴）逆向解析出完整物傷、物防、魔防與六維加成"""
    res = {
        "atk": 0, "def": 0, "mdef": 0, "price": 50,
        "strength": 0, "agility": 0, "intelligence": 0, "vitality": 0, "luck": 0, "sprit": 0,
        "summary": ""
    }
    if not eq_name or eq_name in ("無", "赤手空拳"):
        return res

    # 1. 判定品質倍率
    mult = 1.0
    for r_name, r_info in RARITY_CONFIG.items():
        if r_name in eq_name:
            mult = r_info["multiplier"]
            break

    # 2. 檢查是否為 weapons.py 中的神兵武器
    pure_w = weapons.get_pure_weapon_name(eq_name)
    for aff in AFFIX_POOL:
        pure_w = pure_w.replace(aff["name"], "")
    pure_w = pure_w.strip()

    if pure_w in weapons.SHOP_WEAPONS and pure_w != "赤手空拳":
        res["atk"] = weapons.get_weapon_atk(eq_name)
        res["price"] = max(50, int(weapons.SHOP_WEAPONS[pure_w].get("price", 100) * 0.5))

    # 3. 檢查是否為 BASE_TEMPLATES 中的基礎武器/防具/飾品
    for slot_cat, items_dict in BASE_TEMPLATES.items():
        for b_name, b_stat in items_dict.items():
            if b_name in pure_w or b_name in eq_name:
                if res["atk"] == 0:
                    res["atk"] = int(b_stat["atk"] * mult)
                res["def"] = int(b_stat["def"] * mult)
                res["mdef"] = int(b_stat["mdef"] * mult)
                res["price"] = max(20, int(b_stat["price"] * mult * 0.5))
                break

    # 4. 解析隨機詞綴加成 (鋒利的/疾風的/深邃的/不壞的/至運的/神聖的)
    affix_texts = []
    for aff in AFFIX_POOL:
        if aff["name"] in eq_name:
            bonus_val = max(2, int(aff["val"] * mult))
            res[aff["stat"]] += bonus_val
            affix_texts.append(f"{aff['desc']}+{bonus_val}")

    # 5. 組裝精簡素質摘要字串 (供背包與裝備欄直接顯示)
    parts = []
    if res["atk"] > 0: parts.append(f"💥物傷+{res['atk']}")
    if res["def"] > 0: parts.append(f"🧱物防+{res['def']}")
    if res["mdef"] > 0: parts.append(f"🌀魔防+{res['mdef']}")
    parts.extend(affix_texts)

    res["summary"] = " ".join(parts) if parts else "🛡️ 基礎防具"
    return res

def get_player_total_equipment_bonus(p):
    """🛡️ 統計玩家身上穿戴的 14 個欄位所有裝備總加成"""
    totals = {
        "atk": int(p.get("forge_weapon_bonus", 0)),
        "def": 0, "mdef": 0,
        "strength": 0, "agility": 0, "intelligence": 0, "vitality": 0, "luck": 0, "sprit": 0
    }
    for _, field in ALL_SLOTS_FIELDS:
        eq_name = p.get(field, "無")
        if eq_name and eq_name not in ("無", "赤手空拳"):
            st = parse_equipment_stats(eq_name)
            for k in totals.keys():
                totals[k] += st.get(k, 0)
    return totals
