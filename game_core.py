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

    # 🧮 【原創六大天賦實體衍生數值公式計算 - 完美吃進本命職業乘數加成】
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
        
        # 🔒 【真・本命死鎖驗證】嚴格限制只能走自己流派的下一階，斷絕跨系跨線！
        if target_job not in job_mod["next_jobs"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！你目前的本命职业是【{current_job}】，無法跨系覺醒為【{target_job}】。"))
            return
            
        # 等級門檻限制驗證
        if p["level"] < target_info["req_lvl"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 境界未到！轉職為【{target_job}】需要突破至 Lv.{target_info['req_lvl']}+，你目前只有 Lv.{p['level']}。"))
            return
            
        # 🔓 驗證完全通過！執行雲端本命進階覺醒
        p["job"] = target_job
        db_core.save_player(p)
        
        log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n勇者，你成功打破命運桎梏，本命血脈引來瘋狂覺醒！\n\n🛡️ 你從【{current_job}】正式進階為更高的職業形態——🔥【{target_job}】！\n專屬天賦加成已全線翻倍刷新！快輸入【我的狀態】查看全新戰力！"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="轉職成功", contents=db_core.make_battle_card(log_text, p, None)))

    # 9. 處理【尋找怪物】判定
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
