import db_core
import weapons

def get_status_text(p):
    """【原創六大天賦面板】讀取資料庫六大屬性，根據自主設計公式動態計算衍生戰鬥數值"""
    level = p.get("level", 1)
    
    # 🎲 1. 讀取六大基礎天賦屬性（若為新玩家，開機自動依等級初始化基礎值）
    str_val = p.get("strength", 10 + (level * 3))       # 💪 力量
    agi_val = p.get("agility", 10 + (level * 2))        # ⚡ 敏捷
    int_val = p.get("intelligence", 10 + (level * 2))   # 🔮 智力
    vit_val = p.get("vitality", 10 + (level * 3))       # 🛡️ 體力
    luk_val = p.get("luck", 10 + (level * 1))           # 🍀 幸運
    men_val = p.get("sprit", 10 + (level * 2))          # 🌟 精神 (資料庫寫法對齊 sprit)
    
    # ⚔️ 2. 讀取裝備與基礎攻擊力
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0
    
    # 🧮 3. 實體連動公式計算（完全對齊你的設計需求）：
    
    # 💪 力量影響：物理傷害 (基礎加上力量增幅，並受到武器加成)
    min_p_dmg = 5 + (str_val // 2) + w_bonus
    max_p_dmg = 12 + str_val + w_bonus
    
    # ⚡ 敏捷影響：閃避率、連續攻擊機率
    evade_chance = min(50, 5 + (agi_val // 8))          # 閃避率上限 50%
    double_atk_chance = min(60, 2 + (agi_val // 6))     # 連擊率上限 60%
    
    # 🔮 智力影響：魔法攻擊與最大最小魔法傷害
    min_m_dmg = 3 + (int_val // 2)
    max_m_dmg = 10 + int_val
    
    # 🛡️ 體力影響：防禦力與血量上限
    defense = vit_val // 2
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    
    # 🍀 幸運影響：爆擊率、爆擊傷害倍率
    crit_chance = min(80, 10 + (luk_val // 5))          # 暴擊率上限 80%
    crit_dmg_multiplier = 1.5 + (luk_val * 0.005)       # 基礎 1.5 倍，每點幸運再加 0.5% 暴擊傷害
    
    # 🌟 精神影響：魔法防禦力、最大魔力(MP)
    m_defense = men_val // 2
    max_mp = 50 + (men_val * 4) + (level * 5)
    current_mp = p.get("mp", max_mp)

    return (
        f"👤 【勇者狀態面板】\n"
        f"─────────────────\n"
        f"🏅 冒險等級：Lv.{level}\n"
        f"📍 當前位置：📍【{p.get('current_map', '新手村')}】\n"
        f"💖 生命狀態：{p['hp']} / {calculated_max_hp}\n"
        f"🔷 魔力狀態：{current_mp} / {max_mp}\n"
        f"⚔️ 當前裝備：{p['weapon']} (傷害+{w_bonus})\n"
        f"💰 擁有金幣：💰 {p['gold']}\n"
        f"🌟 經驗進度：{p['exp']} / {level * 50}\n"
        f"─────────────────\n"
        f"💪 力量 (STR)：{str_val} 點\n"
        f"   ┠ 🚀 物理傷害：⚔️ {min_p_dmg} ～ {max_p_dmg}\n"
        f"⚡ 敏捷 (AGI)：{agi_val} 點\n"
        f"   ┠ 💨 戰場閃避率：{evade_chance}%\n"
        f"   ┠ 🌪️ 連續攻擊率：{double_atk_chance}%\n"
        f"🔮 智力 (INT)：{int_val} 點\n"
        f"   ┠ 🔮 魔法傷害：✨ {min_m_dmg} ～ {max_m_dmg}\n"
        f"🛡️ 體力 (VIT)：{vit_val} 點\n"
        f"   ┠ 🧱 物理防禦：{defense} 點\n"
        f"🍀 幸運 (LUK)：{luk_val} 點\n"
        f"   ┠ 🔥 致命爆擊率：{crit_chance}%\n"
        f"   ┠ 💥 爆擊傷害：{int(crit_dmg_multiplier * 100)}%\n"
        f"🌟 精神 (MEN)：{men_val} 點\n"
        f"   ┠ 🌀 魔法防禦：{m_defense} 點\n"
        f"─────────────────\n"
        f"💡 提示：點擊下方選單即可直接出發冒險！"
    )

def handle_resurrect(p):
    if p["hp"] > 0:
        return "你還活著呢！"
    else:
        level = p.get("level", 1)
        vit_val = p.get("vitality", 10 + (level * 3))
        max_hp = 100 + (vit_val * 5) + (level * 15)
        
        p["hp"] = int(max_hp * 0.5)
        p["gold"] = max(0, p["gold"] - 20)
        db_core.save_player(p)
        return f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
