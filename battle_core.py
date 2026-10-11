import random
from linebot.models import TextSendMessage, FlexSendMessage

import db_core
import monsters
import weapons
import bag
import jobs

def process_battle_logic(event, line_bot_api, p, user_msg):
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 六大屬性初始化與計算
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
    
    # 動態計算最大魔力，並設定目前 MP
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    if "mp" not in p:
        p["mp"] = calculated_max_mp

    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0

    # A. 轉職處理
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
        log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n🛡️ 你從【{current_job}】正式進階為更高的職業形態——🔥【{target_job}】！\n專屬天賦加成已全線翻倍刷新！快輸入【我的狀態】查看全新戰力！"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="轉職成功", contents=db_core.make_battle_card(log_text, p, None)))
        return

    # 轉職卡關防呆
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["尋找怪物", "尋怪", "攻擊", "技能"]:
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】\n勇者！你目前已達到了 Lv.{p['level']} 的天賦瓶頸，必須完成天賦覺醒才能繼續獲取經驗與冒險！\n\n{job_notice}"))
            return

    # B. 處理【加點 / 配點】指令判定 (完美相容有無空白格式)
    if user_msg.startswith("加點") or user_msg.startswith("配點"):
        # 🧪 【無痛字串全自動拆解】直接從乾淨的原始訊息中提取屬性與數字
        clean_msg = event.message.text.strip().replace("配點", "加點")
        raw_parts = clean_msg.split()
        
        # 如果玩家輸入有帶空白 (例如: 加點 力量 200)
        if len(raw_parts) == 3:
            attr_name = raw_parts[1].strip()
            pts_str = raw_parts[2].strip()
        else:
            # 如果空白被 game_core 剃除了 (例如: 加點力量200)
            # 嘗試用關鍵字切開
            try:
                target_str = clean_msg.replace("加點", "") # 剩餘 "力量200"
                attr_name = target_str[:2] # 抓前兩個字 "力量"
                pts_str = target_str[2:]   # 抓後面的數字 "200"
            except Exception:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 格式錯誤！正確口令：【加點 屬性名稱 點數】\n（例如：加點 力量 5）"))
                return
                
        try: 
            pts_to_add = int(pts_str)
        except ValueError:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 點數必須是阿拉伯數字！"))
            return
            
        free_pts = p.get("attribute_points", 0)
        if pts_to_add <= 0 or free_pts < pts_to_add:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 點數分配不合法或潛能點不足！你目前剩餘 {free_pts} 點。"))
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
        return

    # C. 尋找怪物處理
    elif user_msg in ["尋找怪物", "尋怪"]:
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】重整旗鼓。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 你的眼前還卡著一隻怪！請專心應戰（輸入【攻擊】或【技能】）！"))
            return
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        env_now = p.get("map_env_status", "🟢 平靜")
        title_log = f"⚠️ 警報！你在📍【{current_location}】遭遇強敵！\n當前天象：【{env_now}】\n怪物能力：🔰 {random_monster['skill']}"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(title_log, p, random_monster)))
        return

    # D. ✨ 企劃一：處理【攻擊】與【技能】核心戰鬥邏輯
    elif user_msg in ["攻擊", "技能"]:
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        is_using_skill = (user_msg == "技能")
        
        # 讀取當前職業解鎖的所有可用主動招式清單
        available_skills = {k: v for k, v in job_mod["skills"].items() if v.get("type") == "active"}
        
        if is_using_skill:
            if current_job == "初心者" or not available_skills:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 【初心者】階段尚未覺醒任何秘術主動技能，請先使用【攻擊】普通揮砍！"))
                return
            
            # 自動抓取該職業的第一個主動技能
            skill_name = list(available_skills.keys())[0]
            skill_info = available_skills[skill_name]
            mp_cost = skill_info.get("mp_cost", 0)
            
            # 檢查魔力是否足夠
            if p["mp"] < mp_cost:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔷 魔力枯竭！施放【{skill_name}】需要 {mp_cost} 點 MP，你目前只有 {p['mp']} 點！"))
                return
                
            # 扣除魔力
            p["mp"] -= mp_cost
            log += f"🔮 ✨ 【奧義爆發】！你消耗了 {mp_cost} 點魔力，發動了天賦大招 ── ⚡【{skill_name}】！\n"
        
        # 🎲 屬性機率公式連動
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        evade_chance = min(50, 5 + (agi_val // 8)) / 100.0          
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
        
        # ── 1. 玩家輸出計算 ──
        total_p_dmg = 0
        
        if is_using_skill:
            # 🔮 各職業專屬技能傷害公式實體連動！
            skill_name = list(available_skills.keys())[0]
            if skill_name == "蓄力重擊":
                # 戰士/狂戰士/修羅：物理基礎傷害 1.6 倍
                base_dmg = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
                total_p_dmg = int(base_dmg * 1.6)
                log += f"💥 重擊命中！對怪物造成高達 {total_p_dmg} 點巨額物理重傷！\n"
            elif skill_name == "火球術":
                # 魔法師/魔導士/元素使：智力倍率 1.8 倍
                total_p_dmg = int(int_val * 1.8) + random.randint(10, 30)
                log += f"🔥 烈焰吞噬！火球轟鳴炸裂，造成 {total_p_dmg} 點致命烈火魔傷！\n"
            elif skill_name == "二連矢":
                # 弓箭手/獵人/遊俠：必定射出兩箭
                for i in range(2):
                    d = random.randint(4 + (agi_val // 2), 10 + agi_val) + w_bonus
                    total_p_dmg += d
                    log += f"🏹 飛箭疾射！第 {i+1} 箭穿透防線，造成 {d} 點物理傷害！\n"
            elif skill_name == "治癒術":
                # 祭師/賢者/大主教：主動大補血，同時造成微量神聖魔傷
                heal_amt = int((int_val + men_val) * 1.5)
                old_hp = p["hp"]
                calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
                p["hp"] = min(calculated_max_hp, p["hp"] + heal_amt)
                total_p_dmg = int(int_val * 0.5)  # 附帶神聖微量魔傷
                log += f"💖 聖光降臨！大幅恢復了 {p['hp'] - old_hp} 點生命值！並附帶神聖餘波重創怪物 {total_p_dmg} 點！\n"
            elif skill_name == "神聖盾擊":
                # 十字軍/督軍：防禦力的 2.5 倍轉化為傷害
                defense_val = vit_val // 2
                total_p_dmg = int(defense_val * 2.5) + random.randint(5, 15)
                log += f"🛡️ 盾牌猛擊！鐵壁神聖橫掃，造成 {total_p_dmg} 點神聖破防衝擊！\n"
            elif skill_name == "毒刃襲擊":
                # 刺客/暗夜行者：敏捷增幅 1.5 倍，必定命中不被閃避
                total_p_dmg = int(agi_val * 1.5) + random.randint(15, 25)
                log += f"🩸 毒刃襲擊！背刺魅影閃現，對怪物造成 {total_p_dmg} 點毒素劇傷（此招無視閃避）！\n"
            elif skill_name == "元素暴風":
                total_p_dmg = int(int_val * random.uniform(2.5, 3.5))
                log += f"🌪️ 元素暴風狂嘯！虛空魔能傾瀉，粉碎怪物造成 {total_p_dmg} 點奧術暴轟！\n"
            elif skill_name == "阿修羅霸凰拳":
                total_p_dmg = int(str_val * random.uniform(4.0, 6.0))
                log += f"🔥 燃燒靈魂！阿修羅霸凰拳轟碎一切虛無，造成極致毀滅性傷害 {total_p_dmg} 點！\n"
            elif skill_name == "極凍終焉":
                total_p_dmg = int(int_val * 5.0)
                log += f"❄️ 絕對零度爆發！極凍終焉將戰場凍結，降下 {total_p_dmg} 點極致魔傷！\n"
            elif skill_name == "弒神終結":
                total_p_dmg = int((agi_val + luk_val) * 2.5)
                log += f"💥 隱匿弒神終結！黑夜之刃瞬殺，造成 {total_p_dmg} 點物理極限致命重傷！\n"
            elif skill_name == "聖光懲戒":
                total_p_dmg = int(men_val * 2.2)
                log += f"✨ 聖光懲戒法陣！天劫神雷降臨，湮滅怪物 {total_p_dmg} 點法術傷害！\n"
            elif skill_name == "暴風萬箭破":
                total_p_dmg = int(agi_val * random.uniform(3.8, 5.0))
                log += f"🎯 暴風萬箭破！漫天箭雨攜帶風行者之力，傾瀉致命巨傷 {total_p_dmg} 點！\n"
            else:
                total_p_dmg = random.randint(5 + (str_val // 2) + w_bonus, 12 + str_val + w_bonus)
                log += f"⚔️ 命中對手，造成 {total_p_dmg} 點基礎傷害！\n"
        else:
            # 普通攻擊（保留原有的神速連擊與暴擊公式）
            is_double_atk = random.random() < double_atk_chance
            attack_count = 2 if is_double_atk else 1
            if is_double_atk:
                log += f"🌪️ 🚀 【神速連擊】！！發動了雙重連續攻擊！\n"
            
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

        # 扣減怪物血量
        enemy["hp"] -= total_p_dmg
        
        # ── 2. 戰鬥結果判定 ──
        if enemy["hp"] <= 0:
            # 擊殺怪物結算
            min_m_dmg = 3 + (int_val // 2)
            max_m_dmg = 10 + int_val
            m_dmg = random.randint(min_m_dmg, max_m_dmg)
        # ── 2. 戰鬥結果判定（與前半部的 enemy["hp"] -= total_p_dmg 對齊） ──
        if enemy["hp"] <= 0:
            # 擊殺怪物結算
            min_m_dmg = 3 + (int_val // 2)
            max_m_dmg = 10 + int_val
            m_dmg = random.randint(min_m_dmg, max_m_dmg)
            
            gold_mod = p.get("map_gold_mod", 1.0)
            # 💰 【黃金絕殺解包】精準解包 tuple 索引，防範類型錯誤
            base_gold = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            final_gold = int(base_gold * gold_mod)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            
            # ✨ 企劃一：擊殺怪物時，自然冥想恢復 25 點 MP 魔力
            calculated_max_mp = 50 + (men_val * 4) + (level * 5)
            p["mp"] = min(calculated_max_mp, p.get("mp", calculated_max_mp) + 25)
            
            log += f"✨ 🔮 智力附加！最終凝聚魔法追加爆轟，造成 {m_dmg} 點魔傷！\n"
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}、經驗值 +{enemy['exp']}！\n"
            log += f"🔷 戰鬥結束調息，勇者魔力值自然冥想恢復 +25 點。\n"
            
            # 幸運掉寶
            if random.random() < 0.50 and enemy.get("drop_item"):
                import bag as bg_mod
                bg_mod.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！搜刮到了素材：【{enemy['drop_item']}】x1！\n"
                
            # 升級判定機制
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
            
            # 檢查是否觸發等級死鎖臨界點，是的話拋出轉職提示
            if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
            
        else:
            # ── 3. 怪物反擊與特殊技能機制（與 if enemy["hp"] <= 0 對齊） ──
            dmg_mod = p.get("map_dmg_mod", 1.0)
            base_m_atk = random.randint(1, enemy["atk"])
            final_m_atk = int(base_m_atk * dmg_mod)
            
            # ✨ 企劃二：至高邪神克蘇魯被動技能發動，吸乾魔力
            if "精神污染" in enemy.get("skill", ""):
                p["mp"] = max(0, p["mp"] - 20)
                log += f"\n👁️ 🚨 邪神被動【精神污染】發動！不可名狀的瘋狂低語奪走了你 20 點 MP 魔力！"
            
            # 判斷勇者是否閃避反擊
            is_p_evade = (random.random() < evade_chance) if (user_msg != "技能" or skill_name != "毒刃襲擊") else False
            
            if is_p_evade:
                log += f"\n💨 殘影！你發動敏捷身法，【完美閃避】了怪物的反擊傷害！"
            else:
                p_defense = vit_val // 2
                final_received_dmg = max(1, final_m_atk - p_defense)
                p["hp"] -= final_received_dmg
                log += f"\n🩹 【{enemy['name']}】發動反擊！你受到 {final_received_dmg} 點物理傷害！"
                if p_defense > 0:
                    log += f" (體力防禦減免 -{p_defense} 點)"
            
            # 檢查勇者是否死亡
            if p["hp"] <= 0:
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你受傷過重被擊倒了！請點擊【復活】重整旗鼓。"
                db_core.save_player(p)
                card = db_core.make_battle_card(log, p, None)
            else:
                # 戰鬥未結束，暫存入記憶體快取
                db_core.MEMORY_PLAYERS[event.source.user_id] = p
                card = db_core.make_battle_card(log, p, enemy)
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
