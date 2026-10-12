# game_core.py (優化版)
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
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    p = db_core.load_player(user_id)
    current_loc = p.get("current_map", "主城")

    # 🏙️ 快捷口令：回城
    if user_msg in ["回城", "飛回城鎮", "傳送主城"]:
        p["current_map"] = "主城"
        p["enemy"] = None
        db_core.save_player(p)
        card_data = db_core.make_battle_card("🦅 ✨ 飛向天空！你引導傳送羽毛，順利回到安全城鎮：📍【 主城 】！\n\n🏪 城市功能（補給商店、每日簽到、工坊、挑戰賽）已全數為您解鎖！", p, None)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "回城成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"

    # 😇 處理復活
    if user_msg in ["復活", "祈求復活"]:
        card_data = player.handle_resurrect(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "勇者復活歸來", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"

    # 👤 基礎狀態面板
    if user_msg in ["我的狀態", "狀態"]:
        card_data = player.get_status_card(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "我的狀態面板", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"
        
    if user_msg in ["我的背包", "背包"]:
        card_data = bag.get_bag_card(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "我的私人物品倉庫", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"
        
    if user_msg in ["我的裝備", "裝備"]:
        card_data = forge_system.get_equipment_card(p)
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "我的神聖裝備欄", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"

    # 📊 屬性配點管線
    if user_msg.startswith("加點") or user_msg.startswith("配點"):
        clean_cmd = user_msg.replace("配點", "加點")
        attr_name = clean_cmd.replace("加點", "")[:2]
        pts_str = clean_cmd.replace("加點", "")[2:]
        try:
            pts_to_add = int(pts_str)
        except ValueError:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 點數解析失敗！格式範例：【加點 力量 5】"))
            return "OK"
            
        free_pts = p.get("attribute_points", 0)
        if pts_to_add <= 0 or free_pts < pts_to_add:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 潛能點數不足！你目前剩餘的自由潛能點只有 {free_pts} 點！"))
            return "OK"
            
        attr_mapping = {"力量": "strength", "敏捷": "agility", "智力": "intelligence", "體力": "vitality", "幸運": "luck", "精神": "sprit"}
        if attr_name not in attr_mapping:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 可加點項目僅限：力量、敏捷、智力、體力、幸運、精神。"))
            return "OK"
            
        db_field = attr_mapping[attr_name]
        p[db_field] = p.get(db_field, 10) + pts_to_add
        p["attribute_points"] = free_pts - pts_to_add
        db_core.save_player(p)
        
        reply_log = f"💪 【 屬性配點成功 】 💪\n─────────────────\n你將 {pts_to_add} 點數分配給了 ✨【 {attr_name} 】！\n\n請輸入【我的狀態】查閱全新數值面板！"
        card_data = db_core.make_battle_card(reply_log, p, p.get("enemy"))
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "屬性配點結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"

    # 戰鬥與裝備變更指令導流
    if user_msg.startswith("使用技能") or user_msg == "使用技能防禦":
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
        return "OK"
        
    if user_msg.startswith("裝備") or user_msg.startswith("穿上"):
        res_text = bag.equip_weapon_from_bag(p, user_msg)
        card_data = db_core.make_battle_card(res_text, p, p.get("enemy"))
        msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "更換裝備結果", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"
        
    if user_msg == "脫下裝備":
        # ✨ 【Bug 修正】確保調用完 LINE API 後，回傳符合 Flask 路由規範的字串
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=forge_system.execute_unequip_weapon(p)))
        return "OK"

    if user_msg in ["世界地圖", "出城冒險"]:
        if current_loc == "主城" and p.get("enemy") is not None:
            p["enemy"] = None
            db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟世界傳送選單", contents=maps.get_maps_carousel(p)))
        return "OK"

    if user_msg.startswith("前往") or user_msg.startswith("傳送"):
        res_text = maps.change_map(p, user_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res_text))
        return "OK"

    if user_msg.startswith("使用"):
        potion_name = user_msg.replace("使用", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.use_potion(p, potion_name)))
        return "OK"

    # 🔒 城市專屬隔離牆
    CITY_ONLY_COMMANDS = ["冒險商店", "購買", "簽到", "挑戰", "挑戰爬塔", "挑戰世界Boss", "世界Boss", "工坊", "鍛造"]
    is_city_cmd = any(user_msg.startswith(cmd) or user_msg == cmd for cmd in CITY_ONLY_COMMANDS)
    
    if is_city_cmd and current_loc != "主城":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 鎖定限制！你目前位於野外【{current_loc}】。請先輸入【回城】！"))
        return "OK"

    # 主城內功能
    if current_loc == "主城":
        if user_msg == "冒險商店":
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
            return "OK"
        if user_msg.startswith("購買"):
            item = user_msg.replace("購買", "").strip()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
            return "OK"
        if user_msg == "簽到":
            reward_gold = random.randint(500, 2000)
            today_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
            if p.get("last_sign_in") == today_str:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 你今天 ({today_str}) 已經簽到過了！"))
                return "OK"
            p["gold"] += reward_gold
            p["last_sign_in"] = today_str
            bag.add_to_inventory(p, "高級生命藥水")
            bag.add_to_inventory(p, "高級生命藥水")
            db_core.save_player(p)
            card_data = db_core.make_battle_card(f"📆 簽到成功！獲得金幣 +{reward_gold}、高級生命藥水 x2！", p, None)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "簽到成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return "OK"
        if user_msg in ["冒險挑戰", "挑戰"]:
            card_data = challenge_system.get_challenge_menu(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "挑戰場", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return "OK"
        if user_msg == "挑戰爬塔":
            res = challenge_system.execute_tower_climb(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "試煉戰況", "contents": res["flex"], "quickReply": res["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return "OK"
        if user_msg in ["挑戰世界Boss", "世界Boss"]:
            res = challenge_system.execute_world_boss_raid(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "Boss戰報", "contents": res["flex"], "quickReply": res["quick_reply"]}]}
            with ApiClient(configuration) as api_client: MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
            return "OK"
        if user_msg in ["鍛造工坊", "鍛造", "工坊"]:
            card_data = forge_system.get_forge_menu(p)
            msg_payload = {"replyToken": event.reply_token, "messages": [{"type": "flex", "altText": "鍛造工坊", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]}
        # （此處承接主城內的「工坊/鍛造」選單發送之後...）
        with ApiClient(configuration) as api_client: 
            MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"

    if user_msg.startswith("鍛造"):
        res = forge_system.execute_forge_weapon(p, user_msg)
        if isinstance(res, str):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res))
        else:
            msg_payload = {
                "replyToken": event.reply_token, 
                "messages": [{
                    "type": "flex", 
                    "altText": "工坊熔煉結果", 
                    "contents": res["flex"], 
                    "quickReply": res["quick_reply"]
                }]
            }
            with ApiClient(configuration) as api_client: 
                MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
        return "OK"

    if user_msg in ["尋找怪物", "尋怪", "攻擊", "使用技能"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 主城安全區禁止械鬥！請點擊【🚪 出城冒險】。"))
        return "OK"

    # 🌲 處於野外危險區的指令導流（脫離 current_loc == "主城" 的層級）
    if user_msg.startswith("轉職"):
        jobs_system.handle_job_transfer(event, line_bot_api, p, user_msg, configuration)
        return "OK"

    # 🕹️ 預設交給戰鬥核心處理（尋怪、攻擊、逃跑）
    battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
    return "OK"
