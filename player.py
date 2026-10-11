import db_core
import weapons
import jobs
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

def get_status_card(p):
    """👤 【狀態面板 UI 優化版】徹底拔除後方臃腫括號說明，重現極簡極致質感"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    # 衍生計算
    str_val = int(p.get("strength", 10 + (level * 3)) * job_mod["str_mod"])
    agi_val = int(p.get("agility", 10 + (level * 2)) * job_mod["agi_mod"])
    int_val = int(p.get("intelligence", 10 + (level * 2)) * job_mod["int_mod"])
    vit_val = int(p.get("vitality", 10 + (level * 3)) * job_mod["vit_mod"])
    luk_val = int(p.get("luck", 10 + (level * 1)) * job_mod["luk_mod"])
    men_val = int(p.get("sprit", 10 + (level * 2)) * job_mod["men_mod"])
    free_pts = p.get("attribute_points", 0)
    
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    
    # 魔力空值過濾器
    current_mp = p.get("mp")
    if current_mp is None or current_mp == "None":
        current_mp = calculated_max_mp
        p["mp"] = calculated_max_mp
    
    status_color = "#FFCC00" if free_pts > 0 else "#8E8E93"
    
    flex_bubble = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#111111"}},
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "contents": [
                {"type": "text", "text": f"👤 勇者天賦狀態卡 (Lv.{level})", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
                {"type": "separator", "color": "#333333"},
                # 基礎狀態區
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"🎭 目前職業：🔥【{current_job}】", "size": "sm", "color": "#007AFF", "weight": "bold"},
                    {"type": "text", "text": f"📍 目前位置：📍【{p.get('current_map', '主城')}】", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"💖 生命狀態：{p['hp']} / {calculated_max_hp}", "size": "sm", "color": "#4CD964"},
                    {"type": "text", "text": f"🔷 魔力狀態：{current_mp} / {calculated_max_mp}", "size": "sm", "color": "#34AADC"},
                    {"type": "text", "text": f"💰 擁有金幣：🪙 {p['gold']}", "size": "sm", "color": "#FFD700"},
                    {"type": "text", "text": f"🌟 經驗進度：{p['exp']} / {level * 50}", "size": "sm", "color": "#AF52DE"},
                    {"type": "text", "text": f"✨ 剩餘潛能：{free_pts} 點", "size": "sm", "color": status_color, "weight": "bold"}
                ]},
                {"type": "separator", "color": "#333333"},
                # ✨ 【UI 升級優化】乾淨、清爽的純能力六圍展現，徹底與難看的括號道別！
                {"type": "text", "text": "⚔️ 核心戰術屬性六圍", "weight": "bold", "size": "sm", "color": "#FFFFFF"},
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"💪 力量 (STR): {str_val}", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"⚡ 敏捷 (AGI): {agi_val}", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🔮 智力 (INT): {int_val}", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🛡️ 體力 (VIT): {vit_val}", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🍀 幸運 (LUK): {luk_val}", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🌟 精神 (MEN): {men_val}", "size": "sm", "color": "#E0E0E0"}
                ]}
            ]
        }
    }
    
    if free_pts > 0:
        flex_bubble["footer"] = {
            "type": "box", "layout": "vertical", "backgroundColor": "#1C1C1E",
            "contents": [{"type": "text", "text": "💡 提示：輸入【加點 屬性名稱 點數】配點。（例如：加點 力量 5）", "size": "xs", "color": "#8E8E93", "align": "center", "wrap": True}]
        }

    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 我的背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="🛡️ 我的裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="🏪 補給商店", text="冒險商店")),
        QuickReplyItem(action=MessageAction(label="🦅 返回城鎮", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items)}
