import random
import json
from linebot.models import TextSendMessage, FlexSendMessage

# 🎮 跨檔案導入你全新優化、功能完美獨立分開的 8 大黃金頁面
import db_core
import player
import monsters
import weapons
import shop
import bag
import maps

def process_game_logic(event, line_bot_api):
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    # 從資料庫核心讀取玩家與記憶體快取資料
    p = db_core.load_player(user_id)
    level = p.get("level", 1)

    # 🧮 【原創六大天賦實體衍生數值公式計算】
    str_val = p.get("strength", 10 + (level * 3))
    agi_val = p.get("agility", 10 + (level * 2))
    int_val = p.get("intelligence", 10 + (level * 2))
    vit_val = p.get("vitality", 10 + (level * 3))
    luk_val = p.get("luck", 10 + (level * 1))
    men_val = p.get("sprit", 10 + (level * 2))
    
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
        
    # 4. 處理【前往 / 傳送】全新原創世界地圖指令判定
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
        
    # 8. 處理【尋找怪物】判定
    elif user_msg == "尋找怪物" or user_msg == "尋怪":
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】重整旗鼓。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(f"⚔️ 你的眼前還卡著一隻怪！請專心應戰！", p, p["enemy"])))
            return
            
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        
        p["enemy"] = random_monster
        db_core.save_player(p)
        
        env_now = p.get("map_env_status", "🟢 平靜")
        title_log = f"⚠️ 警報！你在📍【{current_location}】遭遇強敵！\n當前天象：【{env_now}】\n怪物能力：🔰 {random_monster['skill']}"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(title_log, p, p["enemy"])))
        
    # 9. 處理【攻擊】包含「物理/魔法傷害起伏、敏捷連擊與閃避、幸運爆擊」的原創天賦回合判定
    elif user_msg == "攻擊":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        
        # 🧮 基礎機率計算對齊
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          # 爆擊率
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     # 爆擊傷害倍率
        evade_chance = min(50, 5 + (agi_val // 8)) / 100.0          # 閃避率
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     # 連擊率
        
        # 🎲 判定本次攻擊是否為「連續攻擊」
        is_double_atk = random.random() < double_atk_chance
        attack_count = 2 if is_double_atk else 1
        
        if is_double_atk:
            log += f"🌪️ 🚀 【神速連擊】！！你身形化為疾風，觸發連續攻擊判定！\n"
            
        total_p_dmg = 0
        for i in range(attack_count):
            # 💪 力量影響：計算最大跟最小物理傷害起伏
            min_p_dmg = 5 + (str_val // 2) + w_bonus
            max_p_dmg = 12 + str_val + w_bonus
            p_dmg = random.randint(min_p_dmg, max_p_dmg)
            
            # 🍀 幸運影響：爆擊率判定
            is_crit = random.random() < crit_chance
            if is_crit:
                p_dmg = int(p_dmg * crit_dmg_mod)
                log += f"💥 🔥 【致命爆擊】！第 {i+1} 刀揮出物理爆擊傷害 {p_dmg} 點！\n"
            else:
                log += f"⚔️ 第 {i+1} 刀物理命中，造成 {p_dmg} 點傷害！\n"
            total_p_dmg += p_dmg
            
        # 實體扣減怪物血量
        enemy["hp"] -= total_p_dmg
        
        # ── 檢查怪物是否死亡 ──
        if enemy["hp"] <= 0:
            # 🔮 智力影響：計算最大跟最小魔法傷害作為最終一擊
            min_m_dmg = 3 + (int_val // 2)
            max_m_dmg = 10 + int_val
            m_dmg = random.randint(min_m_dmg, max_m_dmg)
            
            gold_mod = p.get("map_gold_mod", 1.0)
            base_gold = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            final_gold = int(base_gold * gold_mod)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            
            log += f"✨ 🔮 智力共鳴！最終引導魔法追加轟炸，造成 {m_dmg} 點魔傷！\n"
            log += f"🎉 順利擊敗對手！獲得金幣 +{final_gold}"
            if gold_mod > 1.0:
                log += f" (含天象加成 {int((gold_mod-1)*100)}%)"
            log += f"、經驗值 +{enemy['exp']}！\n"
            
            # 🎲 50% 機率隨機掉落怪物素材
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸運掉寶】！搜刮到了素材：【{enemy['drop_item']}】x1！\n"
                
            # 升級判定與六大屬性固定分配成長
            if p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                
                # 🛡️ 體力影響：自動提升基礎體力與計算全新血量上限
                p["strength"] = p.get("strength", 10) + 3
                p["agility"] = p.get("agility", 10) + 2
                p["intelligence"] = p.get("intelligence", 10) + 2
                p["vitality"] = p.get("vitality", 10) + 3
                p["luck"] = p.get("luck", 10) + 1
                p["sprit"] = p.get("sprit", 10) + 2
                
                # 動態重新計算最大生命值
                calculated_max_hp = 100 + (p["vitality"] * 5) + (p["level"] * 15)
                p["max_hp"] = calculated_max_hp
                p["hp"] = calculated_max_hp
                log += f"🎊 👑 恭喜升級到 Lv.{p['level']}！六大天賦全屬性大幅提升，血量已完全補滿！"
                
            db_core.save_player(p)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
        else:
            # ── 怪物沒死，發動反擊 ──
            # ⚡ 敏捷影響：計算戰場閃避率
            is_p_evade = random.random() < evade_chance
            
            if is_p_evade:
                log += f"💨 殘影！你發動神級閃避身法，【完美閃避】了怪物的反擊傷害！"
            else:
                dmg_mod = p.get("map_dmg_mod", 1.0)
                base_m_atk = random.randint(1, enemy["atk"])
                final_m_atk = int(base_m_atk * dmg_mod)
                
                # 🛡️ 體力影響：物理防禦力實體扣減反擊傷害（最少受 1 點傷害）
                p_defense = vit_val // 2
                final_received_dmg = max(1, final_m_atk - p_defense)
                
                p["hp"] -= final_received_dmg
                log += f"🩹 【{enemy['name']}】發動反擊！你受到 {final_received_dmg} 點物理傷害！"
                if p_defense > 0:
                    log += f" (體力防禦減免 -{p_defense} 點)"
                if dmg_mod > 1.0:
                    log += f" (含天象加成)"
            
            if p["hp"] <= 0:
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你受傷過重被擊倒了！請點擊【復活】重整旗鼓。"
                db_core.save_player(p)
                card = db_core.make_battle_card(log, p, None)
            else:
                # ⚔️ 普通回合：快取高速秒回
                db_core.MEMORY_PLAYERS[user_id] = p
                card = db_core.make_battle_card(log, p, enemy)
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
            
    # 10. 處理【逃跑】判定
    elif user_msg == "逃跑":
        p["enemy"] = None
        db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💨 成功逃跑了！"))
        
    # 11. 處理【復活】判定
    elif user_msg == "復活":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.handle_resurrect(p)))
        
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方選單開始遊戲！"))
