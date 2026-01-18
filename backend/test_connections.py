"""Quick test script to verify API keys and connections work."""

import asyncio
import sys

# Add backend to path
sys.path.insert(0, "/Users/danieltong/nexus/backend")


async def test_mongodb():
    """Test MongoDB connection."""
    print("\n🔍 Testing MongoDB connection...")
    try:
        from config.settings import settings
        from motor.motor_asyncio import AsyncIOMotorClient
        
        client = AsyncIOMotorClient(settings.mongodb_uri)
        # Ping the database
        await client.admin.command('ping')
        print(f"✅ MongoDB connected successfully!")
        print(f"   Database: {settings.mongodb_database}")
        
        # List collections
        db = client[settings.mongodb_database]
        collections = await db.list_collection_names()
        print(f"   Collections: {collections if collections else '(none yet)'}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


async def test_gemini():
    """Test Google Gemini API key."""
    print("\n🔍 Testing Google Gemini API key...")
    try:
        from config.settings import settings
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        
        if not settings.google_api_key:
            print("❌ GOOGLE_API_KEY is empty or not set")
            return False
        
        print(f"   Model: {settings.classifier_model}")
        
        llm = ChatGoogleGenerativeAI(
            model=settings.classifier_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )
        
        # Simple test message
        response = await llm.ainvoke([HumanMessage(content="Say 'API working' in exactly 2 words")])
        print(f"✅ Gemini API working!")
        print(f"   Response: {response.content[:100]}")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False


async def test_classifier():
    """Test the actual classifier."""
    print("\n🔍 Testing Classifier with real LLM...")
    try:
        from src.graph.classifier import classify_request
        from src.models.state import GraphState
        
        state = GraphState(
            request_id="test-1",
            user_message="Just finished a meeting with Google who agreed to pay $1,000 for boothing at Blueprint",
        )
        
        result = await classify_request(state)
        agents = result.get("target_agents", [])
        
        print(f"✅ Classifier working!")
        print(f"   Test prompt: 'Sponsor meeting with Google...'")
        print(f"   Routed to: {agents}")
        return True
    except Exception as e:
        print(f"❌ Classifier failed: {e}")
        return False


async def main():
    print("=" * 50)
    print("NEXUS BACKEND CONNECTION TEST")
    print("=" * 50)
    
    results = {}
    
    # Test MongoDB
    results["mongodb"] = await test_mongodb()
    
    # Test Gemini
    results["gemini"] = await test_gemini()
    
    # Test Classifier (uses Gemini)
    if results["gemini"]:
        results["classifier"] = await test_classifier()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️ Some tests failed"))
    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
