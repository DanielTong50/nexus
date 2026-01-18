"""MongoDB query tools for Nexus.

Provides tools for querying event data stored in MongoDB,
enabling Q&A workflows like "How many coffee chat delegates do we need?"
"""

import logging
from typing import Literal, Optional, Any

from langchain_core.tools import tool

from src.services.database import db_service
from src.services.organization import DEFAULT_ORG_ID

logger = logging.getLogger(__name__)


@tool
async def query_event_data(
    query_type: Literal["count", "search", "lookup", "list"],
    collection: str,
    filters: Optional[dict] = None,
    search_text: str = "",
    limit: int = 50,
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Query event data from MongoDB.
    
    Use this tool to answer questions about event data like delegates,
    registrations, sponsors, and other organizational data.
    
    Args:
        query_type: Type of query to perform
            - "count": Count matching documents
            - "search": Search for documents matching criteria
            - "lookup": Find a specific document
            - "list": List all documents in collection
        collection: MongoDB collection to query (e.g., "delegates", "registrations")
        filters: Query filters as a dictionary (e.g., {"status": "confirmed"})
        search_text: Text to search for in document fields
        limit: Maximum number of results to return
        org_id: Organization identifier
        
    Returns:
        Query results as formatted string
    """
    try:
        # Collection name is used directly - LLM outputs exact names from org context
        # Get the collection
        coll = db_service.db[collection]
        
        # Build query
        query = filters or {}
        
        # Add text search if provided
        if search_text:
            # Try to search across common text fields
            query["$or"] = [
                {"name": {"$regex": search_text, "$options": "i"}},
                {"title": {"$regex": search_text, "$options": "i"}},
                {"company": {"$regex": search_text, "$options": "i"}},
                {"email": {"$regex": search_text, "$options": "i"}},
                {"description": {"$regex": search_text, "$options": "i"}},
            ]
        
        # Execute query based on type
        if query_type == "count":
            count = await coll.count_documents(query)
            
            # Provide context
            filter_desc = ""
            if filters:
                filter_desc = f" matching {filters}"
            
            return f"Found {count} {collection}{filter_desc}."
        
        elif query_type == "lookup":
            doc = await coll.find_one(query, {"_id": 0})
            
            if doc:
                return format_document(doc, collection)
            else:
                return f"No {collection} found matching the criteria."
        
        elif query_type == "list" or query_type == "search":
            cursor = coll.find(query, {"_id": 0}).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            if not docs:
                return f"No {collection} found."
            
            # Format results
            results = [f"Found {len(docs)} {collection}:"]
            for i, doc in enumerate(docs, 1):
                summary = summarize_document(doc)
                results.append(f"{i}. {summary}")
            
            if len(docs) == limit:
                results.append(f"\n(Showing first {limit} results)")
            
            return "\n".join(results)
        
        else:
            return f"Unknown query type: {query_type}"
    
    except Exception as e:
        logger.error(f"MongoDB query error: {e}")
        return f"Error querying database: {str(e)}"


@tool
async def get_collection_stats(
    collection: str,
    group_by: str = "",
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Get statistics about a MongoDB collection.
    
    Useful for answering questions like "How many delegates per status?"
    or "What's the breakdown of sponsors by tier?"
    
    Args:
        collection: MongoDB collection name
        group_by: Field to group by for breakdown (optional)
        org_id: Organization identifier
        
    Returns:
        Collection statistics
    """
    try:
        # Collection name is used directly - LLM outputs exact names from org context
        coll = db_service.db[collection]
        
        # Get total count
        total = await coll.count_documents({})
        
        if not group_by:
            return f"Collection '{collection}' has {total} documents."
        
        # Get breakdown by field
        pipeline = [
            {"$group": {"_id": f"${group_by}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        cursor = coll.aggregate(pipeline)
        groups = await cursor.to_list(length=100)
        
        if not groups:
            return f"Collection '{collection}' has {total} documents. No grouping data available for '{group_by}'."
        
        # Format breakdown
        results = [f"Statistics for '{collection}' (total: {total}):"]
        results.append(f"\nBreakdown by {group_by}:")
        
        for group in groups:
            value = group["_id"] or "Not specified"
            count = group["count"]
            percentage = (count / total * 100) if total > 0 else 0
            results.append(f"  - {value}: {count} ({percentage:.1f}%)")
        
        return "\n".join(results)
    
    except Exception as e:
        logger.error(f"MongoDB stats error: {e}")
        return f"Error getting statistics: {str(e)}"


@tool
async def search_all_collections(
    search_text: str,
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Search across multiple collections for matching data.
    
    Useful when you're not sure which collection contains the data.
    
    Args:
        search_text: Text to search for
        org_id: Organization identifier
        
    Returns:
        Search results from all collections
    """
    try:
        # Collections to search
        collections_to_search = [
            "delegates",
            "registrations",
            "partnerships_boothing_companies",
            "partnerships_judges",
            "partnerships_mentors",
            "event_logistics",
        ]
        
        all_results = []
        
        for coll_name in collections_to_search:
            try:
                coll = db_service.db[coll_name]
                
                # Search common fields
                query = {
                    "$or": [
                        {"name": {"$regex": search_text, "$options": "i"}},
                        {"title": {"$regex": search_text, "$options": "i"}},
                        {"company": {"$regex": search_text, "$options": "i"}},
                        {"email": {"$regex": search_text, "$options": "i"}},
                        {"contact_name": {"$regex": search_text, "$options": "i"}},
                    ]
                }
                
                count = await coll.count_documents(query)
                if count > 0:
                    cursor = coll.find(query, {"_id": 0}).limit(5)
                    docs = await cursor.to_list(length=5)
                    
                    all_results.append({
                        "collection": coll_name,
                        "count": count,
                        "samples": docs
                    })
            except Exception:
                # Skip collections that don't exist
                continue
        
        if not all_results:
            return f"No results found for '{search_text}' across all collections."
        
        # Format results
        output = [f"Search results for '{search_text}':\n"]
        
        for result in all_results:
            output.append(f"**{result['collection']}** ({result['count']} matches):")
            for doc in result["samples"]:
                summary = summarize_document(doc)
                output.append(f"  - {summary}")
            if result["count"] > 5:
                output.append(f"  ... and {result['count'] - 5} more")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"Search all collections error: {e}")
        return f"Error searching: {str(e)}"


@tool
async def list_available_collections(
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """List all available MongoDB collections.
    
    Use this to see what data is available to query.
    
    Args:
        org_id: Organization identifier
        
    Returns:
        List of collections with document counts
    """
    try:
        # Get all collection names
        collection_names = await db_service.db.list_collection_names()
        
        if not collection_names:
            return "No collections found in the database."
        
        # Get counts for each
        results = ["Available collections:\n"]
        
        for name in sorted(collection_names):
            try:
                coll = db_service.db[name]
                count = await coll.count_documents({})
                results.append(f"  - {name}: {count} documents")
            except Exception:
                results.append(f"  - {name}: (unable to count)")
        
        return "\n".join(results)
    
    except Exception as e:
        logger.error(f"List collections error: {e}")
        return f"Error listing collections: {str(e)}"


# Helper functions

def format_document(doc: dict, collection: str) -> str:
    """Format a document for display."""
    lines = [f"**{collection.replace('_', ' ').title()}**:\n"]
    
    for key, value in doc.items():
        if key.startswith("_"):
            continue
        
        # Format key
        display_key = key.replace("_", " ").title()
        
        # Format value
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in value.items())
        elif isinstance(value, list):
            value = ", ".join(str(v) for v in value[:5])
            if len(value) > 5:
                value += "..."
        
        lines.append(f"  - {display_key}: {value}")
    
    return "\n".join(lines)


def summarize_document(doc: dict) -> str:
    """Create a one-line summary of a document."""
    # Try common identifying fields
    identifiers = ["name", "title", "company", "contact_name", "email"]
    
    parts = []
    for field in identifiers:
        if field in doc and doc[field]:
            parts.append(str(doc[field]))
            if len(parts) >= 2:
                break
    
    if not parts:
        # Fall back to first few fields
        for key, value in doc.items():
            if not key.startswith("_") and value:
                parts.append(f"{key}: {value}")
                if len(parts) >= 2:
                    break
    
    summary = " - ".join(parts) if parts else "No summary available"
    
    # Add status if available
    if "status" in doc:
        summary += f" [{doc['status']}]"
    
    return summary


# Export tools for agent binding
MONGODB_QUERY_TOOLS = [
    query_event_data,
    get_collection_stats,
    search_all_collections,
    list_available_collections,
]
