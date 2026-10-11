import db_core
import weapons
import jobs
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

def get_status_card(p):
    """👤 【狀態面板 3.0 極簡傳奇版】移除波動範圍、拿掉贅餘標題、完美解決經驗吃字"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    # 🌟 1. 核心基礎六圍計算
    str_val = int(p.get("strength", 10 + (level * 3)) * job_mod["str_mod"])
    agi_val = int(p.get("agility", 10 + (level * 2)) * job_mod["agi_mod"])
    int_val = int(p.get("intelligence", 10 + (level * 2)) * job_mod["int_mod"])
    vit_val = int(p.get("vitality", 10 + (level * 3)) * job_mod["vit_mod"])
    luk_val = int(p.get("luck", 10 + (level * 1)) * job_mod["luk_mod"])
    men_val = int(p.get("sprit", 10 + (level * 2)) * job_mod["men_mod"])
    free_pts = p.get("attribute_points", 0)
    
    # 🌟 2. 攻防進階與上限衍生計算 (依需求：內部保留波動計算，面板只顯示最大單一數字)
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    p_atk_single = 12 + str_val + w_bonus
    m_atk_single = 10 + int_val
    
    p_def = vit_val // 2
    m_def = men_val // 2
    
    double_chance = min(60, 2 + (agi_val // 6))
    crit_chance = min(80, 10 + (luk_val // 5))
    
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    
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
                {"type": "text", "text": f"👤 勇者狀態面板 (Lv.{level})", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
                {"type": "separator", "color": "#333333"},
                
                # 📜 基礎大狀態展示區 (✨ 經驗值優化：切分至單獨下一行，徹底解決吃字問題)
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"🎭 目前職業：🔥【{current_job}】", "size": "sm", "color": "#007AFF", "weight": "bold"},
                    {"type": "text", "text": f"💰 擁有金幣：🪙 {p['gold']}", "size": "sm", "color": "#FFD700"},
                    {"type": "text", "text": f"🌟 經驗進度：{p['exp']} / {level * 50}", "size": "sm", "color": "#AF52DE"},
                    {"type": "text", "text": f"✨ 剩餘潛能點數：{free_pts} 點", "size": "sm", "color": status_color, "weight": "bold"}
                ]},
                {"type": "separator", "color": "#333333"},
                
                # ⚔️ 欄位一：角色素質 (✨ 依需求：更名為【 角色素質 】)
                {"type": "text", "text": "🧬 【 角色素質 】", "weight": "bold", "size": "xs", "color": "#8E8E93"},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💪 力量: {str_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"⚡ 敏捷: {agi_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"🔮 智力: {int_val}", "size": "xs", "color": "#FFFFFF", "flex": 1}
                ]},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"🛡️ 體力: {vit_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"🍀 幸運: {luk_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"🌟 精神: {men_val}", "size": "xs", "color": "#FFFFFF", "flex": 1}
                ]},
                {"type": "separator", "color": "#222222", "margin": "sm"},
                
                # ⚔️ 欄位二：攻防數值欄 (✨ 依需求：拔除「戰術攻防進階值」字串，改用單一數字展示)
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💥 物傷: {p_atk_single}", "size": "xs", "color": "#FF9500", "flex": 1},
                    {"type": "text", "text": f"🔮 魔傷: {m_atk_single}", "size": "xs", "color": "#5AC8FA", "flex": 1}
                ]},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"🧱 物防: {p_def}", "size": "xs", "color": "#FF3B30", "flex": 1},
                    {"type": "text", "text": f"🌀 法防: {m_def}", "size": "xs", "color": "#AF52DE", "flex": 1}
                ]},
                {"type": "separator", "color": "#222222", "margin": "sm"},
                
                # ⚔️ 欄位三：戰術機率欄 (✨ 依需求：拔除「戰場觸發修正率」字串)
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💨 連擊率: {double_chance}%", "size": "xs", "color": "#E0E0E0", "flex": 1},
                    {"type": "text", "text": f"✨ 爆擊率: {crit_chance}%", "size": "xs", "color": "#FFCC00", "weight": "bold", "flex": 1}
                ]},
                {"type": "separator", "color": "#222222", "margin": "sm"},
                
                # ⚔️ 欄位四：血量魔力上限欄 (✨ 依需求：拔除「當前狀態精準值」字串)
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💖 血量: {p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#4CD964", "flex": 1},
                    {"type": "text", "text": f"🔷 魔力: {current_mp} / {calculated_max_mp}", "size": "xs", "color": "#007AFF", "flex": 1}
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
