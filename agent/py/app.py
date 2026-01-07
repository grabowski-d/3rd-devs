"""Demo agent application."""
import asyncio
from agent_service import AgentService
from types import State


async def main():
    """Run agent demo."""
    # Initialize state
    state = State(
        messages=[{
            'role': 'user',
            'content': 'What are the latest developments in AI?'
        }]
    )
    
    # Create agent
    agent = AgentService(state)
    
    print('Starting agent...\n')
    
    # Execute agent loop
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f'Iteration {iteration}:')
        
        # Plan next action
        plan = await agent.plan()
        if not plan:
            print('No plan found')
            break
        
        print(f'  Tool: {plan.get("tool")}')
        print(f'  Reasoning: {plan.get("_reasoning")}')
        
        # Check if final answer
        if plan.get('tool') == 'final_answer':
            print(f'  Query: {plan.get("query")}')
            break
        
        # Get parameters
        params = await agent.describe(plan['tool'], plan['query'])
        print(f'  Parameters: {params}')
        
        # Execute tool
        await agent.use_tool(plan['tool'], params, 'test-conversation')
        print()
    
    # Generate final answer
    if state.actions:
        print('\nGenerating final answer...')
        answer = await agent.generate_answer()
        print(f'\nFinal Answer:\n{answer}')


if __name__ == '__main__':
    asyncio.run(main())
