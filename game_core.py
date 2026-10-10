import random
import json
from linebot.models import TextSendMessage, FlexSendMessage

# 🎮 跨檔案導入你全新優化、完全模組化分離的 8 大黃金頁面
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

    # 1. 處理【我的狀態】判定
    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.get_status_text(p)))
        
    # 2. 處理【我的背包】判定
    elif user_msg == "我的背包":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.get_bag_text(p)))
        
    # 3. 處理【世界地圖】傳送陣清單查詢判定
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.get_maps_list_text(p)))
        
    # 4. 處理【前往 / 傳送】全新編年史地標地圖指令判定（100% 對齊前端橫向按鈕）
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
        
    # 8. 處理【尋找怪物】根據據點動態孵化隨機怪物
    elif user_msg == "尋找怪物" or user_msg == "尋怪":
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】重整旗鼓。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(f"⚔️ 你的眼前還卡著一隻怪！請專心應戰！", p, p["enemy"])))
            return
            
        # 🎲 根據玩家當前的精密據點（若無欄位預設晨曦堡壘），從獨立怪物庫中生成對應強度的強敵
        current_location = p.get("current_map", "晨曦堡壘")
        random_monster = monsters.generate_random_monster(current_location)
        
        p["enemy"] = random_monster
        # 尋找怪物算大事件，強制跨海寫入 Supabase 連線存檔
        db_core.save_player(p)
        
        env_now = p.get("map_env_status", "🟢 平靜")
        title_log = f"⚠️ 警報！你在📍【{current_location}】遭遇強敵！\n當前天象：【{env_now}】\n怪物能力：🔰 {random_monster['skill']}"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(title_log, p, p["enemy"])))
        
    # 9. 處理【攻擊】融入「蝕潮傷害、金幣加成」的史詩級回合判定
    elif user_msg == "攻擊":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
        
        # 🎲 計算勇者是否觸發 15% 暴擊
        is_p_crit = random.random() < 0.15
        base_dmg = random.randint(5, 12) + (p["level"] * 2) + w_bonus
        p_dmg = int(base_dmg * 1.5) if is_p_crit else base_dmg
        
        # 🎲 計算怪物是否觸發 10% 閃避
        is_m_evade = random.random() < 0.10
        
        log = ""
        if is_m_evade:
            log += f"💨 殘影！【{enemy['name']}】展現極速身法，完美閃避了你的攻擊！\n"
        else:
            enemy["hp"] -= p_dmg
            if is_p_crit:
                log += f"💥 🔥 🌟 【致命暴擊】！！你揮舞【{p['weapon']}】對【{enemy['name']}】造成高達 {p_dmg} 點傷害！\n"
            else:
                log += f"⚔️ 命中！你對【{enemy['name']}】造成 {p_dmg} 點傷害！\n"
                
        # ── 檢查怪物是否死亡 ──
        if enemy["hp"] <= 0:
            # 🔮 讀取地圖天象的金幣加成倍率（若無預設為 1.0）
            gold_mod = p.get("map_gold_mod", 1.0)
            base_gold = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            final_gold = int(base_gold * gold_mod)
            
            p["gold"] += final_gold
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            
            log += f"🎉 擊敗對手！獲得金幣 +{final_gold}"
            if gold_mod > 1.0:
                log += f" (含天象加成 {int((gold_mod-1)*100)}%)"
            log += f"、經驗值 +{enemy['exp']}！\n"
            
            # 🎲 50% 機率隨機掉落怪物素材送進背包
            if random.random() < 0.50 and enemy.get("drop_item"):
                bag.add_to_inventory(p, enemy["drop_item"], is_material=True)
                log += f"💎 【幸編年史掉寶】！搜刮到了素材：【{enemy['drop_item']}】x1！\n"
                
            # 升級判定
            if p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                p["max_hp"] += 15
                p["hp"] = p["max_hp"]
                log += f"🎊 👑 恭喜升級到 Lv.{p['level']}！血量已完全補滿！"
                
            # 打死怪算最高級大事件，強制連線鎖進雲端
            db_core.save_player(p)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
        else:
            # ── 怪物沒死，發動反擊 ──
            # 🔮 讀取地圖天象的怪物傷害加成倍率（若無預設為 1.0）
            dmg_mod = p.get("map_dmg_mod", 1.0)
            base_m_atk = random.randint(1, enemy["atk"])
            final_m_atk = int(base_m_atk * dmg_mod)
            
            p["hp"] -= final_m_atk
            log += f"🩹 【{enemy['name']}】發動反擊！你受到 {final_m_atk} 點傷害！"
            if dmg_mod > 1.0:
                log += f" (內含蝕潮環境增幅 {int((dmg_mod-1)*100)}%)"
            
            if p["hp"] <= 0:
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你受傷過重被擊倒了！請點擊【復活】重整旗鼓。"
                db_core.save_player(p)
                card = db_core.make_battle_card(log, p, None)
            else:
                # ⚔️ 普通回合：留在記憶體高速快取，0.01 秒秒噴卡片！
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
