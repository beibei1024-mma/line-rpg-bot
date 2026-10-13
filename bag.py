import json
from db_core import execute_query

# 預先將列表轉換為字典，優化迴圈查詢為 O(1)
ITEMS = [
    {"id": 1, "name": "生命藥水", "type": "potion", "hp": 50, "mp": 0, "atk": 0, "def": 0, "price": 10},
    {"id": 2, "name": "魔法藥水", "type": "potion", "hp": 0, "mp": 30, "atk": 0, "def": 0, "price": 10},
    {"id": 3, "name": "力量藥劑", "type": "potion", "hp": 0, "mp": 0, "atk": 5, "def": 0, "price": 50},
    {"id": 4, "name": "御守藥劑", "type": "potion", "hp": 0, "mp": 0, "atk": 0, "def": 5, "price": 50},
]
ITEMS_DICT = {item["id"]: item for item in ITEMS}

WEAPONS = [
    {"id": 1, "name": "新手短劍", "type": "weapon", "hp": 0, "mp": 0, "atk": 10, "def": 0, "price": 50},
    {"id": 2, "name": "新手皮甲", "type": "armor", "hp": 50, "mp": 0, "atk": 0, "def": 10, "price": 50},
    {"id": 3, "name": "鋼鐵巨劍", "type": "weapon", "hp": 0, "mp": 0, "atk": 30, "def": 0, "price": 200},
    {"id": 4, "name": "鋼鐵重鎧", "type": "armor", "hp": 150, "mp": 0, "atk": 0, "def": 30, "price": 250},
]
WEAPONS_DICT = {w["id"]: w for w in WEAPONS}

def get_item_by_id(item_id):
    # 移除原本的 O(N) 尋找迴圈
    return ITEMS_DICT.get(item_id)

def get_weapon_by_id(weapon_id):
    # 移除原本的 O(N) 尋找迴圈
    return WEAPONS_DICT.get(weapon_id)

def get_player_bag(user_id):
    sql = "SELECT items, weapons FROM bag WHERE user_id = %s"
    res = execute_query(sql, (user_id,))
    if not res:
        return {"items": {}, "weapons": {}}
    
    # 善用 Dict Comprehension 批量轉換型態
    return {
        "items": {int(k): v for k, v in json.loads(res[0][0]).items()} if res[0][0] else {},
        "weapons": {int(k): v for k, v in json.loads(res[0][1]).items()} if res[0][1] else {}
    }

def save_player_bag(user_id, bag_data):
    sql = "UPDATE bag SET items = %s, weapons = %s WHERE user_id = %s"
    execute_query(sql, (json.dumps(bag_data["items"]), json.dumps(bag_data["weapons"]), user_id), is_update=True)

def add_item_to_bag(user_id, item_id, count=1):
    bag = get_player_bag(user_id)
    bag["items"][item_id] = bag["items"].get(item_id, 0) + count
    save_player_bag(user_id, bag)

def add_weapon_to_bag(user_id, weapon_id, count=1):
    bag = get_player_bag(user_id)
    bag["weapons"][weapon_id] = bag["weapons"].get(weapon_id, 0) + count
    save_player_bag(user_id, bag)

def remove_item_from_bag(user_id, item_id, count=1):
    bag = get_player_bag(user_id)
    if item_id in bag["items"] and bag["items"][item_id] >= count:
        bag["items"][item_id] -= count
        if bag["items"][item_id] == 0:
            del bag["items"][item_id]
        save_player_bag(user_id, bag)
        return True
    return False

def remove_weapon_from_bag(user_id, weapon_id, count=1):
    bag = get_player_bag(user_id)
    if weapon_id in bag["weapons"] and bag["weapons"][weapon_id] >= count:
        bag["weapons"][weapon_id] -= count
        if bag["weapons"][weapon_id] == 0:
            del bag["weapons"][weapon_id]
        save_player_bag(user_id, bag)
        return True
    return False
