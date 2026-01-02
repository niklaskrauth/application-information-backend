"""
Test that the application startup initializes AI models correctly.
This test verifies the startup event handler and model initialization.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_startup_event_registered():
    """Test that the lifespan is configured in FastAPI"""
    from app.main import app
    
    # Check that lifespan is configured
    assert app.router.lifespan_context is not None, "Lifespan should be configured"
    print("✓ Lifespan configured in FastAPI")


def test_global_ai_agent_exists():
    """Test that global ai_agent variable is defined"""
    from app.main import ai_agent
    
    # ai_agent should be defined (will be None initially until startup)
    assert 'ai_agent' in dir(sys.modules['app.main']), "Global ai_agent not defined"
    print("✓ Global ai_agent variable exists")


def test_processor_accepts_ai_agent():
    """Test that JobProcessor accepts optional ai_agent parameter"""
    from app.services.processor import JobProcessor
    import inspect
    
    # Check that ai_agent is a parameter in __init__
    sig = inspect.signature(JobProcessor.__init__)
    params = sig.parameters
    
    assert 'ai_agent' in params, "JobProcessor.__init__ doesn't accept ai_agent parameter"
    assert params['ai_agent'].default is not inspect.Parameter.empty, "ai_agent parameter should be optional"
    print("✓ JobProcessor accepts optional ai_agent parameter")


def test_ai_agent_initialization():
    """Test that AIAgent can be initialized (without actually loading models)"""
    # This test only checks that the class can be imported and has the right structure
    from app.services.ai_agent import AIAgent
    
    assert hasattr(AIAgent, '__init__'), "AIAgent has no __init__ method"
    assert hasattr(AIAgent, 'extract_multiple_jobs'), "AIAgent has no extract_multiple_jobs method"
    print("✓ AIAgent class structure is correct")


if __name__ == "__main__":
    print("Running startup tests...")
    print()
    
    try:
        test_startup_event_registered()
        test_global_ai_agent_exists()
        test_processor_accepts_ai_agent()
        test_ai_agent_initialization()
        
        print()
        print("✓ All startup tests passed!")
        print()
        print("Note: These tests verify the structure is correct.")
        print("Actual model download happens when the server starts.")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
