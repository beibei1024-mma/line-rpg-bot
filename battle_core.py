import random
from linebot.models import TextSendMessage, FlexSendMessage

# 🎮 跨檔案調用基礎庫
import db_core
import monsters
import weapons
import bag
import jobs

def process_battle_logic(event, line_bot_api, p, user_msg):
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])

    # 🧮 六大屬性實體公式連動
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
    
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0

    # A. 處理【轉職】天賦進階判定
    if user_msg.startswith("轉職"):
        target_job = user_msg.replace("轉職", "").strip()
        if target_job not in jobs.JOBS_DATA:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！秘法圖鑑中不存在【{target_job}】這個職業。"))
            return
        target_info = jobs.JOBS_DATA[target_job]
        if target_job not in job_mod["next_jobs"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！你目前的本命職業是【{current_job}】，無法跨系進階。"))
            return
        if p["level"] < target_info["req_lvl"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 境界未到！轉職為【{target_job}】需要突破至 Lv.{target_info['req_lvl']}+。"))
            return
            
        p["job"] = target_job
        db_core.save_player(p)
        log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n🛡️ 你從【{current_job}】正式進階為更高的職業形態——🔥【{target_job}】！\n專屬天賦加成已全線翻倍刷新！卡關狀態已解除，快輸入【我的狀態】查看全新戰力！"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="轉職成功", contents=db_core.make_battle_card(log_text, p, None)))
        return

    # 🚨 【真・轉職卡關防呆強制判定】
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["尋找怪物", "尋怪", "攻擊"]:
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】\n勇者！你目前已達到了 Lv.{p['level']} 的天賦瓶頸，必須完成天賦覺醒才能繼續獲取經驗與冒險！\n\n{job_notice}"))
            return

    # B. 處理【加點 / 配點】指令判定
    if user_msg.startswith("加點") or user_msg.startswith("配點"):
        raw_msg = event.message.text.strip().split()
        if len(raw_msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 格式錯誤！正確口令：【加點 屬性名稱 點數】\n（例如：加點 敏捷 5）"))
            return
        attr_name = raw_msg[1].strip()
        try: pts_to_add = int(raw_msg[2].strip())
        except ValueError:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 點數必須是阿拉伯數字！"))
            return
        free_pts = p.get("attribute_points", 0)
        if pts_to_add <= 0 or free_pts < pts_to_add:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 點數分配不合法或潛能點不足！"))
            return
        attr_mapping = {"力量": "strength", "敏捷": "agility", "智力": "intelligence", "體力": "vitality", "幸運": "luck", "精神": "sprit"}
        if attr_name not in attr_mapping:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 可加點項目：力量、敏捷、智力、體力、幸運、精神。"))
            return
        db_field = attr_mapping[attr_name]
        p[db_field] = p.get(db_field, 10) + pts_to_add
        p["attribute_points"] = free_pts - pts_to_add
        db_core.save_player(p)
        reply_log = f"💪 🧪 【配點成功】 🧪 💪\n你成功將 {pts_to_add} 點潛能自由點數，分配給了──✨【{attr_name}】屬性！\n\n🔹 剩餘未分配點數：{p['attribute_points']} 點。"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="配點成功", contents=db_core.make_battle_card(reply_log, p, None)))

    # C. 處理【尋找怪物】判定
    elif user_msg == "尋找怪物" or user_msg == "尋怪":
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】重整旗鼓。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 你的眼前還卡著一隻怪！請專心應戰（輸入【攻擊】揮刀，或輸入【逃跑】）！"))
            return
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        env_now = p.get("map_env_status", "🟢 平靜")
        title_log = f"⚠️ 警報！你在📍【{current_location}】遭遇強敵！\n當前天象：【{env_now}】\n怪物能力：🔰 {random_monster['skill']}"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(title_log, p, random_monster)))

    # D. 處理【攻擊】判定
    elif user_msg == "攻擊":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        evade_chance = min(50, 5 + (agi_val // 8)) / 100.0          
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
        
        is_double_atk = random.random() < double_atk_chance
        attack_count = 2 if is_double_atk else 1
        
        if is_double_atk:
            log += f"🌪️ 🚀 【神速連擊】！！發動了雙重連續攻擊！\n"
            
        total_p_dmg = 0
        for i in range(attack_count):
            min_p_dmg = 5 + (str_val // 2) + w_bonus
            max_p_dmg = 12 + str_val + w_bonus
            p_dmg = random.randint(min_p_dmg, max_p_dmg)
            
            is_crit = random.random() < crit_chance
            if is_crit:
                p_dmg = int(p_dmg * crit_dmg_mod)
                log += f"💥 🔥 【致命爆擊】！第 {i+1} 刀物理爆擊傷害 {p_dmg} 點！\n"
            else:
                log += f"⚔️ 第 {i+1} 刀物理命中，造成 {p_dmg} 點傷害！\n"
            total_p_dmg += p_dmg
            
        enemy["hp"] -= total_p_dmg
        
        if enemy["hp"] <= 0:
            min_m_dmg = 3 + (int_val // 2)
            max_m_dmg = 10 + int_val
            m_dmg = random.randint(min_m_dmg, max_m_dmg)
            
            gold_mod = p.get("map_gold_mod", 1.0)
            base_gold = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            final_gold = int(base_gold * gold_mod)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            
            log += f"✨ 🔮 智力附加！最終凝聚魔法追加爆轟，造成 {m_dmg} 點魔傷！\n"
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy['exp']}！\n"
            
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！搜刮到了素材：【{enemy['drop_item']}】x1！\n"
                
            while p["exp"] >= p["level"] * 50:
                if p["level"] == 24 and job_mod["tier"] == 0:
                    p["level"] = 25
                    p["exp"] = 0
                    log += f"\n突破！你的等級已卡死在 Lv.25 轉職臨界點！請先手動完成天賦轉職！"
                    break
                elif p["level"] == 49 and job_mod["tier"] == 1:
                    p["level"] = 50
                    p["exp"] = 0
                    log += f"\n突破！你的等級已卡死在 Lv.50 二轉臨界點！請先手動完成天賦轉職！"
                    break
                elif p["level"] == 99 and job_mod["tier"] == 2:
                    p["level"] = 100
                    p["exp"] = 0
                    log += f"\n突破！你的等級已卡死在 Lv.100 三轉臨界點！請先手動完成天賦轉職！"
                    break
                    
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                p["strength"] = p.get("strength", 10) + 3
                p["agility"] = p.get("agility", 10) + 2
                p["intelligence"] = p.get("intelligence", 10) + 2
                p["vitality"] = p.get("vitality", 10) + 3
                p["luck"] = p.get("luck", 10) + 1
                p["sprit"] = p.get("sprit", 10) + 2
                p["attribute_points"] = p.get("attribute_points", 0) + 5
                log += f"\n🎊 👑 歷練突破！恭喜晉升至 Lv.{p['level']}！獲得潛能點數 +5 點！"
                
            new_vit = int(p.get("vitality", 10) * job_mod["vit_mod"])
            calculated_max_hp = 100 + (new_vit * 5) + (p["level"] * 15)
            p["max_hp"] = calculated_max_hp
            p["hp"] = calculated_max_hp
            log += f"\n💚 當前生命狀態已完全補滿（{calculated_max_hp}/{calculated_max_hp}）！"
            
            db_core.save_player(p)
            
            if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
        else:
            # 🔮 先算好怪物本次反擊的基礎破壞力，確保下方變數 100% 存在，消滅 NameError！
            dmg_mod = p.get("map_dmg_mod", 1.0)
            base_m_atk = random.randint(1, enemy["atk"])
            final_m_atk = int(base_m_atk * dmg_mod)

            is_p_evade = random.random() < evade_chance
         if is_p_evade:
             log += f"💨 殘影！你發動敏捷身法，【完美閃避】了怪物的反擊傷害！"
         else:
             p_defense = vit_val // 2
             final_received_dmg = max(1, final_m_atk - p_defense)
             p["hp"] -= final_received_dmg
             log += f"🩹 【{enemy['name']}】發動反擊！你受到 {final_received_dmg} 點物理傷害！"
             if p_defense > 0:
                 log += f" (體力防禦減免 -{p_defense} 點)"

            
            if p["hp"] <= 0:
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你受傷過重被擊倒了！請點擊【復活】重整旗鼓。"
                db_core.save_player(p)
                card = db_core.make_battle_card(log, p, None)
            else:
                db_core.MEMORY_PLAYERS[event.source.user_id] = p
                card = db_core.make_battle_card(log, p, enemy)
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方選單開始遊戲！"))
