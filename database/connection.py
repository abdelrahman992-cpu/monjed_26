"""
MONJED MongoDB Connection

Central MongoDB connection manager.
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/",
)

DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "monjed",
)


client = None
db = None


def connect_to_mongodb():
    """
    Connect to MongoDB and return MONJED database.
    """

    global client, db

    if db is not None:
        return db

    try:

        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
        )

        # Confirm that MongoDB is reachable.
        client.admin.command("ping")

        db = client[DB_NAME]

        print(
            f"MongoDB connected successfully: {DB_NAME}"
        )

        return db

    except PyMongoError as exc:

        client = None
        db = None

        raise RuntimeError(
            f"MongoDB connection failed: {exc}"
        ) from exc


def get_database():
    """
    Return active database connection.

    Connect automatically when necessary.
    """

    global db

    if db is None:
        return connect_to_mongodb()

    return db


def close_connection():
    """
    Close MongoDB connection safely.
    """

    global client, db

    if client is not None:
        client.close()

    client = None
    db = None