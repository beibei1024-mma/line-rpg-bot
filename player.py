import db_core
import weapons

def get_status_text(p):
    # 讀取當前裝備的武器傷害加成數值，組裝成彩色字體狀態
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    return (
        f"👤 【勇者狀態】\n"
        f"等級: Lv.{p['level']}\n"
        f"血量: {p['hp']} / {p['max_hp']}\n"
        f"裝備: ⚔️ {p['weapon']} (傷害+{w_bonus})\n"
        f"經驗值: {p['exp']} / {p['level'] * 50}\n"
        f"金幣: 💰 {p['gold']}\n\n"
        f"💡 輸入【冒險商店】購買神兵利器！"
    )

def handle_resurrect(p):
    # 復活判定判定邏輯：若玩家還活著則提示，已陣亡則扣除金幣並恢復 50% 滿血狀態
    if p["hp"] > 0:
        return "你還活著呢！"
    else:
        p["hp"] = int(p["max_hp"] * 0.5)
        p["gold"] = max(0, p["gold"] - 20)
        # 復活屬於特定大事件，強制寫入雲端資料庫存檔
        db_core.save_player(p)
        return f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
