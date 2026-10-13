import random
from player import get_player_battle_stats, save_player_battle_stats
from monsters import get_monster_by_id
from bag import add_item_to_bag, add_weapon_to_bag

def execute_battle(user_id, monster_id):
    # 優化：先在迴圈外載入玩家與怪物資料，避免戰鬥過程中重複存取或用迴圈查找
    player = get_player_battle_stats(user_id)
    monster = get_monster_by_id(monster_id)
    if not player or not monster:
        return "戰鬥初始化失敗。"

    p_hp = player["max_hp"] + player["equip_hp"]
    p_atk = player["atk"] + player["equip_atk"]
    p_def = player["def"] + player["equip_def"]
    
    m_hp = monster["hp"]
    m_atk = monster["atk"]
    m_def = monster["def"]
    
    battle_log = [f"⚔️ 遇到【{monster['name']}】！開始戰鬥！"]
    round_count = 0
    
    # 戰鬥核心迴圈優化：移除內部無用的狀態判斷，只做核心數值扣減
    while p_hp > 0 and m_hp > 0 and round_count < 30:
        round_count += 1
        
        # 玩家回合
        p_dmg = max(1, p_atk - m_def)
        m_hp -= p_dmg
        battle_log.append(f"第 {round_count} 回合：你對【{monster['name']}】造成 {p_dmg} 點傷害。")
        if m_hp <= 0:
            break
            
        # 怪物回合
        m_dmg = max(1, m_atk - p_def)
        p_hp -= m_dmg
        battle_log.append(f"第 {round_count} 回合：【{monster['name']}】對你造成 {m_dmg} 點傷害。")

    if m_hp <= 0:
        battle_log.append(f"🎉 戰鬥勝利！獲得經驗值 {monster['exp']}，金幣 {monster['gold']}。")
        # 掉落物處理迴圈優化：改用直觀的條件檢查，去除多層 nested 結構
        rewards_text = []
        for drop in monster.get("drops", []):
            if random.random() <= drop["rate"]:
                if drop["type"] == "item":
                    add_item_to_bag(user_id, drop["id"], 1)
                elif drop["type"] == "weapon":
                    add_weapon_to_bag(user_id, drop["id"], 1)
                rewards_text.append(f"{drop['name']}x1")
        
        if rewards_text:
            battle_log.append(f"🎁 獲得掉落物：{', '.join(rewards_text)}")
            
        save_player_battle_stats(user_id, monster["exp"], monster["gold"], p_hp)
    elif p_hp <= 0:
        battle_log.append("💀 你被擊敗了...（體力恢復至 20%）")
        save_player_battle_stats(user_id, 0, 0, int(player["max_hp"] * 0.2))
    else:
        battle_log.append("⏳ 戰鬥平手，不分勝負。")
        save_player_battle_stats(user_id, 0, 0, p_hp)
        
    return "\n".join(battle_log)
