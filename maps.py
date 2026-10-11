import db_core

MAPS_DATA = {
    "新手村": {
        "level_req": 1, 
        "description": "🌲 和平祥和的小村莊，四周潛伏著史萊姆與哥布林小偷。"
    },
    "骷髏荒漠": {
        "level_req": 4, 
        "description": "🌵 風沙漫天的危險荒漠，充斥著強盜與遠古精英骷髏戰士！"
    },
    "巨龍巢穴": {
        "level_req": 7, 
        "description": "🔥 滿布岩漿的煉獄深淵，世界Boss地獄紅蓮巨龍的沉睡之地！"
    },
    # ✨ 企劃二：擴充全新神階終極地圖
    "湮滅神殿": {
        "level_req": 50, 
        "description": "👁️ 漂浮於虛空之中的破碎神殿，充斥著不可名狀的舊神守衛，以及至高邪神！"
    }
}

def get_maps_list_text(p):
    text = "🗺️ 🪐 【世界地圖傳送陣】\n"
    text += f"💡 你目前所在位置：📍【{p.get('current_map', '新手村')}】\n"
    text += "─────────────────\n"
    for name, info in MAPS_DATA.items():
        if p["level"] >= info["level_req"]:
            status = f"🟢 可進入 (Lv.{info['level_req']}+)"
        else:
            status = f"🔒 鎖定中 (需達到 Lv.{info['level_req']})"
        text += f"📍 【{name}】\n   狀態：{status}\n   簡介：{info['description']}\n\n"
    text += "✍️ 輸入指令【傳送 地圖名稱】即可前往新世界！\n（例如：傳送 骷髏荒漠）"
    return text

def change_map(p, target_map):
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
    
    return f"✨ 🔮 傳送成功！你已成功穿越時空傳送陣，抵達了——📍【{target_map}】！\n\n{info['description']}"
