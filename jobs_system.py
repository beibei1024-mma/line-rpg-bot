import jobs
import db_core
from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi
# ⚡ 核心修復：直接從官方 models 安全引入 TextSendMessage，封印原先呼叫 db_core 的 AttributeError 地雷！
from linebot.models import TextSendMessage

def handle_job_transfer(event, line_bot_api, p, user_msg, configuration):
    """🎭 獨立處理【轉職】口令，絕不干擾戰鬥公式"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: 
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    target_job = user_msg.replace("轉職", "").strip()
    
    # ⚡ 優化：提早攔截不合法的轉職目標，避免後續查表虛耗
    if target_job not in jobs.JOBS_DATA:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！不存在【{target_job}】。"))
        return
        
    target_info = jobs.JOBS_DATA[target_job]
    if target_job not in job_mod["next_jobs"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！【{current_job}】無法進階為【{target_job}】。"))
        return
        
    if level < target_info["req_lvl"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 境界未到！需要 Lv.{target_info['req_lvl']}+，你目前 Lv.{level}。"))
        return
        
    p["job"] = target_job
    db_core.save_player(p)
    
    log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n🛡️ 恭喜！你正式進階為更高的職業形態 ── 🔥【{target_job}】！\n快輸入【我的狀態】或開啟【🔮 技能書】查看全新絕世天賦！"
    card_data = db_core.make_battle_card(log_text, p, None)
    msg_payload = {
        "replyToken": event.reply_token,
        "messages": [{"type": "flex", "altText": "轉職成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]
    }
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))

def check_level_lock(p, job_mod):
    """🔒 核心卡等判定：檢查經驗值是否撞上轉職瓶頸死鎖"""
    is_job_locked = False
    
    # ⚡ 優化：本地變數快取，避免 while 迴圈內部頻繁對字典做雜湊查表
    p_level = p["level"]
    p_exp = p["exp"]
    tier = job_mod["tier"]
    
    while p_exp >= p_level * 50:
        if p_level == 24 and tier == 0:
            p_level = 25
            p_exp = 0
            is_job_locked = True
            break
        elif p_level == 49 and tier == 1:
            p_level = 50
            p_exp = 0
            is_job_locked = True
            break
        elif p_level == 99 and tier == 2:
            p_level = 100
            p_exp = 0
            is_job_locked = True
            break
            
        p_exp -= p_level * 50
        p_level += 1
        p["strength"] = p.get("strength", 10) + 3
        p["agility"] = p.get("agility", 10) + 2
        p["attribute_points"] = p.get("attribute_points", 0) + 5
        
    # 寫回主要字典
    p["level"] = p_level
    p["exp"] = p_exp
    
    # ⚡ 核心修復：修正原先寫成 is_job_locked(p) 的呼叫錯誤，改為正確回傳布林值，封印升級時已讀不回的 TypeError！
    return is_job_locked
