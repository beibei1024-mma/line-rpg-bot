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
    """【純粹戰鬥計算機 v1.0】所有非戰鬥系統全數分家，縮排完美對齊"""
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

    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0

    # 1. 轉職卡關防呆 (純讀取，不執行轉職動作)
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["尋找怪物", "尋怪", "攻擊", "技能書", "使用技能"]:
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】請先完成手動天賦轉職！\n\n{job_notice}"))
            return

    # 2. 尋找怪物處理
    elif user_msg in ["尋找怪物", "尋怪"]:
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 你已經陣亡了！請點擊底部【😇 祈求復活】小圖卡。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"⚔️ 眼前還有怪物！請點擊底部滑動選單的【🗡️ 攻擊】！"))
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

    # 3. 戰鬥技能書呼叫
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
            buttons.append({"type": "button", "style": "primary", "color": "#5856D6", "margin": "xs", "height": "sm", "action": {"type": "message", "label": f"🔮 {s_name} (消耗:{s_info.get('mp_cost',0)}MP)", "text": f"使用技能 {s_name}"}})
        flex_menu = {"type": "bubble", "styles": {"body": {"backgroundColor": "#1C1C1E"}}, "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [{"type": "text", "text": "📖 勇者神聖法術技能書", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"}, {"type": "text", "text": f"當前魔力殘餘：🔷 {p.get('mp', calculated_max_mp)} 點", "size": "xs", "color": "#34AADC", "align": "center"}, {"type": "separator", "margin": "sm"}, {"type": "box", "layout": "vertical", "spacing": "xs", "contents": buttons}]}}
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟技能書", contents=flex_menu))
        return
    # 4. 核心戰鬥揮刀與技能扣血邏輯
    elif user_msg == "攻擊" or user_msg.startswith("使用技能"):
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法發動攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        is_skill = user_msg.startswith("使用技能")
        skill_name = user_msg.replace("使用技能", "").strip() if is_skill else ""
        
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
        
        total_p_dmg = 0
        if is_skill:
            if skill_name in ["蓄力重擊", "火球術", "二連矢", "治癒術", "神聖盾擊", "毒刃襲擊", "元素暴風", "阿修羅霸凰拳", "極凍終焉", "弒神終結", "聖光懲戒", "暴風萬箭破"]:
                if skill_name == "蓄力重擊": total_p_dmg = int(random.randint(5+(str_val//2)+w_bonus, 12+str_val+w_bonus) * 1.6)
                elif skill_name == "火球術": total_p_dmg = int(int_val * 1.8) + random.randint(10, 30)
                elif skill_name == "二連矢": total_p_dmg = random.randint(4+(agi_val//2), 10+agi_val)*2 + w_bonus
                elif skill_name == "毒刃襲擊": total_p_dmg = int(agi_val * 1.5) + random.randint(15, 25)
                elif skill_name == "弒神終結": total_p_dmg = int((agi_val + luk_val) * 2.5)
                else: total_p_dmg = int((str_val + agi_val + int_val) * 1.5)
                log += f"🔮 【{skill_name}】爆發！轟出 {total_p_dmg} 點致命魔法傷害！\n"
        else:
            is_double = random.random() < double_atk_chance
            for i in range(2 if is_double else 1):
                d = random.randint(5+(str_val//2)+w_bonus, 12+str_val+w_bonus)
                if random.random() < crit_chance:
                    d = int(d * crit_dmg_mod)
                    log += f"💥 致命爆擊！第 {i+1} 擊斬出 {d} 點爆擊傷害！\n"
                else: log += f"⚔️ 第 {i+1} 擊命中，造成 {d} 點物理傷害！\n"
                total_p_dmg += d

        enemy["hp"] -= total_p_dmg
        
        # ── 5. 戰鬥大獲全勝結算 ──
        if enemy["hp"] <= 0:
            gold_mod = p.get("map_gold_mod", 1.0)
            gold_data = enemy["gold_range"]
            
            # ✨ 【Bug 終極封印】精準抓取元組/列表的第 0 位與第 1 位進行數字提煉，徹底消滅 tuple 轉換閃退！
            min_gold = int(gold_data[0])
            max_gold = int(gold_data[1])
            final_gold = int(random.randint(min_gold, max_gold) * gold_mod)
            
            p["gold"] += final_gold; p["exp"] += enemy["exp"]
            
            p["mp"] = min(calculated_max_mp, (p.get("mp") if p.get("mp") is not None else calculated_max_mp) + 25)
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy['exp']}！\n🔷 戰鬥結束調息，魔力值恢復 +25 點。\n"
            
            # 5% 爆區域專屬神裝 (放回背包連動)
            if random.random() < 0.05:
                current_loc = p.get("current_map", "新手村")
                matched_weapons = [w_name for w_name in weapons.SHOP_WEAPONS.keys() if current_loc[:2] in w_name or (current_loc == "新手村" and "新手" in w_name)]
                if matched_weapons:
                    drop_w = random.choice(matched_weapons); old_w = p.get("weapon", "赤手空拳")
                    if old_w != "赤手空拳": forge_system.add_to_weapon_inventory(p, old_w)
                    p["weapon"] = drop_w
                    log += f"💎 🔥 【神裝降臨】！你驚喜搜刮到了專屬神兵：⚔️【{drop_w}】！已全自動換裝！\n"

            # 📢 全服世界公告
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
                msg_payload["messages"].append({"type": "text", "text": f"🔒 【天賦界限卡關中】\n勇者！你目前已達到了 Lv.{p['level']} 的天賦瓶頸，必須完成天賦轉職才能繼續獲取經驗！\n\n{jobs.get_job_options_text(p)}"})
                
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)
                messaging_api.reply_message(ReplyMessageRequest.from_dict(msg_payload))
        else:
            # ── 6. 怪物殘存與環境反擊 ──
            env_str = enemy.get("env", "")
            if "暴雨滂沱" in env_str: vit_val = int(vit_val * 0.8)
            if "精神污染" in enemy.get("skill", ""): p["mp"] = max(0, (p.get("mp") if p.get("mp") is not None else calculated_max_mp) - 20); log += f"\n👁️ 🚨 邪神被動【精神污染】！魔力值被吸走 20 點！"

            final_m_atk = random.randint(1, enemy["atk"])
            p_def = vit_val // 2
            dmg_received = max(1, final_m_atk - p_def)
            p["hp"] = max(0, p["hp"] - dmg_received)
            log += f"\n🩹 【{enemy['name']}】發動反擊！你受到 {dmg_received} 點物理傷害！"
            
            if p["hp"] <= 0:
                p["enemy"] = None; log += "\n💀 你受傷過重陣亡了！請點擊底部【😇 祈求復活】小圖卡。"
                db_core.save_player(p); card_data = db_core.make_battle_card(log, p, None)
            else:
                db_core.MEMORY_PLAYERS[event.source.user_id] = p; card_data = db_core.make_battle_card(log, p, enemy)
                
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "戰鬥回合", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)
                messaging_api.reply_message(ReplyMessageRequest.from_dict(msg_payload))
    else:
        card_data = db_core.make_battle_card("💡 系統提示：請利用螢幕最下方可以左右橫向滑動的小圖標，直接點擊按鈕來展開您的冒險旅程！", p, None)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "冒險導引", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message(ReplyMessageRequest.from_dict(msg_payload))
