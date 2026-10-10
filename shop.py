import weapons
import db_core

def get_shop_card(p):
    # 繪製精美的彩色 Flex Message 武器店購物面板
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "🏪 村莊武器店", "weight": "bold", "size": "xl", "color": "#1DB446"},
                {"type": "text", "text": f"你目前擁有: 💰 {p['gold']} 金幣", "size": "sm", "color": "#555555", "margin": "md"},
                {"type": "separator", "margin": "lg"},
                {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [
                    {"type": "text", "text": "⚔️ 木劍 (傷害+50)", "weight": "bold", "size": "md", "flex": 3},
                    {"type": "button", "action": {"type": "message", "label": "💰 50", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}
                ]},
                {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [
                    {"type": "text", "text": "⚔️ 鐵劍 (傷害+150)", "weight": "bold", "size": "md", "flex": 3},
                    {"type": "button", "action": {"type": "message", "label": "💰 150", "text": "購買鐵劍"}, "style": "primary", "color": "#F56C6C", "height": "sm", "flex": 2}
                ]}
                {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [
                    {"type": "text", "text": "⚔️ 銅劍 (傷害+300)", "weight": "bold", "size": "md", "flex": 3},
                    {"type": "button", "action": {"type": "message", "label": "💰 300", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}
                ]},
                {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [
                    {"type": "text", "text": "⚔️ 銀劍 (傷害+600)", "weight": "bold", "size": "md", "flex": 3},
                    {"type": "button", "action": {"type": "message", "label": "💰 600", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}
                ]},
                {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [
                    {"type": "text", "text": "⚔️ 黃金劍 (傷害+1200)", "weight": "bold", "size": "md", "flex": 3},
                    {"type": "button", "action": {"type": "message", "label": "💰 1200", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}
                ]},
                {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [
                    {"type": "text", "text": "⚔️ 神劍 (傷害+2400)", "weight": "bold", "size": "md", "flex": 3},
                    {"type": "button", "action": {"type": "message", "label": "💰 2400", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}
                ]}
            ]
        }
    }

def buy_weapon(p, item_name):
    # 購買判定判定與扣錢邏輯：成功扣錢後會觸發跨海大事件同步
    if item_name in weapons.SHOP_WEAPONS:
        cost = weapons.SHOP_WEAPONS[item_name]["price"]
        if p["gold"] >= cost:
            p["gold"] -= cost
            p["weapon"] = item_name
            db_core.save_player(p)
            return f"🛍️ 購買成功！你裝備了【{item_name}】！\n💰 剩餘金幣: {p['gold']}"
        else:
            return f"❌ 金幣不足！還差 {cost - p['gold']} 金幣。"
    return "❌ 本店沒有販售這項商品。"
