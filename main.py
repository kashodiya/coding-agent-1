

#!/usr/bin/env python3
"""
Main entry point for the AI Coding Agent
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from chat_interface import main as run_chat


def check_environment():
    """Check environment for EC2 IAM role"""
    # When running on EC2 with IAM role, credentials are automatically handled
    # Just check if we can set the region if needed
    if not os.environ.get("AWS_REGION"):
        os.environ["AWS_REGION"] = "us-east-1"
        print("ℹ️  AWS_REGION not set, defaulting to us-east-1")
    
    print("✅ Using EC2 IAM role for AWS Bedrock access")
    return True


if __name__ == "__main__":
    print("🤖 AI Coding Agent - Powered by FastMCP and Bedrock")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
        
    # Run the chat interface
    try:
        asyncio.run(run_chat())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

