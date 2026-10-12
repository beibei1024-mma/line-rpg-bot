# battle_core.py - 皇家戰鬥計算機 v3.8 (全死鎖終修復版)

import random
import json
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, ApiClient
from linebot.models import TextSendMessage
import db_core
import monsters
import bag
import jobs
import jobs_system

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    """核心揮刀計算機：徹底封印 None 減法與 Tuple 解包崩潰地雷"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 🛡️ 1. 裝備白字與副詞綴加成動態累加回流器
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    eq_atk, eq_def = 0, 0
    eq_affixes = {"strength": 0, "agility": 0, "intelligence": 0, "vitality": 0, "luck": 0, "sprit": 0}
    for slot, eq in equipped.items():
        eq_atk += eq.get("atk", 0)
        eq_def += eq.get("def", 0)
        for stat, val in eq.get("affixes", {}).items():
            eq_affixes[stat] = eq_affixes.get(stat, 0) + val

    # 實體加算基礎六大屬性
    str_val = int((p.get("strength", 10) + eq_affixes["strength"]) * job_mod["str_mod"])
    agi_val = int((p.get("agility", 10) + eq_affixes["agility"]) * job_mod["agility"]) if "agility" in job_mod else int((p.get("agility", 10) + eq_affixes["agility"]) * job_mod.get("agi_mod", 1.0))
    int_val = int((p.get("intelligence", 10) + eq_affixes["intelligence"]) * job_mod["int_mod"])
    vit_val = int((p.get("vitality", 10) + eq_affixes["vitality"]) * job_mod["vit_mod"])
    luk_val = int((p.get("luck", 10) + eq_affixes["luck"]) * job_mod["luk_mod"])
    men_val = int((p.get("sprit", 10) + eq_affixes["sprit"]) * job_mod["men_mod"])
    
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)

    # ✨【💥 核心死鎖修正一】徹底封印資料庫 None 值的扣減崩潰 (強制作保底校正)
    if p.get("hp") is None or p["hp"] <= 0: p["hp"] = calculated_max_hp
    if p.get("mp") is None or p["mp"] == "None": p["mp"] = calculated_max_mp
    p["mp"] = int(p["mp"]) # 強制轉為整數，阻絕一切類型死鎖

    # 2. 🔍 尋怪指令判定
    if user_msg in ["尋找怪物", "尋怪"]:
        if p.get("enemy") is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 眼前還有怪物！請發動【攻擊】或施放職業技能！"))
            return
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        
        title_log = f"⚠️ 野外危險區：{current_location}\n\n遭遇強敵！撞見了對手！\n📢 環境：{random_monster['env']}\n🔰 被動：{random_monster['skill']}"
        card_data = db_core.make_battle_card(title_log, p, random_monster)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "遭遇怪物", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 3. ⚔️ 攻擊、防禦指令判定
    elif user_msg in ["攻擊", "使用技能防禦", "技能防禦"]:
        if p.get("enemy") is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 周圍沒有怪物，請先點擊【尋怪】！"))
            return
            
        enemy = p["enemy"]
        log = ""
        is_defense = (user_msg in ["使用技能防禦", "技能防禦"])
        p_defense_multiplier = 3.0 if is_defense else 1.0
        total_p_dmg = 0
        
        if is_defense:
            log += "🛡️ 戰術防禦！本回合防禦力暴增 3 倍，準備迎擊反擊！\n"
        else:
            # 物理普通揮刀公式
            d = random.randint(5 + (str_val // 2) + eq_atk, 12 + str_val + eq_atk)
            log += f"⚔️ 揮刀命中，對【{enemy['name']}】造成 {d} 點物理傷害！\n"
            total_p_dmg = d

        enemy["hp"] -= total_p_dmg
# battle_core.py - 皇家戰鬥計算機 v3.8 (第二部分：技能與升級連通)

        # ── 🔮 技能施放分流計算處理 ──
        elif user_msg.startswith("使用技能"):
            skill_name = user_msg.replace("使用技能", "").strip()
            if skill_name not in job_mod.get("skills", {}):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 技能錯誤！你目前職業的天賦樹中不會【{skill_name}】法術。"))
                return
                
            mp_cost = job_mod["skills"][skill_name].get("mp_cost", 0)
            if p["mp"] < mp_cost:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔷 魔力不足！施放【{skill_name}】需要 {mp_cost} 點 MP，你目前只有 {p['mp']} 點！"))
                return
                
            p["mp"] -= mp_cost
            log += f"🔮 奧義發動！你消耗了 🔷 {mp_cost} 點 MP 施放秘術 ── ⚡【{skill_name}】！\n"
            base_weapon_atk = 12 + str_val + eq_atk
            
            # ⚔️ 1. 戰士 ➡️ 狂戰 ➡️ 修羅體系技能
            if skill_name == "蓄力重擊": total_p_dmg = int(base_weapon_atk * 1.5)
            elif skill_name == "橫掃千軍": total_p_dmg = int(base_weapon_atk * 1.8) + 50
            elif skill_name == "戰吼震懾": total_p_dmg = int(base_weapon_atk * 1.3) + 100
            elif skill_name == "破甲一擊": total_p_dmg = int(base_weapon_atk * 2.2) + 150
            elif skill_name == "血性狂暴": total_p_dmg = int(base_weapon_atk * 2.9) + 300
            elif skill_name == "旋風斬": total_p_dmg = int(base_weapon_atk * 3.4) + 450
            elif skill_name == "怒火重擊": total_p_dmg = int(base_weapon_atk * 4.0) + 600
                
            # 🛡️ 2. 騎士 ➡️ 十字軍 ➡️ 督軍體系技能
            elif skill_name == "盾擊": total_p_dmg = int((12 + vit_val + eq_atk) * 1.4)
            elif skill_name == "神聖之光": total_p_dmg = int((10 + int_val) * 1.6) + 40
            elif skill_name == "神聖盾擊": total_p_dmg = int((12 + vit_val + eq_atk) * 2.6) + 200
                
            # 🔮 3. 魔法師 ➡️ 魔導士 ➡️ 元素使體系技能
            elif skill_name == "魔能彈": total_p_dmg = int((10 + int_val) * 1.3)
            elif skill_name == "火球術": total_p_dmg = int((10 + int_val) * 2.0) + 60
            elif skill_name == "閃電術": total_p_dmg = int((10 + int_val) * 2.4) + 110
            elif skill_name == "奧術飛彈": total_p_dmg = int((10 + int_val) * 2.7) + 160
            
            else: total_p_dmg = int(base_weapon_atk * 1.2)
            log += f"💥 重創命中！技能對【{enemy['name']}】造成了 {total_p_dmg} 點實體傷害！\n"

        enemy["hp"] -= total_p_dmg

        # ── 🎉 4. 戰鬥大獲全勝結算 ──
        if enemy["hp"] <= 0:
            gold_data = enemy.get("gold_range", (10, 50))
            if isinstance(gold_data, (list, tuple)) and len(gold_data) >= 2:
                final_gold = random.randint(int(gold_data[0]), int(gold_data[1]))
            else:
                final_gold = random.randint(int(gold_data) // 2, int(gold_data)) if int(gold_data) > 0 else 10
                
            p["gold"] += final_gold
            p["exp"] += enemy.get("exp", 15)
            p["mp"] = min(calculated_max_mp, p["mp"] + 25) 
            log += f"\n🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy.get('exp', 15)}！\n🔷 調息魔力恢復 +25 點。\n"
            
            # 🛠️ 【即刻接入升級中樞大腦】徹底解決不會升等的 Bug
            try:
                import player_level_up
                level_up_bonus_msg = player_level_up.check_and_execute_level_up(p)
                log += level_up_bonus_msg
            except: pass
            
            # 3% 機率掉落素材
            if random.random() < 0.30 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！素材：【{enemy['drop_item']}】x1！\n"
                
            p["enemy"] = None
            db_core.save_player(p)
            card_data = db_core.make_battle_card(log, p, None)
        else:
            # ── 🩹 5. 怪物殘存發動環境反擊 ──
            final_m_atk = random.randint(1, enemy.get("atk", 5))
            p_def = int((vit_val // 2) * p_defense_multiplier) + eq_def
            dmg_received = max(1, final_m_atk - p_def)
            p["hp"] = max(0, p["hp"] - dmg_received)
            log += f"\n🩹 【{enemy['name']}】發動反擊！你受到 {dmg_received} 點傷害！"
            
            if p["hp"] <= 0:
                p["enemy"] = None
                p["current_map"] = "主城"
                log += "\n💀 你受傷過重陣亡了！已被大天使靈魂傳送回主城。"
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, None)
            else:
                p["enemy"] = enemy
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, enemy)
                
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰報結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))

        # ── 🎉 4. 戰鬥大獲全勝結算 ──
        if enemy["hp"] <= 0:
            gold_data = enemy.get("gold_range", (10, 50))
            
            # ✨【💥 核心死鎖修正二】完美相容 Tuple 與單一 Int 的動態金幣解包算法
            if isinstance(gold_data, (list, tuple)) and len(gold_data) >= 2:
                final_gold = random.randint(int(gold_data[0]), int(gold_data[1]))
            else:
                final_gold = random.randint(int(gold_data) // 2, int(gold_data)) if int(gold_data) > 0 else 10
                
            p["gold"] += final_gold
            p["exp"] += enemy.get("exp", 15)
            p["mp"] = min(calculated_max_mp, p["mp"] + 25) 
            log += f"\n🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy.get('exp', 15)}！\n🔷 調息魔力恢復 +25 點。\n"
            
            # 3% 機率掉落素材
            if random.random() < 0.30 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！素材：【{enemy['drop_item']}】x1！\n"
                
            p["enemy"] = None
            db_core.save_player(p)
            card_data = db_core.make_battle_card(log, p, None)
        else:
            # ── 🩹 5. 怪物殘存發動環境反擊 ──
            final_m_atk = random.randint(1, enemy.get("atk", 5))
            p_def = int((vit_val // 2) * p_defense_multiplier) + eq_def
            dmg_received = max(1, final_m_atk - p_def)
            p["hp"] = max(0, p["hp"] - dmg_received)
            log += f"\n🩹 【{enemy['name']}】發動反擊！你受到 {dmg_received} 點傷害！"
            
            if p["hp"] <= 0:
                p["enemy"] = None
                p["current_map"] = "主城"
                log += "\n💀 你受傷過重陣亡了！已被大天使靈魂傳送回主城。"
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, None)
            else:
                p["enemy"] = enemy
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, enemy)
                
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰報結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
