# battle_core.py - 純粹戰鬥計算機 v3.2 (勝利自動回滿血魔版)

import random
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, ApiClient
from linebot.models import TextSendMessage
import db_core
import monsters
import weapons
import bag
import jobs
import jobs_system
import notice_system
import forge_system
import challenge_system
import skills_calculator
import equipment_core

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    """【純粹戰鬥計算機 v3.2 技能樹解耦與世界Boss戰功完全體】"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    eq_bonus = equipment_core.get_player_total_equipment_bonus(p)

    base_str = p.get("strength", 10 + (level * 3)) + eq_bonus["strength"]
    base_agi = p.get("agility", 10 + (level * 2)) + eq_bonus["agility"]
    base_int = p.get("intelligence", 10 + (level * 2)) + eq_bonus["intelligence"]
    base_vit = p.get("vitality", 10 + (level * 3)) + eq_bonus["vitality"]
    base_luk = p.get("luck", 10 + (level * 1)) + eq_bonus["luck"]
    base_men = p.get("sprit", 10 + (level * 2)) + eq_bonus["sprit"]

    str_val = int(base_str * job_mod["str_mod"])
    agi_val = int(base_agi * job_mod["agi_mod"])
    int_val = int(base_int * job_mod["int_mod"])
    vit_val = int(base_vit * job_mod["vit_mod"])
    luk_val = int(base_luk * job_mod["luk_mod"])
    men_val = int(base_men * job_mod["men_mod"])

    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    if p.get("mp") is None:
        p["mp"] = calculated_max_mp

    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.get_weapon_atk(current_weapon) + int(p.get("forge_weapon_bonus", 0))

    # 1. 轉職卡關防呆
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ("攻擊", "使用技能") or user_msg.startswith("使用技能"):
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔒 【天賦界限卡關中】請先完成手動天賦轉職！\n\n" + job_notice))
            return

    # 2. 🔍 尋找怪物處理
    if user_msg in ("尋找怪物", "尋怪"):
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊底部【😇 祈求復活】按鈕。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 眼前還有怪物！請發動【攻擊】或施放職業技能！"))
            return

        current_location = p.get("current_map", "新手村")
        if current_location == "世界Boss":
            boss_hp = challenge_system.check_boss_rebirth_and_get_hp()
            random_monster = {
                "name": challenge_system.WORLD_BOSS_NAME, "hp": boss_hp, "max_hp": challenge_system.WORLD_BOSS_TOTAL_HP,
                "atk": 160, "gold_range": (1000, 5000), "exp": 5000, "skill": "👁️ 邪神神格：環境常駐【魔能潮汐】！",
                "drop_item": "舊神支配者之眼", "env": "🔮 魔能潮汐 (全服大混戰，法術增幅異常狂暴)", "is_world_boss": True
            }
        else:
            random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)

        title_log = "⚠️ 遭遇強敵！在📍【" + current_location + "】撞見了對手！\n\n📢 環境狀態：" + random_monster['env'] + "\n🔰 怪物被動：" + random_monster['skill']
        card_data = db_core.make_battle_card(title_log, p, random_monster)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "遭遇怪物", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 3. 🏃 逃跑扣罰與博弈機制
    elif user_msg == "逃跑":
        if p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 周圍沒有怪物，你不需要逃跑。"))
            return
        enemy = p["enemy"]
        if random.random() < 0.30:
            p_def = vit_val // 2
            backlash_dmg = max(1, (random.randint(1, enemy["atk"]) - p_def) * 2)
            p["hp"] = max(0, p["hp"] - backlash_dmg)
            log = "🏃 ❌ 逃跑失敗！你露出了巨大的破綻，遭到【" + enemy['name'] + "】憤怒的背後致命重擊，受到雙倍傷害 -" + str(backlash_dmg) + " 點！"
            if p["hp"] <= 0:
                p["enemy"] = None
                log += "\n💀 你受傷過重在逃跑途中陣亡了！"
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, None)
            else:
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, enemy)
        else:
            p["gold"] = max(0, p["gold"] - 10)
            p["enemy"] = None
            db_core.save_player(p)
            log = "🏃 💨 逃跑成功！你慌忙丟下了 🪙 10 金幣引開注意，狼狽地逃離了戰場！"
            card_data = db_core.make_battle_card(log, p, None)

        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "逃跑結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 4. ⚔️ 核心戰鬥公式
    elif user_msg == "攻擊" or user_msg.startswith("使用技能") or user_msg == "使用技能防禦":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法發動戰鬥（可能已陣亡或周圍沒有怪物）。"))
            return

        enemy = p["enemy"]
        log = ""
        clean_msg = user_msg.replace(" ", "").strip()
        is_defense = (clean_msg in ("使用技能防禦", "技能防禦"))
        is_skill = clean_msg.startswith("使用技能") and not is_defense
        skill_name = clean_msg.replace("使用技能", "").strip() if is_skill else ""

        p_defense_multiplier = 1.0
        total_p_dmg = 0

        if is_defense:
            p_defense_multiplier = 3.0
            log += "🛡️ 戰術防禦！你架起鋼鐵防護姿態，本回合防禦力暴增 3 倍，全神貫注準備抵擋目標的反擊！\n"
        elif is_skill:
            if skill_name not in job_mod["skills"]:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 技能錯誤！你目前職業的天賦樹中不會【" + skill_name + "】法術。"))
                return

            mp_cost = job_mod["skills"][skill_name].get("mp_cost", 0)
            safe_mp = p.get("mp", calculated_max_mp)
            if safe_mp < mp_cost:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔷 魔力枯竭！施放【" + skill_name + "】需要 " + str(mp_cost) + " 點 MP，你目前只有 " + str(safe_mp) + " 點！"))
                return

            p["mp"] = safe_mp - mp_cost
            log += "🔮 奧義發動！你消耗了 🔷 " + str(mp_cost) + " 點 MP 施放秘術 ── ⚡【" + skill_name + "】！\n"

            if skill_name in ("治癒術", "群體療癒", "淨化術", "復活預言"):
                mult = 3.5 if skill_name in ("群體療癒", "復活預言") else 2.5
                heal = int((int_val + men_val) * mult)
                old_h = p["hp"]
                p["hp"] = min(100 + (vit_val * 5) + (level * 15), p["hp"] + heal)
                log += "💖 聖光治癒！神聖恢復了生命值 +" + str(p['hp'] - old_h) + " 點！\n"
                if skill_name in ("淨化術", "復活預言"):
                    p_defense_multiplier = 2.0
                    log += "✨ 聖光護體！本回合防禦力額外提升 2 倍！\n"

            base_weapon_atk = 12 + str_val + w_bonus
            calc_res = skills_calculator.calculate_active_skill_damage(skill_name, base_weapon_atk, int_val, vit_val, str_val, agi_val, luk_val, men_val)
            total_p_dmg = calc_res["damage"]
            if calc_res["log"]:
                log += calc_res["log"].format(enemy_name=enemy["name"])
        else:
            crit_chance = min(80, 10 + (luk_val // 5)) / 100.0
            crit_dmg_mod = 1.5 + (luk_val * 0.005)
            double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0
            is_double = random.random() < double_atk_chance

            d1 = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
            if random.random() < crit_chance:
                d1 = int(d1 * crit_dmg_mod)
                log += "💥 致命爆擊！第 1 擊斬出 " + str(d1) + " 點爆擊物理傷害！\n"
            else:
                log += "⚔️ 第 1 擊普通命中，造成 " + str(d1) + " 點物理傷害！\n"
            total_p_dmg += d1

            if is_double:
                d2 = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
                if random.random() < crit_chance:
                    d2 = int(d2 * crit_dmg_mod)
                    log += "💥 致命爆擊！第 2 擊斬出 " + str(d2) + " 點爆擊物理傷害！\n"
                else:
                    log += "⚔️ 第 2 擊普通命中，造成 " + str(d2) + " 點物理傷害！\n"
                total_p_dmg += d2

        enemy["hp"] -= total_p_dmg

        # 🌋 世界 Boss 戰功即時累計
        if enemy.get("is_world_boss") and total_p_dmg > 0:
            p["world_boss_damage"] = (p.get("world_boss_damage", 0) or 0) + total_p_dmg
            log += "🌋 【世界Boss討伐戰功】累計輸出：⚔️ " + str(p['world_boss_damage']) + " 點！\n"

        # ── 5. 戰鬥大獲全勝結算 ──
        if enemy["hp"] <= 0:
            gold_mod = p.get("map_gold_mod", 1.0)
            gold_data = enemy["gold_range"]
            if isinstance(gold_data, (tuple, list)) and len(gold_data) >= 2:
                min_gold, max_gold = int(gold_data[0]), int(gold_data[1])
            else:
                min_gold, max_gold = int(gold_data), int(gold_data)

            final_gold = int(random.randint(min_gold, max_gold) * gold_mod)
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            
            log += "🎉 順利擊敗對手！獲得金幣 +" + str(final_gold) + "、經驗值 +" + str(enemy['exp']) + "！\n🔷 戰鬥結束調息，魔力完全恢復！\n"

            if random.random() < 0.05:
                current_loc = p.get("current_map", "新手村")
                matched_weapons = [w_name for w_name in weapons.SHOP_WEAPONS.keys() if w_name not in ("赤手空拳", "GM滅世制裁之劍") and ((current_loc[:2] in w_name) or (current_loc == "新手村" and "新手" in w_name))]
                if matched_weapons:
                    drop_w = random.choice(matched_weapons)
                    forge_system.add_to_weapon_inventory(p, drop_w)
                    log += "💎 🔥 🗺️ 【神裝降臨・直接入庫】 🗺️ 🔥 💎\n你擊敗魔物搜刮戰場，驚喜搜刮到了該區域的專屬神兵 ── ⚔️【" + drop_w + "】！\n📦 存放去向：寶物已為您送入【我的背包】裝備收藏庫，快去開包更換吧！\n"

            raw_monster_name = enemy["name"]
            if "地獄紅蓮巨龍" in raw_monster_name or "邪神克蘇魯" in raw_monster_name or enemy.get("is_world_boss"):
                notice_system.push_world_boss_broadcast(raw_monster_name, configuration)
                log += "\n👑 🏆 諸神見證！首殺捷報已推播給全服所有玩家！"

            p["enemy"] = None
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += "💎 【幸運掉寶】！素材：【" + enemy['drop_item'] + "】x1！\n"

            is_job_locked = jobs_system.check_level_lock(p, job_mod)
            
            # ✨ 關鍵修復：戰鬥勝利結算時，血量與魔力同步完美充滿至最新上限！
            p["hp"] = 100 + (vit_val * 5) + (p["level"] * 15)
            p["mp"] = calculated_max_mp
            
            db_core.save_player(p)

            card_data = db_core.make_battle_card(log, p, None)
            msg_payload = {
                "replyToken": event.reply_token,
                "messages": [{
                    "type": "flex",
                    "altText": "戰鬥結束",
                    "contents": card_data["flex"],
                    "quickReply": card_data["quick_reply"]
                }]
            }
            if is_job_locked:
                msg_payload["messages"].append({"type": "text", "text": "🔒 【天賦界限卡關中】\n勇者！你目前已達到了 Lv." + str(p['level']) + " 的天賦瓶頸，必須完成天賦轉職才能繼續獲取經驗！\n\n" + jobs.get_job_options_text(p)})

            with ApiClient(configuration) as api_client:
                MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        else:
            # ── 6. 怪物殘存與環境反擊 ──
            if "暴雨滂沱" in enemy.get("env", ""):
                vit_val = int(vit_val * 0.8)
            if "精神污染" in enemy.get("skill", ""):
                p["mp"] = max(0, p["mp"] - 20)
                log += "\n👁️ 🚨 邪神被動【精神污染】！魔力值被吸走 20 點！"

            p_def = int((vit_val // 2) * p_defense_multiplier)
            dmg_received = max(1, random.randint(1, enemy["atk"]) - p_def)
            p["hp"] = max(0, p["hp"] - dmg_received)
            log += "\n🩹 【" + enemy['name'] + "】發動殘暴反擊！你受到 " + str(dmg_received) + " 點物理傷害！"

            if p["hp"] <= 0:
                p["enemy"] = None
                log += "\n💀 你受傷過重陣亡了！請點擊底部【😇 祈求復活】按鈕。"
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, None)
            else:
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, enemy)

            msg_payload = {
                "replyToken": event.reply_token,
                "messages": [{
                    "type": "flex",
                    "altText": "戰鬥回合",
                    "contents": card_data["flex"],
                    "quickReply": card_data["quick_reply"]
                }]
            }
            with ApiClient(configuration) as api_client:
                MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
    else:
        card_data = db_core.make_battle_card("💡 系統提示：請利用螢幕最下方可以左右橫向滑動的小圖標，直接點擊按鈕來展開您的冒險旅程！", p, None)
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{
                "type": "flex",
                "altText": "冒險導引",
                "contents": card_data["flex"],
                "quickReply": card_data["quick_reply"]
            }]
        }
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
# === END OF FILE ===
