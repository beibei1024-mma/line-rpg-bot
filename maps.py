import db_core

# 🌐 完整世界時空廊道資料庫 - 已正式擴建「世界Boss」專屬時空副本
MAPS_DATA = {
    "主城": {"level_req": 1, "desc": "🏙️ 皇家安全城鎮。禁止械鬥，聚集了各行各業的 NPC 補給大師。"},
    "世界Boss": {"level_req": 1, "desc": "🌋 遠古禁忌副本。滅世泰坦正盤踞於此！全職業神聖技能已全數解鎖，全服勇者合力圍剿吧！"},
    "新手村": {"level_req": 1, "desc": "🌲 冒險者誕生的小聚落。"},
    "微光森林": {"level_req": 5, "desc": "🌳 螢光菇散落的迷幻之森。"},
    "寒冰極地": {"level_req": 10, "desc": "❄️ 萬年不化的封印雪原。"},
    "炙熱熔岩": {"level_req": 15, "desc": "🔥 岩漿縱橫的煉獄地帶。"},
    "骷髏荒漠": {"level_req": 20, "desc": "🌵 風沙埋葬遠古戰士的死寂沙丘。"},
    "風暴峽谷": {"level_req": 25, "desc": "⚡ 雷霆萬鈞的狂風裂谷。"},
    "幽暗地窖": {"level_req": 30, "desc": "💀 屍氣瀰漫的地下亡靈死域。"},
    "翡翠竹林": {"level_req": 35, "desc": "🎋 隱居東方刺客的清幽翠林。"},
    "亞特蘭提斯": {"level_req": 40, "desc": "🔱 沉沒海底的遠古波賽頓神殿。"},
    "天空之城": {"level_req": 45, "desc": "☁️ 漂浮雲端的傲慢諸神前庭。"},
    "巨龍巢穴": {"level_req": 50, "desc": "🐉 世界Boss巨龍的甦醒之地。"}
}

def get_maps_carousel(p):
    """【世界傳送廊 v2.5】動態把地圖包裝成可左右滑動的 Carousel 按鈕圖卡"""
    map_list = list(MAPS_DATA.items())
    columns = []
    p_level = p["level"]
    
    for i in range(0, len(map_list), 6):
        chunk = map_list[i:i+6]
        page_num = (i // 6) + 1
        
        body_contents = [
            {"type": "text", "text": f"🗺️ 世界傳送陣 - 第 {page_num} 頁", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
            {"type": "separator", "margin": "sm", "color": "#333333"}
        ]
        
        footer_buttons = []
        for name, info in chunk:
            if p_level >= info["level_req"]:
                if name == "主城": btn_color = "#007AFF"
                elif name == "世界Boss": btn_color = "#FF3B30" # 世界 Boss 副本專屬亮紅色按鈕
                else: btn_color = "#1478FF"
                
                btn_label = f"📍前往 {name}" if name in ("主城", "世界Boss") else f"📍前往 {name} (Lv.{info['level_req']})"
            else:
                btn_color = "#444444" 
                btn_label = f"🔒 {name} (需 Lv.{info['level_req']})"
                
            footer_buttons.append({
                "type": "button", "style": "primary", "color": btn_color, "margin": "xs", "height": "sm",
                "action": {"type": "message", "label": btn_label, "text": f"傳送 {name}"}
            })
            
        columns.append({
            "type": "bubble",
            "styles": {"body": {"backgroundColor": "#1C1C1E"}, "footer": {"backgroundColor": "#111111"}},
            "body": {"type": "box", "layout": "vertical", "contents": body_contents},
            "footer": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": footer_buttons}
        })
        
    return {"type": "carousel", "contents": columns}

def change_map(p, target_map):
    """處理時空傳送邏輯"""
    target_map = target_map.replace("前往", "").replace("傳送", "").replace(" ", "").strip()
    
    if target_map not in MAPS_DATA:
        return f"❌ 傳送失敗！時空地圖庫中沒有【{target_map}】這張地圖。"
        
    info = MAPS_DATA[target_map]
    if p["level"] < info["level_req"]:
        return f"🔒 傳送失敗！【{target_map}】限制門檻為 Lv.{info['level_req']}+，你目前只有 Lv.{p['level']}。"
        
    if p.get("current_map") == target_map:
        return f"📍 你目前已經在【{target_map}】區域了，不需要重複傳送。"
        
    # ✨ 核心優化：允許玩家自由離開危險地圖，唯獨身上如果正卡著普通野外小怪才需要防呆
    if p["enemy"] is not None and p.get("current_map") != "世界Boss":
        return "❌ 傳送失敗！你的眼前還卡著一隻野外怪物，請先打倒牠或選擇【逃跑】後才能引導傳送陣！"

    p["current_map"] = target_map
    
    # 📌 核心更新：如果玩家傳送的地點是世界Boss地圖，進去一落地的瞬間，主控台自動幫他生成魔神怪物實體
    if target_map == "世界Boss":
        import challenge_system
        boss_hp = challenge_system.check_boss_rebirth_and_get_hp()
        p["enemy"] = {
            "name": challenge_system.WORLD_BOSS_NAME,
            "hp": boss_hp,
            "max_hp": challenge_system.WORLD_BOSS_TOTAL_HP,
            "atk": 160,
            "gold_range": (1000, 5000),
            "exp": 5000,
            "skill": "👁️ 邪神神格：環境常駐【魔能潮汐】！",
            "drop_item": "舊神支配者之眼",
            "env": "🔮 魔能潮汐 (全屏大混戰，法術增幅異常狂暴)",
            "is_world_boss": True
        }
    else:
        # 如果飛去別的地方，自動卸載世界 Boss 狀態
        if p["enemy"] and p["enemy"].get("is_world_boss"):
            p["enemy"] = None
            
    db_core.save_player(p)
    return f"✨ 🔮 傳送成功！時空法陣光芒收束，你已順利跨越時空抵達 ── 📍【{target_map}】！\n\n{info['desc']}"
