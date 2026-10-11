import db_core
import player
import shop
import bag
import maps
import battle_core
import challenge_system
import forge_system

from linebot.models import TextSendMessage, FlexSendMessage

def process_game_logic(event, line_bot_api, configuration):
    """【真・防彈主控台】導正 else 區塊順序，徹底封印 SyntaxError 編譯死機"""
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    # 1. 優先讀取好玩家存檔資料，以便後面所有分流系統安全共用變數 p
    p = db_core.load_player(user_id)

    # 2. 處理【我的狀態】面板判定
    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的狀態面板", contents=player.get_status_card(p)))
        return
        
    # 2. 處理【我的背包】倉庫判定 (維持原樣)
    elif user_msg == "我的背包" or user_msg == "背包":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的私人物品倉庫", contents=bag.get_bag_card(p)))
        return

    # ✨ 擴充：處理【我的裝備】皇家裝備欄查看面板
    elif user_msg == "我的裝備" or user_msg == "裝備":
        import forge_system
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的神聖裝備欄", contents=forge_system.get_equipment_card(p)))
        return
        
    # ✨ 擴充：處理【脫下裝備】一鍵卸下並放回背包的動作
    elif user_msg == "脫下裝備":
        import forge_system
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=forge_system.execute_unequip_weapon(p)))
        return
        
    # 4. 處理【世界地圖】橫滑傳送廊判定
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟世界傳送選單", contents=maps.get_maps_carousel(p)))
        return
        
    # 5. 處理【前往 / 傳送】地圖位移判定
    elif user_msg.startswith("前往") or user_msg.startswith("傳送"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.change_map(p, user_msg)))
        return
        
    # 6. 處理【使用】藥水道具補血判定
    elif user_msg.startswith("使用"):
        potion_name = user_msg.replace("使用", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.use_potion(p, potion_name)))
        return
        
    # 7. 處理【冒險商店】皇家補給商店面板開啟判定
    elif user_msg == "冒險商店":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
        return
        
    # 8. 處理【購買物品】商店交易判定
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        return
        
    # 9. 處理【簽到】每日福利領取判定
    elif user_msg == "簽到":
        import random
        import datetime
        reward_gold = random.randint(500, 2000)
        today_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
        if p.get("last_sign_in") == today_str:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 勇者！你今天 ({today_str}) 已經簽到過了，明天再來吧！"))
            return
        p["gold"] += reward_gold
        p["last_sign_in"] = today_str
        bag.add_to_inventory(p, "高級生命藥水")
        bag.add_to_inventory(p, "高級生命藥水")
        db_core.save_player(p)
        
        card_data = db_core.make_battle_card(f"📆 簽到成功！獲得金幣 +{reward_gold}、高級生命藥水 x2！", p, None)
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{"type": "flex", "altText": "簽到成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]
        }
        from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 10. 處理【冒險挑戰】爬塔與世界 Boss 獨立頁面分流
    elif user_msg == "冒險挑戰" or user_msg == "挑戰":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="皇家試煉選單", contents=challenge_system.get_challenge_menu(p)))
        return
        
    elif user_msg == "挑戰爬塔":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=challenge_system.execute_tower_climb(p)))
        return
        
    elif user_msg == "挑戰世界Boss" or user_msg == "世界Boss":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=challenge_system.execute_world_boss_raid(p)))
        return

    # 11. 處理【鍛造 / 工坊】手工史詩神裝合成獨立頁面分流
    elif user_msg == "鍛造工坊" or user_msg == "鍛造" or user_msg == "工坊":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遠古鍛造工坊", contents=forge_system.get_forge_menu(p)))
        return
        
    elif user_msg.startswith("鍛造"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=forge_system.execute_forge_weapon(p, user_msg)))
        return

    # 🛑 12. 【終極保底出口】移至最底部：其餘普通攻擊、尋怪、施放法術指令，全自動安全移交戰鬥大腦處理
    else:
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
