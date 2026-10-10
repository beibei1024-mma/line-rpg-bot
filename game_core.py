import random
import json
from linebot.models import TextSendMessage, FlexSendMessage

# 🎮 跨檔案導入你全新優化、完全模組化分離的 9 大黃金頁面
import db_core
import player
import monsters
import weapons
import shop
import bag
import maps
import jobs

def process_game_logic(event, line_bot_api):
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    # 從資料庫核心讀取玩家與記憶體快取資料
    p = db_core.load_player(user_id)
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
        p["job"] = "初心者"
        
    job_mod = jobs.JOBS_DATA[current_job]

    # 🧮 【原創六大天賦實體衍生數值公式計算 - 基礎值完美疊加玩家的手動配點】
    base_str = p.get("strength", 10 + (level * 3))
    base_agi = p.get("agility", 10 + (level * 2))
    base_int = p.get("intelligence", 10 + (level * 2))
    base_vit = p.get("vitality", 10 + (level * 3))
    base_luk = p.get("luck", 10 + (level * 1))
    base_men = p.get("sprit", 10 + (level * 2))
    
    # 乘上本命職業專屬加成倍率
    str_val = int(base_str * job_mod["str_mod"])
    agi_val = int(base_agi * job_mod["agi_mod"])
    int_val = int(base_int * job_mod["int_mod"])
    vit_val = int(base_vit * job_mod["vit_mod"])
    luk_val = int(base_luk * job_mod["luk_mod"])
    men_val = int(base_men * job_mod["men_mod"])
    
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0

    # 1. 處理【我的狀態】判定
    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.get_status_text(p)))
        
    # 2. 處理【我的背包】判定
    elif user_msg == "我的背包":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.get_bag_text(p)))
        
    # 3. 處理【世界地圖】傳送陣清單查詢判定
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.get_maps_list_text(p)))
        
    # 4. 處理【前往 / 傳送】指令判定
    elif user_msg.startswith("前往") or user_msg.startswith("傳送"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.change_map(p, user_msg)))
        
    # 5. 處理【使用】藥水道具指令判定
    elif user_msg.startswith("使用"):
        potion_name = user_msg.replace("使用", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.use_potion(p, potion_name)))
        
    # 6. 處理【冒險商店】面板開啟判定
    elif user_msg == "冒險商店":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
        
    # 7. 處理【購買物品】判定
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        
    # 8. 處理【轉職】天賦覺醒本命死鎖升階指令核心判定
    elif user_msg.startswith("轉職"):
        target_job = user_msg.replace("轉職", "").strip()
        if target_job not in jobs.JOBS_DATA:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！秘法圖鑑中不存在【{target_job}】這個職業。"))
            return
        target_info = jobs.JOBS_DATA[target_job]
        if target_job not in job_mod["next_jobs"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！你目前的本命職業是【{current_job}】，無法跨系覺醒為【{target_job}】。"))
            return
        if p["level"] < target_info["req_lvl"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 境界未到！轉職為【{target_job}】需要突破至 Lv.{target_info['req_lvl']}+，你目前只有 Lv.{p['level']}。"))
            return
        p["job"] = target_job
        db_core.save_player(p)
        log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n勇者，你成功打破命運桎梏，本命血脈引來瘋狂覺醒！\n\n🛡️ 你從【{current_job}】正式進階為更高的職業形態——🔥【{target_job}】！\n專屬天賦加成已全線翻倍刷新！快輸入【我的狀態】查看全新戰力！"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="轉職成功", contents=db_core.make_battle_card(log_text, p, None)))

    # 🛠️ 8.5. 處理【加點 / 配點】自由分配屬性點核心指令判定
    elif user_msg.startswith("加點") or user_msg.startswith("配點"):
        # 拆解格式：加點 敏捷 5
        raw_msg = event.message.text.strip().split()
        if len(raw_msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 格式錯誤！正確口令請打：【加點 屬性名稱 點數】\n（例如：加點 敏捷 5）"))
            return
        attr_name = raw_msg[1].strip()
        try: pts_to_add = int(raw_msg[2].strip())
        except ValueError:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 點數必須是阿拉伯數字！"))
            return
        free_pts = p.get("attribute_points", 0)
        if pts_to_add <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 分配的潛能點數必須大於 0 點！"))
            return
        if free_pts < pts_to_add:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 潛能點不足！你目前僅剩餘 {free_pts} 點未分配點數。"))
            return
            
        attr_mapping = {"力量": "strength", "敏捷": "agility", "智力": "intelligence", "體力": "vitality", "幸運": "luck", "精神": "sprit"}
        if attr_name not in attr_mapping:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 找不到該屬性！可加點項目：力量、敏捷、智力、體力、幸運、精神。"))
            return
            
        db_field = attr_mapping[attr_name]
        # 實體疊加配點並扣除自由點數
        p[db_field] = p.get(db_field, 10 + (level * 2)) + pts_to_add
        p["attribute_points"] = free_pts - pts_to_add
        db_core.save_player(p)
        
        reply_log = f"💪 🧪 【配點成功】 🧪 💪\n天賦潛能完全實體化！你成功將 {pts_to_add} 點潛能自由點數，分配給了──✨【{attr_name}】屬性！\n\n🔹 剩餘未分配點數：{p['attribute_points']} 點。\n快輸入指令【我的狀態】查看衍生物理傷害、連擊率等戰力的暴漲暴風吧！"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="配點成功", contents=db_core.make_battle_card(reply_log, p, None)))

    # 9. 處理【尋找怪物】判定
    elif user_msg == "尋找怪物" or user_msg == "尋怪":
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】重整旗鼓。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card("⚔️ 你的眼前還卡著一隻怪！請專心應戰！", p, p["enemy"])))
            return

        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        env_now = p.get("map_env_status", "🟢 平靜")
        title_log = f"⚠️ 警報！你在📍【{current_location}】遭遇強敵！\n當前天象：【{env_now}】\n怪物能力：🔰 {random_monster['skill']}"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(title_log, p, p["enemy"])))
    # 10. 處理【攻擊】包含「基礎能力、職業加成、物理連擊、魔傷附加、爆擊閃避」的原創回合判定
    elif user_msg == "攻擊":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        
        # 🧮 基礎機率與公式計算對齊
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        evade_chance = min(50, 5 + (agi_val // 8)) / 100.0          
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
        
        # 🎲 本命敏捷連續攻擊判定
        is_double_atk = random.random() < double_atk_chance
        attack_count = 2 if is_double_atk else 1
        
        if is_double_atk:
            log += f"🌪️ 🚀 【神速連擊】！！你身形化為疾風，發動了雙重連續攻擊！\n"
            
        total_p_dmg = 0
        for i in range(attack_count):
            min_p_dmg = 5 + (str_val // 2) + w_bonus
            max_p_dmg = 12 + str_val + w_bonus
            p_dmg = random.randint(min_p_dmg, max_p_dmg)
            
            is_crit = random.random() < crit_chance
            if is_crit:
                p_dmg = int(p_dmg * crit_dmg_mod)
                log += f"💥 🔥 【致命爆擊】！第 {i+1} 刀揮出物理爆擊傷害 {p_dmg} 點！\n"
            else:
                log += f"⚔️ 第 {i+1} 刀物理命中，造成 {p_dmg} 點傷害！\n"
            total_p_dmg += p_dmg
            
        enemy["hp"] -= total_p_dmg
        
        # ── 檢查怪物是否死亡 ──
        if enemy["hp"] <= 0:
            min_m_dmg = 3 + (int_val // 2)
            max_m_dmg = 10 + int_val
            m_dmg = random.randint(min_m_dmg, max_m_dmg)
            
            gold_mod = p.get("map_gold_mod", 1.0)
            # 💯 【真・黃金絕殺防呆】精準抓取元組的第一位和第二位，徹底消滅 TypeError 地雷！
            base_gold = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            final_gold = int(base_gold * gold_mod)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            
            log += f"✨ 🔮 智力附加！最終凝聚魔法追加爆轟，造成 {m_dmg} 點魔傷！\n"
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}"
            if gold_mod > 1.0:
                log += f" (含天象加成 {int((gold_mod-1)*100)}%)"
            log += f"、經驗值 +{enemy['exp']}！\n"
            
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！搜刮到了素材：【{enemy['drop_item']}】x1！\n"
                
            # 👑 【While 連續升級與屬性成長、潛能發放公式】
            while p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                
                # 基礎屬性連續成長
                p["strength"] = p.get("strength", 10) + 3
                p["agility"] = p.get("agility", 10) + 2
                p["intelligence"] = p.get("intelligence", 10) + 2
                p["vitality"] = p.get("vitality", 10) + 3
                p["luck"] = p.get("luck", 10) + 1
                p["sprit"] = p.get("sprit", 10) + 2
                
                # 👑 【潛能獎勵發放】每升一級，未分配潛能點實體增加 5 點！
                p["attribute_points"] = p.get("attribute_points", 0) + 5
                
                log += f"\n🎊 👑 歷練突破！恭喜晉升至 Lv.{p['level']}！獲得潛能點數 +5 點！"
                
            # 動態核算最新生命上限並回滿血
            new_vit = int(p.get("vitality", 10) * job_mod["vit_mod"])
            calculated_max_hp = 100 + (new_vit * 5) + (p["level"] * 15)
            p["max_hp"] = calculated_max_hp
            p["hp"] = calculated_max_hp
            log += f"\n💚 當前生命狀態已完全補滿（{calculated_max_hp}/{calculated_max_hp}）！"
            
            db_core.save_player(p)
            
            # 本命轉職臨界點判定
            if p["level"] >= 25 and job_mod["tier"] == 0:
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
            elif p["level"] >= 50 and job_mod["tier"] == 1:
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
            elif p["level"] >= 100 and job_mod["tier"] == 2:
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
        else:
            # ── 怪物沒死，發動反擊 ──
            is_p_evade = random.random() < evade_chance
            
            if is_p_evade:
                log += f"💨 殘影！你發動敏捷身法，【完美閃避】了怪物的反擊傷害！"
            else:
                dmg_mod = p.get("map_dmg_mod", 1.0)
                base_m_atk = random.randint(1, enemy["atk"])
                final_m_atk = int(base_m_atk * dmg_mod)
                
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
                db_core.MEMORY_PLAYERS[user_id] = p
                card = db_core.make_battle_card(log, p, enemy)
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
            
    # 11. 處理【逃跑】判定
    elif user_msg == "逃跑":
        p["enemy"] = None
        db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💨 成功逃跑了！"))
        
    # 12. 處理【復活】判定
    elif user_msg == "復活":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.handle_resurrect(p)))
        
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方選單開始遊戲！"))

if __name__ == "__main__":
    app.run()
