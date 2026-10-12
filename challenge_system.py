# challenge_system.py - 世界 Boss 全服共鬥與傷害貢獻排行中樞 v3.0

import random
import json
import time
import db_core

def get_challenge_menu(p):
    """⚔️ 生成世界 Boss 與深淵試煉塔的 Flex 選單"""
    # 讀取全服 Boss 殘餘血量與目前排行（保底防爆）
    boss_hp = db_core.load_global_value("world_boss_hp", 50000)
    boss_max = 50000
    
    contents = [
        {"type": "text", "text": "🏆 皇家遠古烈焰試煉挑戰場", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "separator", "margin": "sm", "color": "#333333"},
        {"type": "text", "text": "🌋 【全服連線 · 世界挑戰賽】", "weight": "bold", "size": "sm", "color": "#FF3B30", "margin": "md"},
        {"type": "text", "text": "👿 當前巨獸：🌋 滅世紅蓮地獄巨龍 (T4神格)", "size": "xs", "color": "#FF9500"},
        {"type": "text", "text": f"🩸 全服共用血量：{boss_hp} / {boss_max}", "size": "xs", "color": "#FF2D55"},
        {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "marginTop": "xs",
         "action": {"type": "message", "label": "🔥 立即切入戰場圍剿 Boss", "text": "挑戰世界Boss"}},
        {"type": "separator", "margin": "md", "color": "#333333"},
        {"type": "text", "text": "👑 【天梯排行榜 · 傷害貢獻名人堂】", "weight": "bold", "size": "xs", "color": "#FFCC00", "margin": "sm"}
    ]
    
    # 讀取並渲染前 5 名貢獻度
    rank_str = db_core.load_global_value("world_boss_ranks", "[]")
    try: rank_list = json.loads(rank_str)
    except: rank_list = []
    
    if not rank_list:
        contents.append({"type": "text", "text": "   暫無戰意，等待首位勇者拔刀開荒！", "size": "xxs", "color": "#8E8E93"})
    else:
        for idx, r in enumerate(rank_list[:5]):
            medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                    {"type": "text", "text": f"{medals[idx]} No.{idx+1} {r['name']}", "size": "xxs", "color": "#E0E0E0", "flex": 4},
                    {"type": "text", "text": f"💥 {r['dmg']}", "size": "xxs", "color": "#FFCC00", "align": "end", "flex": 2}
                ]
            })
            
    return {"flex": {"type": "bubble", "styles": {"body": {"backgroundColor": "#1A1A1A"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}, "quick_reply": db_core.make_battle_card("", p, None)["quick_reply"]}

def execute_world_boss_raid(p):
    """💥 發動突襲：計算個人多部位攻擊力，對世界 Boss 實體削血並登錄名人堂"""
    if p["hp"] <= 0:
        return db_core.make_battle_card("❌ 圍剿失敗！你目前处于陣亡狀態，請先點擊【😇 祈求復活】！", p, None)
        
    # 讀取已穿戴裝備的最終累計物傷
    eq_slots_str = p.get("equipped_slots", "{}")
    try: equipped = json.loads(eq_slots_str)
    except: equipped = {}
    
    eq_atk = sum([eq.get("atk", 0) for eq in equipped.values()])
    base_dmg = 50 + int(p.get("strength", 10) * 1.5) + eq_atk
    
    # 隨機爆擊波動公式 (1.0倍 ~ 2.5倍)
    final_p_dmg = int(base_dmg * random.uniform(1.0, 2.5))
    
    # 讀取並扣除全服 Boss 血量
    global_hp = db_core.load_global_value("world_boss_hp", 5000000)
    if global_hp <= 0:
        return db_core.make_battle_card("👑 🏆 滅世巨龍已被全服勇者攜手屠殺寂滅！請等待新一賽季魔王降臨！", p, None)
        
    global_hp = max(0, global_hp - final_p_dmg)
    db_core.save_global_value("world_boss_hp", global_hp)
    
    # ✍️ 更新即時全服傷害貢獻排行榜
    rank_str = db_core.load_global_value("world_boss_ranks", "[]")
    try: rank_list = json.loads(rank_str)
    except: rank_list = []
    
    p_name = f"勇者_{p['user_id'][:6]}"
    user_rank = next((r for r in rank_list if r["uid"] == p["user_id"]), None)
    
    if user_rank:
        user_rank["dmg"] += final_p_dmg
    else:
        rank_list.append({"uid": p["user_id"], "name": p_name, "dmg": final_p_dmg})
        
    # 依傷害多寡由高到低重新洗牌排序
    rank_list.sort(key=lambda x: x["dmg"], reverse=True)
    db_core.save_global_value("world_boss_ranks", json.dumps(rank_list, ensure_ascii=False))
    
    # 👿 魔王殘暴反擊防壁公式
    boss_retaliate_atk = random.randint(150, 400)
    p["hp"] = max(0, p["hp"] - boss_retaliate_atk)
    
    log = f"🌋 【 世界 Boss 戰報快訊 】 🌋\n───────────────────\n你踏碎熔岩、引導全身神兵武裝，正面突襲滅世巨龍！\n\n💥 戰果重創：你對巨龍轟出了 {final_p_dmg} 點累積傷害！\n🩹 巨龍反噬：巨龍狂暴擺尾，突破你的防線對你造成 -{boss_retaliate_atk} 點真实傷害！"
    
    if p["hp"] <= 0:
        p["enemy"] = None
        p["current_map"] = "主城"
        log += "\n💀 【力戰力竭】你因傷勢過重在巨龍腳下光榮戰死了！已被靈魂傳送回主城。"
        
    db_core.save_player(p)
    return db_core.make_battle_card(log, p, None)
