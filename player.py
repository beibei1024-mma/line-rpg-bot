import db_core
import weapons

def get_status_text(p):
    """【原創能力值面板】讀取資料庫屬性，並將力量、敏捷、智力與動態暴擊率包裝成精美面板"""
    level = p.get("level", 1)
    
    # 🎲 基礎屬性抓取公式：若欄位不存在則依等級自動給予初始成長（力量+3、敏捷+2、智力+2）
    str_val = p.get("strength", 10 + (level * 3))   
    agi_val = p.get("agility", 10 + (level * 2))    
    int_val = p.get("intelligence", 10 + (level * 2)) 
    
    # ⚔️ 讀取武器與攻擊加成
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    
    # 💥 動態暴擊率公式：敏捷越高，戰場上的致命暴擊率越高！（每 5 點敏捷增加 1% 暴擊率，基礎 10%）
    crit_chance = 10 + (agi_val // 5)
    
    return (
        f"👤 🪐 【永劫編年史 ・ 勇者狀態】\n"
        f"─────────────────\n"
        f"🏅 冒險稱號：Lv.{level} 傳奇勇者\n"
        f"📍 當前位置：📍【{p.get('current_map', '新手村')}】\n"
        f"🩸 生命狀態：{p['hp']} / {p['max_hp']}\n"
        f"⚔️ 裝備神兵：{p['weapon']} (傷害+{w_bonus})\n"
        f"💰 雲端金幣：💰 {p['gold']}\n"
        f"🌟 歷練經驗：{p['exp']} / {level * 50}\n"
        f"─────────────────\n"
        f"💪 力量 (STR)：{str_val} 點 (提升物理基礎傷害)\n"
        f"⚡ 敏捷 (AGI)：{agi_val} 點 (提升戰場暴擊機率)\n"
        f"🔮 智力 (INT)：{int_val} 點 (提升藥水魔法治療)\n"
        f"💥 致命暴擊率：🔥 {crit_chance}%\n"
        f"─────────────────\n"
        f"💡 提示：能力值已與戰鬥核心綁定！輸入【世界地圖】或點擊選單開啟傳送陣！"
    )

def handle_resurrect(p):
    # 復活判定邏輯：恢復 50% 滿血狀態並扣除金幣
    if p["hp"] > 0:
        return "你還活著呢！"
    else:
        p["hp"] = int(p["max_hp"] * 0.5)
        p["gold"] = max(0, p["gold"] - 20)
        # 復活屬於特定大事件，強制寫入雲端資料庫存檔
        db_core.save_player(p)
        return f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
