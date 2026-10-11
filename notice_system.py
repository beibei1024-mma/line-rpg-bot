import db_core
from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi, BroadcastRequest

def push_world_boss_broadcast(monster_name, configuration):
    """📢 【獨立公告大腦】負責執行震撼全服的世界 Boss 絕殺廣播推播"""
    try:
        # 🧪 包裝符合 LINE 官方 v3 規範的標準廣播 JSON 數據體
        broadcast_payload = {
            "messages": [{
                "type": "text",
                "text": f"📢 🔥 【全服史詩首殺公告】 🔥 📢\n─────────────────\n震撼！偉大的勇者在剛才成功絕殺了世界級 Boss 👑【{monster_name}】！\n神話已在聊天室誕生，名留青史！"
            }]
        }
        
        # ⚡ 使用萬能字典代理發送，全自動推播給全服所有加入好友的玩家
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.broadcast(BroadcastRequest.from_dict(broadcast_payload))
            
    except Exception:
        # 🛡️ 採最高規格防爆設計，即使全服廣播失敗，也絕不拖累目前玩家的打怪與存檔進度
        pass

def push_system_maintenance_notice(title, content, configuration):
    """🛠️ 【營運廣播擴充點】往後若有重大活動或伺服器維護，直接呼叫此函式即可"""
    try:
        broadcast_payload = {
            "messages": [{
                "type": "text",
                "text": f"🛠️ 🔔 【冒險者公會・官方重要公告】 🔔 🛠️\n─────────────────\n主旨：{title}\n\n內容：{content}"
            }]
        }
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.broadcast(BroadcastRequest.from_dict(broadcast_payload))
    except Exception:
        pass
