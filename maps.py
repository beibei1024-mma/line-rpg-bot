# 🗺️ 世界地圖大數據（完全獨立儲存於 maps.py，你隨時可以來這裡擴充新世界、新副本！）
MAPS_DATA = {
    "新手村": {
        "level_req": 1, 
        "description": "和平祥和的小村莊，冒險的出發點。"
    },
    "骷髏荒漠": {
        "level_req": 5, 
        "description": "危險的沙漠，充斥著不死生物與無盡的寶藏。"
    }
}

def get_maps_list_text(p):
    # 預留未來的地圖選單查詢功能
    text = "🗺️ 【世界地圖列表】\n"
    for name, info in MAPS_DATA.items():
        text += f"📍 {name} (Lv.{info['level_req']}+) - {info['description']}\n"
    return text
