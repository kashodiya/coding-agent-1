

# 🤖 AI Coding Agent

An intelligent software engineering assistant powered by **FastMCP**, **mcp-agent**, and **AWS Bedrock LLM**. This agent behaves like an experienced software engineer, capable of planning, executing, and learning from development tasks.

## ✨ Features

### Core Capabilities
- **📝 File Operations**: Read, write, modify, and manage files
- **📁 Directory Management**: Create, list, and organize directories
- **💻 Code Execution**: Execute shell commands and Python code
- **🔍 Code Search**: Search through codebases with pattern matching
- **🔧 Git Operations**: Check status, view diffs, and manage repositories

### Intelligent Agent Features
- **🧠 Planning**: Breaks down complex tasks into actionable steps
- **💾 Memory**: Persistent memory across sessions for context retention
- **🔄 Feedback Loop**: Learns from errors and improves over time
- **📊 Task Tracking**: Monitors progress and maintains task history
- **🎯 Goal-Oriented**: Focuses on completing user objectives efficiently

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **AWS Account** with Bedrock access enabled
3. **EC2 Instance** with IAM role that has Bedrock access permissions

### Installation

1. Clone or download this repository:
```bash
cd /workspace/ai-coding-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. AWS Authentication:
   - **On EC2**: The instance IAM role automatically provides credentials
   - **Optional**: Set region if different from us-east-1:
     ```bash
     export AWS_REGION='your-preferred-region'
     ```
   - **Local Development**: If not on EC2, you can still use explicit credentials:
     ```bash
     export AWS_ACCESS_KEY_ID='your-access-key'
     export AWS_SECRET_ACCESS_KEY='your-secret-key'
     ```

### Running the Agent

```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py chat_interface.py
./main.py
```

## 💬 Usage

### Basic Commands

Once the agent is running, you can:

- **Ask questions**: "What is a REST API?"
- **Request tasks**: "Create a Python function to calculate fibonacci numbers"
- **Debug code**: "Fix the syntax error in this code: ..."
- **Build features**: "Create a web scraper for news articles"

### Special Commands

- `/help` - Show help message and capabilities
- `/exit` or `/quit` - Exit the chat
- `/clear` - Clear the screen
- `/history` - Show conversation history
- `/memory` - Display agent's memory statistics
- `/plans` - Show task plans
- `/status` - Show current agent status
- `/tools` - List available tools
- `/reset` - Reset agent memory
- `/save` - Save current session
- `/load` - Load previous session

## 🏗️ Architecture

### Components

1. **MCP Server (`mcp_dev_server.py`)**
   - Implements developer tools using FastMCP
   - Provides file operations, code execution, and git tools
   - Runs as a separate process accessible via MCP protocol

2. **AI Coding Agent (`ai_coding_agent.py`)**
   - Core agent logic with planning and execution
   - Integrates with AWS Bedrock LLM (Claude 3.5 Sonnet)
   - Implements memory management and feedback loops
   - Connects to MCP server for tool usage

3. **Chat Interface (`chat_interface.py`)**
   - Command-line interface using prompt-toolkit
   - Rich formatting with syntax highlighting
   - Interactive commands and session management

4. **Main Entry Point (`main.py`)**
   - Environment validation
   - Application initialization
   - Error handling

### Agent Workflow

```
User Request
    ↓
Planning Phase (Break down into steps)
    ↓
For each step:
    ├─→ Execute Step (using MCP tools)
    ├─→ Evaluate Result (feedback loop)
    └─→ Learn & Adapt (store in memory)
    ↓
Return Results to User
```

## 🧠 How It Works

### Planning
When given a task, the agent:
1. Analyzes the requirements
2. Creates a detailed plan with steps
3. Stores the plan in memory

### Execution
For each step in the plan:
1. Uses available tools via MCP server
2. Executes commands or code
3. Captures results and errors

### Feedback Loop
After each execution:
1. Evaluates success/failure
2. Identifies errors to fix
3. Learns patterns for future use
4. Retries if necessary

### Memory
The agent maintains:
- Conversation history
- Task plans and results
- Learned patterns
- Error logs
- Completed tasks

Memory is persisted in `agent_memory.json` between sessions.

## 🛠️ Available Tools

The MCP server provides these tools:

### File Operations
- `read_file` - Read file contents
- `write_file` - Write content to file
- `append_file` - Append to existing file
- `delete_file` - Delete a file
- `move_file` - Move or rename files
- `copy_file` - Copy files or directories

### Directory Operations
- `list_directory` - List directory contents
- `create_directory` - Create new directories
- `delete_directory` - Remove directories

### Code Execution
- `execute_command` - Run shell commands
- `execute_python` - Execute Python code

### Search & Analysis
- `search_files` - Search for patterns in files
- `get_file_info` - Get file metadata

### Git Operations
- `git_status` - Check repository status
- `git_diff` - View changes

## 🔧 Configuration

### Model Configuration
The agent uses Claude 3.5 Sonnet by default. To change the model, edit `ai_coding_agent.py`:

```python
model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
```

### Memory File
Agent memory is stored in `agent_memory.json`. You can:
- Back it up to preserve context
- Delete it to start fresh
- Share it to transfer context

### MCP Server Configuration
The MCP server configuration is in `mcp_config.json`. Modify it to:
- Add more MCP servers
- Change server parameters
- Set environment variables

## 📝 Examples

### Example 1: Create a Python Script
```
You: Create a Python script that fetches weather data from an API

Agent: I'll create a Python script to fetch weather data. Let me break this down:
1. Create the script file
2. Add necessary imports
3. Implement API fetching logic
4. Add error handling
5. Test the script
...
```

### Example 2: Debug Code
```
You: Fix this code that's giving an error:
def calculate_average(numbers)
    return sum(numbers) / len(numbers)

Agent: I can see the syntax error. The function definition is missing a colon...
```

### Example 3: Build a Feature
```
You: Build a todo list application with add, remove, and list functions

Agent: I'll create a todo list application with the requested features...
```

## 🐛 Troubleshooting

### AWS Authentication Error
If you encounter authentication issues:
1. **On EC2**: Ensure the instance has an IAM role with Bedrock permissions
2. **IAM Role Permissions**: The role should include:
   - `bedrock:InvokeModel` permission
   - Access to the Claude 3.5 Sonnet model
3. **Local Development**: Set AWS credentials as environment variables
4. Verify Bedrock access is enabled in your AWS account and region

### MCP Server Connection Error
If the agent can't connect to MCP server:
1. Check that `mcp_dev_server.py` is in the same directory
2. Ensure all dependencies are installed
3. Try running the MCP server directly: `python mcp_dev_server.py`

### Memory Issues
If the agent behaves unexpectedly:
1. Check `agent_memory.json` for corruption
2. Use `/reset` command to clear memory
3. Delete `agent_memory.json` to start fresh

## 🤝 Contributing

Feel free to enhance the agent by:
- Adding more tools to the MCP server
- Improving the planning algorithms
- Enhancing the feedback loop logic
- Adding support for more LLM providers
- Creating specialized agent behaviors

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **FastMCP** - For the excellent MCP framework
- **mcp-agent** - For agent patterns and architecture
- **AWS Bedrock** - For providing powerful LLM capabilities
- **Anthropic** - For Claude 3.5 Sonnet model

---

Built with ❤️ using FastMCP, mcp-agent, and AWS Bedrock


