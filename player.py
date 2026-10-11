import db_core
import weapons
import jobs

def get_status_card(p):
    """【企劃 C 史詩級升級】將原先沉悶的純文字面板，轉化為媲美高階網頁的 Flex 狀態卡"""
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
    
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    
    status_color = "#FFCC00" if free_pts > 0 else "#8E8E93"
    
    card_json = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#111111"}},
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "contents": [
                {"type": "text", "text": f"👤 勇者天賦卡 (Lv.{level})", "weight": "bold", "size": "lg", "color": "#FFFFFF", "align": "center"},
                {"type": "separator", "color": "#333333"},
                # 基礎大狀態
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"🎭 目前職業：🔥【{current_job}】", "size": "sm", "color": "#007AFF", "weight": "bold"},
                    {"type": "text", "text": f"📍 目前位置：📍【{p.get('current_map', '新手村')}】", "size": "sm", "color": "#E0E0E0"},
                    {"type": "text", "text": f"💖 生命狀態：{p['hp']} / {calculated_max_hp}", "size": "sm", "color": "#4CD964"},
                    {"type": "text", "text": f"🔷 魔力狀態：{p.get('mp', calculated_max_mp)} / {calculated_max_mp}", "size": "sm", "color": "#34AADC"},
                    {"type": "text", "text": f"💰 擁有金幣：🪙 {p['gold']}", "size": "sm", "color": "#FFD700"},
                    {"type": "text", "text": f"🌟 經驗進度：{p['exp']} / {level * 50}", "size": "sm", "color": "#AF52DE"},
                    {"type": "text", "text": f"✨ 剩餘潛能：{free_pts} 點", "size": "sm", "color": status_color, "weight": "bold"}
                ]},
                {"type": "separator", "color": "#333333"},
                # 六圍屬性排列
                {"type": "text", "text": "⚔️ 核心戰術屬性六圍", "weight": "bold", "size": "sm", "color": "#FFFFFF"},
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"💪 力量 (STR): {str_val}  (物傷: {5+(str_val//2)+w_bonus}~{12+str_val+w_bonus})", "size": "xs", "color": "#E0E0E0"},
                    {"type": "text", "text": f"⚡ 敏捷 (AGI): {agi_val}  (連擊率: {min(60, 2+(agi_val//6))}%)", "size": "xs", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🔮 智力 (INT): {int_val}  (魔傷: {3+(int_val//2)}~{10+int_val})", "size": "xs", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🛡️ 體力 (VIT): {vit_val}  (防禦力: {vit_val//2})", "size": "xs", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🍀 幸運 (LUK): {luk_val}  (爆擊率: {min(80, 10+(luk_val//5))}%)", "size": "xs", "color": "#E0E0E0"},
                    {"type": "text", "text": f"🌟 精神 (MEN): {men_val}  (法防: {men_val//2})", "size": "xs", "color": "#E0E0E0"}
                ]}
            ]
        }
    }
    
    # 若有剩餘點數，自動附加快捷配點提示按鈕
    if free_pts > 0:
        card_json["footer"] = {
            "type": "box", "layout": "vertical", "backgroundColor": "#1C1C1E",
            "contents": [{"type": "text", "text": "💡 提示：輸入【加點 屬性名稱 點數】配點。\n（例如：加點 力量 5）", "size": "xs", "color": "#8E8E93", "align": "center", "wrap": True}]
        }
    return card_json

def handle_resurrect(p):
    if p["hp"] > 0: return "你還活著呢！"
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    base_vit = p.get("vitality", 10 + (level * 3))
    vit_val = int(base_vit * job_mod["vit_mod"])
    max_hp = 100 + (vit_val * 5) + (level * 15)
    p["hp"] = int(max_hp * 0.5)
    p["gold"] = max(0, p["gold"] - 20)
    db_core.save_player(p)
    return f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
