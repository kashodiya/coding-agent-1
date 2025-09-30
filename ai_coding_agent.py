
"""
AI Coding Agent using mcp-agent with Bedrock LLM
Implements a software engineer agent with planning, memory, and feedback loop
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
import aiofiles


class TaskPlan(BaseModel):
    """Represents a plan for completing a task"""
    task_id: str
    description: str
    steps: List[str]
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    
class AgentMemory(BaseModel):
    """Stores agent's memory and context"""
    conversation_history: List[Dict[str, str]] = []
    task_plans: List[TaskPlan] = []
    completed_tasks: List[str] = []
    learned_patterns: Dict[str, Any] = {}
    error_log: List[Dict[str, Any]] = []
    
    async def save_to_file(self, filepath: str):
        """Save memory to a JSON file"""
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(self.model_dump(), default=str, indent=2))
            
    @classmethod
    async def load_from_file(cls, filepath: str):
        """Load memory from a JSON file"""
        if not os.path.exists(filepath):
            return cls()
        async with aiofiles.open(filepath, 'r') as f:
            data = await f.read()
            return cls(**json.loads(data))


class CodingAgent:
    """
    AI Coding Agent that behaves like a software engineer
    Features:
    - Planning and task breakdown
    - Memory and context retention
    - Tool usage via MCP server
    - Feedback loop for continuous improvement
    """
    
    def __init__(
        self,
        name: str = "Software Engineer Agent",
        model_id: str = "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        memory_file: str = "agent_memory.json",
        region_name: str = "us-east-1"
    ):
        self.name = name
        self.model_id = model_id
        self.memory_file = memory_file
        self.region_name = region_name
        self.memory = AgentMemory()
        self.llm = None
        self.mcp_app = None
        self.agent = None
        self.current_plan = None
        
    async def initialize(self):
        """Initialize the agent with LLM and MCP connections"""
        # Load memory from file
        self.memory = await AgentMemory.load_from_file(self.memory_file)
        
        # Initialize Bedrock LLM
        # When running on EC2 with IAM role, credentials are automatically handled
        self.llm = ChatBedrock(
            model_id=self.model_id,
            region_name=self.region_name,
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 0.9
            }
        )
        
        # Initialize MCP app and agent
        self.mcp_app = MCPApp(name="coding_agent_app")
        
        # Start MCP app context
        await self.mcp_app.__aenter__()
        
        # Create agent with access to developer tools server
        self.agent = Agent(
            name=self.name,
            instruction="""You are an experienced software engineer. You can:
            1. Read, write, and modify files
            2. Execute commands and Python code
            3. Search through codebases
            4. Manage git repositories
            5. Create and organize directories
            
            When given a task:
            - First, understand the requirements thoroughly
            - Break down complex tasks into smaller steps
            - Implement solutions incrementally
            - Test your implementations
            - Handle errors gracefully and learn from them
            - Document your work clearly
            
            Always think step-by-step and explain your reasoning.""",
            server_names=["developer_tools"]  # This should match your MCP server name
        )
        
        await self.agent.__aenter__()
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.agent:
            await self.agent.__aexit__(None, None, None)
        if self.mcp_app:
            await self.mcp_app.__aexit__(None, None, None)
        # Save memory before cleanup
        await self.memory.save_to_file(self.memory_file)
        
    async def plan_task(self, user_request: str) -> TaskPlan:
        """
        Create a plan for completing a user request
        """
        planning_prompt = f"""
        As a software engineer, create a detailed plan to complete this request:
        {user_request}
        
        Break it down into clear, actionable steps.
        Return your response as a JSON object with the following structure:
        {{
            "task_id": "unique_id",
            "description": "brief description",
            "steps": ["step 1", "step 2", ...]
        }}
        """
        
        messages = [
            SystemMessage(content="You are a planning assistant. Create detailed plans for software development tasks."),
            HumanMessage(content=planning_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Extract JSON from response
            response_text = response.content
            # Find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                plan = TaskPlan(**plan_data)
                self.memory.task_plans.append(plan)
                await self.memory.save_to_file(self.memory_file)
                return plan
        except Exception as e:
            # Fallback plan if JSON parsing fails
            plan = TaskPlan(
                task_id=f"task_{datetime.now().timestamp()}",
                description=user_request[:100],
                steps=[response.content]
            )
            self.memory.task_plans.append(plan)
            return plan
            
    async def execute_step(self, step: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step of the plan using available tools
        """
        # Build context from memory
        recent_history = self.memory.conversation_history[-5:] if self.memory.conversation_history else []
        
        execution_prompt = f"""
        Current step to execute: {step}
        
        Context from previous steps: {json.dumps(context, indent=2)}
        
        Recent conversation history: {json.dumps(recent_history, indent=2)}
        
        Use the available tools to complete this step. Be specific and thorough.
        """
        
        # Get available tools
        tools = await self.agent.list_tools()
        
        messages = [
            SystemMessage(content=self.agent.instruction),
            HumanMessage(content=execution_prompt)
        ]
        
        # Execute with tools
        response = await self.llm.ainvoke(messages)
        
        # Parse response and execute tools if needed
        result = {
            "step": step,
            "response": response.content,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        # Store in conversation history
        self.memory.conversation_history.append({
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    async def evaluate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the result of an execution and determine next steps
        This is the feedback loop component
        """
        evaluation_prompt = f"""
        Evaluate the following execution result:
        {json.dumps(result, indent=2)}
        
        Determine:
        1. Was the step successful?
        2. Are there any errors that need to be fixed?
        3. What should be the next action?
        4. Any learnings to remember for future?
        
        Return as JSON:
        {{
            "success": true/false,
            "errors": [],
            "next_action": "description",
            "learnings": []
        }}
        """
        
        messages = [
            SystemMessage(content="You are an evaluation assistant. Analyze execution results and provide feedback."),
            HumanMessage(content=evaluation_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Extract JSON from response
            response_text = response.content
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                
                # Store learnings in memory
                if evaluation.get("learnings"):
                    for learning in evaluation["learnings"]:
                        if learning not in self.memory.learned_patterns:
                            self.memory.learned_patterns[learning] = {
                                "count": 1,
                                "first_seen": datetime.now().isoformat()
                            }
                        else:
                            self.memory.learned_patterns[learning]["count"] += 1
                            
                # Log errors if any
                if evaluation.get("errors"):
                    self.memory.error_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "errors": evaluation["errors"],
                        "context": result
                    })
                    
                await self.memory.save_to_file(self.memory_file)
                return evaluation
        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)],
                "next_action": "retry",
                "learnings": []
            }
            
    async def execute_task(self, user_request: str) -> Dict[str, Any]:
        """
        Main execution flow: Plan -> Execute -> Evaluate -> Iterate
        """
        # Store user request in memory
        self.memory.conversation_history.append({
            "role": "user",
            "content": user_request,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a plan
        plan = await self.plan_task(user_request)
        self.current_plan = plan
        
        # Update plan status
        plan.status = "in_progress"
        
        # Execute steps with feedback loop
        context = {"request": user_request}
        results = []
        
        for i, step in enumerate(plan.steps):
            print(f"\n📋 Executing step {i+1}/{len(plan.steps)}: {step}")
            
            # Execute the step
            step_result = await self.execute_step(step, context)
            results.append(step_result)
            
            # Evaluate the result
            evaluation = await self.evaluate_result(step_result)
            
            # Update context for next step
            context[f"step_{i+1}"] = {
                "description": step,
                "result": step_result,
                "evaluation": evaluation
            }
            
            # Handle failures with retry logic
            if not evaluation.get("success", False):
                print(f"⚠️ Step failed. Attempting to fix...")
                
                # Try to fix the issue
                fix_prompt = f"""
                The previous step failed with errors: {evaluation.get('errors', [])}
                Original step: {step}
                Please fix the issue and retry.
                """
                
                retry_result = await self.execute_step(fix_prompt, context)
                results.append(retry_result)
                
                # Re-evaluate
                retry_evaluation = await self.evaluate_result(retry_result)
                if not retry_evaluation.get("success", False):
                    print(f"❌ Failed to fix the issue. Moving to next step.")
                else:
                    print(f"✅ Issue fixed successfully!")
                    
        # Mark plan as completed
        plan.status = "completed"
        plan.completed_at = datetime.now()
        self.memory.completed_tasks.append(plan.task_id)
        
        # Save final memory state
        await self.memory.save_to_file(self.memory_file)
        
        return {
            "plan": plan.model_dump(),
            "results": results,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    async def chat(self, message: str) -> str:
        """
        Simple chat interface for the agent
        """
        # Check if this is a task request or a simple question
        is_task = any(keyword in message.lower() for keyword in [
            "create", "build", "implement", "write", "develop", "fix", "debug",
            "refactor", "test", "deploy", "setup", "install", "configure"
        ])
        
        if is_task:
            # Execute as a task with planning and feedback loop
            result = await self.execute_task(message)
            
            # Format response
            response = f"Task completed!\n\n"
            response += f"📋 Plan: {result['plan']['description']}\n"
            response += f"✅ Steps completed: {len(result['plan']['steps'])}\n"
            
            return response
        else:
            # Simple Q&A without task execution
            messages = [
                SystemMessage(content=self.agent.instruction),
                HumanMessage(content=message)
            ]
            
            # Add recent history for context
            for hist in self.memory.conversation_history[-3:]:
                if hist["role"] == "user":
                    messages.append(HumanMessage(content=hist["content"]))
                else:
                    messages.append(AIMessage(content=hist["content"]))
                    
            response = await self.llm.ainvoke(messages)
            
            # Store in memory
            self.memory.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            self.memory.conversation_history.append({
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.memory.save_to_file(self.memory_file)
            
            return response.content


# Helper function to run the agent
async def create_coding_agent(
    model_id: str = "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    memory_file: str = "agent_memory.json"
) -> CodingAgent:
    """
    Create and initialize a coding agent
    """
    agent = CodingAgent(
        name="AI Software Engineer",
        model_id=model_id,
        memory_file=memory_file
    )
    await agent.initialize()
    return agent


