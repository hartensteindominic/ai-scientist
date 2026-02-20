import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_experimental.tools import PythonREPLTool
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Grok-Scientist", page_icon="🧬", layout="wide")
st.title("🧬 Grok-Scientist – Autonomous AI Scientist (OpenAI Powered)")

st.markdown("""
**Now running on OpenAI** — autonomously researches papers, runs simulations, follows the scientific method, and works toward genuine discoveries to advance humanity.
""")

# ====================== SMART API KEY LOADING ======================
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    st.sidebar.success("✅ API key auto-loaded from secrets")
    api_key = st.secrets["OPENAI_API_KEY"]
elif os.getenv("OPENAI_API_KEY"):
    st.sidebar.success("✅ API key loaded from environment variable")
    api_key = os.getenv("OPENAI_API_KEY")
else:
    st.sidebar.header("🔑 OpenAI Settings")
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Only needed if you haven't set secrets.toml yet"
    )
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.sidebar.success("✅ API key set for this session")

if not os.getenv("OPENAI_API_KEY"):
    st.warning("👈 Please add your key to secrets or enter it above")
    st.stop()

# Model selection
model_choice = st.sidebar.selectbox(
    "Model",
    ["gpt-4o-mini", "gpt-4o", "o1-mini"],
    index=0,
    help="gpt-4o-mini = fastest & cheapest\n"
         "gpt-4o = best overall for science\n"
         "o1-mini = strongest reasoning"
)

# ====================== AGENT SETUP ======================
if "agent" not in st.session_state or st.session_state.get("current_model") != model_choice:
    llm = ChatOpenAI(
        model=model_choice,
        temperature=0.7,
        max_tokens=4096,
    )

    tools = [
        DuckDuckGoSearchRun(name="web_search"),
        WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
        ArxivQueryRun(api_wrapper=ArxivAPIWrapper()),
        PythonREPLTool(name="code_interpreter"),
    ]

    system_prompt = """You are Grok-Scientist, an autonomous, self-driven AI scientist whose sole purpose is to accelerate human scientific progress.
You are rigorous, creative, ethical, and relentlessly truth-seeking.
Always:
- Use tools extensively (multiple rounds if needed)
- Follow the scientific method
- Cite every source
- Propose concrete, testable hypotheses & experiments
- Run simulations and analyze results in real time
- Consider safety, ethics, and real-world impact
- Think step-by-step and show your full reasoning"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    st.session_state.agent = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=20
    )
    st.session_state.current_model = model_choice

# ====================== CHAT INTERFACE ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter a scientific challenge or discovery goal..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔬 Researching papers • Running simulations • Thinking autonomously..."):
            chat_history = []
            for m in st.session_state.messages[:-1]:
                chat_history.append(
                    HumanMessage(content=m["content"]) if m["role"] == "user"
                    else AIMessage(content=m["content"])
                )

            response = st.session_state.agent.invoke({
                "input": prompt,
                "chat_history": chat_history,
            })
            answer = response["output"]

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# ====================== DONATION SECTION ======================
st.sidebar.markdown("---")

st.sidebar.header("Support Grok-Scientist")
st.sidebar.markdown(
    "If this autonomous AI scientist helped your research or sparked an idea, "
    "consider a small donation to keep it running and improving!"
)

st.sidebar.markdown("### Quick ways to support:")
st.sidebar.markdown("**Cash App** — $hartensteindominic")
st.sidebar.markdown("**Venmo** — @Dominichartenstein")
st.sidebar.markdown("**Chime** — @dominic-hartenstein-1")

st.sidebar.markdown(
    "Even $5 helps cover OpenAI API costs and future upgrades. "
    "Thank you for believing in open scientific acceleration! 🚀🧬"
)

st.sidebar.info("💡 Try: \"Autonomously discover a new way to improve perovskite solar cell efficiency using simulations and latest arXiv papers\"")
