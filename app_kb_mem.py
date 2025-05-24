import os
import streamlit as st
from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_llm, memory, mem0_memory

# Import the specialized assistants
from strands_multi_agent_example.computer_science_assistant import computer_science_assistant
from strands_multi_agent_example.english_assistant import english_assistant
from strands_multi_agent_example.language_assistant import language_assistant
from strands_multi_agent_example.math_assistant import math_assistant
from strands_multi_agent_example.no_expertise import general_assistant

# Define the teacher's assistant system prompt
TEACHER_SYSTEM_PROMPT = """
You are TeachAssist, a sophisticated educational orchestrator designed to coordinate educational support across multiple subjects. Your role is to:

1. Analyze incoming student queries and determine the most appropriate specialized agent to handle them:
   - Math Agent: For mathematical calculations, problems, and concepts
   - English Agent: For writing, grammar, literature, and composition
   - Language Agent: For translation and language-related queries
   - Computer Science Agent: For programming, algorithms, data structures, and code execution
   - General Assistant: For all other topics outside these specialized domains

2. Key Responsibilities:
   - Accurately classify student queries by subject area
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed

3. Decision Protocol:
   - If query involves calculations/numbers → Math Agent
   - If query involves writing/literature/grammar → English Agent
   - If query involves translation → Language Agent
   - If query involves programming/coding/algorithms/computer science → Computer Science Agent
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

# System prompt to determine action
ACTION_SYSTEM_PROMPT = """
You are an assistant that determines whether a query should be handled by:
1. A teacher agent for educational questions (math, language, English, computer science, general knowledge)
2. A knowledge base agent for personal information storage and retrieval

Reply with EXACTLY ONE WORD - either "teacher" or "knowledgebase".
DO NOT include any explanations or other text.

Examples:
- "What is the capital of France?" -> "teacher"
- "How do I solve this equation: 2x + 5 = 15?" -> "teacher"
- "Translate 'hello' to Spanish" -> "teacher"
- "Remember that my birthday is July 4" -> "knowledgebase"
- "What's my birthday?" -> "knowledgebase"
- "My favorite color is blue" -> "knowledgebase"
- "What is my favorite color?" -> "knowledgebase"

Only respond with "teacher" or "knowledgebase" - no explanation, prefix, or any other text.
"""

# System prompt for knowledge base actions
KB_ACTION_SYSTEM_PROMPT = """
You are a knowledge base assistant focusing ONLY on classifying user queries.
Your task is to determine whether a user query requires STORING information to a knowledge base
or RETRIEVING information from a knowledge base.

Reply with EXACTLY ONE WORD - either "store" or "retrieve".
DO NOT include any explanations or other text.

Examples:
- "Remember that my birthday is July 4" -> "store"
- "What's my birthday?" -> "retrieve"
- "The capital of France is Paris" -> "store"
- "What is the capital of France?" -> "retrieve"
- "My name is John" -> "store" 
- "Who am I?" -> "retrieve"
- "I live in Seattle" -> "store"
- "Where do I live?" -> "retrieve"

Only respond with "store" or "retrieve" - no explanation, prefix, or any other text.
"""

# System prompt for generating answers from retrieved information
ANSWER_SYSTEM_PROMPT = """
You are a helpful knowledge assistant that provides clear, concise answers 
based on information retrieved from a knowledge base.

The information from the knowledge base contains document IDs, titles, 
content previews and relevance scores. Focus on the actual content and 
ignore the metadata.

Your responses should:
1. Be direct and to the point
2. Not mention the source of information (like document IDs or scores)
3. Not include any metadata or technical details
4. Be conversational but brief
5. Acknowledge when information is conflicting or missing
6. Begin the response with \n

When analyzing the knowledge base results:
- Higher scores (closer to 1.0) indicate more relevant results
- Look for patterns across multiple results
- Prioritize information from results with higher scores
- Ignore any JSON formatting or technical elements in the content

Example response for conflicting information:
"Based on my records, I have both July 4 and August 8 listed as your birthday. Could you clarify which date is correct?"

Example response for clear information:
"Your birthday is on July 4."

Example response for missing information:
"I don't have any information about your birthday stored."
"""

# System prompt for the memory agent
MEMORY_SYSTEM_PROMPT = """You are a personal assistant that maintains context by remembering user details.

Capabilities:
- Store new information using mem0_memory tool (action="store")
- Retrieve relevant memories (action="retrieve")
- List all memories (action="list")
- Provide personalized responses

Key Rules:
- Always include user_id=mem0_user in tool calls
- Be conversational and natural in responses
- Format output clearly
- Acknowledge stored information
- Only share relevant information
- Politely indicate when information is unavailable
"""

# Check if OpenSearch is available
OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST', None)

# Set up the page
st.set_page_config(page_title="TeachAssist - Educational Assistant", layout="wide")
st.title("TeachAssist - Educational Assistant")
st.write("Ask a question in any subject area or store/retrieve personal information.")

# Initialize session state for conversation history and settings
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "memory_backend" not in st.session_state:
    st.session_state.memory_backend = "bedrock_kb"
    
if "model_id" not in st.session_state:
    st.session_state.model_id = "us.amazon.nova-pro-v1:0"
    
if "enabled_agents" not in st.session_state:
    st.session_state.enabled_agents = {
        "math_assistant": True,
        "language_assistant": True,
        "english_assistant": True,
        "computer_science_assistant": True,
        "general_assistant": True
    }

# Add sidebar for settings
st.sidebar.title("Settings")

# Memory backend selection
st.sidebar.subheader("Memory Backend")
memory_options = ["Bedrock Knowledge Base"]
if OPENSEARCH_HOST:
    memory_options.append("OpenSearch Memory")
    
selected_backend = st.sidebar.radio(
    "Select memory backend:",
    memory_options,
    disabled=not OPENSEARCH_HOST and len(memory_options) > 1
)

# Update the memory backend based on selection
if selected_backend == "Bedrock Knowledge Base":
    st.session_state.memory_backend = "bedrock_kb"
elif selected_backend == "OpenSearch Memory":
    st.session_state.memory_backend = "opensearch"

# Model selection
st.sidebar.subheader("Model Selection")
model_options = [
    "us.amazon.nova-pro-v1:0",
    "us.amazon.nova-lite-v1:0",
    "us.amazon.nova-micro-v1:0",
    "anthropic.claude-3-5-haiku-20241022-v1:0",
    "anthropic.claude-3-7-sonnet-20250219-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0"
]
selected_model = st.sidebar.selectbox(
    "Select Bedrock model:",
    model_options,
    index=model_options.index(st.session_state.model_id)
)
st.session_state.model_id = selected_model

# Teacher agent toggles
st.sidebar.subheader("Teacher Agents")
st.session_state.enabled_agents["math_assistant"] = st.sidebar.checkbox(
    "Math Assistant", 
    value=st.session_state.enabled_agents["math_assistant"]
)
st.session_state.enabled_agents["language_assistant"] = st.sidebar.checkbox(
    "Language Assistant", 
    value=st.session_state.enabled_agents["language_assistant"]
)
st.session_state.enabled_agents["english_assistant"] = st.sidebar.checkbox(
    "English Assistant", 
    value=st.session_state.enabled_agents["english_assistant"]
)
st.session_state.enabled_agents["computer_science_assistant"] = st.sidebar.checkbox(
    "Computer Science Assistant", 
    value=st.session_state.enabled_agents["computer_science_assistant"]
)
st.session_state.enabled_agents["general_assistant"] = st.sidebar.checkbox(
    "General Assistant", 
    value=st.session_state.enabled_agents["general_assistant"]
)

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize the teacher agent
@st.cache_resource(hash_funcs={dict: lambda _: None})
def get_teacher_agent():
    # Specify the Bedrock ModelID from session state
    bedrock_model = BedrockModel(
        model_id=st.session_state.model_id,
        temperature=0.3,
    )
    
    # Filter tools based on enabled agents
    enabled_tools = []
    if st.session_state.enabled_agents["math_assistant"]:
        enabled_tools.append(math_assistant)
    if st.session_state.enabled_agents["language_assistant"]:
        enabled_tools.append(language_assistant)
    if st.session_state.enabled_agents["english_assistant"]:
        enabled_tools.append(english_assistant)
    if st.session_state.enabled_agents["computer_science_assistant"]:
        enabled_tools.append(computer_science_assistant)
    if st.session_state.enabled_agents["general_assistant"]:
        enabled_tools.append(general_assistant)
    
    # Ensure at least one tool is available
    if not enabled_tools:
        enabled_tools = [general_assistant]
    
    # Create the teacher agent with specialized tools
    return Agent(
        model=bedrock_model,
        system_prompt=TEACHER_SYSTEM_PROMPT,
        callback_handler=None,
        tools=enabled_tools,
    )

# Initialize the knowledge base agent
@st.cache_resource(hash_funcs={dict: lambda _: None})
def get_kb_agent():
    # Specify the Bedrock ModelID from session state
    bedrock_model = BedrockModel(
        model_id=st.session_state.model_id,
        temperature=0.3,
    )
    
    # Create the knowledge base agent with memory tools
    return Agent(
        model=bedrock_model,
        tools=[memory, use_llm],
    )

# Initialize the OpenSearch memory agent
@st.cache_resource(hash_funcs={dict: lambda _: None})
def get_memory_agent():
    # Specify the Bedrock ModelID from session state
    bedrock_model = BedrockModel(
        model_id=st.session_state.model_id,
        temperature=0.3,
    )
    
    # Create the memory agent with OpenSearch memory tools
    return Agent(
        model=bedrock_model,
        system_prompt=MEMORY_SYSTEM_PROMPT,
        tools=[mem0_memory, use_llm],
    )

def determine_action(query):
    """Determine if the query should be handled by the teacher agent or knowledge base agent."""
    agent = get_kb_agent()
    
    result = agent.tool.use_llm(
        prompt=f"Query: {query}",
        system_prompt=ACTION_SYSTEM_PROMPT
    )
    
    # Clean and extract the action
    action_text = str(result).lower().strip()
    
    # Determine which agent to use
    if "teacher" in action_text:
        return "teacher"
    else:
        return "knowledgebase"

def run_kb_agent(query):
    """Process a user query with the knowledge base agent."""
    agent = get_kb_agent()
    
    # Determine the action - store or retrieve
    result = agent.tool.use_llm(
        prompt=f"Query: {query}",
        system_prompt=KB_ACTION_SYSTEM_PROMPT
    )
    
    # Clean and extract the action
    action_text = str(result).lower().strip()
    
    # Default to retrieve if response isn't clear
    if "store" in action_text:
        # For store actions, store the full query
        agent.tool.memory(action="store", content=query)
        return "I've stored this information."
    else:
        # For retrieve actions, query the knowledge base with appropriate parameters
        result = agent.tool.memory(
            action="retrieve", 
            query=query,
            min_score=0.4,  # Set reasonable minimum score threshold
            max_results=9   # Retrieve a good number of results
        )
        # Convert the result to a string to extract just the content text
        result_str = str(result)
        
        # Generate a clear, conversational answer using the retrieved information
        answer = agent.tool.use_llm(
            prompt=f"User question: \"{query}\"\n\nInformation from knowledge base:\n{result_str}\n\nStart your answer with newline character and provide a helpful answer based on this information:",
            system_prompt=ANSWER_SYSTEM_PROMPT
        )
        
        return str(answer)

def run_memory_agent(query):
    """Process a user query with the OpenSearch memory agent."""
    agent = get_memory_agent()
    
    # Determine the action - store or retrieve
    result = agent.tool.use_llm(
        prompt=f"Query: {query}",
        system_prompt=KB_ACTION_SYSTEM_PROMPT
    )
    
    # Clean and extract the action
    action_text = str(result).lower().strip()
    
    # Default to retrieve if response isn't clear
    if "store" in action_text:
        # For store actions, store the full query
        agent.tool.mem0_memory(action="store", content=query, user_id="mem0_user")
        return "I've stored this information."
    else:
        # For retrieve actions, query the memory with appropriate parameters
        result = agent.tool.mem0_memory(
            action="retrieve", 
            query=query,
            user_id="mem0_user",
            max_results=9
        )
        
        # If no results, try listing all memories
        if not result:
            result = agent.tool.mem0_memory(
                action="list",
                user_id="mem0_user"
            )
        
        # Convert the result to a string
        result_str = str(result)
        
        # Generate a clear, conversational answer using the retrieved information
        answer = agent.tool.use_llm(
            prompt=f"User question: \"{query}\"\n\nInformation from memory:\n{result_str}\n\nStart your answer with newline character and provide a helpful answer based on this information:",
            system_prompt=ANSWER_SYSTEM_PROMPT
        )
        
        return str(answer)

# Get user input
query = st.chat_input("Ask your question here...")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Determine which agent should handle the query
            with st.spinner("Analyzing query..."):
                action = determine_action(query)
            
            content = ""
            if action == "teacher":
                # Get the teacher agent
                teacher_agent = get_teacher_agent()
                
                # Process the query with the teacher agent
                with st.spinner("Consulting educational specialists..."):
                    response = teacher_agent(query)
                    content = str(response)
            else:
                # Process the query with the selected memory backend
                if st.session_state.memory_backend == "bedrock_kb":
                    with st.spinner("Accessing Bedrock knowledge base..."):
                        content = run_kb_agent(query)
                elif st.session_state.memory_backend == "opensearch" and OPENSEARCH_HOST:
                    with st.spinner("Accessing OpenSearch memory..."):
                        content = run_memory_agent(query)
                else:
                    # Fallback to Bedrock KB if OpenSearch is not available
                    with st.spinner("Accessing Bedrock knowledge base (OpenSearch not available)..."):
                        content = run_kb_agent(query)
            
            # Display the response
            message_placeholder.markdown(content)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": content})
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
