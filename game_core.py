import random
import json
from linebot.models import TextSendMessage, FlexSendMessage

# 🎮 跨檔案導入您全新大分散、功能完美解耦的各個專屬遊戲頁面
import db_core
import player
import shop
import bag
import maps

# ⚔️ 導入您全新分流出去的「第二部分專屬頁面：戰鬥與養成核心大腦」
import battle_core

def process_game_logic(event, line_bot_api):
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    
    # 從資料庫核心讀取玩家與記憶體快取資料
    p = db_core.load_player(user_id)

    # 1. 處理【我的狀態】判定
    if user_msg == "我的狀態":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.get_status_text(p)))
        return
        
    # 2. 處理【我的背包】判定
    elif user_msg == "我的背包":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bag.get_bag_text(p)))
        return
        
    # 3. 處理【世界地圖】傳送陣清單查詢判定
    elif user_msg == "世界地圖":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=maps.get_maps_list_text(p)))
        return
        
    # 4. 處理【前往 / 傳送】指令判定
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
        
    # 7. 處理【購買物品】判定
    elif user_msg.startswith("購買"):
        item = user_msg.replace("購買", "").strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=shop.buy_weapon(p, item)))
        return

    # 8. 處理【加點 / 配點 / 轉職 / 尋怪 / 攻擊】
    # ⚡ 核心分流最高指標：大腦直接打包，全自動轉交給第二部分專屬頁面處理！
    else:
        battle_core.process_battle_logic(event, line_bot_api, p, user_msg)
