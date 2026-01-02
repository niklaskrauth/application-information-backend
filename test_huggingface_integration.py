"""
Test for Hugging Face integration.
This test verifies that the AI agent is configured to use Hugging Face.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_huggingface_provider_selection():
    """Test that Hugging Face provider is selected"""
    from app.config import settings
    assert settings.AI_PROVIDER == 'huggingface'
    print("✓ Hugging Face provider selection test passed")


def test_huggingface_config_defaults():
    """Test that Hugging Face configuration has correct defaults"""
    from app.config import settings
    
    assert settings.HUGGINGFACE_MODEL == 'Veronika-T/mistral-german-7b'
    assert settings.HUGGINGFACE_EMBEDDING_MODEL == 'deutsche-telekom/gbert-large-paraphrase-cosine'
    print("✓ Hugging Face configuration defaults test passed")


def test_ai_agent_with_huggingface_provider():
    """Test AIAgent initialization with Hugging Face provider"""
    # Import after environment setup
    from app.services.ai_agent import AIAgent
    
    agent = AIAgent()
    
    assert agent.provider == 'huggingface'
    # Agent will be disabled if langchain-huggingface is not installed
    # This is expected behavior
    print("✓ AIAgent with Hugging Face provider test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Hugging Face Integration Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_huggingface_provider_selection,
        test_huggingface_config_defaults,
        test_ai_agent_with_huggingface_provider,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
