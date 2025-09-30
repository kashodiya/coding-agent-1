
#!/usr/bin/env python3
"""
Test script to demonstrate the AI Coding Agent creating a calculator
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import the agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_coding_agent import CodingAgent


async def test_calculator_creation():
    """Test the agent by asking it to create a calculator"""
    
    print("=" * 60)
    print("🧪 Testing AI Coding Agent - Calculator Creation")
    print("=" * 60)
    
    # Initialize the agent
    print("\n📋 Initializing agent...")
    agent = CodingAgent(
        name="Calculator Builder Agent",
        model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        memory_file="test_calculator_memory.json"
    )
    
    try:
        await agent.initialize()
        print("✅ Agent initialized successfully!")
        
        # Request to create a calculator
        request = """
        Create a Python calculator application with the following features:
        1. Basic operations: addition, subtraction, multiplication, division
        2. Advanced operations: power, square root, modulo
        3. A command-line interface where users can input expressions
        4. Error handling for division by zero and invalid inputs
        5. A help menu showing available operations
        6. Save the calculator in a file called 'calculator.py'
        
        Also create a test file 'test_calculator.py' with at least 5 test cases.
        """
        
        print("\n📝 Request:")
        print(request)
        print("\n" + "=" * 60)
        print("🤖 Agent is working on your request...")
        print("=" * 60 + "\n")
        
        # Execute the task
        result = await agent.execute_task(request)
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 Task Completion Summary")
        print("=" * 60)
        
        if result['success']:
            print("✅ Task completed successfully!")
            
            # Show plan details
            plan = result['plan']
            print(f"\n📋 Plan: {plan['description']}")
            print(f"📝 Total steps: {len(plan['steps'])}")
            print(f"⏱️ Status: {plan['status']}")
            
            # Show steps executed
            print("\n📌 Steps executed:")
            for i, step in enumerate(plan['steps'], 1):
                print(f"  {i}. {step}")
            
            # Check if files were created
            print("\n📁 Checking created files:")
            import os
            
            if os.path.exists('calculator.py'):
                print("  ✅ calculator.py created")
                with open('calculator.py', 'r') as f:
                    lines = f.readlines()
                    print(f"     - {len(lines)} lines of code")
                    
            if os.path.exists('test_calculator.py'):
                print("  ✅ test_calculator.py created")
                with open('test_calculator.py', 'r') as f:
                    lines = f.readlines()
                    print(f"     - {len(lines)} lines of code")
            
            # Try to run the tests
            print("\n🧪 Running the created tests...")
            import subprocess
            try:
                result = subprocess.run(
                    ["python", "test_calculator.py"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print("  ✅ All tests passed!")
                    if result.stdout:
                        print(f"  Output: {result.stdout[:200]}")
                else:
                    print(f"  ⚠️ Tests failed with return code: {result.returncode}")
                    if result.stderr:
                        print(f"  Error: {result.stderr[:200]}")
            except subprocess.TimeoutExpired:
                print("  ⚠️ Tests timed out")
            except Exception as e:
                print(f"  ⚠️ Could not run tests: {e}")
                
        else:
            print("❌ Task failed")
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Make sure the EC2 instance has proper IAM role with Bedrock access")
        
    finally:
        # Cleanup
        await agent.cleanup()
        print("\n✅ Agent cleanup completed")
        
    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_calculator_creation())
