# battle_core.py
import random
from linebot.models import TextSendMessage, FlexSendMessage

import db_core
import monsters
import weapons
import bag
import jobs

def process_battle_logic(event, line_bot_api, p, user_msg):
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    if current_job not in jobs.JOBS_DATA:
        current_job = "初心者"
    job_mod = jobs.JOBS_DATA[current_job]

    # 六大屬性實體公式連動
    base_str = p.get("strength", 10 + (level * 3))
    base_agi = p.get("agility", 10 + (level * 2))
    base_int = p.get("intelligence", 10 + (level * 2))
    base_vit = p.get("vitality", 10 + (level * 3))
    base_luk = p.get("luck", 10 + (level * 1))
    base_men = p.get("sprit", 10 + (level * 2))
    
    str_val = int(base_str * job_mod["str_mod"])
    agi_val = int(base_agi * job_mod["agi_mod"])
    int_val = int(base_int * job_mod["int_mod"])
    vit_val = int(base_vit * job_mod["vit_mod"])
    luk_val = int(base_luk * job_mod["luk_mod"])
    men_val = int(base_men * job_mod["men_mod"])
    
    w_bonus = weapons.SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in weapons.SHOP_WEAPONS else 0

    # 魔力上限與當前魔力維護
    max_mp = 50 + (men_val * 4) + (level * 5)
    if "mp" not in p:
        p["mp"] = max_mp

    # A. 處理【轉職】
    if user_msg.startswith("轉職"):
        target_job = user_msg.replace("轉職", "").strip()
        if target_job not in jobs.JOBS_DATA:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！秘法圖鑑中不存在【{target_job}】這個職業。"))
            return
        if target_job not in job_mod["next_jobs"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 轉職失敗！你目前的本命職業是【{current_job}】，無法跨系進階。"))
            return
        if p["level"] < jobs.JOBS_DATA[target_job]["req_lvl"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 境界未到！轉職為【{target_job}】需要突破至 Lv.{jobs.JOBS_DATA[target_job]['req_lvl']}+。"))
            return
            
        p["job"] = target_job
        # 轉職後自動把 MP 補滿
        p["mp"] = 50 + (men_val * 4) + (level * 5)
        db_core.save_player(p)
        log_text = f"✨ 🎉 【本命階級突破成功】 🎉 ✨\n🛡️ 你從【{current_job}】正式進階為更高的職業形態——🔥【{target_job}】！\n專屬技能與魔力已全線翻倍刷新！快輸入【我的狀態】查看全新戰力！"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="轉職成功", contents=db_core.make_battle_card(log_text, p, None)))
        return

    # 【轉職卡關防呆強制判定】
    if (p["level"] == 25 and job_mod["tier"] == 0) or (p["level"] == 50 and job_mod["tier"] == 1) or (p["level"] == 100 and job_mod["tier"] == 2):
        if user_msg in ["尋尋怪", "尋怪", "攻擊", "技能", "施放技能"]:
            job_notice = jobs.get_job_options_text(p)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🔒 【天賦界限卡關中】\n勇者！你目前已達到了 Lv.{p['level']} 的天賦瓶頸，必須完成天賦覺醒才能繼續獲取經驗與冒險！\n\n{job_notice}"))
            return

    # B. 處理【加點 / 配點】
    if user_msg.startswith("加點") or user_msg.startswith("配點"):
        raw_msg = user_msg.replace("配點", "加點").split()
        # 由於大腦前端去除了空格，為了相容原本的加點解析，做簡單切分
        if not user_msg.startswith("加點"): return
        # 格式防呆提示
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💡 請輸入乾淨的口令格式，例如：加點 力量 5 (注意中間要留空格喔！)"))
        return

    # C. 處理【尋找怪物】
    elif user_msg in ["尋找怪物", "尋怪"]:
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】重整旗鼓。"))
            return
        if p["enemy"] is not None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚔️ 你的眼前還卡著一隻怪！請專心應戰（輸入【攻擊】或【技能】）！"))
            return
        current_location = p.get("current_map", "新手村")
        random_monster = monsters.generate_random_monster(current_location)
        p["enemy"] = random_monster
        db_core.save_player(p)
        env_now = p.get("map_env_status", "🟢 平靜")
        title_log = f"⚠️ 警報！你在📍【{current_location}】遭遇強敵！\n當前天象：【{env_now}】\n怪物能力：🔰 {random_monster['skill']}"
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=db_core.make_battle_card(title_log, p, random_monster)))
        return

    # D. 處理【攻擊】與【技能】核心戰鬥邏輯
    elif user_msg in ["攻擊", "技能", "施放技能"]:
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法戰鬥（可能已陣亡或周圍沒有怪物）。"))
            return
            
        enemy = p["enemy"]
        log = ""
        is_using_skill = "技能" in user_msg or user_msg == "技能"
        
        # 讀取當前職業技能庫
        avail_skills = job_mod["skills"]
        active_skill_name = [k for k, v in avail_skills.items() if v.get("type") == "active"]
        
        # 決定本輪發動的技能名稱
        skill_to_cast = active_skill_name[0] if active_skill_name else None
        
        # 戰鬥屬性衍生計算
        crit_chance = min(80, 10 + (luk_val // 5)) / 100.0          
        crit_dmg_mod = 1.5 + (luk_val * 0.005)                     
        evade_chance = min(50, 5 + (agi_val // 8)) / 100.0          
        double_atk_chance = min(60, 2 + (agi_val // 6)) / 100.0     
        
        total_p_dmg = 0
        
        # ── 🔮 企劃一：處理【技能施放】分支 ──
        if is_using_skill:
            if current_job == "初心者" or not skill_to_cast:
                log += "💨 你目前還是【初心者】，沒有學會任何職業主動技能！自動切換為普通攻擊！\n"
                is_using_skill = False
            else:
                s_config = avail_skills[skill_to_cast]
                mp_cost = s_config.get("mp_cost", 0)
                
                # 檢查魔力是否足夠
                if p["mp"] < mp_cost:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ 魔力不足！施放【{skill_to_cast}】需要 {mp_cost} 點魔力，你目前只有 {p['mp']} 點！"))
                    return
                
                # 扣除魔力
                p["mp"] -= mp_cost
                log += f"✨ 【{skill_to_cast}】！！（消耗魔力 -{mp_cost}）\n"
                
                # 依據職業特性動態計算傷害/補血
                if current_job == "戰士":
                    min_p_dmg = int((5 + (str_val // 2) + w_bonus) * s_config["dmg_mod"])
                    max_p_dmg = int((12 + str_val + w_bonus) * s_config["dmg_mod"])
                    total_p_dmg = random.randint(min_p_dmg, max_p_dmg)
                    log += f"💥 重擊爆破！你對怪物造成 {total_p_dmg} 點巨額物理傷害！\n"
                    
                elif current_job == "狂戰士":
                    mod = s_config["dmg_mod"]
                    # 被動血性狂暴觸發判定
                    if p["hp"] < (max_mp * 0.5): 
                        mod += 0.5
                        log += "🩸 觸發【血性狂暴】！技能破壞力暴增 50%！\n"
                    min_p_dmg = int((5 + (str_val // 2) + w_bonus) * mod)
                    max_p_dmg = int((12 + str_val + w_bonus) * mod)
                    total_p_dmg = random.randint(min_p_dmg, max_p_dmg)
                    log += f"💥 狂暴重擊！造成 {total_p_dmg} 點狂暴物理傷害！\n"
                    
                elif current_job == "修羅":
                    # 阿修羅霸凰拳特殊浮動倍率
                    mod = random.uniform(s_config["min_mod"], s_config["max_mod"])
                    total_p_dmg = int(str_val * mod)
                    log += f"🔥 【阿修羅霸凰拳】極限全開！轟出 {mod:.1f} 倍靈魂毀滅魔法重創 {total_p_dmg} 點！\n"
                    
                elif current_job in ["魔法師", "元素使", "魔導士"]:
                    if "int_mod" in s_config:
                        total_p_dmg = int(int_val * s_config["int_mod"])
                    elif "min_mod" in s_config:
                        total_p_dmg = int(int_val * random.uniform(s_config["min_mod"], s_config["max_mod"]))
                    log += f"🔮 元素共鳴！引導奧術狂轟，造成 {total_p_dmg} 點純魔法傷害！\n"
                    
                elif current_job in ["刺客", "暗夜行者"]:
                    # 必定命中（怪物無法閃避）
                    mod = s_config.get("agi_mod", 1.5) if current_job == "刺客" else s_config.get("dmg_mod", 4.5)
                    total_p_dmg = int(agi_val * mod)
                    log += f"⚡ 幻影背刺！刺客死角絕殺，造成 {total_p_dmg} 點無視閃避身法傷害！\n"
                    
                elif current_job in ["祭師", "賢者", "大主教"]:
                    if skill_to_cast == "治癒術":
                        heal_amount = int((int_val + men_val) * s_config["heal_mod"])
                        calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
                        old_hp = p["hp"]
                        p["hp"] = min(calculated_max_hp, p["hp"] + heal_amount)
                        log += f"💖 聖光降臨！為自己恢復了 {p['hp'] - old_hp} 點生命值！\n"
                    elif skill_to_cast == "聖光懲戒":
                        total_p_dmg = int(men_val * s_config["men_mod"])
                        log += f"✨ 神聖懲戒法陣！對怪物施加 {total_p_dmg} 點聖光魔法傷害！\n"
                        
                elif current_job in ["弓箭手", "獵人", "遊俠"]:
                    # 二連矢或萬箭破
                    if skill_to_cast == "二連矢":
                        d1 = random.randint(5 + (str_val//2), 12 + str_val)
                        d2 = random.randint(5 + (str_val//2), 12 + str_val)
                        total_p_dmg = d1 + d2
                        log += f"🏹 二連連射！箭矢精準穿透，分別造成 {d1} 與 {d2} 點物理傷害！\n"
                    else:
                        mod = random.uniform(s_config["min_mod"], s_config["max_mod"])
                        total_p_dmg = int(agi_val * mod)
                        log += f"🎯 箭雨漫天！【暴風萬箭破】狂暴清洗戰場，造成 {total_p_dmg} 點致命箭傷！\n"

        # ── 普通攻擊分支 ──
        if not is_using_skill:
            is_double_atk = random.random() < double_atk_chance
            attack_count = 2 if is_double_atk else 1
            if is_double_atk: log += f"🌪️ 🚀 【神速連擊】！！發動了雙重連續攻擊！\n"
                
            for i in range(attack_count):
                min_p_dmg = 5 + (str_val // 2) + w_bonus
                max_p_dmg = 12 + str_val + w_bonus
                p_dmg = random.randint(min_p_dmg, max_p_dmg)
                
                is_crit = random.random() < crit_chance
                if is_crit:
                    p_dmg = int(p_dmg * crit_dmg_mod)
