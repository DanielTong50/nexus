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
        
        print(f"   URI: {settings.mongodb_uri[:50]}...")
        print(f"   Database: {settings.mongodb_database}")
        
        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print(f"✅ MongoDB connected successfully!")
        
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
        
        api_key = settings.google_api_key.get_secret_value()
        if not api_key:
            print("❌ GOOGLE_API_KEY is empty or not set")
            return False
        
        print(f"   Model: {settings.classifier_model}")
        print(f"   API Key: {api_key[:10]}...")
        
        llm = ChatGoogleGenerativeAI(
            model=settings.classifier_model,
            google_api_key=api_key,
            temperature=0,
        )
        
        response = await llm.ainvoke([HumanMessage(content="Say 'API working' in exactly 2 words")])
        print(f"✅ Gemini API working!")
        print(f"   Response: {response.content[:50]}")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False


async def test_vultr():
    """Test Vultr Serverless Inference API key."""
    print("\n🔍 Testing Vultr Serverless Inference API key...")
    try:
        from config.settings import settings
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        api_key = settings.vultr_api_key.get_secret_value()
        if not api_key:
            print("❌ VULTR_API_KEY is empty or not set")
            return False
        
        print(f"   URL: {settings.vultr_inference_url}")
        print(f"   Model: {settings.vultr_agent_model}")
        print(f"   API Key: {api_key[:10]}...")
        
        # Vultr uses OpenAI-compatible API
        llm = ChatOpenAI(
            base_url=settings.vultr_inference_url,
            api_key=api_key,
            model=settings.vultr_agent_model,
            temperature=0,
        )
        
        response = await llm.ainvoke([HumanMessage(content="Say 'Vultr working' in exactly 2 words")])
        print(f"✅ Vultr API working!")
        print(f"   Response: {response.content[:50]}")
        return True
    except Exception as e:
        print(f"❌ Vultr API failed: {e}")
        return False


async def test_settings():
    """Test that settings load correctly."""
    print("\n🔍 Testing Settings Configuration...")
    try:
        from config.settings import settings
        
        print(f"   App Name: {settings.app_name}")
        print(f"   Environment: {settings.app_env}")
        print(f"   Active Provider: {settings.active_agent_provider}")
        print(f"   Classifier Model: {settings.classifier_model}")
        print(f"   Agent Model: {settings.agent_model}")
        print(f"   Current Agent Model: {settings.current_agent_model}")
        
        return True
    except Exception as e:
        print(f"❌ Settings failed: {e}")
        return False


async def main():
    print("=" * 50)
    print("NEXUS BACKEND CONNECTION TEST")
    print("=" * 50)
    
    results = {}
    
    # Test Settings
    results["settings"] = await test_settings()
    
    # Test MongoDB
    results["mongodb"] = await test_mongodb()
    
    # Test Gemini (always needed for classifier)
    results["gemini"] = await test_gemini()
    
    # Test Vultr
    results["vultr"] = await test_vultr()
    
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
