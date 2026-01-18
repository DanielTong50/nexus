"""Base repository with generic CRUD operations for MongoDB collections."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, Optional, Type, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

from src.models.base import BaseDocument

T = TypeVar("T", bound=BaseDocument)


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with generic CRUD operations."""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: Type[T]):
        """
        Initialize repository with database connection.

        Args:
            db: Motor async database instance
            collection_name: Name of the MongoDB collection
            model_class: Pydantic model class for this collection
        """
        self._db = db
        self._collection_name = collection_name
        self._model_class = model_class

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection."""
        return self._db[self._collection_name]

    @abstractmethod
    async def create_indexes(self) -> None:
        """Create indexes for this collection. Must be implemented by subclasses."""
        pass

    async def create(self, document: T) -> T:
        """
        Create a new document.

        Args:
            document: The document to create

        Returns:
            The created document with generated _id
        """
        data = document.to_mongo()
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)

        return self._model_class.from_mongo(data)

    async def find_by_id(self, document_id: str) -> Optional[T]:
        """
        Find a document by its _id.

        Args:
            document_id: The document's _id as a string

        Returns:
            The document if found, None otherwise
        """
        try:
            object_id = ObjectId(document_id)
        except Exception:
            return None

        data = await self.collection.find_one({"_id": object_id})
        if data is None:
            return None

        return self._model_class.from_mongo(data)

    async def find_one(self, query: dict) -> Optional[T]:
        """
        Find a single document matching the query.

        Args:
            query: MongoDB query dict

        Returns:
            The first matching document or None
        """
        data = await self.collection.find_one(query)
        if data is None:
            return None

        return self._model_class.from_mongo(data)

    async def find_many(
        self,
        query: dict,
        sort: Optional[list[tuple[str, int]]] = None,
        limit: int = 0,
        skip: int = 0,
    ) -> list[T]:
        """
        Find multiple documents matching the query.

        Args:
            query: MongoDB query dict
            sort: List of (field, direction) tuples for sorting
            limit: Maximum number of documents to return (0 = no limit)
            skip: Number of documents to skip

        Returns:
            List of matching documents
        """
        cursor = self.collection.find(query)

        if sort:
            cursor = cursor.sort(sort)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)

        documents = []
        async for data in cursor:
            documents.append(self._model_class.from_mongo(data))

        return documents

    async def update_by_id(self, document_id: str, update: dict) -> Optional[T]:
        """
        Update a document by its _id.

        Args:
            document_id: The document's _id as a string
            update: Dict of fields to update

        Returns:
            The updated document or None if not found
        """
        try:
            object_id = ObjectId(document_id)
        except Exception:
            return None

        # Always update the updated_at timestamp
        update["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update},
            return_document=True,
        )

        if result is None:
            return None

        return self._model_class.from_mongo(result)

    async def update_one(self, query: dict, update: dict) -> Optional[T]:
        """
        Update a single document matching the query.

        Args:
            query: MongoDB query dict
            update: Dict of fields to update

        Returns:
            The updated document or None if not found
        """
        # Always update the updated_at timestamp
        update["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            query,
            {"$set": update},
            return_document=True,
        )

        if result is None:
            return None

        return self._model_class.from_mongo(result)

    async def update_many(self, query: dict, update: dict) -> int:
        """
        Update multiple documents matching the query.

        Args:
            query: MongoDB query dict
            update: Dict of fields to update

        Returns:
            Number of documents modified
        """
        update["updated_at"] = datetime.utcnow()

        result = await self.collection.update_many(query, {"$set": update})
        return result.modified_count

    async def delete_by_id(self, document_id: str) -> bool:
        """
        Delete a document by its _id.

        Args:
            document_id: The document's _id as a string

        Returns:
            True if deleted, False if not found
        """
        try:
            object_id = ObjectId(document_id)
        except Exception:
            return False

        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    async def delete_one(self, query: dict) -> bool:
        """
        Delete a single document matching the query.

        Args:
            query: MongoDB query dict

        Returns:
            True if deleted, False if not found
        """
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

    async def delete_many(self, query: dict) -> int:
        """
        Delete multiple documents matching the query.

        Args:
            query: MongoDB query dict

        Returns:
            Number of documents deleted
        """
        result = await self.collection.delete_many(query)
        return result.deleted_count

    async def count(self, query: Optional[dict] = None) -> int:
        """
        Count documents matching the query.

        Args:
            query: MongoDB query dict (None for all documents)

        Returns:
            Number of matching documents
        """
        if query is None:
            query = {}
        return await self.collection.count_documents(query)

    async def exists(self, query: dict) -> bool:
        """
        Check if any document matches the query.

        Args:
            query: MongoDB query dict

        Returns:
            True if at least one document matches
        """
        count = await self.collection.count_documents(query, limit=1)
        return count > 0

    async def upsert(self, query: dict, document: T) -> T:
        """
        Update or insert a document.

        Args:
            query: Query to find existing document
            document: Document to insert or update with

        Returns:
            The upserted document
        """
        data = document.to_mongo()
        now = datetime.utcnow()
        data["updated_at"] = now

        result = await self.collection.find_one_and_update(
            query,
            {
                "$set": data,
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
            return_document=True,
        )

        return self._model_class.from_mongo(result)
