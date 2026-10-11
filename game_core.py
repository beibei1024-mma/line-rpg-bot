import db_core
import player
import shop
import bag
import maps
import battle_core

from linebot.models import TextSendMessage, FlexSendMessage

def process_game_logic(event, line_bot_api, configuration):
    """【Quick Reply 相容版主控台】完美梳理玩家資料讀取與分流大腦"""
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    # ✨ 修正關鍵：必須先在最前面讀取好玩家存檔資料，後面的分流才能共用變數 p！
    p = db_core.load_player(user_id)

    # 1. 處理【我的狀態】判定 ➡️ 渲染黑曜石勇者天賦卡
    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的狀態面板", contents=player.get_status_card(p)))
        return
        
    # 2. 處理【我的背包】判定 ➡️ 渲染實體網格倉庫卡片
    elif user_msg == "我的背包":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="我的私人物品倉庫", contents=bag.get_bag_card(p)))
        return
        
    # 3. 處理【世界地圖】查詢判定 ➡️ 渲染左右橫滑 20 大世界傳送陣廊
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟世界傳送選單", contents=maps.get_maps_carousel(p)))
        return
        
    # 4. 處理【前往 / 傳送】指令傳送判定
    elif user_msg.startswith("前往") or user_msg.startswith("傳送"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.change_map(p, user_msg)))
        return
        
    # 5. 處理【使用】藥水道具指令判定
    elif user_msg.startswith("使用"):
        potion_name = user_msg.replace("使用", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.use_potion(p, potion_name)))
        return
        
    # 6. 處理【冒險商店】面板開啟判定
    elif user_msg == "冒險商店":
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟商店", contents=shop.get_shop_card(p)))
        return
        
    # 7. 處理【購買物品】商店交易判定
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        return

    # 8. 其餘普通攻擊、尋怪、釋放技能指令，全自動轉交給 battle_core 戰鬥大腦處理
    else:
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg, configuration)
