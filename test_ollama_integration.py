"""
Test for Ollama integration.
This test verifies that the AI agent is configured to use Ollama.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ollama_provider_selection():
    """Test that Ollama provider is selected"""
    from app.config import settings
    assert settings.AI_PROVIDER == 'ollama'
    print("✓ Ollama provider selection test passed")


def test_ollama_config_defaults():
    """Test that Ollama configuration has correct defaults"""
    from app.config import settings
    
    assert settings.OLLAMA_BASE_URL == 'http://localhost:11434'
    assert settings.OLLAMA_MODEL == 'llama3.1:8b'
    print("✓ Ollama configuration defaults test passed")


def test_ai_agent_with_ollama_provider():
    """Test AIAgent initialization with Ollama provider (without langchain-ollama installed)"""
    # Import after environment setup
    from app.services.ai_agent import AIAgent
    
    agent = AIAgent()
    
    assert agent.provider == 'ollama'
    # Agent will be disabled if langchain-ollama is not installed
    # This is expected behavior
    print("✓ AIAgent with Ollama provider test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Ollama Integration Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_ollama_provider_selection,
        test_ollama_config_defaults,
        test_ai_agent_with_ollama_provider,
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
