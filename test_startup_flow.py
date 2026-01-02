"""
Test to verify that the startup flow works correctly without actually downloading models.
This test simulates the startup process to ensure proper integration.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_startup_flow_simulation():
    """
    Simulate the startup flow without actually downloading/loading models.
    This verifies that all the pieces fit together correctly.
    """
    print("Testing startup flow simulation...")
    
    # Import the ai_agent directly
    from app.main import ai_agent, app
    
    # Verify ai_agent is initialized to None
    assert ai_agent is None, "ai_agent should be None before startup"
    print("  ✓ ai_agent initially None")
    
    # Simulate what would happen during startup (without actually downloading models)
    # In production, lifespan() would create a real AIAgent
    # For this test, we just verify the structure is correct
    
    # Verify that we can import AIAgent
    from app.services.ai_agent import AIAgent
    print("  ✓ AIAgent can be imported")
    
    # Verify that JobProcessor can use an ai_agent
    from app.services.processor import JobProcessor
    
    # Create a dummy ai_agent (not initialized, just to test parameter passing)
    dummy_agent = None  # In production, this would be AIAgent()
    
    # Verify JobProcessor can be created with ai_agent parameter
    # (we won't actually create it since we don't have Excel file)
    import inspect
    sig = inspect.signature(JobProcessor.__init__)
    params = list(sig.parameters.keys())
    
    assert 'ai_agent' in params, "JobProcessor should accept ai_agent parameter"
    print("  ✓ JobProcessor accepts ai_agent parameter")
    
    # Verify the lifespan function exists
    from app.main import lifespan
    assert lifespan is not None, "lifespan function should exist"
    print("  ✓ lifespan function exists")
    
    # Verify that the app has lifespan configured
    assert app.router.lifespan_context is not None, "Lifespan should be configured"
    print("  ✓ Lifespan is configured with FastAPI")
    
    print()
    print("✓ Startup flow simulation passed!")
    print()
    print("In production:")
    print("1. FastAPI app starts")
    print("2. lifespan() is called automatically")
    print("3. AIAgent() is created (downloads/loads models)")
    print("4. Global ai_agent is set")
    print("5. All requests use the same ai_agent instance")


if __name__ == "__main__":
    try:
        test_startup_flow_simulation()
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
