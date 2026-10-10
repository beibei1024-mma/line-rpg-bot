            # 👑 【核心優化：While 連續升級與屬性連續疊加爆發公式】
            # 當經驗值爆表時，Python 會像開外掛一樣自動連續扣除、連續升級，直到經驗值不夠為止！
            while p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50
                p["level"] += 1
                
                # 六大天賦屬性隨著每一級的提升，在記憶體裡連續瘋狂疊加成長！
                p["strength"] = p.get("strength", 10) + 3
                p["agility"] = p.get("agility", 10) + 2
                p["intelligence"] = p.get("intelligence", 10) + 2
                p["vitality"] = p.get("vitality", 10) + 3
                p["luck"] = p.get("luck", 10) + 1
                p["sprit"] = p.get("sprit", 10) + 2
                
                log += f"\n🎊 👑 歷練突破！恭喜晉升至 Lv.{p['level']}！全屬性天賦獲得大幅成長！"
                
            # 重新動態核算最新等級與體力倍率下的血量總上限，並原地回滿血！
            new_vit = int(p.get("vitality", 10) * job_mod["vit_mod"])
            calculated_max_hp = 100 + (new_vit * 5) + (p["level"] * 15)
            p["max_hp"] = calculated_max_hp
            p["hp"] = calculated_max_hp
            log += f"\n💚 當前生命狀態已完全補滿（{calculated_max_hp}/{calculated_max_hp}）！"
            
            db_core.save_player(p)
            
            # 🔔 【本命轉職臨界點自動爆發機制】
            # 如果連續升級後的最新等級，剛好衝破了一轉(25等)、二轉(50等)、三轉(100等)的大關，且階級符合，當場在戰報下方炸出轉職口令圖鑑！
            if p["level"] >= 25 and job_mod["tier"] == 0:
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
            elif p["level"] >= 50 and job_mod["tier"] == 1:
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
            elif p["level"] >= 100 and job_mod["tier"] == 2:
                job_notice = jobs.get_job_options_text(p)
                line_bot_api.reply_message(event.reply_token, [
                    FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)),
                    TextSendMessage(text=job_notice)
                ])
                return
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=db_core.make_battle_card(log, p, None)))
        else:
            # ── 怪物沒死，發動反擊 ──
            is_p_evade = random.random() < evade_chance
            
            if is_p_evade:
                log += f"💨 殘影！你發動敏捷身法，【完美閃避】了怪物的反擊傷害！"
            else:
                dmg_mod = p.get("map_dmg_mod", 1.0)
                base_m_atk = random.randint(1, enemy["atk"])
                final_m_atk = int(base_m_atk * dmg_mod)
                
                # 🧱 體力與本命職業加成影響防禦力扣減
                p_defense = vit_val // 2
                final_received_dmg = max(1, final_m_atk - p_defense)
                
                p["hp"] -= final_received_dmg
                log += f"🩹 【{enemy['name']}】發動反擊！你受到 {final_received_dmg} 點物理傷害！"
                if p_defense > 0:
                    log += f" (體力防禦減免 -{p_defense} 點)"
            
            if p["hp"] <= 0:
                p["hp"] = 0
                p["enemy"] = None
                log += "\n💀 你受傷過重被擊倒了！請點擊【復活】重整旗鼓。"
                db_core.save_player(p)
                card = db_core.make_battle_card(log, p, None)
            else:
                db_core.MEMORY_PLAYERS[user_id] = p
                card = db_core.make_battle_card(log, p, enemy)
                
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
            
    # 11. 處理【逃跑】判定
    elif user_msg == "逃跑":
        p["enemy"] = None
        db_core.save_player(p)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💨 成功逃跑了！"))
        
    # 12. 處理【復活】判定
    elif user_msg == "復活":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=player.handle_resurrect(p)))
        
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方選單開始遊戲！"))

if __name__ == "__main__":
    app.run()
