import random
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, ApiClient
from linebot.models import TextSendMessage, FlexSendMessage

import db_core
import monsters
import weapons
import bag
import jobs

def process_battle_logic(event, line_bot_api, p, user_msg, configuration):
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 快捷口令攔截導流
    if user_msg == "我的背包" or user_msg == "背包":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的私人物品倉庫", contents=bag.get_bag_card(p)))
        return
    elif user_msg == "我的狀態" or user_msg == "狀態":
        import player
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的狀態面板", contents=player.get_status_card(p)))
        return

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
    if "mp" not in p: p["mp"] = calculated_max_mp

    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0

    # A. 轉職處理
    if user_msg.startswith("轉職"):
        target_job = user_msg.replace("轉職", "").strip()
        if target_job not in jobs.JOBS_DATA:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！不存在【{target_job}】。"))
            return
        target_info = jobs.JOBS_DATA[target_job]
        if target_job not in job_mod["next_jobs"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！無法跨系進階。"))
            return
        if p["level"] < target_info["req_lvl"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 境界未到！需要 Lv.{target_info['req_lvl']}+。"))
            return
        p["job"] = target_job
        db_core.save_player(p)
        log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n🛡️ 你正式進階為更高的職業形態——🔥【{target_job}】！"
        
        card_data = db_core.make_battle_card(log_text, p, None)
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{
                "type": "flex", "altText": "轉職成功",
                "contents": card_data["flex"],
                "quickReply": card_data["quick_reply"]
            }]
        }
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 轉職卡關防呆
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["尋找怪物", "尋怪", "攻擊", "技能書", "使用技能"]:
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】請先完成手動天賦轉職！\n\n{job_notice}"))
            return

    # B. 處理【加點 / 配點】指令判定
    if user_msg.startswith("加點") or user_msg.startswith("配點"):
        clean_msg = event.message.text.strip().replace("配點", "加點")
        raw_parts = clean_msg.split()
        if len(raw_parts) == 3:
            attr_name = raw_parts.strip()
            pts_str = raw_parts.strip()
        else:
            try:
                target_str = clean_msg.replace("加點", "")
                attr_name = target_str[:2]
                pts_str = target_str[2:]
            except Exception:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 正確口令：【加點 屬性名稱 點數】（例如：加點 力量 5）"))
                return
        try: pts_to_add = int(pts_str)
        except ValueError:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 點數必須是數字！"))
            return
        free_pts = p.get("attribute_points", 0)
        if pts_to_add <= 0 or free_pts < pts_to_add:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 潛能點不足！剩餘 {free_pts} 點。"))
            return
        attr_mapping = {"力量": "strength", "敏捷": "agility", "智力": "intelligence", "體力": "vitality", "幸運": "luck", "精神": "sprit"}
        if attr_name not in attr_mapping:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 可加點項目：力量、敏捷、智力、體力、幸運、精神。"))
            return
        db_field = attr_mapping[attr_name]
        p[db_field] = p.get(db_field, 10) + pts_to_add
        p["attribute_points"] = free_pts - pts_to_add
        db_core.save_player(p)
        reply_log = f"💪 【配點成功】！你將 {pts_to_add} 點潛能點數分配給了──✨【{attr_name}】屬性！"
        
        card_data = db_core.make_battle_card(reply_log, p, None)
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{
                "type": "flex", "altText": "配點成功",
                "contents": card_data["flex"],
                "quickReply": card_data["quick_reply"]
            }]
        }
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # C. 尋找怪物處理
    elif user_msg in ["尋找怪物", "尋怪"]:
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊底部【😇 祈求復活】小圖卡。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 眼前還有怪物！請點擊底部滑動選單的【🗡️ 攻擊】！"))
            return
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        title_log = f"⚠️ 遭遇強敵！在📍【{current_location}】撞見了對手！\n\n📢 環境狀態：{random_monster['env']}\n🔰 怪物被動：{random_monster['skill']}"
        
        card_data = db_core.make_battle_card(title_log, p, random_monster)
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{
                "type": "flex", "altText": "遭遇怪物",
                "contents": card_data["flex"],
                "quickReply": card_data["quick_reply"]
            }]
        }
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return
    # 處理【技能書】呼叫與 D. 核心戰鬥扣血邏輯
    elif user_msg == "技能書":
        if p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 戰場外無法呼叫戰鬥技能書面板。"))
            return
        active_skills = {k: v for k, v in job_mod["skills"].items() if v.get("type") == "active"}
        if current_job == "初心者" or not active_skills:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 【初心者】階段尚未覺醒 any 秘術招式，請直接普通攻擊！"))
            return
        buttons = []
        for s_name, s_info in active_skills.items():
            buttons.append({
                "type": "button", "style": "primary", "color": "#5856D6", "margin": "xs", "height": "sm",
                "action": {"type": "message", "label": f"🔮 {s_name} (消耗:{s_info.get('mp_cost',0)}MP)", "text": f"使用技能 {s_name}"}
            })
        flex_menu = {
            "type": "bubble",
            "styles": {"body": {"backgroundColor": "#1C1C1E"}},
            "body": {
                "type": "box", "layout": "vertical", "spacing": "sm",
                "contents": [
                    {"type": "text", "text": "📖 勇者神聖法術技能書", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
                    {"type": "text", "text": f"當前魔力殘餘：🔷 {p['mp']} 點", "size": "xs", "color": "#34AADC", "align": "center"},
                    {"type": "separator", "margin": "sm"},
                    {"type": "box", "layout": "vertical", "spacing": "xs", "contents": buttons}
                ]
            }
        }
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟技能書", contents=flex_menu))
        return

    elif user_msg == "攻擊" or user_msg.startswith("使用技能"):
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法發動攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        is_skill = user_msg.startswith("使用技能")
        skill_name = user_msg.replace("使用技能", "").strip() if is_skill else ""
        
        if is_skill:
            if skill_name not in job_mod["skills"]:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 你目前職業不會【{skill_name}】法術！"))
                return
            mp_cost = job_mod["skills"][skill_name].get("mp_cost", 0)
            if p["mp"] < mp_cost:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔷 魔力枯竭！施放【{skill_name}】需要 {mp_cost} 點 MP，你只有 {p['mp']} 點！"))
                return
            p["mp"] -= mp_cost
            log += f"🔮 ✨ 【奧義爆發】！你引導魔能發動了大招 ── ⚡【{skill_name}】！\n"

        # 基礎機率計算
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        evade_chance = min(50, 5 + (agi_val // 8)) / 100.0          
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
        
        # ── 1. 玩家輸出傷害公式實體連動 ──
        total_p_dmg = 0
        if is_skill:
            if skill_name in ["蓄力重擊", "火球術", "二連矢", "治癒術", "神聖盾擊", "毒刃襲擊", "元素暴風", "阿修羅霸凰拳", "極凍終焉", "弒神終結", "聖光懲戒", "暴風萬箭破"]:
                if skill_name == "蓄力重擊":
                    total_p_dmg = int(random.randint(5+(str_val//2)+w_bonus, 12+str_val+w_bonus) * 1.6)
                elif skill_name == "火球術":
                    total_p_dmg = int(int_val * 1.8) + random.randint(10, 30)
                elif skill_name == "二連矢":
                    total_p_dmg = random.randint(4+(agi_val//2), 10+agi_val)*2 + w_bonus
                elif skill_name == "治癒術":
                    h = int((int_val + men_val) * 1.5)
                    max_h = 100 + (vit_val * 5) + (level * 15)
                    old = p["hp"]
                    p["hp"] = min(max_h, p["hp"] + h)
                    total_p_dmg = int(int_val * 0.5)
                    log += f"💖 聖光降臨！大幅恢復了 {p['hp'] - old} 點生命值！\n"
                elif skill_name == "毒刃襲擊":
                    total_p_dmg = int(agi_val * 1.5) + random.randint(15, 25)
                elif skill_name == "弒神終結":
                    total_p_dmg = int((agi_val + luk_val) * 2.5)
                else:
                    total_p_dmg = int((str_val + agi_val + int_val) * 1.5)
                log += f"💥 【{skill_name}】重擊命中，造成 {total_p_dmg} 點致命神聖傷害！\n"
        else:
            is_double = random.random() < double_atk_chance
            for i in range(2 if is_double else 1):
                d = random.randint(5+(str_val//2)+w_bonus, 12+str_val+w_bonus)
                if random.random() < crit_chance:
                    d = int(d * crit_dmg_mod)
                    log += f"💥 致命爆擊！第 {i+1} 擊物理爆擊轟出 {d} 點傷害！\n"
                else: 
                    log += f"⚔️ 第 {i+1} 擊普通命中，造成 {d} 點傷害！\n"
                total_p_dmg += d

        enemy["hp"] -= total_p_dmg
        
        # ── 2. 戰鬥結果判定 ──
        if enemy["hp"] <= 0:
            gold_mod = p.get("map_gold_mod", 1.0)
            
            # 🔮 【List 解包完全修復】精準指定 [0] 與 [1] 的索引位置，徹底瓦解 TypeError 閃退！
            gold_data = enemy["gold_range"]
            final_gold = int(random.randint(int(gold_data[0]), int(gold_data[1])) * gold_mod)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            p["mp"] = min(calculated_max_mp, p.get("mp", calculated_max_mp) + 25)
            
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy['exp']}！\n🔷 戰鬥結束調息，魔力值自然冥想恢復 +25 點。\n"
            
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！搜刮到了素材：【{enemy['drop_item']}】x1！\n"
                
            while p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                p["strength"] = p.get("strength", 10) + 3
                p["agility"] = p.get("agility", 10) + 2
                p["attribute_points"] = p.get("attribute_points", 0) + 5
                log += f"\n🎊 歷練突破！恭喜晉升至 Lv.{p['level']}！獲得潛能點數 +5 點！"
                
            p["hp"] = 100 + (vit_val * 5) + (p["level"] * 15)
            db_core.save_player(p)
            
            card_data = db_core.make_battle_card(log, p, None)
            msg_payload = {
                "replyToken": event.reply_token,
                "messages": [{
                    "type": "flex", "altText": "戰鬥結束",
                    "contents": card_data["flex"],
                    "quickReply": card_data["quick_reply"]
                }]
            }
            with ApiClient(configuration) as api_client:
                MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        else:
            # ── 3. 怪物反擊與環境效果連動 ──
            env_str = enemy.get("env", "")
            if "暴雨滂沱" in env_str: vit_val = int(vit_val * 0.8)
            if "魔能潮汐" in env_str and skill_name == "火球術": log += "🌀 【環境魔能湧動】！火球術威力額外暴衝！\n"
            if "精神污染" in enemy.get("skill", ""):
                p["mp"] = max(0, p["mp"] - 20)
                log += f"\n👁️ 🚨 邪神被動【精神污染】！魔力值被吸走 20 點！"

            final_m_atk = random.randint(1, enemy["atk"])
            if "流沙肆虐" in env_str and random.random() < 0.20:
                log += f"\n💨 怪物利用【流沙掩護】輕巧閃過了你的部分攻勢！"
                
            p_def = vit_val // 2
            dmg_received = max(1, final_m_atk - p_def)
            p["hp"] -= dmg_received
            log += f"\n🩹 【{enemy['name']}】發動反擊！你受到 {dmg_received} 點物理傷害！"
            
            if p["hp"] <= 0:
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你受傷過重陣亡了！請點擊底部【😇 祈求復活】小圖卡。"
                db_core.save_player(p)
                card_data = db_core.make_battle_card(log, p, None)
            else:
                db_core.MEMORY_PLAYERS[event.source.user_id] = p
                card_data = db_core.make_battle_card(log, p, enemy)
                
            msg_payload = {
                "replyToken": event.reply_token,
                "messages": [{
                    "type": "flex", "altText": "戰鬥回合",
                    "contents": card_data["flex"],
                    "quickReply": card_data["quick_reply"]
                }]
            }
            with ApiClient(configuration) as api_client:
                MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方 QuickReply 智慧小按鈕開始冒險！"))
