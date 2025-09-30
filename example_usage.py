

#!/usr/bin/env python3
"""
Example usage of the AI Coding Agent
This demonstrates how to use the agent programmatically without the chat interface
"""

import asyncio
import os
from ai_coding_agent import CodingAgent


async def example_simple_task():
    """Example of a simple coding task"""
    # Create and initialize the agent
    agent = CodingAgent(
        name="Example Agent",
        model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        memory_file="example_memory.json"
    )
    
    # Note: This will only work if AWS credentials are set
    # await agent.initialize()
    
    # Example task
    task = "Create a Python function that calculates the factorial of a number"
    
    # Execute the task
    # result = await agent.execute_task(task)
    
    # Print results
    # print(f"Task completed: {result['success']}")
    # print(f"Plan: {result['plan']['description']}")
    
    # Cleanup
    # await agent.cleanup()
    
    print("Note: To run this example, you need to:")
    print("1. Set AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)")
    print("2. Uncomment the code above")
    print("3. Ensure you have Bedrock access enabled in your AWS account")


async def example_with_memory():
    """Example showing how memory persists across sessions"""
    print("\n=== Memory Persistence Example ===")
    
    # First session
    agent1 = CodingAgent(memory_file="persistent_memory.json")
    # await agent1.initialize()
    
    # Add some context to memory
    agent1.memory.conversation_history.append({
        "role": "user",
        "content": "My project uses FastAPI",
        "timestamp": "2024-01-01T10:00:00"
    })
    
    agent1.memory.learned_patterns["use_fastapi"] = {
        "count": 1,
        "first_seen": "2024-01-01T10:00:00"
    }
    
    # Save memory
    await agent1.memory.save_to_file("persistent_memory.json")
    print("✓ First session: Added context about FastAPI")
    
    # Second session - memory is retained
    agent2 = CodingAgent(memory_file="persistent_memory.json")
    agent2.memory = await agent2.memory.load_from_file("persistent_memory.json")
    
    print(f"✓ Second session: Found {len(agent2.memory.conversation_history)} conversations")
    print(f"✓ Second session: Found {len(agent2.memory.learned_patterns)} learned patterns")
    
    # The agent remembers the context
    if "use_fastapi" in agent2.memory.learned_patterns:
        print("✓ Agent remembers: Project uses FastAPI")


async def example_planning():
    """Example showing the planning capability"""
    print("\n=== Planning Example ===")
    
    from ai_coding_agent import TaskPlan
    from datetime import datetime
    
    # Create a sample plan
    plan = TaskPlan(
        task_id="example_001",
        description="Build a REST API for a todo application",
        steps=[
            "1. Set up project structure",
            "2. Create database models",
            "3. Implement CRUD operations",
            "4. Add authentication",
            "5. Write tests",
            "6. Add documentation"
        ],
        status="pending",
        created_at=datetime.now()
    )
    
    print(f"✓ Created plan: {plan.description}")
    print(f"✓ Number of steps: {len(plan.steps)}")
    
    # Simulate executing steps
    plan.status = "in_progress"
    print(f"✓ Status updated to: {plan.status}")
    
    # Mark as completed
    plan.status = "completed"
    plan.completed_at = datetime.now()
    print(f"✓ Plan completed!")


async def example_tools():
    """Example showing direct tool usage"""
    print("\n=== Direct Tool Usage Example ===")
    
    from mcp_dev_server import (
        write_file, read_file, list_directory,
        execute_python, get_file_info
    )
    
    # Create a test file
    test_file = "example_test.py"
    code = """
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("AI Agent"))
"""
    
    # Write file
    result = await write_file(test_file, code)
    print(f"✓ {result}")
    
    # Get file info
    info = get_file_info(test_file)
    print(f"✓ File size: {info['size']} bytes")
    print(f"✓ Lines of code: {info.get('line_count', 'N/A')}")
    
    # Execute the Python code
    exec_result = execute_python(code)
    if exec_result['success']:
        print(f"✓ Code output: {exec_result['stdout'].strip()}")
    
    # List directory
    dir_contents = list_directory(".")
    print(f"✓ Files in directory: {len(dir_contents['files'])}")
    
    # Clean up
    import os
    os.remove(test_file)
    print(f"✓ Cleaned up test file")


async def main():
    """Run all examples"""
    print("🤖 AI Coding Agent - Usage Examples")
    print("=" * 40)
    
    # Run examples that don't require AWS credentials
    await example_with_memory()
    await example_planning()
    await example_tools()
    
    # This requires AWS credentials
    await example_simple_task()
    
    print("\n" + "=" * 40)
    print("✅ Examples completed!")
    print("\nTo use the full agent with Bedrock LLM:")
    print("1. Set up AWS credentials")
    print("2. Run: python main.py")


if __name__ == "__main__":
    asyncio.run(main())


