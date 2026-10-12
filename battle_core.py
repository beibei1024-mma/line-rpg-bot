# battle_core.py (優化分段完全體 - 第一部分)
import random
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, ApiClient, BroadcastRequest
from linebot.models import TextSendMessage, FlexSendMessage

import db_core
import monsters
import weapons
import bag
import jobs
import jobs_system
import notice_system
import forge_system

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    """【純粹戰鬥計算機 v2.6】加入主城安全區物理隔離防禦鎖，保障城鎮秩序"""
    current_location = p.get("current_map", "主城")
    
    # 🛡️ 【中央安全攔截牆】若玩家在主城卻執行此戰鬥大腦，直接就地清空怪物並退回請求
    if current_location == "主城":
        p["enemy"] = None
        db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 安全區秩序鎖定！主城禁止任何械鬥、尋怪、攻擊或使用主動技能！請先出城冒險！"))
        return

    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 六大屬性初始化
    base_str = p.get("strength", 10 + (level * 3))
    base_agi = p.get("agility", 10 + (level * 2))
    base_int = p.get("intelligence", 10 + (level * 2))
    base_vit = p.get("vitality", 10 + (level * 3))
    base_luk = p.get("luck", 10 + (level * 1))
    base_men = p.get("sprit", 10 + (level * 2))
    
    str_val = int(base_str * job_mod["str_mod"])
    agi_val = int(base_agi * job_mod["agi_mod"])
    int_val = int(base_int * job_mod["int_mod"])
    vit_val = int(base_vit * job_mod["vit_mod"])
    luk_val = int(base_luk * job_mod["luk_mod"])
    men_val = int(base_men * job_mod["men_mod"])
    
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    if p.get("mp") is None: p["mp"] = calculated_max_mp

    # 讀取武器與手工裝備附加屬性
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0
    forge_bonus = int(p.get("forge_weapon_bonus", 0))
    w_bonus += forge_bonus

    # 1. 轉職卡關防呆
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["攻擊", "使用技能"] or user_msg.startswith("使用技能"):
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】請先完成手動天賦轉職！\n\n{job_notice}"))
            return

    # 2. 🔍 尋找怪物處理
    if user_msg in ["尋找怪物", "尋怪"]:
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊底部【😇 祈求復活】按鈕。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 眼前還有怪物！請發動【攻擊】或施放職業技能！"))
            return
            
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        title_log = f"⚠️ 遭遇強敵！在📍【{current_location}】撞見了對手！\n\n📢 環境狀態：{random_monster['env']}\n🔰 怪物被動：{random_monster['skill']}"
        card_data = db_core.make_battle_card(title_log, p, random_monster)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "遭遇怪物", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 3. 🏃 逃跑扣罰與博弈機制
    elif user_msg == "逃跑":
        if p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 周圍沒有怪物，你不需要逃跑。"))
            return
        enemy = p["enemy"]
        if random.random() < 0.30:
            m_atk = random.randint(1, enemy["atk"])
            p_def = vit_val // 2
            backlash_dmg = max(1, (m_atk - p_def) * 2)
            p["hp"] = max(0, p["hp"] - backlash_dmg)
            log = f"🏃 ❌ 逃跑失敗！你露出了巨大的破綻，遭到【{enemy['name']}】憤怒的背後致命重擊，受到雙倍傷害 -{backlash_dmg} 點！"
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
            log = f"🏃 💨 逃跑成功！你慌忙丟下了 🪙 10 金幣引開注意，狼狽地逃離了戰場！"
            card_data = db_core.make_battle_card(log, p, None)
            
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "逃跑結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 4. ⚔️ 核心戰鬥揮刀、防禦與主動技能公式實體連動
    elif user_msg == "攻擊" or user_msg.startswith("使用技能") or user_msg == "使用技能防禦":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法發動戰鬥（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        clean_msg = user_msg.replace(" ", "").strip()
        is_defense = (clean_msg == "使用技能防禦" or clean_msg == "技能防禦")
        is_skill = clean_msg.startswith("使用技能") and not is_defense
        skill_name = clean_msg.replace("使用技能", "").strip() if is_skill else ""
        
        p_defense_multiplier = 1.0
        total_p_dmg = 0
        
        if is_defense:
            p_defense_multiplier = 3.0 
            log += "🛡️ 戰術防禦！你架起鋼鐵防護姿態，本回合防禦力暴增 3 倍，全神貫注準備抵擋目標的反擊！\n"
            
        elif is_skill:
            if skill_name not in job_mod["skills"]:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 技能錯誤！你目前職業的天賦樹中不會【{skill_name}】法術。"))
                return
            mp_cost = job_mod["skills"][skill_name].get("mp_cost", 0)
            safe_mp = p.get("mp", calculated_max_mp)
            if safe_mp < mp_cost:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔷 魔力枯竭！施放【{skill_name}】需要 {mp_cost} 點 MP，你目前只有 {safe_mp} 點！"))
                return
                
            p["mp"] = safe_mp - mp_cost
            log += f"🔮 奧義發動！你消耗了 🔷 {mp_cost} 點 MP 施放秘術 ── ⚡【{skill_name}】！\n"
            
            # 👑 【真．一/二/三轉 13 招核心主動技能公式大分家】 👑
            base_weapon_atk = 12 + str_val + w_bonus
            
            # ⚔️ [1] 戰士 ➡️ 狂戰 ➡️ 修羅體系
            if skill_name == "蓄力重擊":
                total_p_dmg = int(base_weapon_atk * 1.5)
            elif skill_name == "橫掃千軍":
                total_p_dmg = int(base_weapon_atk * 1.8) + 50
            elif skill_name == "戰吼震懾":
                total_p_dmg = int(base_weapon_atk * 1.3) + 100
            elif skill_name == "破甲一擊":
                total_p_dmg = int(base_weapon_atk * 2.2) + 150
            elif skill_name == "血性狂暴":
                total_p_dmg = int(base_weapon_atk * 2.9) + 300
            elif skill_name == "旋風斬":
                total_p_dmg = int(base_weapon_atk * 3.4) + 450
            elif skill_name == "怒火重擊":
                total_p_dmg = int(base_weapon_atk * 4.0) + 600
            elif skill_name == "阿修羅霸凰拳":
                total_p_dmg = int(base_weapon_atk * 6.5) + 1200
            elif skill_name == "百裂拳":
                total_p_dmg = int(base_weapon_atk * 4.8) + 800
            elif skill_name == "虎咆爪":
                total_p_dmg = int(base_weapon_atk * 5.3) + 950
                
            # 🛡️ [2] 騎士 ➡️ 十字軍 ➡️ 督軍體系 (防禦維度加成)
            elif skill_name == "盾擊":
                total_p_dmg = int((12 + vit_val + w_bonus) * 1.4)
            elif skill_name == "神聖之光":
                total_p_dmg = int((10 + int_val) * 1.6) + 40
            elif skill_name == "神聖盾擊":
                total_p_dmg = int((12 + vit_val + w_bonus) * 2.6) + 200
            elif skill_name == "審判聖刃":
                total_p_dmg = int((10 + int_val) * 3.2) + 400
            elif skill_name == "正義裁決":
                total_p_dmg = int((12 + vit_val + str_val) * 4.8) + 900
            # 🔮 [3] 魔法師 ➡️ 魔導士 ➡️ 元素使體系（法術加成）
            elif skill_name == "魔能彈":
                total_p_dmg = int((10 + int_val) * 1.3)
            elif skill_name == "火球術":
                total_p_dmg = int((10 + int_val) * 1.8) + 60
            elif skill_name == "雷擊術":
                total_p_dmg = int((10 + int_val) * 2.2) + 120
            elif skill_name == "暴風雪":
                total_p_dmg = int((10 + int_val) * 3.5) + 350
            elif skill_name == "末日審判":
                total_p_dmg = int((10 + int_val) * 5.5) + 1000
            else:
                # 保底法術傷害
                total_p_dmg = int((10 + int_val) * 1.2)
                
            log += f"💥 魔能炸裂！法術對【{enemy['name']}】造成了 {total_p_dmg} 點魔法傷害！\n"
        else:
            # 🗡️ 執行普通攻擊（有連擊與爆擊的判定體系）
            double_chance = min(60, 2 + (agi_val // 6))
            crit_chance = min(80, 10 + (luk_val // 5))
            
            is_double = random.random() < (double_chance / 100.0)
            is_crit = random.random() < (crit_chance / 100.0)
            
            base_dmg = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
            
            if is_crit:
                base_dmg = int(base_dmg * 1.5)
                log += "✨ 【致命爆擊】！"
                
            total_p_dmg = base_dmg
            log += f"⚔️ 普通攻擊命中，造成 {base_dmg} 點物理傷害！\n"
            
            if is_double:
                second_dmg = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
                if is_crit:
                    second_dmg = int(second_dmg * 1.5)
                total_p_dmg += second_dmg
                log += f"💨 連擊發動！追擊造成 {second_dmg} 點物理傷害！\n"

        # 🎯 物理扣減怪物的生命值值
        enemy["hp"] -= total_p_dmg
        
        # 🏆 5. 戰鬥獲勝結算
        if enemy["hp"] <= 0:
            gold_data = enemy["gold_range"]
            min_gold, max_gold = gold_data[0], gold_data[1]
            final_gold = random.randint(min_gold, max_gold)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["mp"] = min(calculated_max_mp, p.get("mp", 0) + 25)  # 戰勝回藍 25 點
            p["enemy"] = None
            
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy['exp']}！\n🔷 戰鬥吐納恢復 25 點魔力！"
            
            # 💎 5% 機率掉落區域專屬神兵利器
            if random.random() < 0.05:
                matched_weapons = [w_name for w_name in weapons.SHOP_WEAPONS.keys() if current_location[:2] in w_name or (current_location == "新手村" and "新手" in w_name)]
                if matched_weapons:
                    drop_w = random.choice(matched_weapons)
                    forge_system.add_to_weapon_inventory(p, drop_w)
                    log += f"\n💎 🔥 【神裝降臨・直接入庫】 💎 🔥\n驚喜搜刮到了該區域專屬神兵 ── ⚔️【{drop_w}】！"

            # 驗證等級天賦界限鎖
            jobs_system.check_level_lock(p, job_mod)
            db_core.save_player(p)
            
            card_data = db_core.make_battle_card(log, p, None)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥結束", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return

        # 🩹 6. 敵方回合：魔物反擊運算
        else:
            final_m_atk = random.randint(1, enemy["atk"])
            p_def = int((vit_val // 2) * p_defense_multiplier)
            dmg_received = max(1, final_m_atk - p_def)
            
            p["hp"] = max(0, p["hp"] - dmg_received)
            log += f"\n🩹 【{enemy['name']}】發動殘暴反擊！你受到 {dmg_received} 點物理傷害！"
            
            # 勇者不幸陣亡
            if p["hp"] <= 0:
                p["enemy"] = None
                log += "\n💀 你受傷過重不幸陣亡了！請點擊底部【😇 祈求復活】法陣重鑄靈魂。"
                
            db_core.save_player(p)
            
            card_data = db_core.make_battle_card(log, p, enemy)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥回合", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
