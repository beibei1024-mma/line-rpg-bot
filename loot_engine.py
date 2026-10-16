# loot_engine.py - 皇家戰利品與擊殺結算獨立核心 (金幣、經驗、掉寶、首殺廣播)

import random
import db_core
import bag
import weapons
import forge_system
import notice_system
import jobs_system

def process_monster_defeat(p, enemy, configuration):
    """🎁 處理怪物擊殺後的金幣、經驗、掉寶與等級突破判定"""
    log = ""
    
    # 1. 金幣計算
    gold_mod = p.get("map_gold_mod", 1.0)
    gold_data = enemy.get("gold_range", (10, 50))
    if isinstance(gold_data, (tuple, list)) and len(gold_data) >= 2:
        min_gold, max_gold = int(gold_data[0]), int(gold_data[1])
    else:
        min_gold, max_gold = int(gold_data), int(gold_data)

    final_gold = int(random.randint(min_gold, max_gold) * gold_mod)
    p["gold"] = p.get("gold", 0) + final_gold
    
    # 2. 經驗值計算
    exp_gained = enemy.get("exp", 20)
    p["exp"] = p.get("exp", 0) + exp_gained
    
    # 3. 戰後調息回覆 25 MP
    level = p.get("level", 1)
    men_val = p.get("sprit", 10)
    max_mp_val = 50 + (men_val * 4) + (level * 5)
    p["mp"] = min(max_mp_val, p.get("mp", max_mp_val) + 25)

    log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{exp_gained}！\n🔷 戰鬥結束調息，魔力恢復 +25 點。\n"

    # 4. 5% 機率掉落區域專屬神兵
    if random.random() < 0.05:
        current_loc = p.get("current_map", "新手村")
        matched_weapons = [
            w_name for w_name in weapons.SHOP_WEAPONS.keys() 
            if w_name not in ("赤手空拳", "GM滅世制裁之劍") and ((current_loc[:2] in w_name) or (current_loc == "新手村" and "新手" in w_name))
        ]
        if matched_weapons:
            drop_w = random.choice(matched_weapons)
            forge_system.add_to_weapon_inventory(p, drop_w)
            log += f"💎 🔥 🗺️ 【神裝降臨・直接入庫】 🗺️ 🔥 💎\n你擊敗魔物搜刮戰場，驚喜搜刮到了該區域的專屬神兵 ── ⚔️【{drop_w}】！\n📦 存放去向：寶物已為您送入【我的背包】裝備收藏庫，快去開包更換吧！\n"

    # 5. 世界 Boss / 巨龍首殺廣播判定
    raw_monster_name = enemy.get("name", "野外魔獸")
    if "地獄紅蓮巨龍" in raw_monster_name or "邪神克蘇魯" in raw_monster_name or enemy.get("is_world_boss"):
        notice_system.push_world_boss_broadcast(raw_monster_name, configuration)
        log += "\n👑 🏆 諸神見證！首殺捷報已推播給全服所有玩家！"

    p["enemy"] = None

    # 6. 50% 機率掉落怪物珍稀原料
    if random.random() < 0.50 and enemy.get("drop_item"):
        bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
        log += f"💎 【幸運掉寶】包包入庫！素材：【{enemy['drop_item']}】x1！\n"

    # 7. 檢查等級突破與轉職卡關
    from jobs import JOBS_DATA
    current_job = p.get("job", "初心者")
    job_mod = JOBS_DATA.get(current_job, JOBS_DATA["初心者"])
    is_job_locked = jobs_system.check_level_lock(p, job_mod)

    # 8. 戰鬥勝利結算時精確回滿血量與魔力上限
    eq_bonus = equipment_core.get_player_total_equipment_bonus(p) if 'equipment_core' in globals() else {"vitality": 0, "sprit": 0}
    vit_val = int((p.get("vitality", 10) + eq_bonus.get("vitality", 0)) * job_mod["vit_mod"])
    p["hp"] = 100 + (vit_val * 5) + (p["level"] * 15)
    p["mp"] = 50 + (int((p.get("sprit", 10) + eq_bonus.get("sprit", 0)) * job_mod["men_mod"]) * 4) + (p["level"] * 5)

    db_core.save_player(p)
    return log, is_job_locked
# === END OF FILE ===
