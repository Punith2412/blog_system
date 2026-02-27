print("Testing AI setup...")

# Test 1: Can we import models?
try:
    import models
    print("✓ models.py imported successfully")
except Exception as e:
    print(f"✗ Error importing models: {e}")

# Test 2: Can we import ai_service?
try:
    import ai_service
    print("✓ ai_service.py imported successfully")
    print(f"  API Key configured: {ai_service.GEMINI_API_KEY[:20]}...")
except Exception as e:
    print(f"✗ Error importing ai_service: {e}")

# Test 3: Can we get posts?
try:
    posts = models.get_all_posts()
    print(f"✓ Found {len(posts)} posts")
except Exception as e:
    print(f"✗ Error getting posts: {e}")

# Test 4: Can we get AI context?
try:
    ai_posts = models.get_all_posts_for_ai()
    context = models.format_posts_for_context(ai_posts)
    print(f"✓ AI context created ({len(context)} chars)")
except Exception as e:
    print(f"✗ Error creating AI context: {e}")

print("\nDone testing!")