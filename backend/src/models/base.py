"""Base document model with common fields for MongoDB documents."""

from datetime import datetime
from typing import Annotated, Any, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator


def validate_object_id(value: Any) -> Union[ObjectId, str]:
    """Validate and convert value to ObjectId."""
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str):
        if ObjectId.is_valid(value):
            return ObjectId(value)
        return value  # Allow string IDs for flexibility
    raise ValueError(f"Invalid ObjectId: {value}")


# Custom type for MongoDB ObjectId fields
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x) if isinstance(x, ObjectId) else x)]


class BaseDocument(BaseModel):
    """Base model for all MongoDB documents with common fields."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda dt: dt.isoformat()},
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Document creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Document last update timestamp")

    def to_mongo(self) -> dict:
        """Convert model to MongoDB document format."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Ensure timestamps are present
        now = datetime.utcnow()
        if "created_at" not in data:
            data["created_at"] = now
        data["updated_at"] = now
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "BaseDocument":
        """Create model instance from MongoDB document."""
        if data is None:
            return None
        # Convert _id to string if it's an ObjectId
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)


class TimestampMixin(BaseModel):
    """Mixin for adding timestamp fields to non-document models."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
