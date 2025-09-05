from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import Request

# Global database instance
db: AsyncIOMotorDatabase = None

def init_db(database: AsyncIOMotorDatabase):
    """Initialize the global database instance"""
    global db
    db = database

def get_db():
    """Get the database instance"""
    return db

def get_database_from_request(request: Request) -> AsyncIOMotorDatabase:
    """Get database instance from FastAPI request object"""
    return request.app.mongodb

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if key == "_id" and isinstance(value, ObjectId):
                serialized["id"] = str(value)
            elif isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, dict):
                serialized[key] = serialize_doc(value)
            elif isinstance(value, list):
                serialized[key] = [serialize_doc(item) for item in value]
            else:
                serialized[key] = value
        return serialized
    return doc
