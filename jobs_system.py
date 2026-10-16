# jobs_system.py - 皇家轉職與等級突破核心 (升級自動回滿血魔版)

import jobs
import db_core
import equipment_core
from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi
from linebot.models import TextSendMessage

def handle_job_transfer(event, line_bot_api, p, user_msg, configuration):
    """🎭 獨立處理【轉職】口令，絕不干擾戰鬥公式"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    target_job = user_msg.replace("轉職", "").strip()

    if target_job not in jobs.JOBS_DATA:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 轉職失敗！不存在【" + target_job + "】。"))
        return

    target_info = jobs.JOBS_DATA[target_job]
    if target_job not in job_mod["next_jobs"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 轉職失敗！【" + current_job + "】無法進階為【" + target_job + "】。"))
        return

    if level < target_info["req_lvl"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔒 境界未到！需要 Lv." + str(target_info['req_lvl']) + "+，你目前 Lv." + str(level) + "。"))
        return

    p["job"] = target_job
    db_core.save_player(p)

    log_text = "✨ 🎉 【本命階級突破成功】 🎉 ✨\n🛡️ 恭喜！你正式進階為更高的職業形態 ── 🔥【" + target_job + "】！\n快輸入【我的狀態】或開啟戰鬥查看全新絕世天賦！"
    card_data = db_core.make_battle_card(log_text, p, None)

    msg_payload = {
        "replyToken": event.reply_token,
        "messages": [{"type": "flex", "altText": "轉職成功", "contents": card_data["flex"], "quickReply": card_data["quick_reply"]}]
    }
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(ReplyMessageRequest.from_dict(msg_payload))

def check_level_lock(p, job_mod):
    """🔒 核心卡等判定：檢查經驗值是否撞上轉職瓶頸死鎖，升級時同步充滿血量與魔力"""
    is_job_locked = False
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
        p["intelligence"] = p.get("intelligence", 10) + 2
        p["vitality"] = p.get("vitality", 10) + 3
        p["luck"] = p.get("luck", 10) + 1
        p["sprit"] = p.get("sprit", 10) + 2
        p["attribute_points"] = p.get("attribute_points", 0) + 5

    p["level"] = p_level
    p["exp"] = p_exp

    # ✨ 關鍵修復：升級成功後，自動將血量與魔力充滿至最新上限！
    eq_bonus = equipment_core.get_player_total_equipment_bonus(p)
    vit_val = int((p.get("vitality", 10) + eq_bonus["vitality"]) * job_mod["vit_mod"])
    men_val = int((p.get("sprit", 10) + eq_bonus["sprit"]) * job_mod["men_mod"])
    
    p["hp"] = 100 + (vit_val * 5) + (p["level"] * 15)
    p["mp"] = 50 + (men_val * 4) + (p["level"] * 5)

    return is_job_locked
# === END OF FILE ===
