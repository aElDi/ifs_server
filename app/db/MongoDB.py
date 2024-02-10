from pymongo import MongoClient
from ..config import MONGO_URI
from ..models import User

class MongoDB(object):

    def __init__(self, connect_string: str | None = None,
                db_name: str | None = None):
        if connect_string is not None:
            self._client = MongoClient(connect_string)
        else:
            raise ValueError()
        self._users_collection = self._client[db_name]["users"]

    def create_user(self, user: User):
        try:
            if self._users_collection.find_one({"username": user.get('username')}) == None:
                self._users_collection.insert_one(user)
                print(f"Added New user: {user.get('username')}")
            else:
                print(f"User: {user.get('username')} in collection")
        except Exception as ex:
            print("[create_user] Some problem...")
            print(ex)

    def is_user(self, username: str):
        try:
            return self._users_collection.find_one({"username": username}) != None
        except Exception as ex:
            print("[is_user] Some problem...")
            print(ex)

    def get_all_users(self):
        try:
            data = self._users_collection.find()
            print("Get all users")
            return data
        except Exception as ex:
            print("[get_all] Some problem...")
            print(ex)

    def find_by_username(self, username: str):
        try:
            data = self._users_collection.find_one({"username": username})
            print("Get user by username")
            return data
        except Exception as ex:
            print("[find_by_username] Some problem...")
            print(ex)

    def change_user(self, username: str, key: str, value: str):
        try:
            if self._users_collection.find_one({"username": username}) is not None:
                self._users_collection.update_one({"username": username}, {"$set": {key: value}})
            else:
                print(f'User: {username} not find')
        except Exception as ex:
            print("[change_user] Some problem...")
            print(ex)

db = MongoDB(MONGO_URI, "ifs")