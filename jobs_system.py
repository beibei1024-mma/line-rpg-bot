import jobs
import db_core
from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi

def handle_job_transfer(event, line_bot_api, p, user_msg, configuration):
    """🎭 處理【轉職】指令主動判定"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA: current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    target_job = user_msg.replace("轉職", "").strip()
    if target_job not in jobs.JOBS_DATA:
        line_bot_api.reply_message(event.reply_token, db_core.TextSendMessage(text=f"❌ 轉職失敗！不存在【{target_job}】這個本命職業。"))
        return True
        
    target_info = jobs.JOBS_DATA[target_job]
    if target_job not in job_mod["next_jobs"]:
        line_bot_api.reply_message(event.reply_token, db_core.TextSendMessage(text=f"❌ 轉職失敗！【{current_job}】無法跨系進階至【{target_job}】。"))
        return True
        
    if p["level"] < target_info["req_lvl"]:
        line_bot_api.reply_message(event.reply_token, db_core.TextSendMessage(text=f"🔒 境界未到！進階【{target_job}】需要達 Lv.{target_info['req_lvl']}+，你目前只有 Lv.{p['level']}。"))
        return True
        
    # 成功進階，改寫資料庫
    p["job"] = target_job
    db_core.save_player(p)
    
    log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n─────────────────\n🛡️ 恭喜！你正式進階為更高的職業形態 ── 🔥【{target_job}】！\n快點擊底部【我的狀態】或【🔮 技能書】查看全新解鎖的絕世天賦！"
    card_data = db_core.make_battle_card(log_text, p, None)
    msg_payload = {
        "replyToken": event.reply_token,
        "messages": [{"type": "flex", "altText": "轉職成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]
    }
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))
    return True

def check_level_lock(p, job_mod):
    """🔒 檢查當前經驗值是否撞上轉職死鎖上限 (回傳是否卡關、以及卡關通知)"""
    is_job_locked = False
    
    while p["exp"] >= p["level"] * 50:
        if p["level"] == 24 and job_mod["tier"] == 0:
            p["level"] = 25
            p["exp"] = 0
            is_job_locked = True
            break
        elif p["level"] == 49 and job_mod["tier"] == 1:
            p["level"] = 50
            p["exp"] = 0
            is_job_locked = True
            break
        elif p["level"] == 99 and job_mod["tier"] == 2:
            p["level"] = 100
            p["exp"] = 0
            is_job_locked = True
            break
            
        # 正常升級發放潛能點
        p["exp"] -= p["level"] * 50
        p["level"] += 1
        p["strength"] = p.get("strength", 10) + 3
        p["agility"] = p.get("agility", 10) + 2
        p["attribute_points"] = p.get("attribute_points", 0) + 5
        
    return is_job_locked
