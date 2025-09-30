
#!/usr/bin/env python3
"""
Command-line chat interface for the AI Coding Agent
Provides an interactive terminal interface for chatting with the software engineer agent
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner

from ai_coding_agent import create_coding_agent, CodingAgent


# Custom style for the prompt
custom_style = Style.from_dict({
    'prompt': '#00aa00 bold',
    'input': '#ffffff',
})

# Command completions
command_completer = WordCompleter([
    '/help', '/exit', '/quit', '/clear', '/history', '/memory', '/plans',
    '/reset', '/save', '/load', '/status', '/tools'
], ignore_case=True)


class ChatInterface:
    """
    Interactive command-line interface for the AI Coding Agent
    """
    
    def __init__(self, agent: Optional[CodingAgent] = None):
        self.agent = agent
        self.console = Console()
        self.session = PromptSession(
            history=FileHistory('.chat_history'),
            auto_suggest=AutoSuggestFromHistory(),
            completer=command_completer,
            style=custom_style
        )
        self.running = True
        
    async def initialize(self):
        """Initialize the agent if not provided"""
        if not self.agent:
            self.console.print("\n[bold cyan]🚀 Initializing AI Coding Agent...[/bold cyan]")
            
            # When running on EC2 with IAM role, credentials are automatically handled
            # No need to check for explicit AWS credentials
            self.console.print("[dim]Using EC2 IAM role for AWS Bedrock access[/dim]")
                
            try:
                with self.console.status("[bold green]Loading agent components..."):
                    self.agent = await create_coding_agent()
                self.console.print("[bold green]✅ Agent initialized successfully![/bold green]\n")
                return True
            except Exception as e:
                self.console.print(f"[bold red]❌ Failed to initialize agent: {e}[/bold red]")
                self.console.print("[yellow]Note: Ensure this EC2 instance has an IAM role with Bedrock access[/yellow]")
                return False
        return True
        
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🤖 AI Coding Agent

Welcome to the AI Coding Agent - your intelligent software engineering assistant!

## Capabilities:
- 📝 Read, write, and modify files
- 🔍 Search through codebases
- 💻 Execute commands and Python code
- 📁 Manage directories and files
- 🔧 Git operations
- 🧠 Intelligent planning and task breakdown
- 💾 Persistent memory across sessions

## Commands:
- `/help` - Show this help message
- `/exit` or `/quit` - Exit the chat
- `/clear` - Clear the screen
- `/history` - Show conversation history
- `/memory` - Show agent's memory stats
- `/plans` - Show task plans
- `/status` - Show current status
- `/tools` - List available tools
- `/reset` - Reset agent memory
- `/save` - Save current session
- `/load` - Load previous session

## Usage:
Just type your request or question and press Enter. The agent will:
1. Understand your requirements
2. Create a plan if needed
3. Execute the task step by step
4. Learn from any errors
5. Provide you with the results

Type `/help` anytime to see this message again.
        """
        
        self.console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="cyan"))
        
    async def handle_command(self, command: str) -> bool:
        """
        Handle special commands
        Returns True if should continue, False if should exit
        """
        command = command.lower().strip()
        
        if command in ['/exit', '/quit']:
            self.console.print("\n[bold cyan]👋 Goodbye! Thanks for using AI Coding Agent.[/bold cyan]")
            return False
            
        elif command == '/help':
            self.display_welcome()
            
        elif command == '/clear':
            os.system('clear' if os.name == 'posix' else 'cls')
            
        elif command == '/history':
            if self.agent and self.agent.memory.conversation_history:
                table = Table(title="Conversation History", show_header=True)
                table.add_column("Time", style="cyan")
                table.add_column("Role", style="magenta")
                table.add_column("Message", style="white")
                
                for entry in self.agent.memory.conversation_history[-10:]:
                    timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M:%S")
                    role = entry['role'].capitalize()
                    message = entry['content'][:100] + "..." if len(entry['content']) > 100 else entry['content']
                    table.add_row(timestamp, role, message)
                    
                self.console.print(table)
            else:
                self.console.print("[yellow]No conversation history yet.[/yellow]")
                
        elif command == '/memory':
            if self.agent:
                memory_stats = Panel(
                    f"""
📊 Memory Statistics:
• Conversations: {len(self.agent.memory.conversation_history)}
• Task Plans: {len(self.agent.memory.task_plans)}
• Completed Tasks: {len(self.agent.memory.completed_tasks)}
• Learned Patterns: {len(self.agent.memory.learned_patterns)}
• Error Log Entries: {len(self.agent.memory.error_log)}
                    """,
                    title="Agent Memory",
                    border_style="green"
                )
                self.console.print(memory_stats)
            else:
                self.console.print("[yellow]Agent not initialized.[/yellow]")
                
        elif command == '/plans':
            if self.agent and self.agent.memory.task_plans:
                table = Table(title="Task Plans", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Description", style="white")
                table.add_column("Status", style="magenta")
                table.add_column("Steps", style="green")
                
                for plan in self.agent.memory.task_plans[-5:]:
                    table.add_row(
                        plan.task_id[:8],
                        plan.description[:50],
                        plan.status,
                        str(len(plan.steps))
                    )
                    
                self.console.print(table)
            else:
                self.console.print("[yellow]No task plans yet.[/yellow]")
                
        elif command == '/status':
            if self.agent:
                status = "🟢 Active" if self.agent.llm else "🔴 Inactive"
                current_plan = "None"
                if self.agent.current_plan:
                    current_plan = f"{self.agent.current_plan.description[:50]} ({self.agent.current_plan.status})"
                    
                status_panel = Panel(
                    f"""
🤖 Agent: {self.agent.name}
📊 Status: {status}
🧠 Model: {self.agent.model_id}
📋 Current Plan: {current_plan}
💾 Memory File: {self.agent.memory_file}
                    """,
                    title="Agent Status",
                    border_style="blue"
                )
                self.console.print(status_panel)
            else:
                self.console.print("[yellow]Agent not initialized.[/yellow]")
                
        elif command == '/tools':
            if self.agent and self.agent.agent:
                try:
                    tools = await self.agent.agent.list_tools()
                    table = Table(title="Available Tools", show_header=True)
                    table.add_column("Tool Name", style="cyan")
                    table.add_column("Description", style="white")
                    
                    for tool in tools:
                        name = tool.get('name', 'Unknown')
                        description = tool.get('description', 'No description')[:80]
                        table.add_row(name, description)
                        
                    self.console.print(table)
                except Exception as e:
                    self.console.print(f"[red]Error listing tools: {e}[/red]")
            else:
                self.console.print("[yellow]Agent not initialized.[/yellow]")
                
        elif command == '/reset':
            if self.agent:
                confirm = await self.session.prompt_async("Are you sure you want to reset agent memory? (y/n): ")
                if confirm.lower() == 'y':
                    self.agent.memory = type(self.agent.memory)()
                    await self.agent.memory.save_to_file(self.agent.memory_file)
                    self.console.print("[green]✅ Agent memory reset.[/green]")
                else:
                    self.console.print("[yellow]Reset cancelled.[/yellow]")
            else:
                self.console.print("[yellow]Agent not initialized.[/yellow]")
                
        elif command == '/save':
            if self.agent:
                await self.agent.memory.save_to_file(self.agent.memory_file)
                self.console.print(f"[green]✅ Session saved to {self.agent.memory_file}[/green]")
            else:
                self.console.print("[yellow]Agent not initialized.[/yellow]")
                
        elif command == '/load':
            if self.agent:
                self.agent.memory = await type(self.agent.memory).load_from_file(self.agent.memory_file)
                self.console.print(f"[green]✅ Session loaded from {self.agent.memory_file}[/green]")
            else:
                self.console.print("[yellow]Agent not initialized.[/yellow]")
                
        else:
            self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
            self.console.print("Type /help for available commands.")
            
        return True
        
    async def process_message(self, message: str):
        """Process a user message"""
        if not self.agent:
            self.console.print("[red]Agent not initialized. Please restart the application.[/red]")
            return
            
        try:
            # Show thinking indicator
            with self.console.status("[bold green]🤔 Agent is thinking..."):
                response = await self.agent.chat(message)
                
            # Display response
            self.console.print("\n[bold cyan]🤖 Agent:[/bold cyan]")
            
            # Format response as markdown if it contains code blocks or lists
            if "```" in response or "- " in response or "1. " in response:
                self.console.print(Markdown(response))
            else:
                self.console.print(Panel(response, border_style="cyan"))
                
        except Exception as e:
            self.console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
            self.console.print("[yellow]The agent encountered an error. You can try rephrasing your request.[/yellow]")
            
    async def run(self):
        """Main chat loop"""
        # Initialize agent
        if not await self.initialize():
            return
            
        # Display welcome message
        self.display_welcome()
        
        # Main chat loop
        while self.running:
            try:
                # Get user input
                user_input = await self.session.prompt_async(
                    "\n[bold green]You:[/bold green] ",
                    multiline=False
                )
                
                # Skip empty input
                if not user_input.strip():
                    continue
                    
                # Check if it's a command
                if user_input.startswith('/'):
                    self.running = await self.handle_command(user_input)
                else:
                    # Process as regular message
                    await self.process_message(user_input)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /exit to quit.[/yellow]")
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Unexpected error: {e}[/bold red]")
                continue
                
        # Cleanup
        if self.agent:
            await self.agent.cleanup()
            

async def main():
    """Main entry point"""
    interface = ChatInterface()
    await interface.run()
    

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)


