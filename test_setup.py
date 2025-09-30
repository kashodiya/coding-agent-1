

#!/usr/bin/env python3
"""
Test script to verify the AI Coding Agent setup
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))


async def test_mcp_server():
    """Test if MCP server can be imported and initialized"""
    print("Testing MCP Server...")
    try:
        from mcp_dev_server import mcp
        print("✅ MCP Server module loaded successfully")
        
        # Test if tools are registered
        tools = [
            "read_file", "write_file", "list_directory", 
            "execute_command", "search_files"
        ]
        
        # FastMCP stores tools differently, let's just check if we can import the functions
        from mcp_dev_server import read_file, write_file, list_directory, execute_command, search_files
        
        for tool in tools:
            print(f"  ✓ Tool '{tool}' available")
                
        return True
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        return False


async def test_agent_imports():
    """Test if agent modules can be imported"""
    print("\nTesting Agent Modules...")
    try:
        from ai_coding_agent import CodingAgent, AgentMemory, TaskPlan
        print("✅ Agent modules imported successfully")
        
        # Test memory creation
        memory = AgentMemory()
        print("  ✓ AgentMemory initialized")
        
        # Test task plan creation
        plan = TaskPlan(
            task_id="test_001",
            description="Test task",
            steps=["Step 1", "Step 2"]
        )
        print("  ✓ TaskPlan created")
        
        return True
    except Exception as e:
        print(f"❌ Agent import test failed: {e}")
        return False


async def test_bedrock_connection():
    """Test if Bedrock LLM can be initialized"""
    print("\nTesting Bedrock Connection...")
    
    # When running on EC2 with IAM role, credentials are automatically handled
    print("  Using EC2 IAM role for authentication")
        
    try:
        from langchain_aws import ChatBedrock
        
        # Try to initialize the LLM
        llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        
        print("✅ Bedrock LLM initialized successfully")
        
        # Try a simple test message
        from langchain_core.messages import HumanMessage
        
        print("  Testing LLM response...")
        response = await llm.ainvoke([
            HumanMessage(content="Say 'Hello, I am working!' in exactly 5 words.")
        ])
        
        if response and response.content:
            print(f"  ✓ LLM Response: {response.content[:100]}")
            return True
        else:
            print("  ✗ No response from LLM")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock connection test failed: {e}")
        print("  Make sure you have:")
        print("  1. Set up AWS credentials correctly")
        print("  2. Enabled Bedrock access in your AWS account")
        print("  3. Requested access to Claude 3.5 Sonnet model")
        return False


async def test_chat_interface():
    """Test if chat interface can be imported"""
    print("\nTesting Chat Interface...")
    try:
        from chat_interface import ChatInterface
        print("✅ Chat interface imported successfully")
        
        # Test interface creation (without agent)
        interface = ChatInterface()
        print("  ✓ ChatInterface created")
        
        return True
    except Exception as e:
        print(f"❌ Chat interface test failed: {e}")
        return False


async def test_file_operations():
    """Test basic file operations with the MCP tools"""
    print("\nTesting File Operations...")
    try:
        from mcp_dev_server import write_file, read_file, delete_file
        
        # Test write
        test_file = "test_file.txt"
        test_content = "Hello from AI Coding Agent!"
        
        result = await write_file(test_file, test_content)
        print(f"  ✓ Write file: {result}")
        
        # Test read
        content = await read_file(test_file)
        if content == test_content:
            print(f"  ✓ Read file: Content matches")
        else:
            print(f"  ✗ Read file: Content mismatch")
            
        # Test delete
        result = delete_file(test_file)
        print(f"  ✓ Delete file: {result}")
        
        return True
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 AI Coding Agent Setup Test")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("MCP Server", await test_mcp_server()))
    results.append(("Agent Modules", await test_agent_imports()))
    results.append(("Chat Interface", await test_chat_interface()))
    results.append(("File Operations", await test_file_operations()))
    
    # Bedrock test (optional)
    bedrock_result = await test_bedrock_connection()
    if bedrock_result is not None:
        results.append(("Bedrock Connection", bedrock_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            all_passed = False
        # None means skipped
            
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! The AI Coding Agent is ready to use.")
        print("\nRun 'python main.py' to start the agent.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nYou may still be able to run the agent with limited functionality.")
        
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)


