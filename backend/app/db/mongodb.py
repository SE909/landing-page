from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]


async def close_db():
    global client
    if client:
        client.close()


def get_campaigns_collection():
    return db["campaigns"]
