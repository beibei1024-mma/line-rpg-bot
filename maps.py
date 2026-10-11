import db_core

# 🌐 完整 20 張地圖的等級限制與詳細敘述數據庫
MAPS_DATA = {
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
    "巨龍巢穴": {"level_req": 50, "desc": "🐉 世界Boss巨龍的甦醒之地。"},
    "精靈古都": {"level_req": 55, "desc": "🧝 守護世界樹核心的神秘都城。"},
    "機械工廠": {"level_req": 60, "desc": "🤖 蒸汽機械暴走的鋼鐵核心。"},
    "迷霧沼澤": {"level_req": 65, "desc": "🐊 劇毒泥潭組成的無盡迷宮。"},
    "黃金陵墓": {"level_req": 70, "desc": "👑 沉睡黃金法老王的詛咒地宮。"},
    "翡翠天境": {"level_req": 75, "desc": "🌟 瑞獸麒麟出沒的仙靈福地。"},
    "遺忘孤島": {"level_req": 80, "desc": "🦖 充斥史前恐龍的失落蠻荒孤島。"},
    "星空虛無": {"level_req": 85, "desc": "🌌 寂靜宇宙的群星吞噬黑洞。"},
    "湮滅神殿": {"level_req": 90, "desc": "👁️ 至高邪神克蘇魯的甦醒古殿。"},
    "諸神黃昏": {"level_req": 100, "desc": "⚔️ 終結神話的末日最終古戰場。"}
}

def get_maps_carousel(p):
    """【視覺化傳送陣大進階】動態把 20 張地圖包裝成 4 頁可左右滑動的 Carousel 按鈕圖卡"""
    map_list = list(MAPS_DATA.items())
    columns = []
    
    # 每次塞 5 張地圖進入一個頁籤卡片 (1 個 bubble)
    for i in range(0, len(map_list), 5):
        chunk = map_list[i:i+5]
        page_num = (i // 5) + 1
        
        body_contents = [
            {"type": "text", "text": f"🗺️ 世界傳送陣 - 第 {page_num} 頁", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
            {"type": "separator", "margin": "sm", "color": "#333333"}
        ]
        
        footer_buttons = []
        
        for name, info in chunk:
            if p["level"] >= info["level_req"]:
                btn_color = "#007AFF" # 滿足等級門檻：可點擊的亮藍色按鈕
                btn_label = f"📍前往 {name} (Lv.{info['level_req']})"
            else:
                btn_color = "#444444" # 等級不足：鎖定的低調灰色按鈕
                btn_label = f"🔒 {name} (需 Lv.{info['level_req']})"
                
            footer_buttons.append({
                "type": "button", 
                "style": "primary", 
                "color": btn_color, 
                "margin": "xs", 
                "height": "sm",
                "action": {"type": "message", "label": btn_label, "text": f"傳送 {name}"}
            })
            
        bubble = {
            "type": "bubble",
            "styles": {"body": {"backgroundColor": "#1C1C1E"}, "footer": {"backgroundColor": "#111111"}},
            "body": {"type": "box", "layout": "vertical", "contents": body_contents},
            "footer": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": footer_buttons}
        }
        columns.append(bubble)
        
    return {"type": "carousel", "contents": columns}

def change_map(p, target_map):
    """處理傳送判定邏輯，精準切碎口令提取地名"""
    target_map = target_map.replace("前往", "").replace("傳送", "").replace(" ", "").strip()
    
    if target_map not in MAPS_DATA:
        return f"❌ 傳送失敗！地圖庫中沒有【{target_map}】這張地圖。"
        
    info = MAPS_DATA[target_map]
    if p["level"] < info["level_req"]:
        return f"🔒 傳送失敗！【{target_map}】限制等級為 Lv.{info['level_req']}+，你目前只有 Lv.{p['level']}，請繼續歷練！"
        
    if p.get("current_map") == target_map:
        return f"📍 你目前已經在【{target_map}】了，不需要重複傳送。"
        
    if p["enemy"] is not None:
        return "❌ 傳送失敗！你的眼前還卡著一隻怪物，請先打倒牠或【逃跑】後才能傳送！"

    p["current_map"] = target_map
    db_core.save_player(p)
    return f"✨ 🔮 傳送成功！你已成功穿越時空傳送陣，抵達了——📍【{target_map}】！\n\n{info['desc']}"
