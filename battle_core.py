# battle_core.py - 皇家戰鬥計算機 v2.5 (第一部分)

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

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    """處理核心揮刀、防禦、施法與逃跑邏輯，精準切碎戰鬥口令"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 🛠️ 屬性初始化與職涯倍率實體乘算
    str_val = int(p.get("strength", 10 + (level * 3)) * job_mod["str_mod"])
    agi_val = int(p.get("agility", 10 + (level * 2)) * job_mod["agi_mod"])
    int_val = int(p.get("intelligence", 10 + (level * 2)) * job_mod["int_mod"])
    vit_val = int(p.get("vitality", 10 + (level * 3)) * job_mod["vit_mod"])
    luk_val = int(p.get("luck", 10 + (level * 1)) * job_mod["luk_mod"])
    men_val = int(p.get("sprit", 10 + (level * 2)) * job_mod["men_mod"])
    
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    if p.get("mp") is None: p["mp"] = calculated_max_mp

    # ⚔️ 讀取武器與手工裝備附加屬性
    current_weapon = p.get("weapon", "赤手空拳")
    pure_w_name = current_weapon.split(" 的 ")[-1] if " 的 " in current_weapon else current_weapon
    w_bonus = weapons.SHOP_WEAPONS[pure_w_name]["atk_bonus"] if pure_w_name in weapons.SHOP_WEAPONS else 0
    w_bonus += int(p.get("forge_weapon_bonus", 0))

    # 1. 轉職卡關防呆防禦牆
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["攻擊", "使用技能"] or user_msg.startswith("使用技能"):
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】請先完成手動天賦轉職！\n\n{job_notice}"))
            return

    # 2. 🔍 尋找怪物處理分支
    if user_msg in ["尋找怪物", "尋怪"]:
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊底部【😇 祈求復活】按鈕。"))
            return
        if p.get("enemy") is not None:
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

    # 3. 🏃 逃跑扣罰與博弈機制
    elif user_msg == "逃跑":
        if p.get("enemy") is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 周圍沒有怪物，你不需要逃跑。"))
            return
        enemy = p["enemy"]
        if random.random() < 0.30: # 30% 逃跑失敗
            m_atk = random.randint(1, enemy["atk"])
            backlash_dmg = max(1, (m_atk - (vit_val // 2)) * 2)
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
            log = "🏃 💨 逃跑成功！你慌忙丟下了 🪙 10 金幣引開注意，狼狽地逃離了戰場！"
            card_data = db_core.make_battle_card(log, p, None)
            
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "逃跑結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 4. 核心戰鬥揮刀、防禦與主動技能公式（前段三大職業）
    elif user_msg == "攻擊" or user_msg.startswith("使用技能") or user_msg == "使用技能防禦":
        if p["hp"] <= 0 or p.get("enemy") is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法發動戰鬥（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        clean_msg = user_msg.replace(" ", "").strip()
        is_defense = (clean_msg in ["使用技能防禦", "技能防禦"])
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
            base_weapon_atk = 12 + str_val + w_bonus
            
            # ⚔️ [1] 戰士 ➡️ 狂戰 ➡️ 修羅體系
            if skill_name == "蓄力重擊": total_p_dmg = int(base_weapon_atk * 1.5)
            elif skill_name == "橫掃千軍": total_p_dmg = int(base_weapon_atk * 1.8) + 50
            elif skill_name == "戰吼震懾": total_p_dmg = int(base_weapon_atk * 1.3) + 100
            elif skill_name == "破甲一擊": total_p_dmg = int(base_weapon_atk * 2.2) + 150
            elif skill_name == "血性狂暴": total_p_dmg = int(base_weapon_atk * 2.9) + 300
            elif skill_name == "旋風斬": total_p_dmg = int(base_weapon_atk * 3.4) + 450
            elif skill_name == "怒火重擊": total_p_dmg = int(base_weapon_atk * 4.0) + 600
            elif skill_name == "阿修羅霸凰拳": total_p_dmg = int(base_weapon_atk * 6.5) + 1200
            elif skill_name == "百裂拳": total_p_dmg = int(base_weapon_atk * 4.8) + 800
            elif skill_name == "虎咆爪": total_p_dmg = int(base_weapon_atk * 5.3) + 950
                
            # 🛡️ [2] 騎士 ➡️ 十字軍 ➡️ 督軍體系
            elif skill_name == "盾擊": total_p_dmg = int((12 + vit_val + w_bonus) * 1.4)
            elif skill_name == "神聖之光": total_p_dmg = int((10 + int_val) * 1.6) + 40
            elif skill_name == "神聖盾擊": total_p_dmg = int((12 + vit_val + w_bonus) * 2.6) + 200
            elif skill_name == "審判聖刃": total_p_dmg = int((10 + int_val) * 3.2) + 400
            elif skill_name == "正義裁決": total_p_dmg = int((12 + vit_val + str_val) * 4.8) + 900
                
            # 🔮 [3] 魔法師 ➡️ 魔導士 ➡️ 元素使體系
            elif skill_name == "魔能彈": total_p_dmg = int((10 + int_val) * 1.3)
            elif skill_name == "火球術": total_p_dmg = int((10 + int_val) * 2.0) + 60
            elif skill_name == "閃電術": total_p_dmg = int((10 + int_val) * 2.4) + 110
            elif skill_name == "奧術飛彈": total_p_dmg = int((10 + int_val) * 2.7) + 160
            elif skill_name == "元素暴風": total_p_dmg = int((10 + int_val) * 3.6) + 400
            elif skill_name == "冰凍術": total_p_dmg = int((10 + int_val) * 3.0) + 300
            elif skill_name == "魔力燃燒": total_p_dmg = int((10 + int_val) * 3.3) + 350
            elif skill_name == "極凍終焉": total_p_dmg = int((10 + int_val) * 5.8) + 1000
            elif skill_name == "末日流星": total_p_dmg = int((10 + int_val) * 6.6) + 1300
            elif skill_name == "雷神之怒": total_p_dmg = int((10 + int_val) * 5.0) + 850
            
            # 其餘後續職業分支與戰結算管線，將在第二部分模組無縫接軌續接！
            # 將運算狀態打包交由下一模組接續完成
            _continue_battle_calculation(event, line_bot_api, p, enemy, log, total_p_dmg, is_defense, is_skill, skill_name, p_defense_multiplier, str_val, agi_val, int_val, vit_val, luk_val, men_val, w_bonus, calculated_max_mp, job_mod, configuration)
# battle_core.py - 皇家戰鬥計算機 v2.5 (第二部分)

def _continue_battle_calculation(event, line_bot_api, p, enemy, log, total_p_dmg, is_defense, is_skill, skill_name, p_defense_multiplier, str_val, agi_val, int_val, vit_val, luk_val, men_val, w_bonus, calculated_max_mp, job_mod, configuration):
    """接續後半段戰鬥核心計算（後三大職業技能、物理普攻與勝負存檔管線）"""
    level = p.get("level", 1)
    vit_val_job = int(p.get("vitality", 10) * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val_job * 5) + (level * 15)

    if is_skill and total_p_dmg == 0:
        # 🗡️ 盜賊 ➡️ 刺客 ➡️ 暗夜行者體系
        if skill_name == "背刺": total_p_dmg = int((12 + agi_val + w_bonus) * 1.6)
        elif skill_name == "毒刃襲擊": total_p_dmg = int((12 + agi_val + w_bonus) * 2.3) + 100
        elif skill_name == "影分身": total_p_dmg = int((12 + agi_val + w_bonus) * 3.4) + 350
        elif skill_name == "弒神終結": total_p_dmg = int((12 + agi_val + luk_val + w_bonus) * 5.6) + 900
        elif skill_name == "瞬獄殺": total_p_dmg = int((12 + agi_val + w_bonus) * 6.3) + 1200
            
        # 🏹 弓箭手 ➡️ 獵人 ➡️ 遊俠體系
        elif skill_name == "二連矢": total_p_dmg = int((12 + agi_val + w_bonus) * 1.7) + 40
        elif skill_name == "狙擊一擊": total_p_dmg = int((12 + agi_val + w_bonus) * 2.5) + 200
        elif skill_name == "爆影狂襲": total_p_dmg = int((12 + agi_val + w_bonus) * 3.3) + 400
        elif skill_name == "暴風萬箭破": total_p_dmg = int((12 + agi_val + luk_val + w_bonus) * 5.4) + 1100
            
        # ⛪ 祭師 ➡️ 賢者 ➡️ 大主教體系
        elif skill_name in ["治癒術", "群體療癒"]:
            heal = int((int_val + men_val) * 2.5)
            old_h = p["hp"]
            p["hp"] = min(calculated_max_hp, p["hp"] + heal)
            log += f"💖 聖光治癒！神聖恢復了生命值 +{p['hp'] - old_h} 點！\n"
            total_p_dmg = int(int_val * 0.8)
        elif skill_name == "聖光懲戒": total_p_dmg = int((10 + int_val + men_val) * 2.4) + 150
        elif skill_name == "神聖讚美詩": total_p_dmg = int((10 + int_val + men_val) * 5.5) + 1000
        else: total_p_dmg = int((str_val + int_val + agi_val) * 1.5)
            
        log += f"💥 重創命中！技能對【{enemy['name']}】造成了 {total_p_dmg} 點實體法術傷害！\n"

    elif not is_defense and not is_skill:
        # ⚔️ 普通物理揮刀與爆擊、連擊博弈公式
        crit_chance = min(0.80, 0.10 + (luk_val / 500.0))          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        double_atk_chance = min(0.60, 0.02 + (agi_val / 600.0))     
        
        is_double = random.random() < double_atk_chance
        for i in range(2 if is_double else 1):
            d = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
            if random.random() < crit_chance:
                d = int(d * crit_dmg_mod)
                log += f"💥 致命爆擊！第 {i+1} 擊斬出 {d} 點爆擊物理傷害！\n"
            else:
                log += f"⚔️ 第 {i+1} 擊普通命中，造成 {d} 點物理傷害！\n"
            total_p_dmg += d

    enemy["hp"] -= total_p_dmg

    # ── 5. 戰鬥大獲全勝結算 ──
    if enemy["hp"] <= 0:
        gold_mod = p.get("map_gold_mod", 1.0)
        gold_data = enemy.get("gold_range", [10, 20])
        
        # ✨ 【Bug 完美校正】徹底避免 'list' 或 'int' 類型引發 random.randint 閃退
        min_gold = int(gold_data[0]) if isinstance(gold_data, (tuple, list)) else int(gold_data)
        max_gold = int(gold_data[1]) if isinstance(gold_data, (tuple, list)) else int(gold_data)
        final_gold = int(random.randint(min_gold, max_gold) * gold_mod)
        
        p["gold"] += final_gold
        p["exp"] += enemy.get("exp", 10)
        p["mp"] = min(calculated_max_mp, p.get("mp", calculated_max_mp) + 25) 
        log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy.get('exp', 10)}！\n🔷 戰鬥結束調息，魔力恢復 +25 點。\n"
        
        # 3% 機率觸發區域專屬裝備掉落
        if random.random() < 0.03:
            current_loc = p.get("current_map", "新手村")
            matched_weapons = [w for w in weapons.SHOP_WEAPONS.keys() if current_loc[:2] in w or (current_loc == "新手村" and "新手" in w)]
            if matched_weapons:
                drop_w = random.choice(matched_weapons)
                forge_system.add_to_weapon_inventory(p, drop_w)
                log += f"💎 🔥 🗺️ 【神裝降臨・直接入庫】 🗺️ 🔥 💎\n你擊敗魔物搜刮戰場，驚喜搜刮到了該區域的專屬神兵 ── ⚔️【{drop_w}】！\n📦 存放去向：寶物已送入背包裝備收藏庫！\n"

        if "地獄紅蓮巨龍" in enemy["name"] or "邪神克蘇魯" in enemy["name"]:
            notice_system.push_world_boss_broadcast(enemy["name"], configuration)
            log += "\n👑 🏆 諸神見證！首殺捷報已推播給全服所有玩家！"

        p["enemy"] = None
        if random.random() < 0.50 and enemy.get("drop_item"):
            bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
            log += f"💎 【幸運掉寶】！素材：【{enemy['drop_item']}】x1！\n"
            
        is_job_locked = jobs_system.check_level_lock(p, job_mod)
        p["hp"] = 100 + (int(p.get("vitality", 10) * job_mod["vit_mod"]) * 5) + (p["level"] * 15)
        db_core.save_player(p)
        
        card_data = db_core.make_battle_card(log, p, None)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥結束", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        if is_job_locked:
            msg_payload["messages"].append({"type": "text", "text": f"🔒 【天賦界限卡關中】\n勇者！你已達到天賦瓶頸，必須完成天賦轉職才能繼續獲取經驗！\n\n{jobs.get_job_options_text(p)}"})
    else:
        # ── 6. 怪物殘存與環境反擊 ──
        if "精神污染" in enemy.get("skill", ""):
            p["mp"] = max(0, p.get("mp", 0) - 20)
            log += "\n👁️ 🚨 邪神被動【精神污染】！魔力值被吸走 20 點！"

        final_m_atk = random.randint(1, enemy.get("atk", 10))
        p_def = int((int(p.get("vitality", 10) * job_mod["vit_mod"]) // 2) * p_defense_multiplier)
        dmg_received = max(1, final_m_atk - p_def)
        p["hp"] = max(0, p["hp"] - dmg_received)
        log += f"\n🩹 【{enemy['name']}】發動殘暴反擊！你受到 {dmg_received} 點物理傷害！"
        
        if p["hp"] <= 0:
            p["enemy"] = None
            log += "\n💀 你受傷過重陣亡了！請點擊底部【😇 祈求復活】按鈕。"
            db_core.save_player(p)
            card_data = db_core.make_battle_card(log, p, None)
        else:
            db_core.MEMORY_PLAYERS[event.source.user_id] = p
            db_core.save_player(p)
            card_data = db_core.make_battle_card(log, p, enemy)
            
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥回合", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
