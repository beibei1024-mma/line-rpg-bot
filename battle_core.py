# battle_core.py - 純粹戰鬥調度中心 v4.3 (尋怪與攻擊嚴格分離版)

import random
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, ApiClient
from linebot.models import TextSendMessage
import db_core
import jobs
import combat_engine
import loot_engine
import equipment_core
import weapons
import monsters
import challenge_system

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    """【戰鬥主路由：尋怪與攻擊嚴格分離】"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    eq_bonus = equipment_core.get_player_total_equipment_bonus(p)
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.get_weapon_atk(current_weapon) + int(p.get("forge_weapon_bonus", 0))

    # 1. 轉職卡關防呆
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ("攻擊", "使用技能") or user_msg.startswith("使用技能"):
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔒 【天賦界限卡關中】請先完成手動天賦轉職！\n\n" + job_notice))
            return

    if p["hp"] <= 0:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊底部【😇 祈求復活】按鈕。"))
        return

    # 2. 🔍 尋找怪物處理（純粹遭遇怪物，絕對不主動揮出第一刀！）
    if user_msg in ("尋找怪物", "尋怪"):
        if p[" enemy"] is not None and not p["enemy"].get("is_world_boss"):
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

    # 若沒有怪卻點了攻擊，提示尋找怪物
    if p["enemy"] is None:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 目前周圍沒有怪物，請點擊底部【🔍 尋找怪物】來遭遇對手！"))
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
        log += "🛡️ 戰術防禦！你架起鋼鐵防護姿態，本回合防禦力暴增 3 倍！\n"
    elif is_skill:
        if skill_name not in job_mod["skills"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 技能錯誤！你目前職業的天賦樹中不會【" + skill_name + "】法術。"))
            return

        mp_cost = job_mod["skills"][skill_name].get("mp_cost", 0)
        safe_mp = p.get("mp", 50)
        if safe_mp < mp_cost:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔷 魔力枯竭！施放【" + skill_name + "】需要 " + str(mp_cost) + " 點 MP，你目前只有 " + str(safe_mp) + " 點！"))
            return

        p["mp"] = safe_mp - mp_cost
        log += "🔮 奧義發動！消耗 🔷 " + str(mp_cost) + " MP 施放 ── ⚡【" + skill_name + "】！\n"

        skill_dmg, skill_log = combat_engine.calculate_skill_attack(p, job_mod, eq_bonus, w_bonus, skill_name)
        total_p_dmg = skill_dmg
        log += skill_log.format(enemy_name=enemy["name"])
    else:
        atk_dmg, atk_log = combat_engine.calculate_player_attack(p, job_mod, eq_bonus, w_bonus)
        total_p_dmg = atk_dmg
        log += atk_log

    enemy["hp"] -= total_p_dmg

    if enemy.get("is_world_boss") and total_p_dmg > 0:
        p["world_boss_damage"] = (p.get("world_boss_damage", 0) or 0) + total_p_dmg
        log += "🌋 【世界Boss討伐戰功】累計輸出：⚔️ " + str(p['world_boss_damage']) + " 點！\n"

    if enemy["hp"] <= 0:
        loot_log, is_job_locked = loot_engine.process_monster_defeat(p, enemy, configuration)
        log += loot_log

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
        base_vit = p.get("vitality", 10) + eq_bonus["vitality"]
        vit_val = int(base_vit * job_mod["vit_mod"])
        if "暴雨滂沱" in enemy.get("env", ""):
            vit_val = int(vit_val * 0.8)
        if "精神污染" in enemy.get("skill", ""):
            p["mp"] = max(0, p["mp"] - 20)
            log += "\n👁️ 🚨 邪神被動【精神污染】！魔力值被吸走 20 點！"

        p_def = int((vit_val // 2) * p_defense_multiplier) + eq_bonus["def"]
        dmg_received = max(1, random.randint(1, enemy["atk"]) - p_def)
        p["hp"] = max(0, p["hp"] - dmg_received)
        log += "\n🩹 【" + enemy['name'] + "】發動反擊！你受到 " + str(dmg_received) + " 點傷害！"

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
# === END OF FILE ===
