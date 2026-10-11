import db_core
from linebot.v3.messaging import ApiClient, ReplyMessageRequest, MessagingApi, BroadcastRequest

def push_world_boss_broadcast(monster_name, configuration):
    """📢 獨立公告大腦：負責執行震撼全服的首殺廣播推播"""
    try:
        broadcast_payload = {
            "messages": [{
                "type": "text",
                "text": f"📢 🔥 【全服史詩首殺公告】 🔥 📢\n─────────────────\n震撼！偉大的勇者在剛才成功絕殺了世界級 Boss 👑【{monster_name}】！\n神話已在聊天室誕生，名留青史！"
            }]
        }
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).broadcast(BroadcastRequest.from_dict(broadcast_payload))
    except Exception:
        pass
