"""
Test for Ollama integration.
This test verifies that the AI agent can be configured to use Ollama.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ollama_provider_selection():
    """Test that Ollama provider can be selected"""
    os.environ['AI_PROVIDER'] = 'ollama'
    
    from app.config import settings
    assert settings.AI_PROVIDER == 'ollama'
    print("✓ Ollama provider selection test passed")


def test_groq_provider_selection():
    """Test that Groq provider is the default"""
    os.environ.pop('AI_PROVIDER', None)
    
    # Reload settings
    import importlib
    from app import config
    importlib.reload(config)
    from app.config import settings
    
    assert settings.AI_PROVIDER == 'groq'
    print("✓ Groq provider selection test passed")


def test_ollama_config_defaults():
    """Test that Ollama configuration has correct defaults"""
    os.environ['AI_PROVIDER'] = 'ollama'
    
    # Reload settings
    import importlib
    from app import config
    importlib.reload(config)
    from app.config import settings
    
    assert settings.OLLAMA_BASE_URL == 'http://localhost:11434'
    assert settings.OLLAMA_MODEL == 'llama3.1:8b'
    print("✓ Ollama configuration defaults test passed")


def test_ai_agent_with_groq_provider():
    """Test AIAgent initialization with Groq provider"""
    os.environ['AI_PROVIDER'] = 'groq'
    os.environ.pop('GROQ_API_KEY', None)  # Ensure no API key is set
    
    # Reload modules
    import importlib
    from app import config
    importlib.reload(config)
    
    from app.services.ai_agent import AIAgent
    agent = AIAgent()
    
    assert agent.provider == 'groq'
    assert agent.enabled == False  # Should be disabled without API key
    print("✓ AIAgent with Groq provider test passed")


def test_ai_agent_with_ollama_provider():
    """Test AIAgent initialization with Ollama provider (without langchain-ollama installed)"""
    os.environ['AI_PROVIDER'] = 'ollama'
    os.environ.pop('GROQ_API_KEY', None)  # Ensure Groq API key is not set
    
    # Reload modules to pick up new environment
    import importlib
    from app import config
    importlib.reload(config)
    
    # Import after reload
    from app.services import ai_agent
    importlib.reload(ai_agent)
    from app.services.ai_agent import AIAgent
    
    agent = AIAgent()
    
    assert agent.provider == 'ollama'
    # Agent will be disabled if langchain-ollama is not installed
    # This is expected behavior
    print("✓ AIAgent with Ollama provider test passed")


def test_invalid_provider():
    """Test AIAgent initialization with invalid provider"""
    os.environ['AI_PROVIDER'] = 'invalid'
    
    # Reload modules
    import importlib
    from app import config
    importlib.reload(config)
    
    from app.services.ai_agent import AIAgent
    agent = AIAgent()
    
    assert agent.enabled == False  # Should be disabled with invalid provider
    print("✓ Invalid provider test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Ollama Integration Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_ollama_provider_selection,
        test_groq_provider_selection,
        test_ollama_config_defaults,
        test_ai_agent_with_groq_provider,
        test_ai_agent_with_ollama_provider,
        test_invalid_provider,
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
