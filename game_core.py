import db_core
import player
import shop
import bag
import maps
import battle_core
import challenge_system
import forge_system
import jobs_system
import random
import datetime

from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi
from linebot.models import TextSendMessage, FlexSendMessage

def process_game_logic(event, line_bot_api, configuration):
    """【皇家主控台 終極完全體】補齊換裝阻斷路由，完美實裝一鍵換裝智慧圖標回圈"""
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    p = db_core.load_player(user_id)
    current_loc = p.get("current_map", "主城")

    # 🏙️ 快捷口令：回城 / 飛回城鎮 
    if user_msg == "回城" or user_msg == "飛回城鎮" or user_msg == "傳送主城":
        p["current_map"] = "主城"
        p["enemy"] = None
        db_core.save_player(p)
        card_data = db_core.make_battle_card(f"🦅 ✨ 飛向天空！你引導傳送羽毛，順利回到安全城鎮：📍【 主城 】！\n\n🏪 城市功能（補給商店、每日簽到、工坊、挑戰賽）已全數為您解鎖！", p, None)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "回城成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 😇 處理【復活】
    elif user_msg == "復活" or user_msg == "祈求復活":
        card_data = player.handle_resurrect(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "勇者復活歸來", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return

    # 👤 1. 處理【我的狀態】面板 
    if user_msg == "我的狀態" or user_msg == "狀態":
        card_data = player.get_status_card(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "我的狀態面板", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return
        
    # 🎒 2. 處理【我的背包】倉庫 
    elif user_msg == "我的背包" or user_msg == "背包":
        card_data = bag.get_bag_card(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "我的私人物品倉庫", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return
        
    # 🛡️ 3. 處理【我的裝備】裝備欄
    elif user_msg == "我的裝備" or user_msg == "裝備":
        card_data = forge_system.get_equipment_card(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "我的神聖裝備欄", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return
        
    # ✨ 【Bug 終極修正點】一鍵換裝攔截點完美對齊 Dict 發送模型，補齊 return 徹底阻斷重疊字！
    elif user_msg.startswith("裝備") or user_msg.startswith("穿上"):
        res_text = bag.equip_weapon_from_bag(p, user_msg)
        # 呼叫 db_core 生成符合勇者當前地圖（主城或野外）的智慧小圖標控制列，形成流暢體驗
        card_data = db_core.make_battle_card(res_text, p, p["enemy"])
        
        msg_payload = {
            "replyToken": event.reply_token,
            "messages": [{
                "type": "flex", 
                "altText": "更換裝備結果", 
                "contents": card_data["flex"], 
                "quickReply": card_data["quick_reply"]
            }]
        }
        with ApiClient(configuration) as api_client: 
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return # ⛔ 鋼鐵阻斷！絕對不再讓代碼下滑到後方的 else 分流！
        
    elif user_msg == "脫下裝備":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=forge_system.execute_unequip_weapon(p)))
        return
    elif user_msg == "世界地圖" or user_msg == "出城冒險":
        if current_loc == "主城" and p["enemy"] is not None:
            p["enemy"] = None
            db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟世界傳送選單", contents=maps.get_maps_carousel(p)))
        return
    elif user_msg.startswith("前往") or user_msg.startswith("傳送"):
        res_text = maps.change_map(p, user_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res_text))
        return
    elif user_msg.startswith("使用"):
        potion_name = user_msg.replace("使用", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.use_potion(p, potion_name)))
        return

    # 🔒 城市專屬鎖死功能安全隔離牆
    CITY_ONLY_COMMANDS = ["冒險商店", "購買", "簽到", "挑戰", "挑戰爬塔", "挑戰世界Boss", "世界Boss", "工坊", "鍛造"]
    is_city_cmd = any(user_msg.startswith(cmd) or user_msg == cmd for cmd in CITY_ONLY_COMMANDS)
    
    if is_city_cmd and current_loc != "主城":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 鎖定限制！你目前位於野外【{current_loc}】。野外無法開啟商店、簽到、工坊或發起爬塔！請先點擊小圖標【🦅 飛回城鎮】或輸入【回城】！"))
        return

    # 🏙️ 處於主城安全區內的指令導流
    if current_loc == "主城":
        if user_msg == "冒險商店":
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
            return
        elif user_msg.startswith("購買"):
            item = user_msg.replace("購買", "").strip()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
            return
        elif user_msg == "簽到":
            reward_gold = random.randint(500, 2000)
            today_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
            if p.get("last_sign_in") == today_str:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 勇者！你今天 ({today_str}) 已經簽到過了，明天再來吧！"))
                return
            p["gold"] += reward_gold; p["last_sign_in"] = today_str
            bag.add_to_inventory(p, "高級生命藥水"); bag.add_to_inventory(p, "高級生命藥水"); db_core.save_player(p)
            card_data = db_core.make_battle_card(f"📆 簽到成功！獲得金幣 +{reward_gold}、高級生命藥水 x2！", p, None)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "簽到成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
        elif user_msg == "冒險挑戰" or user_msg == "挑戰":
            card_data = challenge_system.get_challenge_menu(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "挑戰場", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
        elif user_msg == "挑戰爬塔":
            res = challenge_system.execute_tower_climb(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "試煉戰況", "contents": res["flex"], "quickReply": res["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
        elif user_msg == "挑戰世界Boss" or user_msg == "世界Boss":
            res = challenge_system.execute_world_boss_raid(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "Boss戰報", "contents": res["flex"], "quickReply": res["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
        elif user_msg == "鍛造工坊" or user_msg == "鍛造" or user_msg == "工坊":
            card_data = forge_system.get_forge_menu(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "鍛造工坊", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
        elif user_msg.startswith("鍛造"):
            res = forge_system.execute_forge_weapon(p, user_msg)
            if isinstance(res, str): line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res))
            else:
                msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "工坊熔煉結果", "contents": res["flex"], "quickReply": res["quick_reply"]}]}
                with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return
        elif user_msg in ["尋找怪物", "尋怪", "攻擊", "使用技能"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 主城安全區禁止械鬥！請點擊小圖標【🚪 出城冒險】傳送至野外獵怪！"))
            return

    # 🌲 處於野外危險區的指令導流
    if user_msg.startswith("轉職"):
        jobs_system.handle_job_transfer(event, line_bot_api, p, user_msg, configuration)
        return
    else:
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
