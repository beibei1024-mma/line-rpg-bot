import db_core
import player
import shop
import bag
import maps
import battle_core

# 🚀 導入新增的簽到福利系統
import datetime

from linebot.models import TextSendMessage, FlexSendMessage

def handle_daily_sign_in(p):
    """🧠 企劃二：每日福利簽到大腦邏輯"""
    # 🕒 獲取台灣目前日期字符串 (格式: YYYY-MM-DD)
    today_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
    
    if p.get("last_sign_in") == today_str:
        return f"❌ 勇者！你今天 ({today_str}) 已經簽到過了，太貪心神明會生氣的！明天再來吧！"
        
    # 發放隨機金幣福利與藥水
    reward_gold = random.randint(500, 2000) if "random" in globals() else 1200
    p["gold"] += reward_gold
    p["last_sign_in"] = today_str
    
    # 塞入 2 瓶補血高級藥水進背包
    bag.add_to_inventory(p, "高級生命藥水")
    bag.add_to_inventory(p, "高級生命藥水")
    
    db_core.save_player(p)
    
    return f"📆 ✨ 【每日簽到大成功】 ✨ 📆\n─────────────────\n冒險者公會發放了今日生存補給：\n🪙 獎勵金幣：+{reward_gold} 🪙\n🧪 高級生命藥水：+2 瓶 🧪\n\n💡 進度已完美同步至 Supabase 雲端！"

def process_game_logic(event, line_bot_api, configuration):
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    p = db_core.load_player(user_id)

    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的狀態面板", contents=player.get_status_card(p)))
        return
    elif user_msg == "我的背包":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的私人物品倉庫", contents=bag.get_bag_card(p)))
        return
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟世界傳送選單", contents=maps.get_maps_carousel(p)))
        return
    elif user_msg.startswith("前往") or user_msg.startswith("傳送"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.change_map(p, user_msg)))
        return
    elif user_msg.startswith("使用"):
        potion_name = user_msg.replace("使用", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.use_potion(p, potion_name)))
        return
    elif user_msg == "冒險商店":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
        return
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        return
        
    # ✨ 企劃二：切分簽到攔截點
    elif user_msg == "簽到":
        # 內嵌隨機補防
        import random
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
        
        # 拋出超帥簽到卡
        card_data = db_core.make_battle_card(f"📆 簽到成功！獲得金幣 +{reward_gold}、高級生命藥水 x2！\n\n狀態已安全儲存。", p, None)
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{"type": "flex", "altText": "簽到成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]
        }
        from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return
    else:
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
    # 6. 處理【冒險商店】面板開啟判定
    elif user_msg == "冒險商店":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
        return
        
    # 7. 處理【購買物品】商店交易判定
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        return
        
    # 8. 處理【簽到】每日福利領取判定
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

    # ✨ 企劃一：處理【冒險挑戰】皇家試煉入口與多人 Boss 攔截點 (導入全新獨立頁面)
    elif user_msg == "冒險挑戰" or user_msg == "挑戰":
        import challenge_system
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="皇家試煉選單", contents=challenge_system.get_challenge_menu(p)))
        return
        
    elif user_msg == "挑戰爬塔":
        import challenge_system
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=challenge_system.execute_tower_climb(p)))
        return
        
    elif user_msg == "挑戰世界Boss" or user_msg == "世界Boss":
        import challenge_system
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=challenge_system.execute_world_boss_raid(p)))
        return

    # ✨ 企劃二：處理【鍛造 / 工坊】禁忌物料熔煉與手工神裝合成攔截點 (導入全新獨立頁面)
    elif user_msg == "鍛造工坊" or user_msg == "鍛造" or user_msg == "工坊":
        import forge_system
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遠古鍛造工坊", contents=forge_system.get_forge_menu(p)))
        return
        
    elif user_msg.startswith("鍛造"):
        import forge_system
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=forge_system.execute_forge_weapon(p, user_msg)))
        return

    # 9. 其餘所有普通攻擊、尋怪、施放法術口令，全自動安全移交戰鬥大腦處理 (維持原樣，絕無干擾)
    else:
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
