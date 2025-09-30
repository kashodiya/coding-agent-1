#!/usr/bin/env python3
"""
Direct test of MCP server tools without the full agent
"""

import asyncio
from mcp_dev_server import write_file, read_file, execute_python

async def test_direct_tools():
    """Test the MCP server tools directly"""
    
    print("=" * 60)
    print("🧪 Testing MCP Server Tools Directly")
    print("=" * 60)
    
    # Create a simple calculator
    calculator_code = '''#!/usr/bin/env python3
"""
Simple Calculator with basic arithmetic operations
"""

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract b from a"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide a by b, handling division by zero"""
    if b == 0:
        return "Error: Division by zero"
    return a / b

def main():
    """Demonstrate calculator operations"""
    print("Simple Calculator Demo")
    print("=" * 30)
    
    # Test values
    x, y = 10, 5
    
    print(f"Numbers: {x} and {y}")
    print(f"Addition: {x} + {y} = {add(x, y)}")
    print(f"Subtraction: {x} - {y} = {subtract(x, y)}")
    print(f"Multiplication: {x} * {y} = {multiply(x, y)}")
    print(f"Division: {x} / {y} = {divide(x, y)}")
    
    # Test division by zero
    print(f"\\nDivision by zero: {x} / 0 = {divide(x, 0)}")

if __name__ == "__main__":
    main()
'''
    
    # Write the calculator file
    print("\n📝 Writing calculator file...")
    result = await write_file("test_workspace/calculator.py", calculator_code)
    print(f"✅ File written: {result}")
    
    # Read it back
    print("\n📖 Reading calculator file...")
    content = await read_file("test_workspace/calculator.py")
    print(f"✅ File has {len(content)} characters")
    
    # Execute it
    print("\n🏃 Running calculator...")
    # Read the file content first
    calc_code = await read_file("test_workspace/calculator.py")
    # Execute the code
    output = execute_python(calc_code)
    print("Output:")
    print("-" * 40)
    if output['success']:
        print(output['stdout'])
    else:
        print(f"Error: {output.get('stderr', output.get('error'))}")
    print("-" * 40)
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_direct_tools())
