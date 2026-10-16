# maps.py - 世界傳送廊與副本傳送重設核心

import db_core
import monsters

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
    "巨龍巢穴": {"level_req": 50, "desc": "🐉 世界Boss巨龍的甦醒之地。"},
    "精靈古都": {"level_req": 55, "desc": "🧝 守護世界樹核心的神秘都城。"},
    "機械工廠": {"level_req": 60, "desc": "🤖 蒸汽機械暴走的鋼鐵核心。"},
    "迷霧沼澤": {"level_req": 65, "desc": "🐊 劇毒泥潭組成的無盡迷宮。"},
    "黃金陵墓": {"level_req": 70, "desc": "👑 沉睡黃金法老王的詛咒地宮。"},
    "翡翠天境": {"level_req": 75, "desc": "🌟 瑞獸麒麟出沒的仙靈福地。"},
    "遺忘孤島": {"level_req": 80, "desc": "🦖 充斥史前恐龍的失落蠻荒孤島。"},
    "星空虛無": {"level_req": 85, "desc": "🌌 寂靜宇宙的群星吞噬黑洞。"},
    "湮滅神殿": {"level_req": 90, "desc": "👁️ 至高邪神克蘇魯的甦醒古殿。"},
    "諸神黃昏": {"level_req": 100, "desc": "⚔️ 終結神話的末日最終古戰場。"},
    "幽冥礦坑[20等副本]": {"level_req": 20, "desc": "⛏️ 20等打寶副本。充斥著怨念骷髏，看守著遠古手工裝備必備的精煉暗鐵礦石！"},
    "沉沒古船[40等副本]": {"level_req": 40, "desc": "🏴‍☠️ 40等打寶副本。幽靈船長看守著遠古詛咒寶箱，出產中階手工神兵的關鍵淬火核心！"},
    "不朽王陵[60等副本]": {"level_req": 60, "desc": "👑 60等打寶副本。沉睡的古代君王傀儡巨像，守護著高等裝備必備的帝王金精！"},
    "天外天境[80等副本]": {"level_req": 80, "desc": "🌌 80等打寶副本。漂浮在星空裂縫中的虛空幻境，出產洗鍊史詩、遠古神話裝備的星海晶核！"},
    "諸神黃昏[100等副本]": {"level_req": 100, "desc": "🔱 100等終極副本。隕落諸神的破碎神殿，產出至高誓約結晶，是打造毀滅級最終神兵的唯一材料！"}
}

def get_maps_carousel(p):
    """【世界傳送廊 v2.7】"""
    map_list = list(MAPS_DATA.items())
    columns = []
    p_level = p["level"]

    for i in range(0, len(map_list), 6):
        chunk = map_list[i:i+6]
        page_num = (i // 6) + 1
        body_contents = [
            {"type": "text", "text": "🗺️ 世界傳送陣 - 第 " + str(page_num) + " 頁", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
            {"type": "separator", "margin": "sm", "color": "#333333"}
        ]
        footer_buttons = []
        for name, info in chunk:
            if p_level >= info["level_req"]:
                if name == "主城": btn_color = "#007AFF"
                elif name == "世界Boss": btn_color = "#FF3B30"
                elif "副本" in name: btn_color = "#AF52DE"
                else: btn_color = "#1478FF"
                btn_label = "📍前往 " + name if name in ("主城", "世界Boss") or "副本" in name else "📍前往 " + name + " (Lv." + str(info['level_req']) + ")"
            else:
                btn_color = "#444444"
                btn_label = "🔒 " + name + " (需 Lv." + str(info['level_req']) + ")"

            footer_buttons.append({
                "type": "button", "style": "primary", "color": btn_color, "margin": "xs", "height": "sm",
                "action": {"type": "message", "label": btn_label, "text": "傳送 " + name}
            })

        columns.append({
            "type": "bubble",
            "styles": {"body": {"backgroundColor": "#1C1C1E"}, "footer": {"backgroundColor": "#111111"}},
            "body": {"type": "box", "layout": "vertical", "contents": body_contents},
            "footer": {"type": "box", "layout": "vertical", "spacing": "xs", "contents": footer_buttons}
        })

    return {"type": "carousel", "contents": columns}

def change_map(p, target_map):
    target_map = target_map.replace("前往", "").replace("傳送", "").replace(" ", "").strip()

    if target_map not in MAPS_DATA:
        return "❌ 傳送失敗！時空地圖庫中沒有【" + target_map + "】這張地圖。"

    info = MAPS_DATA[target_map]
    if p["level"] < info["level_req"]:
        return "🔒 傳送失敗！【" + target_map + "】限制門檻為 Lv." + str(info['level_req']) + "+，你目前只有 Lv." + str(p['level']) + "。"

    if p.get("current_map") == target_map:
        return "📍 你目前已經在【" + target_map + "】區域了，不需要重複傳送。"

    if p["enemy"] is not None and p.get("current_map") != "世界Boss" and "副本" not in p.get("current_map", ""):
        return "❌ 傳送失敗！你的眼前還卡著一隻野外怪物，請先打倒牠或選擇【逃跑】後才能引導傳送陣！"

    p["current_map"] = target_map

    if target_map == "世界Boss":
        import challenge_system
        boss_hp = challenge_system.check_boss_rebirth_and_get_hp()
        p["enemy"] = {
            "name": challenge_system.WORLD_BOSS_NAME, "hp": boss_hp, "max_hp": challenge_system.WORLD_BOSS_TOTAL_HP,
            "atk": 160, "gold_range": (1000, 5000), "exp": 5000, "skill": "👁️ 邪神神格：環境常駐【魔能潮汐】！",
            "drop_item": "舊神支配者之眼", "env": "🔮 魔能潮汐 (全服大混戰，法術增幅異常狂暴)", "is_world_boss": True
        }
    else:
        p["enemy"] = None

    db_core.save_player(p)
    return "✨ 🔮 傳送成功！時空法陣光芒收束，你已順利跨越時空抵達 ── 📍【" + target_map + "】！\n\n" + info['desc'] + "\n\n💡 提示：點擊下方【🔍 尋找怪物】即可在此區域遭遇強敵！"
# === END OF FILE ===
