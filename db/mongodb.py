from config import mongo_config
from fastapi import FastAPI
from motor.core import AgnosticClient, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ASCENDING


async def create_expire_at_ttl_index(collection: AsyncIOMotorCollection):
    indexes = await collection.list_indexes().to_list(length=None)
    index_names = [index["name"] for index in indexes]

    if "expireAt_1" not in index_names:
        await collection.create_index(
            [("expireAt", ASCENDING)],
            expireAfterSeconds=0
        )
        print(f"TTL index(expireAt) created: {collection.name}")
    else:
        print(f"TTL index(expireAt) already exists: {collection.name}")

async def create_indexes(collection: AsyncIOMotorCollection, index_name: str):
    indexes = await collection.list_indexes().to_list(length=None)
    existing_index_names = [index["name"] for index in indexes]

    if index_name not in existing_index_names:
        await collection.create_index([(index_name, ASCENDING)])
        print(f"Index {index_name} created: {collection.name}")
    else:
        print(f"Index {index_name} already exists: {collection.name}")


class MongoAccessor:
    def __init__(self) -> None:
        self.client: AgnosticClient = None
        pass
    def init_app(self, app: FastAPI) -> None:
        app.add_event_handler("startup", self.connect)
        app.add_event_handler("shutdown", self.close)
        
    async def connect(self) -> None:
        try:
            self.client = AsyncIOMotorClient(mongo_config['URL'], tls=mongo_config['TLS'], tlsCAFile=mongo_config['TLS_CA_FILE'])
            await self.client.admin.command('ping')
            print("You have successfully connected to MongoDB!")

            # TTL 인덱스 확인 및 생성
            db = self.client[mongo_config['DB']]
            await create_indexes(db["stamp_history"], "email")
            await create_indexes(db["daily_validation"], "email")
            await create_indexes(db["validate_history"], "email")
            await create_expire_at_ttl_index(db["daily_validation"])
            await create_expire_at_ttl_index(db["validate_history"])

        except Exception as e:
            print(e)
    
    def close(self) -> None:
        self.client.close()
        print("MongoDB closed.")
        
    async def get_database(self) -> AgnosticDatabase:
        return self.client[mongo_config['DB']]
    
