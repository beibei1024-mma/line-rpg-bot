import random
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, ApiClient
from linebot.models import TextSendMessage, FlexSendMessage

import db_core
import monsters
import weapons
import bag
import jobs
import jobs_system
import notice_system

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    """【傳奇戰鬥大腦 v2.0】實裝 MP 扣除、技能專屬公式、戰場防禦、逃跑扣罰，縮排精準過審"""
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
    # 讀取工坊打造武器的隨機額外屬性加成 (優化三預留)
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
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        title_log = f"⚠️ 遭遇強敵！在📍【{current_location}】撞見了對手！\n\n📢 環境狀態：{random_monster['env']}\n🔰 怪物被動：{random_monster['skill']}"
        card_data = db_core.make_battle_card(title_log, p, random_monster)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "遭遇怪物", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 3. 🏃 優化二：逃跑扣罰與博弈機制
    elif user_msg == "逃跑":
        if p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 周圍沒有怪物，你不需要逃跑。"))
            return
        enemy = p["enemy"]
        # 30% 機率逃跑失敗
        if random.random() < 0.30:
            m_atk = random.randint(1, enemy["atk"])
            p_def = vit_val // 2
            backlash_dmg = max(1, (m_atk - p_def) * 2) # 遭到憤怒的雙倍反擊
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
            # 成功逃跑扣除 10 金幣
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
        is_skill = user_msg.startswith("使用技能") and user_msg != "使用技能防禦"
        is_defense = (user_msg == "使用技能防禦")
        skill_name = user_msg.replace("使用技能", "").strip() if is_skill else ""
        
        # 🛡️ 戰場狀態因子初始化
        p_defense_multiplier = 1.0
        total_p_dmg = 0
        
        # ✨ 優化二：臨時技能防禦大腦
        if is_defense:
            p_defense_multiplier = 3.0 # 本回合防禦力暴增 3 倍
            log += "🛡️ 戰術防禦！你架起防禦姿態，本回合防禦力暴增 3 倍，全神貫注準備抵擋目標的反擊！\n"
            
        # ✨ 優化一：技能實體扣 MP 與專屬公式大數據對齊
        elif is_skill:
            if skill_name not in job_mod["skills"]:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 技能錯誤！你目前不會【{skill_name}】法術。"))
                return
            mp_cost = job_mod["skills"][skill_name].get("mp_cost", 0)
            safe_mp = p.get("mp", calculated_max_mp)
            if safe_mp < mp_cost:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔷 魔力枯竭！施放【{skill_name}】需要 {mp_cost} 點 MP，你目前只有 {safe_mp} 點！"))
                return
            # 實體扣除魔力
            p["mp"] = safe_mp - mp_cost
            log += f"🔮 奧義發動！你消耗了 🔷 {mp_cost} 點 MP 施放秘術 ── ⚡【{skill_name}】！\n"
            
            # 🔮 各派系神級主動技能「屬性實體掛鉤公式」連動
            if skill_name in ["蓄力重擊", "旋風斬", "怒火重擊", "橫掃千軍"]:
                total_p_dmg = int((12 + str_val + w_bonus) * 1.8) # 力量型
            elif skill_name in ["火球術", "元素暴風", "極凍終焉", "末日流星", "聖光懲戒"]:
                total_p_dmg = int((10 + int_val) * 2.5) # 智力型
            elif skill_name in ["二連矢", "毒刃襲擊", "狙擊一擊", "暴風萬箭破", "瞬獄殺"]:
                total_p_dmg = int((12 + agi_val + w_bonus) * 2.2) # 敏捷型
            elif skill_name == "治癒術" or skill_name == "群體療癒":
                heal = int((int_val + men_val) * 2.0)
                old_h = p["hp"]
                p["hp"] = min(calculated_max_hp, p["hp"] + heal)
                log += f"💖 聖光治癒！治癒法術實體為你恢復了生命值 +{p['hp'] - old_h} 點！\n"
                total_p_dmg = int(int_val * 0.5)
            else:
                total_p_dmg = int((str_val + int_val + agi_val) * 1.2)
                
            log += f"💥 重創命中！技能對【{enemy['name']}】造成了 {total_p_dmg} 點實體法術傷害！\n"
        else:
            # 普通物理揮刀
            crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
            crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
            double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
            
            is_double = random.random() < double_atk_chance
            for i in range(2 if is_double else 1):
                d = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
                if random.random() < crit_chance:
                    d = int(d * crit_dmg_mod)
                    log += f"💥 致命爆擊！第 {i+1} 擊斬出 {d} 點爆擊物理傷害！\n"
                else:
                    log += f"⚔️ 第 {i+1} 擊普通命中，造成 {d} 點物理傷害！\n"
                total_p_dmg += d

        # 扣除怪獸血量
        enemy["hp"] -= total_p_dmg
        
        # ── 5. 戰鬥大獲全勝結算 ──
        if enemy["hp"] <= 0:
            gold_mod = p.get("map_gold_mod", 1.0)
            gold_data = enemy["gold_range"]
            final_gold = int(random.randint(int(gold_data[0]), int(gold_data[1])) * gold_mod)
            p["gold"] += final_gold; p["exp"] += enemy["exp"]
            
            p["mp"] = min(calculated_max_mp, p["mp"] + 25) # 自然冥想調息
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy['exp']}！\n🔷 戰鬥結束調息，魔力恢復 +25 點。\n"
            
            # 5% 爆區域專屬神裝 (放回背包連動)
            if random.random() < 0.05:
                current_loc = p.get("current_map", "新手村")
                matched_weapons = [w_name for w_name in weapons.SHOP_WEAPONS.keys() if current_loc[:2] in w_name or (current_loc == "新手村" and "新手" in w_name)]
                if matched_weapons:
                    drop_w = random.choice(matched_weapons); old_w = p.get("weapon", "赤手空拳")
                    if old_w != "赤手空拳": forge_system.add_to_weapon_inventory(p, old_w)
                    p["weapon"] = drop_w
                    log += f"💎 🔥 【神裝降臨】！你驚喜搜刮到了該區域的專屬神兵：⚔️【{drop_w}】！已全自動換裝！\n"

            # 📢 移交 notice_system 全服首殺廣播
            raw_monster_name = enemy["name"]
            if "地獄紅蓮巨龍" in raw_monster_name or "邪神克蘇魯" in raw_monster_name:
                notice_system.push_world_boss_broadcast(raw_monster_name, configuration)
                log += f"\n👑 🏆 諸神見證！首殺捷報已推播給全服所有玩家！"

            p["enemy"] = None
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！素材：【{enemy['drop_item']}】x1！\n"
                
            # 🔒 安全移交 jobs_system 獨立大腦進行卡等判定
            is_job_locked = jobs_system.check_level_lock(p, job_mod)
            p["hp"] = 100 + (vit_val * 5) + (p["level"] * 15)
            db_core.save_player(p)
            
            card_data = db_core.make_battle_card(log, p, None)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥結束", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            if is_job_locked:
                msg_payload["messages"].append({"type": "text", "text": f"🔒 【天賦界限卡關中】\n勇者！你目前已達到了 Lv.{p['level']} 的天賦瓶頸，必須完成天賦轉職才能繼續獲取經驗！\n\n{jobs.get_job_options_text(p)}"})
            with ApiClient(configuration) as api_client: api_client.rest_client.post_request(f"https://line.me", headers={"Authorization": f"Bearer {configuration.access_token}", "Content-Type": "application/json"}, body=db_core.json.dumps(msg_payload))
        else:
            # ── 6. 怪物殘存與環境反擊 (防禦力加乘實體扣減) ──
            env_str = enemy.get("env", "")
            if "暴雨滂沱" in env_str: vit_val = int(vit_val * 0.8)
            if "精神污染" in enemy.get("skill", ""): p["mp"] = max(0, p["mp"] - 20); log += f"\n👁️ 🚨 邪神被動【精神污染】！魔力值被吸走 20 點！"

            final_m_atk = random.randint(1, enemy["atk"])
            # ✨ 優化二：套用防禦力加乘
            p_def = int((vit_val // 2) * p_defense_multiplier)
            dmg_received = max(1, final_m_atk - p_def)
            p["hp"] = max(0, p["hp"] - dmg_received)
            log += f"\n🩹 【{enemy['name']}】發動殘暴反擊！你受到 {dmg_received} 點物理傷害！"
            
            if p["hp"] <= 0:
                p["enemy"] = None; log += "\n💀 你受傷過重陣亡了！請點擊底部【😇 祈求復活】按鈕。"
                db_core.save_player(p); card_data = db_core.make_battle_card(log, p, None)
            else:
                db_core.MEMORY_PLAYERS[event.source.user_id] = p; card_data = db_core.make_battle_card(log, p, enemy)
                
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥回合", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: api_client.rest_client.post_request(f"https://line.me", headers={"Authorization": f"Bearer {configuration.access_token}", "Content-Type": "application/json"}, body=db_core.json.dumps(msg_payload))
    else:
        card_data = db_core.make_battle_card("💡 系統提示：請利用螢幕最下方可以左右橫向滑動的小圖標，直接點擊按鈕來展開您的冒險旅程！", p, None)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "冒險導引", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: api_client.rest_client.post_request(f"https://line.me", headers={"Authorization": f"Bearer {configuration.access_token}", "Content-Type": "application/json"}, body=db_core.json.dumps(msg_payload))
