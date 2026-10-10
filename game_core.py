import random
import json
from linebot.models import TextSendMessage, FlexSendMessage

# 🎮 跨檔案導入你全新大分散、高效率的各個專屬遊戲頁面
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
    
    # 從資料庫核心讀取玩家與快取資料
    p = db_core.load_player(user_id)

    # 1. 處理【我的狀態】判定
    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.get_status_text(p)))
        
    # 2. 處理【我的背包】判定（精準連接到全新的 bag.py 頁面）
    elif user_msg == "我的背包":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.get_bag_text(p)))
        
    # 3. 處理【世界地圖】判定（精準連接到全新的 maps.py 頁面）
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.get_maps_list_text(p)))
        
    # 4. 處理【冒險商店】判定
    elif user_msg == "冒險商店":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
        
    # 5. 處理【購買物品】判定
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        
    # 6. 處理【尋找怪物】判定
    elif user_msg == "尋找怪物":
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card("⚔️ 你的眼前還卡著一隻怪！", p, p["enemy"])))
            return
            
        m_type = random.choice(list(monsters.MONSTERS.keys()))
        m_template = monsters.MONSTERS[m_type]
        m_hp = random.randint(m_template["min_hp"], m_template["max_hp"])
        p["enemy"] = {"name": m_template["name"], "hp": m_hp, "max_hp": m_hp, "atk": m_template["atk"], "gold_range": m_template["gold_range"], "exp": m_template["exp"]}
        
        # 遭遇怪物算大事件，強制跨海連線存檔
        db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card("⚠️ 野生怪物出現了！", p, p["enemy"])))
        
    # 7. 處理【攻擊與回合傷害】判定
    elif user_msg == "攻擊":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
        p_dmg = random.randint(5, 12) + (p["level"] * 2) + w_bonus
        enemy["hp"] -= p_dmg
        log = f"💥 你揮舞【{p['weapon']}】對【{enemy['name']}】造成 {p_dmg} 點傷害！\n"
        
        if enemy["hp"] <= 0:
            # 🏆 擊敗對手判定：強制跨海寫入 Supabase 資料庫鎖定高額金幣，防回溯！
            gold_get = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            p["gold"] += gold_get
            p["exp"] += enemy["exp"]
            p["enemy"] = None
            log += f"🎉 擊敗對手！獲得金幣 +{gold_get}、經驗值 +{enemy['exp']}！"
            
            if p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                p["max_hp"] += 15
                p["hp"] = p["max_hp"]
                log += f"\n🎊 恭喜升級到 Lv.{p['level']}！HP已補滿！"
                
            db_core.save_player(p)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
        else:
            m_atk = random.randint(1, enemy["atk"])
            p["hp"] -= m_atk
            log += f"🩹 【{enemy['name']}】反擊！你受到 {m_atk} 點傷害！"
            
            if p["hp"] <= 0:
                # 💀 勇者陣亡判定：強制跨海存檔
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你被擊倒了！請點擊【復活】。"
                db_core.save_player(p)
                card = db_core.make_battle_card(log, p, None)
            else:
                # ⚔️ 互毆扣血回合：只留在 Render 當地記憶體更新，完全不敲資料庫大門！
                # 體感速度狂飆至 0.01 秒，LINE 訊息瞬間秒回！
                db_core.MEMORY_PLAYERS[user_id] = p
                card = db_core.make_battle_card(log, p, enemy)
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
            
    # 8. 處理【逃跑】判定
    elif user_msg == "逃跑":
        p["enemy"] = None
        db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💨 成功逃跑了！"))
        
    # 9. 處理【復活】判定
    elif user_msg == "復活":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.handle_resurrect(p)))
        
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方選單開始遊戲！"))
